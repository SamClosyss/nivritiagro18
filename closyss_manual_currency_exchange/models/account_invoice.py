# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    conversion_rate = fields.Float()
    sale_manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    sale_manual_currency_rate = fields.Float('Rate', digits=(12, 12), readonly=1)

    def write(self, vals):
        res = super().write(vals)
        if 'conversion_rate' in vals:
            currency = self.env['res.currency'].search([('name', '=', self.currency_id.name)])
            today_date = datetime.today().date().strftime('%d/%m/%Y')
            today_date = datetime.strptime(today_date, '%d/%m/%Y').strftime('%Y-%m-%d')
            print(type(today_date), today_date)
            is_currency_rate = self.env['res.currency.rate'].search([('create_uid', '=', self.env.user.id),
                                                                     ('name', '=', today_date),
                                                                     ('currency_id', '=', currency.id)], order='id desc'
                                                                    , limit=1)
            updated_vals = {'inverse_company_rate': self.conversion_rate, 'currency_id': currency.id}
            if is_currency_rate:
                is_currency_rate.write(updated_vals)
                print('Writee', is_currency_rate, is_currency_rate.inverse_company_rate)

            else:
                currency_rate = self.env['res.currency.rate'].create(updated_vals)
                print('created', currency_rate)
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

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    conversion_rate = fields.Float()
    sale_manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    sale_manual_currency_rate = fields.Float('Rate', digits=(12, 12), readonly=1, store=True)

    def _create_payment_vals_from_wizard(self, batch_result):
        vals = super()._create_payment_vals_from_wizard(batch_result)
        if self.sale_manual_currency_rate_active:
            vals.update({'conversion_rate': self.conversion_rate,
                         'sale_manual_currency_rate_active': self.sale_manual_currency_rate_active,
                         'sale_manual_currency_rate': self.sale_manual_currency_rate})
        return vals


    def action_create_payments(self):
        if self.conversion_rate:
            currency = self.env['res.currency'].search([('name', '=', self.currency_id.name)])
            # inr_currency = self.env['res.currency.rate'].search([('currency_id', '=', 20)])
            # print('inr_currency', inr_currency)
            today_date = datetime.today().date().strftime('%d/%m/%Y')

            today_date = datetime.strptime(today_date, '%d/%m/%Y').strftime('%Y-%m-%d')
            print(type(today_date), today_date)
            is_currency_rate = self.env['res.currency.rate'].search([('create_uid', '=', self.env.user.id),
                                                                     ('name', '=', today_date),
                                                                     ('currency_id', '=', currency.id)], order='id desc'
                                                                    , limit=1)

            print(is_currency_rate, '..................')
            updated_vals = {'inverse_company_rate': self.conversion_rate, 'currency_id': currency.id}
            # inr_updated_vals = {'inverse_company_rate': 1, 'currency_id': 20}
            if is_currency_rate:
                is_currency_rate.write(updated_vals)
                # inr_currency.write(inr_updated_vals)
                print('Writee', is_currency_rate, is_currency_rate.inverse_company_rate)

            else:
                currency_rate = self.env['res.currency.rate'].create(updated_vals)
                print('created', currency_rate)
        res = super().action_create_payments()
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


class account_move(models.Model):
    _inherit = 'account.move'

    conversion_rate = fields.Float()
    sale_manual_currency_rate_active = fields.Boolean('Apply Manual Exchange')
    sale_manual_currency_rate = fields.Float('Rate', digits=(12, 12), readonly=1)


    def action_register_payment(self):
        res = self.line_ids.action_register_payment()
        context = res.get('context')
        context.update({'default_conversion_rate': self.conversion_rate,
                        'default_sale_manual_currency_rate_active': self.sale_manual_currency_rate_active})
        res.update({'context':context})
        print(res)
        return res

    def write(self, vals):
        res = super().write(vals)
        print(vals, 'jjjjjjjjjjjjj')
        if 'conversion_rate' in vals:
            currency = self.env['res.currency'].search([('name', '=', self.currency_id.name)])
            # inr_currency = self.env['res.currency.rate'].search([('currency_id', '=', 20)])
            # print('inr_currency', inr_currency)
            today_date = datetime.today().date().strftime('%d/%m/%Y')

            today_date = datetime.strptime(today_date, '%d/%m/%Y').strftime('%Y-%m-%d')
            print(type(today_date), today_date)
            is_currency_rate = self.env['res.currency.rate'].search([('create_uid', '=', self.env.user.id),
                                                                     ('name', '=', today_date),
                                                                     ('currency_id', '=', currency.id)],
                                                                    order='id desc'
                                                                    , limit=1)

            updated_vals = {'inverse_company_rate': self.conversion_rate, 'currency_id': currency.id}
            # inr_updated_vals = {'inverse_company_rate': 1, 'currency_id': 20}
            if is_currency_rate:
                is_currency_rate.write(updated_vals)
                # inr_currency.write(inr_updated_vals)
                print('Writee', is_currency_rate, is_currency_rate.inverse_company_rate)

            else:
                currency_rate = self.env['res.currency.rate'].create(updated_vals)
                print('created', currency_rate)
        return res

    @api.onchange('conversion_rate')
    def calculate_rate(self):
        if self.conversion_rate != 0:
            self.sale_manual_currency_rate = 1 / self.conversion_rate
        else:
            self.sale_manual_currency_rate = 0

    @api.onchange('sale_manual_currency_rate_active', 'currency_id', 'conversion_rate' )
    def check_currency_id(self):
        if self.sale_manual_currency_rate_active:
            if self.currency_id == self.company_id.currency_id:
                self.sale_manual_currency_rate_active = False
                self.conversion_rate = self.sale_manual_currency_rate = 0
                raise UserError(
                    _('Company currency and invoice currency same, You can not add manual Exchange rate for same currency.'))

