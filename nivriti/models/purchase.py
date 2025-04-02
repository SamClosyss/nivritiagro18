from odoo import models, api, _, fields
from num2words import num2words
from odoo.exceptions import ValidationError


class InheritPurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @staticmethod
    def convert_num_to_text(value, currency_unit_label, currency_subunit_label):
        pre = float(value)
        text = ''
        entire_num = int((str(pre).split('.'))[0])
        decimal_num = int((str(pre).split('.'))[1])
        if decimal_num < 10:
            decimal_num = decimal_num * 10
        text += num2words(entire_num, lang='en_IN')
        text += f' {currency_unit_label} '
        if decimal_num >= 1:
            text += ' And '
            text += num2words(decimal_num, lang='en_IN')
            text += f' {currency_subunit_label} Only.'
        else:
            text += ' only '
        return text.title()

    def button_confirm(self):
        for rec in self:
            unactive_product = rec.order_line.filtered(lambda x: x.product_id.product_tmpl_id.active == False)
            if unactive_product:
                raise ValidationError(
                    f'Cannot confirm as this {",".join([i.product_id.name for i in unactive_product])} product is in archive')
        super().button_confirm()
