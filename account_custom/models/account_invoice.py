from odoo import models, fields


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    ou_id = fields.Many2one("operating.unit", "Operating Unit")


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    ou_id = fields.Many2one("operating.unit", "Operating Unit")