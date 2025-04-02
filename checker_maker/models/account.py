from odoo import fields, api, models
from odoo.exceptions import ValidationError
from markupsafe import Markup


class AccountMoveInherited(models.Model):
    _inherit = 'account.move'

    approver_ids = fields.One2many('approval.approver', 'account_move_id')
    approval_status = fields.Selection(
        [('new', 'New'), ('pending', 'Pending'), ('waiting', 'Waiting'), ('approved', "Approved")
            , ('refused', 'Refused'), ('cancel', 'Cancel'), ('posted', 'Completed')], compute="compute_approval_status")

    def compute_approval_status(self):
        for rec in self:
            if rec.state in ('posted', 'cancel'):
                rec.approval_status = rec.state
                continue
            approval_status = self.env['approval.approver'].search([('user_id', '=', self.env.user.id),
                                                                    ('model_name', '=', 'account.move'),
                                                                    ('account_move_id', '=', rec.id)]).status
            rec.approval_status = approval_status

    @api.depends('date', 'auto_post', 'company_id.invoice_approval', 'company_id.bills_approval', 'company_id.journal_entry_approval', 'state')
    def _compute_hide_post_button(self):
        for record in self:
            record.hide_post_button = True
            if record.state == 'draft':
                if record.move_type in ('out_invoice', 'out_refund'):
                    record.hide_post_button = record.company_id.invoice_approval
                elif record.move_type in ('in_invoice', 'in_refund'):
                    record.hide_post_button = record.company_id.bills_approval
                elif record.move_type == 'entry':
                    if record.payment_id and record.payment_id.payment_type == 'inbound':
                        record.hide_post_button = record.company_id.receipt_approval
                    elif record.payment_id and record.payment_id.payment_type == 'outbound':
                        record.hide_post_button = record.company_id.payment_approval
                    else:
                        record.hide_post_button = record.company_id.journal_entry_approval
                elif record.auto_post != 'no' and record.date > fields.Date.context_today(record):
                    record.hide_post_button = record.auto_post != 'no' and record.date > fields.Date.context_today(record)

    def get_approval_category(self):
        if self.move_type in ('out_invoice', 'out_refund'):
            category_invoice = self.env['approval.category'].search([('approval_type', '=', 'invoice'), ('company_id', '=', self.company_id.id)])
            if not category_invoice:
                raise ValidationError("Invoice, Refund Approval Template not found, Kindly contact administrator")
            return category_invoice.id
        elif self.move_type in ("in_invoice", 'in_refund'):
            category_bills = self.env['approval.category'].search([('approval_type', '=', 'bills'), ('company_id', '=', self.company_id.id)])
            if not category_bills:
                raise ValidationError("Bills, Refund Approval Template not found, Kindly contact administrator")
            return category_bills.id
        elif self.move_type == 'entry':
            category_bills = self.env['approval.category'].search([('approval_type', '=', 'entry'), ('company_id', '=', self.company_id.id)])
            if not category_bills:
                raise ValidationError("Journal Entry Approval Template not found, Kindly contact administrator")
            return category_bills.id

    def action_send_for_approval(self):
        if not self.invoice_line_ids:
            raise ValidationError("Please note invoice lines are empty")
        elif self.move_type in ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'):
            if self.journal_id.company_id != self.company_id:
                raise ValidationError(f'Journal {self.journal_id.name} does not belong to {self.company_id.name}')
        # if self.company_id.currency_id != self.currency_id and self.manual_currency_rate_active is False:
        if self.company_id.currency_id != self.currency_id:
            raise ValidationError(f"Kindly Note Currency has been changed to {self.currency_id.name}. \n"
                                  f"Please click on Apply Manual Exchange and enter the Conversion Rate.")
        for rec in self:
            request_id = self.env['approval.request'].search([('account_move_id', '=', rec.id),
                                                              ('model_name', '=', rec._name),
                                                              ('request_status', '=', 'new')])
            if request_id:
                request_id.action_confirm()
                rec.to_check = True
                continue
            data = {'name': dict(rec._fields['move_type'].selection).get(rec.move_type),
                    'request_owner_id': self.env.user.id,
                    'model_name': rec._name,
                    'partner_id': rec.partner_id.id,
                    'reference': rec.ref,
                    'date': rec.invoice_date,
                    'amount': rec.amount_total_signed,
                    'account_move_id': rec.id,
                    'category_id': rec.get_approval_category(),
                    'reason': Markup("<a href=# data-oe-model='%s' data-oe-id='%s'><button class='btn btn-primary'>View Record</button></a>") % (self._name, self.id,)}
            request_id = rec.env['approval.request'].create(data)
            request_id.action_confirm()
            rec.to_check = True

    def action_approve(self):
        request_id = self.env['approval.approver'].search([('status', '=', 'pending'),
                                                          ('user_id', '=', self.env.user.id),
                                                          ('model_name', '=', 'account.move'),
                                                          ('account_move_id', '=', self.id)])
        request_id.action_approve()
        if request_id.request_status == 'approved' and self.state == 'draft':
            self.action_post()

    def action_refuse(self):
        request_id = self.env['approval.approver'].search([('status', '=', 'pending'),
                                                          ('user_id', '=', self.env.user.id),
                                                          ('model_name', '=', 'account.move'),
                                                          ('account_move_id', '=', self.id)])
        request_id.action_refuse()

    def button_draft(self):
        res = super().button_draft()
        for rec in self:
            request_id = self.env['approval.request'].search([('account_move_id', '=', rec.id),
                                                              ('model_name', '=', rec._name),
                                                              ('request_status', '=', 'approved')])
            if request_id:
                request_id.sudo().action_draft()
                rec.to_check = False
        return res

    def action_withdraw(self):
        request_id = self.env['approval.approver'].search([('status', '=',  ('refused', 'approved')),
                                                           ('user_id', '=', self.env.user.id),
                                                           ('model_name', '=', 'account.move'),
                                                           ('account_move_id', '=', self.id)])
        request_id.status = 'pending'

    def action_post(self):
        for rec in self:
            if rec. approver_ids and rec.approver_ids.request_id.request_status != 'approved':
                raise ValidationError("You cannot post the record without the approval")
            elif rec.move_type in ('out_invoice', 'in_invoice', 'out_refund', 'in_refund'):
                if rec.journal_id.company_id != rec.company_id:
                    raise ValidationError(f'Journal {rec.journal_id.name} does not belong to {rec.company_id.name}')
        return super().action_post()


class AccountPaymentInherit(models.Model):
    _inherit = 'account.payment'


    approval_status = fields.Selection(
        [('new', 'New'), ('pending', 'Pending'), ('waiting', 'Waiting'), ('approved', "Approved")
            , ('refused', 'Refused'), ('cancel', 'Cancel'), ('posted', 'Completed')], compute="compute_approval_status")

    def get_approval_category(self):
        if self.payment_type == 'inbound':
            category_receipt = self.env['approval.category'].search([('approval_type', '=', 'receipt'), ('company_id', '=', self.company_id.id)])
            if not category_receipt:
                raise ValidationError("Receipt Approval template not found. Kindly contact administrator")
            return category_receipt.id
        else:
            category_payment = self.env['approval.category'].search([('approval_type', '=', 'payment'), ('company_id', '=', self.company_id.id)])
            if not category_payment:
                raise ValidationError("Payment Approval template not found. Kindly contact administrator")
            return category_payment.id

    def action_send_for_approval(self):
        for rec in self:
            request_id = self.env['approval.request'].search([('account_move_id', '=', rec.move_id.id),
                                                              ('model_name', '=', rec.move_id._name),
                                                              ('request_status', '=', 'new')])
            if request_id:
                request_id.action_confirm()
                rec.to_check = True
                continue
            data = {'request_owner_id': self.env.user.id,
                    'model_name': rec.move_id._name,
                    'account_move_id': rec.move_id.id,
                    'partner_id': rec.partner_id.id,
                    'amount': rec.amount,
                    'date': rec.date,
                    'reference': rec.ref}
            if rec.payment_type == 'inbound':
                data.update({
                   'name': 'Customer Receipt Approval',
                   'category_id': rec.get_approval_category()
                })
            else:
                data.update({
                    'name': 'Vendor Payment Approval',
                    'category_id': rec.get_approval_category()
                })
            request_id = self.env['approval.request'].create(data)
            request_id.action_confirm()
            rec.to_check = True

    def action_approve_payment(self):
        self.move_id.action_approve()
        # request_id = self.env['approval.approver'].search([('status', '=', 'pending'),
        #                                                    ('user_id', '=', self.env.user.id),
        #                                                    ('model_name', '=', 'account.move'),
        #                                                    ('account_move_id', '=', self.id)])
        #
        # request_id.action_approve()
        # if request_id.request_status == 'approved':
        #     self.action_post()

    def action_refuse_payment(self):
        self.move_id.action_refuse()
        # request_id = self.env['approval.approver'].search([('status', '=', 'pending'),
        #                                                    ('user_id', '=', self.env.user.id),
        #                                                    ('model_name', '=', 'account.move'),
        #                                                    ('account_move_id', '=', self.id)])
        # request_id.action_refuse()

    def action_withdraw(self):
        self.move_id.action_withdraw()