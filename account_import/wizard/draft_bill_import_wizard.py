from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import xlrd
import ast


class DraftBillImportWizard(models.TransientModel):
    _name = 'draft.bill.import.wizard'
    _description = 'Draft Bill Import Wizard'

    file = fields.Binary(string='Excel File', required=True, help="Upload your Excel file here.")
    filename = fields.Char(string='Filename')
    count_success = fields.Integer(string="Successfully Imported", default=0)

    def action_import(self):
        if not self.file:
            raise ValueError("Please upload an Excel file before importing.")
        data = base64.b64decode(self.file)
        book = xlrd.open_workbook(file_contents=data)
        success_count = 0
        for sheet in book.sheets():
            try:
                for row_idx in range(1, sheet.nrows):
                    row = sheet.row_values(row_idx)
                    if row[2]:
                        vendor = self.env['res.partner'].search([('ref', '=', row[2])])
                        if not vendor:
                            vendor = self.env['res.partner'].create(
                                {'name': row[1], 'ref': row[2], 'customer': False,
                                 'supplier': True})
                    else:
                        vendor = self.env['res.partner'].create(
                            {'name': row[1], 'ref': row[2], 'customer': False,
                             'supplier': True})
                    analytic_tag = self.env["account.analytic.tag"].search(
                        [('code', '=', row[6])])
                    if not analytic_tag:
                        raise UserError(f"Goal(Analytic Tag) Code {row[6]} does not exit in Finance System. Row {row_idx+1}.")
                    operating_unit = self.env["operating.unit"].search([('code', '=', row[7])])
                    if not operating_unit:
                        raise UserError(f"Operation Unit Code {row[7]} does not exit in Finance System. Row {row_idx+1}.")
                    journal = self.env['account.journal'].search([('code', '=', row[5])])
                    if not journal:
                        raise UserError(f"Journal Code {row[5]} does not exit in Finance System. Roe {row_idx+1}.")
                    try:
                        bill = self.env['draft.bill'].create({
                            'name': row[0],
                            'number': row[0],
                            'partner_id': vendor.id,
                            'reference': 'BUDGET',
                            'analytic_tag_id': analytic_tag.id,
                            'ou_id': operating_unit.id,
                            'date_invoice': row[3],
                            'date_due': row[4],
                            'journal_id': journal.id,
                            'amount_total': row[9]
                        })
                    except Exception as e:
                        raise ValidationError(_(e))
                    line_list = ast.literal_eval(row[8])
                    value_list = []
                    for line in line_list:
                        account = self.env["account.account"].search([('code', '=', line.get('account_code'))])
                        if not account:
                            raise UserError(f"Account Code {line.get('account_code')} does not exit in Finance System. Row {row_idx+1} Column 'Invoice Line'.")
                        analytic_account = self.env["account.analytic.account"].search(
                            [('code', '=', line.get('analytic_account_code'))])
                        if not analytic_account:
                            raise UserError(f"Analytic Account Code {line.get('analytic_account_code')} does not exit in Finance System. Row {row_idx+1} Column 'Invoice Line'.")
                        analytic_tag = self.env["account.analytic.tag"].search(
                            [('code', '=', line.get('analytic_tag_code'))])
                        if not analytic_tag:
                            raise UserError(f"Goal(Analytic Tag) Code {line.get('analytic_tag_code')} does not exit in Finance System. Row {row_idx+1} Column 'Invoice Line'.")
                        operating_unit = self.env["operating.unit"].search([('code', '=', line.get('ou_code'))])
                        if not operating_unit:
                            return UserError(f"Operation Unit Code {line.get('ou_code')} does not exit in Finance System. Row {row_idx+1} Column 'Invoice Line'.")
                        value = {
                            'name': line.get('name'),
                            'account_id': account.id,
                            'account_analytic_id': analytic_account.id,
                            'analytic_tag_id': analytic_tag.id,
                            'ou_id': operating_unit.id,
                            'quantity': line.get('quantity'),
                            'price_unit': line.get('price_unit'),
                            'draft_bill_id': bill.id,
                            'price_subtotal': line.get('price_subtotal')
                        }
                        value_list.append(value)
                    try:
                        self.env['draft.bill.line'].create(value_list)
                    except Exception as e:
                        raise ValidationError(_(e))
                    success_count += 1
            except IndexError:
                pass
        self.count_success = success_count
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'draft.bill.import.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }