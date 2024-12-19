from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    analytic_tag_id = fields.Many2one("account.analytic.tag", "Analytic Tag")
    ou_id = fields.Many2one("operating.unit", "Operating Unit")

    @api.model
    def invoice_line_move_line_get(self):
        res = super(AccountInvoice, self).invoice_line_move_line_get()
        for account_move_line in res:
            invoice_line = self.env['account.invoice.line'].browse(account_move_line['invl_id'])
            if invoice_line and invoice_line.ou_id:
                account_move_line['ou_id'] = invoice_line.ou_id.id
        return res


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    ou_id = fields.Many2one("operating.unit", "Operating Unit")

    def _prepare_invoice_line(self):
        res = super(AccountInvoiceLine, self)._prepare_invoice_line()
        res['ou_id'] = self.ou_id.id
        return res