from odoo import fields, api, _, models


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    intercompany_invoice_journal = fields.Many2one('account.journal',
                                                   domain="[('company_id', '=', id), ('type', '=', 'sale')]")
    interbranch_invoice_journal = fields.Many2one('account.journal',
                                                  domain="[('company_id', '=', id), ('type', '=', 'sale')]")
    intercompany_bill_journal = fields.Many2one('account.journal',
                                                domain="[('company_id', '=', id), ('type', '=', 'purchase')]")
    interbranch_bill_journal = fields.Many2one('account.journal',
                                               domain="[('company_id', '=', id), ('type', '=', 'purchase')]")
