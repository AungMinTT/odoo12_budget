from odoo import fields, models, api
from odoo.exceptions import ValidationError


class AccountAnalyticTag(models.Model):
    _inherit = "account.analytic.tag"

    code = fields.Char("Analytic Code", required=True)

    _sql_constraints = [
        ('analytic_code_unique', 'UNIQUE(code)', 'The value of this field Analytic Code must be unique!')
    ]

    @api.constrains('code')
    def _check_unique_field(self):
        for record in self:
            if self.search_count([('code', '=', record.code)]) > 1:
                raise ValidationError("The value of the field must be unique!")
