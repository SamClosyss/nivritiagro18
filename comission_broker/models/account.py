from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class InheritAccountMove(models.Model):
    _inherit = "account.move"

    broker_id = fields.Many2one('res.partner', tracking=True)
    broker_type = fields.Selection([('disc', 'Discount'), ('rate_diff', 'Rate Difference')])
    broker_value = fields.Float()
    exclude_for_brokerage = fields.Boolean(readonly=True)
    brokerage_amt = fields.Float('Brokerage Amount', compute="compute_brokerage_amount", store=True)
    brokerage_payable = fields.Float('Brokerage Payable', compute='compute_brokerage_payable', store=True)
    brokerage_paid = fields.Float('Brokerage Book', compute='compute_brokerage_paid', store=True)
    brokerage_pending = fields.Float('Brokerage Pending', compute='compute_brokerage_pending', store=True)
    vendor_bill_ids = fields.One2many('account.move', 'bill_ids')
    bill_ids = fields.Many2one('account.move')
    account_payment_ids = fields.One2many('account.payment', 'invoice_id', string='Payment')

    def action_view(self):
        return {
            'name': _("Vendor Bills"),
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'account.move',
            'view_id': self.env.ref('account.view_in_invoice_bill_tree').id,
            'domain': [('id', 'in', self.vendor_bill_ids.ids)],
            'target': 'new',
            'context': {'create': False}
        }

    def js_assign_outstanding_line(self, line_id):
        print(line_id, 'line ID')
        result = super().js_assign_outstanding_line(line_id)
        self.ensure_one()
        lines = self.env['account.move.line'].browse(line_id)
        print(lines, 'lines')
        credit_moves = lines.mapped('move_id').filtered(lambda m: m.move_type == 'out_refund')
        print(credit_moves, 'credit moves')

        for credit_move in credit_moves:
            print(credit_move)
            if not credit_move.reversed_entry_id:
                credit_move.reversed_entry_id = self

        return result

    # code written by sanmeet
    @api.depends('amount_untaxed', 'broker_value', 'reversal_move_ids')
    def compute_brokerage_amount(self):
        for rec in self:
            if rec.broker_type == 'disc':
                if rec.amount_untaxed and rec.broker_value:
                    rec.brokerage_amt = (rec.amount_untaxed * (rec.broker_value / 100)) or 0
                if rec.reversal_move_ids:
                    rec.brokerage_amt = rec.brokerage_amt - sum(rec.reversal_move_ids.mapped('brokerage_amt'))
            if rec.broker_type == 'rate_diff':
                rec.brokerage_amt = rec.broker_value * sum(rec.invoice_line_ids.mapped('quantity'))
                if rec.reversal_move_ids:
                    rec.brokerage_amt = rec.brokerage_amt - sum(rec.reversal_move_ids.mapped('brokerage_amt'))

    @api.depends('amount_total', 'amount_paid', 'broker_value', 'amount_residual', 'account_payment_ids',
                 'account_payment_ids.amount')
    def compute_brokerage_payable(self):
        for rec in self:
            value = 0
            payment = 0
            if rec.account_payment_ids:
                payment = sum(rec.account_payment_ids.filtered(lambda x: x.state == 'posted').mapped('amount'))
            if rec.reversal_move_ids and payment:
                value = (payment / (rec.amount_total - sum(rec.reversal_move_ids.mapped('amount_total')))) * 100
            rec.brokerage_payable = (((value / 100) * rec.brokerage_amt) - rec.brokerage_paid)
            # paid_value = rec.brokerage_payable - ((rec.amount_total - rec.untaxed_amount) - (100 - ratio) * 100)

    @api.depends('vendor_bill_ids', 'vendor_bill_ids.amount_total', 'amount_total')
    def compute_brokerage_paid(self):
        for rec in self:
            if rec.vendor_bill_ids:
                amount = sum(rec.vendor_bill_ids.mapped('amount_untaxed'))
                rec.brokerage_paid = amount
                # rec.brokerage_payable = 0

    @api.depends('brokerage_amt', 'brokerage_paid')
    def compute_brokerage_pending(self):
        for rec in self:
            if rec.brokerage_amt or rec.brokerage_paid:
                rec.brokerage_pending = rec.brokerage_amt - rec.brokerage_paid

    @api.onchange('partner_id')
    def compute_broker_data(self):
        for rec in self:
            if rec.partner_id:
                rec.broker_id = rec.partner_id.broker_id.id
                rec.broker_type = rec.partner_id.broker_type
                rec.broker_value = rec.partner_id.broker_value

    def action_create_bills(self):
        for rec in self:
            if len(self.mapped('broker_id')) > 1:
                raise ValidationError('Cannot create 1 Bills for multiple Broker')
            # print(rec.analytic_distribution)
            # if len(self.mapped('analytic_distribution')) > 1:
            #     raise ValidationError('Multiple Analytic Distribution not allowed')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Bills',
            'view_mode': 'form',
            'res_model': 'product.enquiry',
            'target': 'new',
            'context': {'default_account_move_ids': self.ids}
        }


# class InheritAccountMoveLine(models.Model):
#     _inherit = "account.move.line"
#
#     broker_id = fields.Many2one('res.partner', tracking=True, compute='compute_broker_data_from_move', store=True)
#     broker_type = fields.Selection([('disc', 'Discount'), ('rate_diff', 'Rate Difference')],
#                                    compute='compute_broker_data_from_move', store=True)
#     broker_value = fields.Float(compute='compute_broker_data_from_move', store=True)
#     brokerage_amt = fields.Float('Brokerage Amount')
#     item_rate_val = fields.Float('Item Rate Value')
#     exclude_for_brokerage = fields.Boolean(related='move_id.exclude_for_brokerage',store=True)
#     status = fields.Selection([('unpaid', 'Unpaid'), ('paid', "Paid")], default='unpaid')
#
#     @api.depends('move_id.broker_id', 'move_id.broker_type', 'move_id.broker_value')
#     def compute_broker_data_from_move(self):
#         for rec in self:
#             if rec.move_id:
#                 rec.broker_id = rec.move_id.broker_id.id
#                 rec.broker_type = rec.move_id.broker_type
#                 rec.broker_value = rec.move_id.broker_value
#
#     @api.onchange('broker_value', 'price_subtotal', 'broker_type')
#     def compute_brokerage_amt(self):
#         for line in self:
#             if line.broker_type == 'disc':
#                 line.brokerage_amt = line.price_subtotal * (line.broker_value / 100)
#             if line.broker_type == 'rate_diff':
#                 line.price_subtotal = line.price_unit - (line.item_rate_val * line.quantity)
#
#     def action_create_bills(self):
#         for rec in self:
#             if len(self.mapped('broker_id')) > 1:
#                 raise ValidationError('Cannot create 1 Bills for multiple Broker')
#             # print(rec.analytic_distribution)
#             # if len(self.mapped('analytic_distribution')) > 1:
#             #     raise ValidationError('Multiple Analytic Distribution not allowed')
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Create Bills',
#             'view_mode': 'form',
#             'res_model': 'product.enquiry',
#             'target': 'new',
#             'context': {'default_account_move_line_ids': self.ids}
#         }


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    exclude_for_brokerage = fields.Boolean(default=False)
    invoice_id = fields.Many2one('account.move', string='Invoice')

    @api.depends('move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    def _compute_stat_buttons_from_reconciliation(self):
        res = super()._compute_stat_buttons_from_reconciliation()
        for rec in self.reconciled_invoice_ids:
            if self.exclude_for_brokerage and not rec.exclude_for_brokerage:
                rec.exclude_for_brokerage = True
        return res
