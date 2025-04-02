# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime


class StockPickingOrder(models.Model):
    _inherit = 'stock.picking'

    currency_id = fields.Many2one(comodel_name='res.currency' , string='Currency')
    conversion_rate = fields.Float()
    sale_manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    sale_manual_currency_rate = fields.Float('Rate', digits=(12, 12), readonly=1)

    def button_validate(self):
        if self.conversion_rate:
            currency = self.env['res.currency'].search([('name', '=', self.currency_id.name)])
            today_date = datetime.today().date().strftime('%d/%m/%Y')
            today_date = datetime.strptime(today_date, '%d/%m/%Y').strftime('%Y-%m-%d')
            is_currency_rate = self.env['res.currency.rate'].search([('create_uid', '=', self.env.user.id),
                                                                     ('name', '=', today_date),
                                                                     ('currency_id', '=', currency.id)],
                                                                    order='id desc', limit=1)
            updated_vals = {'inverse_company_rate': self.conversion_rate, 'currency_id': currency.id}
            if is_currency_rate:
                is_currency_rate.write(updated_vals)

            else:
                currency_rate = self.env['res.currency.rate'].create(updated_vals)
                print('created', currency_rate)

        res = super().button_validate()
        return res



    @api.onchange('conversion_rate')
    def calculate_rate(self):
        if self.conversion_rate != 0:
            self.sale_manual_currency_rate = 1 / self.conversion_rate
        else:
            self.sale_manual_currency_rate = 0

    @api.onchange('sale_manual_currency_rate_active', 'currency_id')
    def check_currency_id(self):
        if self.sale_manual_currency_rate_active:
            if self.currency_id == self.company_id.currency_id:
                self.sale_manual_currency_rate_active = False
                self.conversion_rate = self.sale_manual_currency_rate = 0
                raise UserError(
                    _('Company currency and invoice currency same, You can not add manual Exchange rate for same currency.'))