from odoo import fields, api, models, _
from datetime import datetime


class ProductWizard(models.TransientModel):
    _name = 'product.enquiry'
    _description = 'Manual selection of product'

    product_id = fields.Many2one('product.product')
    account_move_ids = fields.Many2many('account.move')
    account_move_line_ids = fields.Many2many('account.move.line')

    def action_create_bills(self):
        today = datetime.now()
        for rec in self.account_move_ids.filtered(lambda x: x.brokerage_pending > 0):
            paid_value = rec.brokerage_payable
            data = {'partner_id': self.account_move_ids.broker_id.id, 'ref': rec.name, 'bill_ids': rec.id,
                    'invoice_date': today, 'move_type': 'in_invoice',
                    'invoice_line_ids': [(0, 0, {'product_id': self.product_id.id,
                                                 'price_unit': paid_value,
                                                 'quantity': 1,
                                                 })]}
            self.env['account.move'].create(data)
            rec.brokerage_payable = 0


# minus_entry = rec.amount_total - rec.amount_residual
#             # value = (minus_entry / rec.amount_total) * 100
#             ratio =  minus_entry / rec.amount_total
#             # paid_value = rec.brokerage_payable - (taxed_ammount * (100 - ratio) * 100)
#             print(rec.amount_total , rec.amount_residual, rec.amount_untaxed, rec.brokerage_payable)
#             is_5 = ((((rec.amount_total- rec.amount_untaxed)/ rec.amount_untaxed) * 100))
#             is_95 = (100 - ((((rec.amount_total- rec.amount_untaxed)/ rec.amount_untaxed) * 100)))
#             print('is_5', is_5 , is_95 )
# paid_value = rec.brokerage_payable * (   (100 - ((((rec.amount_total- rec.amount_untaxed)/ rec.amount_untaxed) * 100))) / 100)
# paid_value = rec.brokerage_payable * 100 / (100 + ((((rec.amount_total- rec.amount_untaxed)/ rec.amount_untaxed) * 100)))
# paid_value = rec.brokerage_payable

class InheritAccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        res.update({'invoice_id': self.line_ids[0].move_id.id})
        return res
