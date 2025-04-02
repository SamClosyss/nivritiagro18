from odoo import fields, api, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import clean_context


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    po_date = fields.Date('PO Date')

    # Inherited from Default
    # Reason of inheriting is that if sales stage is in quotation and Send log note was not generating and we needed it
    def _track_finalize(self):
        """ Generate the tracking messages for the records that have been
        prepared with ``_tracking_prepare``.
        """
        initial_values = self.env.cr.precommit.data.pop(f'mail.tracking.{self._name}', {})
        ids = [id for id, vals in initial_values.items() if vals]
        if not ids:
            return
        records = self.browse(ids).sudo()
        fnames = self._track_get_fields()
        context = clean_context(self._context)
        tracking = records.with_context(context)._message_track(fnames, initial_values)
        for record in records:
            changes, _tracking_value_ids = tracking.get(record.id, (None, None))
            record._message_track_post_template(changes)
        # this method is called after the main flush() and just before commit();
        # we have to flush() again in case we triggered some recomputations
        self.env.flush_all()

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        value = {
            'po_date': self.po_date,
            # 'ref':self.client_order_ref
        }
        res.update(value)
        return res

    def action_confirm(self):
        for rec in self:
            unactive_product = rec.order_line.filtered(lambda x: x.product_template_id.active == False)
            if unactive_product:
                raise ValidationError(
                    f'Cannot confirm as this {",".join([i.product_id.name for i in unactive_product])} product is in archive')
        super().action_confirm()


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    delivery_status = fields.Selection([('yet', 'Yet To Delivered'), ('partial', 'Partially Delivered'),
                                        ('fully', 'Fully Delivered'), ('nothing', 'Nothing to Delivered')],
                                       compute='_compute_deliver_status', store=True)

    @api.depends('qty_delivered', 'product_uom_qty')
    def _compute_deliver_status(self):
        for rec in self:
            if rec.state == 'sale':
                if rec.qty_delivered == 0:
                    rec.delivery_status = 'yet'
                elif rec.product_uom_qty > rec.qty_delivered:
                    rec.delivery_status = 'partial'
                elif rec.product_uom_qty == rec.qty_delivered:
                    rec.delivery_status = 'fully'
            elif rec.state != 'sale':
                rec.delivery_status = 'nothing'

    def action_product_history(self):
        invoice_lines = self.env['account.move.line'].search([('parent_state', '=', 'posted'),
                                                              ('move_type', '=', 'out_invoice'),
                                                              ('partner_id', '=', self.order_id.partner_id.id),
                                                              ('product_id', '=', self.product_id.id)]
                                                             , order='create_date desc', limit=10)
        invoice_lines_other = self.env['account.move.line'].search([('parent_state', '=', 'posted'),
                                                                    ('move_type', '=', 'out_invoice'),
                                                                    ('partner_id', '!=', self.order_id.partner_id.id),
                                                                    ('product_id', '=', self.product_id.id)]
                                                                   , order='create_date desc', limit=10)
        other_price_unit = invoice_lines_other.mapped('price_unit')
        price_unit = invoice_lines.mapped('price_unit')
        latest_price = invoice_lines and invoice_lines.sorted(lambda x: x.invoice_date, reverse=True)[0].price_unit or 0
        other_latest_price = invoice_lines_other and invoice_lines_other.sorted(lambda x: x.invoice_date, reverse=True)[
            0].price_unit or 0
        data = {
            'min_price': price_unit and min(price_unit) or 0,
            'max_price': price_unit and max(price_unit) or 0,
            'average_price': price_unit and (sum(price_unit) / len(price_unit)) or 0,
            'other_min_price': other_price_unit and min(other_price_unit) or 0,
            'other_max_price': other_price_unit and max(other_price_unit) or 0,
            'other_average_price': other_price_unit and (sum(other_price_unit) / len(other_price_unit)) or 0,
            'latest_price': latest_price,
            'other_latest_price': other_latest_price,
            'move_lines_ids': [(0, 0, {'date': line.invoice_date, 'description': line.name, 'qty': line.quantity,
                                       'price': line.price_unit, 'price_total': line.price_subtotal,
                                       'record_type': 'main'}) for line in invoice_lines],
            'other_move_line_ids': [(0, 0, {'date': line.invoice_date, 'description': line.name, 'qty': line.quantity,
                                            'price': line.price_unit, 'price_total': line.price_subtotal,
                                            'record_type': 'other'}) for line in invoice_lines_other],
        }
        res_id = self.env['account.line.wizard'].create(data)
        return {
            'type': 'ir.actions.act_window',
            'name': invoice_lines.product_id.name,
            'view_mode': 'form',
            'res_model': 'account.line.wizard',
            'res_id': res_id.id,
            'context': {'create': 0, 'delete': 0, 'no_open': 1},
            'target': 'new'
        }

    def action_stock_update(self):
        quotation = sum(self.env['sale.order.line'].search([('product_id', '=', self.product_id.id),
                                                            ('order_id.state', 'in', ('draft', 'sent')),
                                                            ]).mapped('product_uom_qty'))
        outgoing = sum(self.env['stock.move'].search([('product_id', '=', self.product_id.id),
                                                      ('state', 'not in', ('draft', 'done', 'cancel')),
                                                      ('picking_code', '=', 'outgoing')]).mapped('product_uom_qty'))
        on_hand = self.env['stock.quant'].search(
            [('product_id', '=', self.product_id.id), ('quantity', '>', 0), ('location_id.usage', '=', 'internal')])

        on_hand_qty = sum(on_hand.mapped('quantity'))
        available = sum(on_hand.mapped('available_quantity'))
        lines = {}
        for rec in on_hand:
            location_id = rec.location_id.id

            if location_id not in lines:
                lines.update({
                    rec.location_id.id: {'available': rec.available_quantity, 'reserved': rec.reserved_quantity,
                                         'onhand_stock': rec.quantity, 'location_id': location_id}
                })
            else:
                lines[location_id]['available'] += rec.available_quantity
                lines[location_id]['reserved'] += rec.reserved_quantity
                lines[location_id]['onhand_stock'] += rec.quantity

        data = {'quotation': quotation, 'outgoing': outgoing, 'onhand': on_hand_qty, 'available': available,
                'location_ids': [(0, 0, line) for line in lines.values()]}
        res_id = self.env['stock.status'].create(data)
        return {
            'type': 'ir.actions.act_window',
            'name': self.product_id.name,
            'view_mode': 'form',
            'res_model': 'stock.status',
            'res_id': res_id.id,
            'context': {'create': 0, 'delete': 0, 'no_open': 1},
            'target': 'new'
        }
