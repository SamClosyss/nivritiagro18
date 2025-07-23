from odoo import fields, api, models


class ApprovalCategoryInherit(models.Model):
    _inherit = 'approval.category'

    approval_type = fields.Selection(selection_add=[('payment', 'Vendor Payment'), ('receipt', 'Customer receipt'),
                                                    ('invoice', 'Invoice'), ('bills', "Bills")])


class ApprovalRequestInherit(models.Model):
    _inherit = 'approval.request'

    model_name = fields.Char()
    account_move_id = fields.Many2oneReference(model_field='model_name')
    approval_type = fields.Selection(related="category_id.approval_type")

    def view_approval_record(self):
        return {
            'name': 'View Approval Record',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': self.model_name,
            'res_id': self.account_move_id,
            'context': {'create': 0, 'delete': 0},
        }

    def action_approve(self, approver=None):
        res = super().action_approve(approver=approver)
        if self.category_id.approval_type in ('payment', 'receipt', 'invoice', 'bills') and self.request_status == 'approved':
            move_id = self.env[self.model_name].browse(self.account_move_id)
            if move_id.state == 'draft':
                move_id.action_post()
        return res


    def action_refuse(self, approver=None):
        res = super().action_refuse(approver=approver)
        account_move_ids = self.env['account.move'].browse(self.mapped('account_move_id'))
        if account_move_ids:
            account_move_ids.write({'to_check': False})
        return res


class ApprovalApproveInherit(models.Model):
    _inherit = 'approval.approver'

    model_name = fields.Char(related='request_id.model_name', store=True)
    account_move_id = fields.Many2oneReference(model_field='model_name', related='request_id.account_move_id', store=True)
    request_status = fields.Selection(related='request_id.request_status')

