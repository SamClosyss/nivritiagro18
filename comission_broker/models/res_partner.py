from odoo import fields, api, models, _


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    broker_id = fields.Many2one('res.partner',tracking=True)
    broker_type = fields.Selection([('disc','Discount'),('rate_diff','Rate Difference')])
    broker_value = fields.Float()