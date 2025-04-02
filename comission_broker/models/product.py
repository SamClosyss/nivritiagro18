from odoo import fields, api, models, _


class InheritProductCategory(models.Model):
    _inherit = "product.category"

    is_raw_material = fields.Boolean(default=False, string="Raw Material")
