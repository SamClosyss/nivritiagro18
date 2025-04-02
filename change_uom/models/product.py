from odoo import api, fields, models


class ProductTemplateInherit(models.Model):
    _inherit = 'product.template'

    def action_open_change_uom(self):
        return{
            'type': 'ir.actions.act_window',
            'name': 'Change UOM',
            'view_mode': 'form',
            'res_model': 'change.uom',
            'context': {'default_product_variant_id': self.id, 'default_old_uom_id': self.uom_id.id},
            'target': 'new',
        }
