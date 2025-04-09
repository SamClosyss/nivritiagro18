from odoo import fields, api, models
from odoo.exceptions import ValidationError

from odoo.addons.sale_amazon import const, utils as amazon_utils
import logging

_logger = logging.getLogger(__name__)


# class InheritAmazon(models.Model):
#     _inherit = "amazon.account"
#
#     def _create_order_from_data(self,order_data):
#         res = super()._create_order_from_data(order_data)
#         print(order_data)
#         _logger.info(order_data)
#         return res
#
#     def _sync_order_by_reference(self, amazon_order_ref):
#         res = super()._sync_order_by_reference(amazon_order_ref)
#         print(amazon_utils.make_sp_api_request())
#         _logger.info(amazon_utils.make_sp_api_request())
#         return res

class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        if self.location_dest_id.id == self.location_dest_id.warehouse_id.pbm_loc_id.id:
            if not self.env.user.has_group('nivriti.pick_component_group'):
                raise ValidationError("Only user with Pick Component access right is allowed to validate the "
                                      "pick component transfer.")
        res = super().button_validate()
        return res

    def action_email(self):
        return {
            'name': 'Email Delivery',
            'type': 'ir.actions.act_window',
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'target': 'new',
            'views': [(False, 'form')],
            'view_id': False,
        }


class StockWarehouseOrderpointInherit(models.Model):
    _inherit = 'stock.warehouse.orderpoint'

    po_qty = fields.Float(string='PO Qty', compute='_compute_po_remaining_qty')

    def _compute_po_remaining_qty(self):
        for rec in self:
            purchase = self.env['purchase.order.line'].search([('state', '=', 'purchase'),
                                                               ('product_id', '=', rec.product_id.id)])
            if purchase:
                quantity = sum(purchase.mapped('product_qty'))
                received = sum(purchase.mapped('qty_received'))
                remaining_qty = quantity - received
                print(f"{quantity} quantity - {received} received = {remaining_qty} in stock.py file")
                rec.po_qty = remaining_qty
            else:
                rec.po_qty = 0


class StockLotInherit(models.Model):
    _inherit = 'stock.lot'

    manufacturing_date = fields.Date()

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('nivriti.lot_and_serial_editable'):
            raise ValidationError("Please note only certain group of users can only edit batch/Lot no .")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.user.has_group('nivriti.lot_and_serial_editable'):
            raise ValidationError("Please note only certain group of users can only edit batch/Lot no .")
        return super().write(vals)


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    cost_price = fields.Float(related='product_id.standard_price')
