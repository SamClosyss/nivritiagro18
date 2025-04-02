from odoo import fields, models, api


class ResSettingInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_approval = fields.Boolean(default=False, related="company_id.invoice_approval")
    bills_approval = fields.Boolean(default=False,  related="company_id.bills_approval")
    receipt_approval = fields.Boolean(default=False, related="company_id.receipt_approval")
    payment_approval = fields.Boolean(default=False, related="company_id.payment_approval")
    journal_entry_approval = fields.Boolean(default=False, related="company_id.journal_entry_approval")
