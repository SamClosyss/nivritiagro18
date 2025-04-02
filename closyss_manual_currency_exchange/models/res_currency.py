# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime


class ResCurrencyRateInherit(models.Model):
    _inherit = 'res.currency'

    def action_register_payment(self):
        return self.line_ids.action_register_payment()

    def _get_rates(self, company, date):
        if not self.ids:
            return {}
        self.env['res.currency.rate'].flush_model(['rate', 'currency_id', 'company_id', 'name'])
        print(date)
        # AND(r.create_uid = %s)
        # , self.create_uid.id
        print(self, self.create_uid.id)
        print(self.env.user.id)
        query = """SELECT c.id,
                          COALESCE((SELECT r.rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                                    AND(r.create_uid = %s) order by r.id DESC
                                  LIMIT 1), 1.0) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.root_id.id, self.env.user.id, tuple(self.ids)))
        print(self._cr.execute(query, (date, company.root_id.id, self.env.user.id, tuple(self.ids))))
        currency_rates = dict(self._cr.fetchall())

        return currency_rates


class ResCurrencyRateInherit(models.Model):
    _inherit = 'res.currency.rate'

    # ID  = 25 shuld be delted from ir.model.constrasints

    ######## REMOVED NAME FROM 'unique (currency_id,company_id)' TO AVOIDE VALIDATION FOR CREATION OF SAME DAY RECORD OF RATE #######
    # _sql_constraints = [
    #     ('unique_name_per_day', 'unique (currency_id,company_id)', 'Only one currency rate per day allowed!'),
    #     ('currency_rate_check', 'CHECK (rate>0)', 'The currency rate must be strictly positive.'),
    # ]

