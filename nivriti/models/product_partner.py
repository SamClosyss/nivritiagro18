from odoo import fields, api, models
from odoo.exceptions import ValidationError
from datetime import datetime


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    status = fields.Selection([('pending', 'Waiting for approval'), ('approve', 'approved')])
    active = fields.Boolean('Active', default=False,
                            help="If unchecked, it will allow you to hide the product without removing it.")

    def action_send_approval(self):
        for rec in self:
            rec.status = 'pending'
            templates = self.env.ref('nivriti.mail_template_of_products_approvals_views')
            templates.scheduled_date = datetime.today()
            templates.send_mail(self.id, force_send=True)
            rec.message_post(body=f"Kindly approve the product.")

    def action_approval(self):
        for rec in self:
            rec.status = 'approve'
            rec.active = True
            rec.message_post(body=f"Approved")

    def action_unarchive(self):
        if not self.env.user.has_group('base.group_erp_manager'):
            raise ValidationError('You are not allowed to unarchive the record. Contact your Administrator')
        for rec in self:
            rec.message_post(body=f"Approved")
        return super().action_unarchive()

    def action_archive(self):
        if not self.env.user.has_group('base.group_erp_manager'):
            raise ValidationError('You are not allowed to archive the record. Contact your Administrator')
        return super().action_archive()


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    status = fields.Selection([('pending', 'Waiting for approval'), ('approve', 'approved')])
    fssai_no = fields.Char(string='FSSAI No.')
    active = fields.Boolean(default=False,
                            help="By unchecking the active field, you may hide a fiscal position without deleting it.")

    def action_send_approval(self):
        for rec in self:
            rec.status = 'pending'
            templates = self.env.ref('nivriti.mail_template_of_customer_vendor_approvals_view')
            templates.scheduled_date = datetime.today()
            templates.send_mail(self.id, force_send=True)
            rec.message_post(body=f"Kindly approve the Contact.")

    def action_approval(self):
        for rec in self:
            rec.status = 'approve'
            rec.active = True
            rec.message_post(body=f"Approved")

    def action_unarchive(self):
        if not self.env.user.has_group('base.group_erp_manager'):
            raise ValidationError('You are not allowed to unarchive the record. Contact your Administrator')
        for rec in self:
            rec.message_post(body=f"Approved")
        return super().action_unarchive()

    def action_archive(self):
        if not self.env.user.has_group('base.group_erp_manager'):
            raise ValidationError('You are not allowed to archive the record. Contact your Administrator')
        return super().action_archive()
