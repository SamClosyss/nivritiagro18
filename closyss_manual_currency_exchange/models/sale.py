# -*- coding: utf-8 -*-

from odoo import fields, models, api, tools, _
from odoo.exceptions import UserError
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    conversion_rate = fields.Float(copy=False)
    sale_manual_currency_rate_active = fields.Boolean('Apply Manual Exchange',copy=False)
    sale_manual_currency_rate = fields.Float('Rate', digits=(12, 12), readonly=1, copy=False)

    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res.update({'sale_manual_currency_rate_active': self.sale_manual_currency_rate_active,
                    'sale_manual_currency_rate': self.sale_manual_currency_rate,
                    'conversion_rate': self.conversion_rate})
        return res


    def action_create_invoice(self):
        prev_invoice = self.picking_ids.ids
        print(prev_invoice)
        res = super(SaleOrder, self).action_create_invoice()
        # Loop through all pickings created from this purchase order
        for order in self:
            for invoice in order.invoice_ids:
                # Pass the value of the custom field to the stock.picking
                if invoice.id not in prev_invoice:
                    invoice.write({
                        'sale_manual_currency_rate_active': order.sale_manual_currency_rate_active,
                        'sale_manual_currency_rate': order.sale_manual_currency_rate,
                        'currency_id': order.currency_id.id,  # Example of passing currency_id
                        'conversion_rate': order.conversion_rate,  # Example of passing conversion rate
                    })
        return res


    def action_confirm(self):
        prev_pickings = self.picking_ids.ids
        print(prev_pickings)
        res = super(SaleOrder, self).action_confirm()
        # Loop through all pickings created from this purchase order
        for order in self:
            for picking in order.picking_ids:
                # Pass the value of the custom field to the stock.picking
                if picking.id not in prev_pickings:
                    picking.write({
                        'sale_manual_currency_rate_active': order.sale_manual_currency_rate_active,
                        'sale_manual_currency_rate': order.sale_manual_currency_rate,
                        'currency_id': order.currency_id.id,  # Example of passing currency_id
                        'conversion_rate': order.conversion_rate,  # Example of passing conversion rate
                    })
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

