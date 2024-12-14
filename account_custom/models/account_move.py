from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"

    ou_id = fields.Many2one("operating.unit", "Operating Unit")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    ou_id = fields.Many2one("operating.unit", "Operating Unit")