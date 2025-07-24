# models/base_model_inherit.py
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class BaseModelInherit(models.AbstractModel):
    _inherit = 'base'

    def unlink(self):
        excluded_models = ['bus.bus', 'ir.cron.progress', 'base_import.import', 'base.module.update', 'bus.presence',
                           'confirm.stock.sms', 'expiry.picking.confirmation', 'change.production.qty',
                           'account.resequence.wizard', 'ir.cron.progress', 'mrp.consumption.warning',
                           'sale.advance.payment.inv', 'sale.order.discount', 'stock.backorder.confirmation',
                           "stock.backorder.confirmation.line", 'stock.register', "stock.return.picking",
                           "stock.return.picking.line", "stock.traceability.report", "stock.warehouse.orderpoint",
                           'ir.actions.server', 'ir.actions.report', 'stock.quant']
        cr = self._cr
        for record in self:
            if record._name in excluded_models:
                continue
            model_data = self.env['ir.model'].sudo().search([('model', '=', record._name)])
            if model_data and model_data.transient is True:
                continue
            cr.execute("select * from %s where id=%d" % (record._name.replace(".", "_"), record.id))
            note = cr.dictfetchone()
            name = record._name + "," + str(record.display_name)  # change to display name instead of id
            self.env['res.delete.history'].create({
                'name': name,
                'model': record._name,
                'note': note,
                'date': fields.Datetime.now(),
                'res_id': record.id,
                'user_id': record.env.user.id,
            })
        _logger.info(f"Successfully recorded delete history.")
        return super(BaseModelInherit, self).unlink()
