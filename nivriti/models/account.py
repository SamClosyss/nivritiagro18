from odoo import fields, api, models, _
from num2words import num2words
import re
from odoo.tools import is_html_empty


# Added but then not needed in 18
# class InheritAccountPayment(models.Model):
#     _inherit = 'account.payment'
#
#     is_internal_transfer = fields.Boolean(string="Internal Transfer",
#                                           readonly=False, store=True,
#                                           tracking=True,
#                                           compute="_compute_is_internal_transfer")
#
#     @api.depends('partner_id', 'journal_id', 'destination_journal_id')
#     def _compute_is_internal_transfer(self):
#         for payment in self:
#             payment.is_internal_transfer = payment.partner_id \
#                                            and payment.partner_id == payment.journal_id.company_id.partner_id \
#                                            and payment.destination_journal_id
#             if self.env.context.get('is_contra_entry'):
#                 self.is_internal_transfer = True


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    po_date = fields.Date('PO Date')

    show_update_fpos = fields.Char()

    def action_update_fpos_values(self):
        pass

    # Over ride the function to
    @api.depends('move_type', 'partner_id', 'company_id')
    def _compute_narration(self):
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms')
        for move in self:
            if not move.is_sale_document(include_receipts=True):
                continue
            if not use_invoice_terms:
                move.narration = False
            else:
                lang = move.partner_id.lang or self.env.user.lang
                if not move.company_id.terms_type == 'html':
                    narration = move.company_id.sudo().with_context(lang=lang).invoice_terms if not is_html_empty(
                        move.company_id.sudo().invoice_terms) else ''
                else:
                    baseurl = self.env.company.get_base_url() + '/terms'
                    context = {'lang': lang}
                    narration = _('Terms & Conditions: %s', baseurl)
                    del context
                move.narration = narration or False

    def get_default_terms(self):
        config_settings = self.env['res.config.settings'].search([])
        for rec in config_settings:
            return rec.invoice_terms

    def cal_hsn_summary(self):
        hsn_code_dict = dict()
        for move_line in self.invoice_line_ids:
            cgst_amt = sgst_amt = igst_amt = 0
            sgst_rate = cgst_rate = igst_rate = 0
            for tax in move_line.tax_ids:
                if 'gst' not in tax.name.lower():
                    continue
                taxes = tax.compute_all(move_line.price_unit, self.currency_id, move_line.quantity,
                                        product=move_line.product_id, partner=move_line.partner_id)
                for tx in taxes['taxes']:
                    name = tx.get('name').lower()
                    if 'cgst' in name:
                        cgst_rate = float(re.findall(r"[-+]?\d*\.\d+|\d+", name)[0])
                        cgst_amt = tx.get('amount', 0)
                    elif 'sgst' in name:
                        sgst_rate = float(re.findall(r"[-+]?\d*\.\d+|\d+", name)[0])
                        sgst_amt = tx.get('amount', 0)
                    elif 'igst' in name:
                        igst_rate = float(re.findall(r"[-+]?\d*\.\d+|\d+", name)[0])
                        igst_amt = tx.get('amount', 0)
            if move_line.product_id.l10n_in_hsn_code in hsn_code_dict:
                hsn_code_dict[move_line.product_id.l10n_in_hsn_code]['qty'] += move_line.quantity
                hsn_code_dict[move_line.product_id.l10n_in_hsn_code]['taxable_value'] += move_line.price_subtotal
                hsn_code_dict[move_line.product_id.l10n_in_hsn_code]['cgst_amt'] += cgst_amt
                hsn_code_dict[move_line.product_id.l10n_in_hsn_code]['sgst_amt'] += sgst_amt
                hsn_code_dict[move_line.product_id.l10n_in_hsn_code]['igst_amt'] += igst_amt
                hsn_code_dict[move_line.product_id.l10n_in_hsn_code][
                    'tax_amt'] += move_line.price_total - move_line.price_subtotal
                hsn_code_dict[move_line.product_id.l10n_in_hsn_code]['total_amt'] += move_line.price_total
            else:
                hsn_code_dict.update({move_line.product_id.l10n_in_hsn_code: {
                    'hsn_code': move_line.product_id.l10n_in_hsn_code,
                    'qty': move_line.quantity,
                    'taxable_value': move_line.price_subtotal,
                    'cgst_percent': cgst_rate,
                    'cgst_amt': cgst_amt,
                    'sgst_percent': sgst_rate,
                    'sgst_amt': sgst_amt,
                    'igst_percent': igst_rate,
                    'igst_amt': igst_amt,
                    'tax_amt': move_line.price_total - move_line.price_subtotal,
                    'total_amt': move_line.price_total
                }})
        return hsn_code_dict.values()

    @staticmethod
    def convert_num_to_text(value, currency_unit_label, currency_subunit_label):
        pre = float(value)
        text = ''
        entire_num = int(pre)
        decimal_num = int((pre - entire_num) * 100)  # Extract decimal part and convert it to integer
        if entire_num == 0 and decimal_num == 0:
            return 'Zero ' + currency_unit_label + ' Only.'  # Handle special case for zero value

        text += num2words(entire_num, lang='en_IN').title()  # Convert entire part to words

        if entire_num != 0:
            text += f' {currency_unit_label} '  # Append currency label for entire part

        if decimal_num > 0:
            text += 'And '  # Add 'And' for decimal part
            text += num2words(decimal_num, lang='en_IN').title()  # Convert decimal part to words
            text += f' {currency_subunit_label} Only.'  # Append currency label for decimal part
        elif entire_num == 0:  # If only decimal part is present
            text = num2words(entire_num, lang='en_IN').title() + f' {currency_subunit_label} Only.'

        return text


class AccountMoveLinesInherit(models.Model):
    _inherit = 'account.move.line'

    move_line_ids = fields.Many2many(
        comodel_name="stock.move",
        relation="stock_move_invoice_line_rel",
        column1="invoice_line_id",
        column2="move_id",
        string="Related Stock Moves",
        readonly=True,
        copy=False,
        help="Related stock moves (only when the invoice has been"
             " generated from a sale order).",
    )

    def action_product_history(self):
        invoice_lines = self.env['account.move.line'].search([('parent_state', '=', 'posted'),
                                                              ('move_type', '=', 'out_invoice'),
                                                              ('partner_id', '=', self.move_id.partner_id.id),
                                                              ('product_id', '=', self.product_id.id)]
                                                             , order='create_date desc', limit=10)
        invoice_lines_other = self.env['account.move.line'].search([('parent_state', '=', 'posted'),
                                                                    ('move_type', '=', 'out_invoice'),
                                                                    ('partner_id', '!=', self.move_id.partner_id.id),
                                                                    ('product_id', '=', self.product_id.id)]
                                                                   , order='create_date desc', limit=10)
        other_price_unit = invoice_lines_other.mapped('price_unit')
        price_unit = invoice_lines.mapped('price_unit')
        latest_price = invoice_lines and invoice_lines.sorted(lambda x: x.invoice_date, reverse=True)[0].price_unit or 0
        other_latest_price = invoice_lines_other and invoice_lines_other.sorted(lambda x: x.invoice_date, reverse=True)[
            0].price_unit or 0
        data = {
            'min_price': price_unit and min(price_unit) or 0,
            'max_price': price_unit and max(price_unit) or 0,
            'average_price': price_unit and (sum(price_unit) / len(price_unit)) or 0,
            'other_min_price': other_price_unit and min(other_price_unit) or 0,
            'other_max_price': other_price_unit and max(other_price_unit) or 0,
            'other_average_price': other_price_unit and (sum(other_price_unit) / len(other_price_unit)) or 0,
            'latest_price': latest_price,
            'other_latest_price': other_latest_price,
            'move_lines_ids': [(0, 0, {'date': line.invoice_date, 'description': line.name, 'qty': line.quantity,
                                       'price': line.price_unit, 'price_total': line.price_subtotal,
                                       'record_type': 'main'}) for line in invoice_lines],
            'other_move_line_ids': [(0, 0, {'date': line.invoice_date, 'description': line.name, 'qty': line.quantity,
                                            'price': line.price_unit, 'price_total': line.price_subtotal,
                                            'record_type': 'other'}) for line in invoice_lines_other],
        }
        res_id = self.env['account.line.wizard'].create(data)
        return {
            'type': 'ir.actions.act_window',
            'name': invoice_lines.product_id.name,
            'view_mode': 'form',
            'res_model': 'account.line.wizard',
            'res_id': res_id.id,
            'context': {'create': 0, 'delete': 0, 'no_open': 1},
            'target': 'new'
        }


# class AccountRegisterPayment(models.TransientModel):
#     _inherit = 'account.payment.register'
#
#     def action_create_payments(self):
#         invoice_ids = self._context.get('active_ids')
#         res = super().action_create_payments()
#         payments = self.env['account.payment'].search([('invoice_ids', 'in', invoice_ids),
#         ('create_date', '>=', fields.Datetime.now() - timedelta(seconds=5))], order='create_date desc')
#         for payment in payments:
#             if payment and payment.company_id.payment_approval:
#                 payment.action_send_for_approval()
#         return res

