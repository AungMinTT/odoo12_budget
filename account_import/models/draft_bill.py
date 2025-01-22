from odoo import fields, models


class DraftBill(models.Model):
    _name = "draft.bill"

    name = fields.Char("Name")
    number = fields.Char("Number")
    partner_id = fields.Many2one('res.partner', "Vendor")
    reference = fields.Char("Vendor Reference")
    analytic_tag_id = fields.Many2one("account.analytic.tag", "Analytic Tag")
    ou_id = fields.Many2one("operating.unit", "Operating Unit")
    date_invoice = fields.Date("Bill Date")
    date_due = fields.Date("Due Date")
    journal_id = fields.Many2one('account.journal', string='Journal')
    draft_bill_line_ids = fields.One2many('draft.bill.line', 'draft_bill_id', string='Bill')
    amount_total = fields.Float("Total")

    _sql_constraints = [
        ('name_unique', 'unique(number)', 'Bill must be unique!(Duplicate Bill)')
    ]


class DraftBillLine(models.Model):
    _name = "draft.bill.line"

    name = fields.Char("Description")
    product_id = fields.Many2one('product.product', 'Product')
    account_id = fields.Many2one('account.account', 'Account')
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_id = fields.Many2one("account.analytic.tag", "Analytic Tag")
    ou_id = fields.Many2one("operating.unit", "Operating Unit")
    quantity = fields.Float("Quantity")
    price_unit = fields.Float("Unit Price")
    draft_bill_id = fields.Many2one('draft.bill', "Draft Bill")
    price_subtotal = fields.Float("Price Subtotal")

