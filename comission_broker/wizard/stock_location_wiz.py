from odoo import fields, api, models, _


class StockLocationWiz(models.TransientModel):
    _name = "stock.location.wiz"

    location_id = fields.Many2one('stock.location')
    dest_location_id = fields.Many2one('stock.location')
    stock_location_line_id = fields.One2many('stock.location.line', 'stock_loc_id')
    picking_id = fields.Many2one('stock.picking')

    def create_transfer(self):
        print(self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1))
        data = {
            'picking_type_id': self.env['stock.picking.type'].search([('code', '=', 'internal')], limit=1).id,
            'location_id': self.location_id.id,
            'location_dest_id': self.dest_location_id.id,

            'move_ids_without_package': [
                (0, 0, {'name': '/','group_id':self.picking_id.group_id.id, 'product_id': line.product_id.id, 'product_uom_qty': line.product_uom_qty,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.dest_location_id.id, }) for line in
                self.stock_location_line_id]
        }
        pick_id = self.env['stock.picking'].create(data)
        pick_id.action_confirm()



class StockLocationLine(models.TransientModel):
    _name = 'stock.location.line'

    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float('Demand')
    stock_loc_id = fields.Many2one('stock.location.wiz')
