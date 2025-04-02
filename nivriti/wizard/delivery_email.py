from odoo import fields, api, models
import html2text


class EmailDelivery(models.TransientModel):
    _name = 'email.delivery.wizard'
    _description = 'Email for delivery'

    partner_id = fields.Many2one('res.partner')
    subject = fields.Char()
    template_id = fields.Many2one('mail.template')
    attach = fields.Binary()
    attachement = fields.Char()
    description = fields.Html(
        'Contents',
        render_engine='qweb', render_options={'post_process': True},
        sanitize_style=True,
        readonly=False, store=True)
    #  compute='_compute_body',

    @api.onchange('template_id')
    def _compute_body(self):
        for composer in self:
            composer.description = False
            if composer.template_id:
                composer.description = composer.template_id.body_html
