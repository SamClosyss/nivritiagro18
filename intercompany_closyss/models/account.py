from odoo import api,_,models,fields
from odoo.exceptions import ValidationError


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

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

    def get_inter_company_branch_journal(self, company_id, invoice_type, journal_from=None):
        journal_id = False
        if company_id:
            company_journal = journal_from and journal_from or company_id
            if invoice_type in ('out_invoice', 'out_refund'):
                if self.company_id == company_id.parent_id or self.company_id.parent_id == company_id or self.company_id.parent_id == company_id.parent_id:
                    if not (journal_id := company_journal.interbranch_invoice_journal):
                        raise ValidationError("Kindly Contact Administrator as Inter Branch Journal not found.")
                else:
                    if not (journal_id := company_journal.intercompany_invoice_journal):
                        raise ValidationError("Kindly Contact Administrator as Inter Branch Journal not found.")
            elif invoice_type in ('in_invoice', 'in_refund'):
                if self.company_id == company_id.parent_id or self.company_id.parent_id == company_id or self.company_id.parent_id == company_id.parent_id:
                    if not (journal_id := company_journal.interbranch_bill_journal):
                        raise ValidationError("Kindly Contact Administrator as Inter Branch Journal not found.")
                else:
                    if not (journal_id := company_journal.intercompany_bill_journal):
                        raise ValidationError("Kindly Contact Administrator as Inter Branch Journal not found.")
        return journal_id

    @api.onchange('partner_id')
    def on_change_inter_branch_transaction(self):
        company_id = self.env['res.company'].sudo()._find_company_from_partner(self.partner_id.id)
        journal_id = self.get_inter_company_branch_journal(company_id, self.move_type, self.company_id)
        if journal_id:
            self.journal_id = journal_id.id
        # self.compute_inter_branch_transaction()
        # self.invoice_line_ids._compute_price_unit()

    def _inter_company_prepare_invoice_data(self, invoice_type):
        res = super()._inter_company_prepare_invoice_data(invoice_type)
        company_id = self.env['res.company'].sudo()._find_company_from_partner(self.partner_id.id)
        journal_id = self.get_inter_company_branch_journal(company_id, invoice_type)
        if journal_id:
            res.update({'journal_id': journal_id.id})
        return res
