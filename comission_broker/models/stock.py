from odoo import fields, api, models, _


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking'

    def fetch_operation_lines(self):
        return {
            'name': _("Stock Location"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.location.wiz',
            'view_mode': 'form',
            'context': {'default_picking_id': self.id, 'default_dest_location_id': self.location_id.id,
                        'default_stock_location_line_id': [
                            (0, 0, {'product_id': rec.product_id.id, 'product_uom_qty': rec.product_uom_qty}) for rec in
                            self.move_ids_without_package]},
            'target': 'new',
        }
