from odoo import fields, api, models, _


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'

    is_internal_transfer = fields.Boolean()
    destination_journal_id = fields.Many2one('account.journal',
                                                 domain="[('type', 'in', ('bank', 'cash')), ('id', '!=', journal_id),('company_id', 'in', (company_id, False))]")

    def action_post(self):
        res = super().action_post()
        self.filtered(
            lambda pay: pay.is_internal_transfer and not pay.paired_internal_transfer_payment_id
        )._create_paired_internal_transfer_payment()
        return res

    def _create_paired_internal_transfer_payment(self):
        third_party_checks = self.filtered(
            lambda x: x.payment_method_line_id.code in ['in_third_party_checks', 'out_third_party_checks']
        )
        for rec in third_party_checks:
            dest_payment_method_code = (
                'in_third_party_checks' if rec.payment_type == 'outbound'
                else 'out_third_party_checks'
            )
            dest_payment_method = rec.destination_journal_id.inbound_payment_method_line_ids.filtered(
                lambda x: x.code == dest_payment_method_code
            ) or rec.destination_journal_id.outbound_payment_method_line_ids.filtered(
                lambda x: x.code == dest_payment_method_code
            )

            paired_payment = rec.copy({
                'journal_id': rec.destination_journal_id.id,
                'destination_journal_id': rec.journal_id.id,
                'payment_type': 'inbound' if rec.payment_type == 'outbound' else 'outbound',
                'move_id': None,
                'memo': rec.memo,
                'paired_internal_transfer_payment_id': rec.id,
                'date': rec.date,
                'payment_method_line_id': dest_payment_method.id if dest_payment_method else False,
                'l10n_latam_check_id': rec.l10n_latam_check_id,
                'is_internal_transfer': True,
            })
            paired_payment.action_post()  # auto confirm
            rec.paired_internal_transfer_payment_id = paired_payment

            body = _("This payment has been created from:") + rec._get_html_link()
            paired_payment.message_post(body=body)
            body = _("A second payment has been created:") + paired_payment._get_html_link()
            rec.message_post(body=body)

            lines = (rec.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                lambda l: l.account_id == rec.destination_account_id and not l.reconciled
            )
            lines.reconcile()
        for payment in self - third_party_checks:
            # Pick a valid payment method for the destination journal
            if payment.payment_type == 'outbound':
                methods = payment.destination_journal_id.inbound_payment_method_line_ids
            else:
                methods = payment.destination_journal_id.outbound_payment_method_line_ids

            valid_method = methods[:1] if methods else False

            paired_payment = payment.copy({
                'journal_id': payment.destination_journal_id.id,
                'destination_journal_id': payment.journal_id.id,
                'payment_type': 'inbound' if payment.payment_type == 'outbound' else 'outbound',
                'move_id': None,
                'memo': payment.memo,
                'paired_internal_transfer_payment_id': payment.id,
                'date': payment.date,
                'payment_method_line_id': valid_method.id if valid_method else False,
                'is_internal_transfer': True,
            })
            paired_payment.action_post()  # auto confirm
            payment.paired_internal_transfer_payment_id = paired_payment

            body = _("This payment has been created from:") + payment._get_html_link()
            paired_payment.message_post(body=body)
            body = _("A second payment has been created:") + paired_payment._get_html_link()
            payment.message_post(body=body)

            # Reconcile liquidity lines
            lines = (payment.move_id.line_ids + paired_payment.move_id.line_ids).filtered(
                lambda l: l.account_id == payment.destination_account_id and not l.reconciled
            )
            lines.reconcile()


    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.journal_id:
            if self.payment_type == 'outbound':
                methods = self.journal_id.outbound_payment_method_line_ids
            else:
                methods = self.journal_id.inbound_payment_method_line_ids

            if self.payment_method_line_id not in methods:
                self.payment_method_line_id = methods[:1] if methods else False

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'destination_journal_id')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.destination_journal_id.company_id.transfer_account_id
            elif pay.partner_type == 'customer':
                # Receive money from invoice or send money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(
                        pay.company_id).property_account_receivable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        *self.env['account.account']._check_company_domain(pay.company_id),
                        ('account_type', '=', 'asset_receivable'),
                        ('deprecated', '=', False),
                    ], limit=1)
            elif pay.partner_type == 'supplier':
                # Send money to pay a bill or receive money to refund it.
                if pay.partner_id:
                    pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                else:
                    pay.destination_account_id = self.env['account.account'].search([
                        *self.env['account.account']._check_company_domain(pay.company_id),
                        ('account_type', '=', 'liability_payable'),
                        ('deprecated', '=', False),
                    ], limit=1)