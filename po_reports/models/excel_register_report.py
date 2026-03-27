from odoo import fields, models, api
from odoo.exceptions import AccessError

class PartnerLedger(models.TransientModel):
    _name = 'excel.register.report'

    start_date = fields.Date(string='From Date', default=fields.Date.today().replace(day=1))
    end_date = fields.Date(string='To Date', default=fields.Date.today())
    partner_id = fields.Many2one('res.partner', string='Partner', help='Select Partner for movement')
    journal_id = fields.Many2many('account.journal', string='Journal Id')
    type = fields.Selection([('partner_ledger', 'Partner Ledger'), ('sales_register', 'Sales Register'),
                             ('purchase_register', 'Purchase Register'),
                             ('detail_purchase_register', 'Detail Purchase Register'),
                             ('ledger_confirm', 'Ledger Confirm'), ('detail_sales_register', 'Detail Sales Register')])

    def print_report(self):
        if self.type == 'partner_ledger':
            data = {'partner_id': self.partner_id.id, 'start_date': self.start_date, 'end_date': self.end_date}
            return self.env.ref('po_reports_v16.action_report_partner_ledger_pdf').report_action(self, data)
        elif self.type == 'ledger_confirm':
            data = {'partner_id': self.partner_id.id, 'start_date': self.start_date, 'end_date': self.end_date}
            return self.env.ref('po_reports_v16.action_ledger_confirm_report_pdf').report_action(self, data)
        else:
            move_type = self._context.get('move_type')
            url = self.get_base_url() + f'/download/reports?report_for={self.type}&start_date={self.start_date}&end_date={self.end_date}&company_id={self.env.company.id}&move_type={move_type}&journal_id={self.journal_id.ids or False}'
            return {'type': 'ir.actions.act_url', 'url': url}

