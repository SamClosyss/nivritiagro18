from odoo import fields, api, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    pan_no = fields.Char(related="partner_id.l10n_in_pan", store=True)

class GrossTdsReport(models.TransientModel):
    _name = "gross.tds.report"

    move_line_id = fields.Many2one(comodel_name='account.move.line')
    company_id = fields.Many2one(
        related='move_line_id.move_id.company_id', store=True, readonly=True, precompute=True,
        index=True,
    )
    company_currency_id = fields.Many2one(
        string='Company Currency',
        related='move_line_id.move_id.company_currency_id', readonly=True, store=True, precompute=True,
    )
    move_name = fields.Char(
        string='Number',
        related='move_line_id.move_id.name', store=True,
        index='btree',
    )

    date = fields.Date(string='Date', related='move_line_id.date')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Customer', related='move_line_id.partner_id')
    pan_no = fields.Char(string='PAN', related='move_line_id.pan_no')
    tax_tag_id = fields.Many2many(comodel_name='account.account.tag', string='Tax Grid',
                                  related='move_line_id.tax_tag_ids')
    tax_line_id = fields.Many2one(comodel_name='account.tax', string='Tax', related='move_line_id.tax_line_id')
    gross_amount = fields.Float(string='Gross Amount', compute='_compute_gross_amount')
    debit = fields.Monetary(string='Debit', currency_field='company_currency_id', related='move_line_id.debit')
    credit = fields.Monetary(string='Credit', currency_field='company_currency_id', related='move_line_id.credit')

    def _compute_move_line(self):
        old_data = self.env['gross.tds.report'].search([])
        if old_data:
            old_data.unlink()
        move_ids = self.env['account.move.line'].search([('account_id.code', '=', '112440')])
        print('111111')
        for rec in move_ids:
            gross_tds = self.env['gross.tds.report'].create({'move_line_id': rec.id})
        return {
            'name': _('TDS Gross Report'),
            'type': 'ir.actions.act_window',
            'res_model': 'gross.tds.report',
            'view_mode': 'tree',
            'views': [(self.env.ref('tds_gross_report_by_closyss.view_archived_tag_move_tree').id, 'tree'), [False, 'form']],
            'target': 'self',
            'domain': [('tax_tag_id', '!=', False)],
        }

    @api.depends('credit', 'tax_tag_id', 'tax_line_id')
    def _compute_gross_amount(self):
        for line in self:
            if line.credit > 0 and line.tax_line_id:
                line.gross_amount = line.credit / (line.tax_line_id.amount / 100)
                print(line.gross_amount)
                line.gross_amount = line.gross_amount * (-1) if line.gross_amount < 0 else line.gross_amount
            else:
                line.gross_amount = 0

