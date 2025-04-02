from odoo import api, fields, models,_
from markupsafe import Markup



class ChangeUom(models.TransientModel):
    _name = 'change.uom'
    _description = 'to change uom from product template'

    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    old_uom_id = fields.Many2one('uom.uom', string='Old Unit of Measure', readonly=True)
    product_variant_id = fields.Many2one('product.template', string='Product', readonly=True)
    reason = fields.Text(required=True,help="Please share the reason to change the uom")

    # revision = fields.Char(default="Main", tracking=True)

    def change_uom_submit(self):
        for record in self:
            self.env.cr.execute(
                f"update stock_move set product_uom = {record.uom_id.id} where product_id = {record.product_variant_id.id}")

            self.env.cr.execute(
                f"update stock_move_line set product_uom_id = {record.uom_id.id} where product_id = {record.product_variant_id.id}")

            self.env.cr.execute(
                f"update sale_order_line set product_uom = {record.uom_id.id} where product_id = {record.product_variant_id.id}")

            self.env.cr.execute(
                f"update purchase_order_line set product_uom = {record.uom_id.id} where product_id = {record.product_variant_id.id}")

            self.env.cr.execute(
                f"update account_move_line set product_uom_id = {record.uom_id.id} where product_id = {record.product_variant_id.id}")

            self.env.cr.execute(
                f"update mrp_bom set product_uom_id = {record.uom_id.id} where product_id = {record.product_variant_id.id}")

            self.env.cr.execute(
                f"update mrp_bom_line set product_uom_id = {record.uom_id.id} where product_id = {record.product_variant_id.id}")

            # self.env.cr.execute(f'update product_template set uom_id = {record.uom_id.id} where id = {record.id}')
            self.env.cr.execute(f'update product_template set uom_id = {record.uom_id.id} where id = {record.product_variant_id.id}')

            # self.env.cr.execute(f'update product_template set uom_po_id = {record.uom_id.id} where id = {record.id}')
            self.env.cr.execute(f'update product_template set uom_po_id = {record.uom_id.id} where id = {record.product_variant_id.id}')

            body = Markup(f'Changed UOM from {record.old_uom_id.name} --> {record.uom_id.name} <br> Reason --> {record.reason}')

            record.product_variant_id.message_post(
                body=body,
                message_type='comment'
            )

            record.product_variant_id.product_variant_id.message_post(
                body=body,
                message_type='comment'
            )

