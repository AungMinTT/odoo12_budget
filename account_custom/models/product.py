from odoo import fields, models, api

class Product(models.Model):
    _inherit = 'product.product'

    @api.model
    def _convert_prepared_anglosaxon_line(self, line, partner):
        res = super(Product, self)._convert_prepared_anglosaxon_line(line, partner)
        res['ou_id'] = line.get('ou_id', False)
        return res