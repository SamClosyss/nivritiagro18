from odoo import fields, models, api, _


class InheritMrpProduction(models.Model):
    _inherit = "mrp.production"

    roasting_diff = fields.Float(string='Roasting Difference')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type', copy=True, readonly=False,
        compute='_compute_picking_type_id', store=True, precompute=True,
        domain="[('code', '=', 'mrp_operation')]",
        required=True, check_company=True, index=True)

    @api.depends('company_id', 'bom_id')
    def _compute_picking_type_id(self):
        domain = [
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', 'in', self.company_id.ids),
        ]
        picking_types = self.env['stock.picking.type'].search_read(domain, ['company_id'], load=False, limit=1)
        picking_type_by_company = {pt['company_id']: pt['id'] for pt in picking_types}
        default_picking_type_id = self._context.get('default_picking_type_id')
        default_picking_type = default_picking_type_id and self.env['stock.picking.type'].browse(
            default_picking_type_id)
        for mo in self:
            if default_picking_type and default_picking_type.company_id == mo.company_id:
                mo.picking_type_id = default_picking_type_id
                continue
            if mo.bom_id and mo.bom_id.picking_id:
                mo.picking_type_id = mo.bom_id.picking_id
                continue
            if mo.picking_type_id and mo.picking_type_id.company_id == mo.company_id:
                continue
            mo.picking_type_id = picking_type_by_company.get(mo.company_id.id, False)

    def compute_roasting_diff(self):
        for rec in self:
            if rec.product_qty:
                move_raw_id = sum(
                    rec.move_raw_ids.filtered(lambda x: x.product_id.categ_id.is_raw_material).mapped('quantity'))
                move_byproduct_id = sum(rec.move_byproduct_ids.mapped('quantity'))
                scrap = sum(rec.scrap_ids.filtered(lambda x: x.product_id.categ_id.is_raw_material).mapped('scrap_qty'))
                rec.roasting_diff = (move_raw_id - scrap) - (rec.product_qty + move_byproduct_id)

    def button_mark_done(self):
        res = super().button_mark_done()
        self.compute_roasting_diff()
        return res


class InheritMrpBom(models.Model):
    _inherit = "mrp.bom"

    picking_id = fields.Many2one('stock.picking.type', domain="[('code', '=', 'mrp_operation')]",
                                 check_company=True)


# class InheritStockRule(models.Model):
#     _inherit = 'stock.rule'
#
#     def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values,
#                          bom):
#         res = super()._prepare_mo_vals(product_id, product_qty, product_uom, location_dest_id, name, origin, company_id,
#                                        values, bom)
#         res.update({
#             'picking_type_id': bom.picking_id.id,
#             'location_src_id': bom.picking_id.default_location_src_id.id,
#             'location_dest_id': bom.picking_id.default_location_dest_id.id,
#         })
#         return res
