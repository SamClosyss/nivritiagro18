from odoo import fields, api, models
from datetime import date


class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        res = super(MrpProductionInherit, self).button_mark_done()
        if self.lot_producing_id:
            self.lot_producing_id.manufacturing_date = date.today()
        return res

    @api.onchange('product_id', 'move_raw_ids', 'never_product_template_attribute_value_ids')
    def _onchange_product_id(self):
        for move in self.move_raw_ids:
            if self.product_id == move.product_id:
                message = _("The component %s should not be the same as the product to produce.",
                            self.product_id.display_name)
                self.move_raw_ids = self.move_raw_ids - move
                return {'warning': {'title': _('Warning'), 'message': message}}
