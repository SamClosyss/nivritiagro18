from odoo import fields, api, models


class ProductSummary(models.TransientModel):
    _name = 'account.line.wizard'
    _description = 'to show data in wizard of min, max'

    min_price = fields.Float(string='Minimum price')
    max_price = fields.Float(string='Maximum price')
    average_price = fields.Float(string='Average price')
    latest_price = fields.Float(string='Latest price')
    product_name = fields.Many2one('product.product', string='Product')
    move_lines_ids = fields.One2many(comodel_name='account.order.lines', inverse_name='account_line_id', string='Data', domain=[('record_type', '=', 'main')])
    other_detail = fields.Boolean(string='Other Customer')
    other_min_price = fields.Float(string='Minimum price')
    other_max_price = fields.Float(string='Maximum price')
    other_average_price = fields.Float(string='Average price')
    other_latest_price = fields.Float(string='Latest price')
    other_move_line_ids = fields.One2many(comodel_name='account.order.lines', inverse_name='account_line_id', domain=[('record_type', '=', 'other')])


class ProductSummaryLines(models.TransientModel):
    _name = 'account.order.lines'
    _description = 'to show one2many data'

    date = fields.Date(string='Date')
    description = fields.Char(string='Description')
    qty = fields.Float(string='Quantity')
    price = fields.Float(string='Price')
    tax_ids = fields.Many2many('account.tax', string='Tax')
    price_total = fields.Float(string='Price Total')
    account_line_id = fields.Many2one('account.line.wizard')
    record_type = fields.Selection([('main', 'Main'), ('other', 'Other')])


class StockStatus(models.TransientModel):
    _name = 'stock.status'
    _description = 'to show availabilty of multiple warehouse product'

    quotation = fields.Float(string="Quotation Qty", readonly=True, help="Quotation qty is calucalted from sales quotation which are in stage draft and sent.")
    outgoing = fields.Float(string='Outgoing Qty', readonly=True, help="Outgoing Qtu is calculated from DC which are not in draft, completed or cancel stage.")
    onhand = fields.Float(string="On-hand Qty", readonly=True, help="On-Hand Qty is actual stock available it also includes reserved stock.")
    available = fields.Float(string="Available Qty", readonly=True, help="Available Qty is calculated by decreasing the quantity reserved against some DC.")
    location_ids = fields.One2many(comodel_name='stock.location.wizard',
                                   inverse_name='location_status_id', string='Location')


class StockLocationWizard(models.TransientModel):
    _name = 'stock.location.wizard'
    _description = 'for one2many'

    available = fields.Float(string="Availabe", readonly=True)
    reserved = fields.Float(string='Reserved', readonly=True)
    onhand_stock = fields.Float(string="Onhand Product", readonly=True)
    location_id = fields.Many2one('stock.location', readonly=True)
    location_status_id = fields.Many2one(comodel_name='stock.status', readonly=True)

