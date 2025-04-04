from odoo import fields, api, _, models
from odoo.exceptions import ValidationError


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    inter_branch_transaction = fields.Boolean(compute="compute_inter_branch_transaction")

    @api.depends('partner_id')
    def compute_inter_branch_transaction(self):
        for rec in self:
            rec.inter_branch_transaction = False
            company_id = self.env['res.company'].sudo()._find_company_from_partner(rec.partner_id.id)
            if company_id:
                if rec.company_id == company_id.parent_id:
                    rec.inter_branch_transaction = True
                elif rec.company_id.parent_id == company_id:
                    rec.inter_branch_transaction = True
                elif company_id.parent_id and rec.company_id.parent_id:
                    if company_id.parent_id == rec.company_id.parent_id:
                        rec.inter_branch_transaction = True

    def get_inter_company_branch_journal(self, company_id):
        journal_id = False
        if company_id:
            if self.company_id == company_id.parent_id or self.company_id.parent_id == company_id or self.company_id.parent_id == company_id.parent_id:
                if not (journal_id := self.company_id.interbranch_bill_journal):
                    raise ValidationError("Kindly Contact Administrator as Inter Branch Journal not found.")
            else:
                if not (journal_id := self.company_id.intercompany_bill_journal):
                    raise ValidationError("Kindly Contact Administrator as Inter Branch Journal not found.")
        return journal_id

    # Inherited the Function from base
    # Function is forwarding the Bill Address and setting InterCompany and InterBranch journal
    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        """This function is used to transfer the data in accounting bills """
        res = super()._prepare_invoice()
        value = {'sales_employee_id': self.buyer_employee_id.id, 'prepared_by': self.prepared_by.id}
        res.update(value)
        company_id = self.env['res.company'].sudo()._find_company_from_partner(self.partner_id.id)
        journal_id = self.get_inter_company_branch_journal(company_id)
        if journal_id:
            res.update({'journal_id': journal_id.id})
        return res
