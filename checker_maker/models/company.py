from odoo import fields, models, api


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    invoice_approval = fields.Boolean(default=False)
    bills_approval = fields.Boolean(default=False)
    receipt_approval = fields.Boolean(default=False)
    payment_approval = fields.Boolean(default=False)
    journal_entry_approval = fields.Boolean(default=False)

