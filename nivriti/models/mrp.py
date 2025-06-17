from odoo import fields, api, models
from datetime import date


class MrpProductionInherit(models.Model):
    _inherit = 'mrp.production'

    def action_generate_serial(self):
        res = super().action_generate_serial()
        if self.lot_producing_id:
            self.lot_producing_id.company_id = self.company_id.id
            self.lot_producing_id.manufacturing_date = date.today()
        return res

    # def button_mark_done(self):
    #     res = super(MrpProductionInherit, self).button_mark_done()
    #     if self.lot_producing_id:
    #         self.lot_producing_id.manufacturing_date = date.today()
    #     return res
