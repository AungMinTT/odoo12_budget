"""Part of odoo. See LICENSE file for full copyright and licensing details."""

import functools
import logging
from odoo import http
from odoo.http import request
from odoo.addons.restful.common import valid_response, invalid_response, extract_arguments, extract_value

_logger = logging.getLogger(__name__)


def validate_token(func):
    """."""
    @functools.wraps(func)
    def wrap(self, *args, **kwargs):
        """."""
        access_token = request.httprequest.headers.get('access_token')
        db = request.httprequest.headers.get('db')
        login = request.httprequest.headers.get('login')
        password = request.httprequest.headers.get('password')
        wso2 = request.httprequest.headers.get('wso2')
        print(wso2)
        if not access_token:
            return invalid_response('access_token_not_found', 'missing access token in request header', 401)

        if wso2 == "wso2":
            request.session.authenticate(db, login, password)
        else:
            request.session.authenticate(kwargs['db'], kwargs['login'], kwargs['password'])

        access_token_data = request.env['api.access_token'].sudo().search(
            [('token', '=', access_token)], order='id DESC', limit=1)

        if access_token_data.find_one_or_create_token(user_id=access_token_data.user_id.id) != access_token:
            return invalid_response('access_token', 'token seems to have expired or invalid', 401)

        request.session.uid = access_token_data.user_id.id
        request.uid = access_token_data.user_id.id
        return func(self, *args, **kwargs)
    return wrap


_routes = [
    '/api/<model>',
    '/api/<model>/<id>',
    '/api/<model>/<id>/<action>'
]


class APIController(http.Controller):
    """."""

    def __init__(self):
        self._model = 'ir.model'

    @validate_token
    @http.route(_routes, type='http', auth="none", methods=['GET'], csrf=False)
    def get(self, model=None, id=None, **payload):
        _id = None
        try:
            if id:
                _id = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid literal %s for id with base ' % id)
        ioc_name = model
        model = request.env[self._model].sudo().search(
            [('model', '=', model)], limit=1)
        if model:
            domain, fields, offset, limit, order, context = extract_arguments(
                payload)
            if not context:
                context = request.env.context.copy()
            if _id:
                domain += [('id', '=', _id)]
            data = request.env[model.model].with_context(context).sudo().search_read(
                domain=domain, fields=fields, offset=offset, limit=limit, order=order)
            if data:
                return valid_response(data)
            else:
                return valid_response(data)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % ioc_name)

    @validate_token
    @http.route(_routes, type='http', auth="none", methods=['POST'], csrf=False)
    def create(self, model=None, id=None, **payload):
        """Create a new record.
        Basic sage:
        import requests

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'access-token': 'access_token'
        }
        data = {
            'name': 'Babatope Ajepe',
            'country_id': 105,
            'child_ids': [
                {
                    'name': 'Contact',
                    'type': 'contact'
                },
                {
                    'name': 'Invoice',
                   'type': 'invoice'
                }
            ],
            'category_id': [{'id': 9}, {'id': 10}]
        }
        req = requests.post('%s/api/res.partner/' %
                            base_url, headers=headers, data=data)

        """
        data = payload.get('data')
        ioc_name = model
        model = request.env[self._model].sudo().search(
            [('model', '=', model)], limit=1)
        if model:
            try:
                domain, fields, offset, limit, order, context = extract_arguments(
                    payload)
                if not context:
                    context = request.env.context.copy()
                payload = extract_value(payload)
                resource = request.env[model.model].with_context(context).sudo().create(payload)
                # resource = request.env[model.model].sudo().create(request.jsonrequest)
            except Exception as e:
                request.cr.rollback()
                return invalid_response('params', e)
            else:
                data = {'id': resource.id}
                if resource:
                    return valid_response(data)
                else:
                    return valid_response(data)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % ioc_name)

    @validate_token
    @http.route('/api/bill/', type='http', auth="none", methods=['POST'], csrf=False)
    def create_bill(self, model=None, id=None, **payload):
        ioc_name = model
        model = request.env[self._model].sudo().search(
            [('model', '=', 'account.invoice')], limit=1)
        if model:
            try:
                domain, fields, offset, limit, order, context = extract_arguments(
                    payload)
                if not context:
                    context = request.env.context.copy()
                payload = extract_value(payload)
                if payload.get('partner_ref'):
                    vendor = request.env['res.partner'].search([('ref', '=', payload.get('partner_ref'))])
                    if not vendor:
                        vendor = request.env['res.partner'].create({'name': payload.get('partner_name'), 'ref': payload.get('ref'), 'customer': False, 'supplier': True})
                else:
                    vendor = request.env['res.partner'].create({'name': payload.get('partner_name'), 'ref': payload.get('ref'), 'customer': False, 'supplier': True })

                journal = request.env['account.journal'].search([('code', '=', payload.get('journal_code'))])
                if not journal:
                    request.cr.rollback()
                    return invalid_response('account.journal', "Journal does not exit in Finance System.")
                analytic_tag = request.env["account.analytic.tag"].search(
                    [('code', '=', payload.get('analytic_tag_code'))])
                if not analytic_tag:
                    request.cr.rollback()
                    return invalid_response('account.analytic.tag', "Analytic Tag does not exit in Finance System.")
                operating_unit = request.env["operating.unit"].search([('code', '=', payload.get('ou_code'))])
                if not operating_unit:
                    request.cr.rollback()
                    return invalid_response('operating.unit', "Operation Unit does not exit in Finance System.")
                bill_values = {
                    # 'name': payload.get('number'),
                    'number': payload.get('number'),
                    'type': payload.get('type'),
                    'state': payload.get('state'),
                    'partner_id': vendor.id,
                    'date_invoice': payload.get('date_invoice'),
                    'date_due': payload.get('date_due'),
                    'journal_id': journal.id,
                    'analytic_tag_id': analytic_tag.id,
                    'ou_id': operating_unit.id
                }
                bill = request.env['account.invoice'].with_context(context).sudo(request.uid).create(bill_values)
                bill_line_values = payload.get('invoice_line_ids', [])
                bill_line_list = []
                for line in bill_line_values:
                    account = request.env["account.account"].search([('code', '=', line.get('account_code'))])
                    if not account:
                        request.cr.rollback()
                        return invalid_response('account.account', "Account does not exit in Finance System.")
                    line['account_id'] = account.id
                    analytic_account = request.env["account.analytic.account"].search([('code', '=', line.get('analytic_account_code'))])
                    if not analytic_account:
                        request.cr.rollback()
                        return invalid_response('account.analytic.tag', "Analytic Account does not exit in Finance System.")
                    line['account_analytic_id'] = analytic_account.id
                    analytic_tag = request.env["account.analytic.tag"].search([('code', '=', line.get('analytic_tag_code'))])
                    if not analytic_tag:
                        request.cr.rollback()
                        return invalid_response('account.analytic.tag', "Analytic Tag does not exit in Finance System.")
                    line['analytic_tag_ids'] = [(4, analytic_tag.id)]
                    operating_unit = request.env["operating.unit"].search([('code', '=', line.get('ou_code'))])
                    if not operating_unit:
                        request.cr.rollback()
                        return invalid_response('operating.unit', "Operation Unit does not exit in Finance System.")
                    line['ou_id'] = operating_unit.id
                    line['name'] = line.get('name')
                    line['invoice_id'] = bill.id
                    bill_line_list.append(line)
                request.env['account.invoice.line'].create(bill_line_list)
                bill.action_invoice_open()
                bill.write({'number': payload.get('number'), 'move_name': payload.get('move_name')})
                journal = request.env['account.move'].search([('id', '=', bill.move_id.id)])
                journal.write({'name': payload.get('number')})
            except Exception as e:
                request.cr.rollback()
                return invalid_response('params', str(e))
            else:
                data = {'id': bill.id}
                if bill:
                    return valid_response(data)
                else:
                    return valid_response(data)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % ioc_name)

    @validate_token
    @http.route('/api/journal/', type='http', auth="none", methods=['POST'], csrf=False)
    def create_journal(self, model=None, id=None, **payload):
        ioc_name = model
        model = request.env[self._model].sudo().search(
            [('model', '=', 'account.move')], limit=1)
        if model:
            try:
                domain, fields, offset, limit, order, context = extract_arguments(
                    payload)
                if not context:
                    context = request.env.context.copy()
                payload = extract_value(payload)
                journal = request.env['account.journal'].search([('code', '=', payload.get('journal_code'))])
                if not journal:
                    request.cr.rollback()
                    return invalid_response('account.journal', "Journal does not exit in Finance System.")
                analytic_tag = request.env["account.analytic.tag"].search(
                    [('code', '=', payload.get('analytic_tag_code'))])
                if not analytic_tag:
                    request.cr.rollback()
                    return invalid_response('account.analytic.tag', "Analytic Tag does not exit in Finance System.")
                operating_unit = request.env["operating.unit"].search([('code', '=', payload.get('ou_code'))])
                if not operating_unit:
                    request.cr.rollback()
                    return invalid_response('operating.unit', "Operation Unit does not exit in Finance System.")
                journal_entries_values = {
                    'date': payload.get('date'),
                    'ref': payload.get('ref'),
                    'journal_id': journal.id,
                    'analytic_tag_id': analytic_tag.id,
                    'ou_id': operating_unit.id,
                    'state': payload.get('state'),
                }
                journal_entries = request.env['account.move'].with_context(context).sudo(request.uid).create(journal_entries_values)
                journal_entries_line_values = payload.get('journal_line_values', [])
                journal_line_list = []
                for line in journal_entries_line_values:
                    if line.get('credit') == 0.0:
                        account = request.env["account.account"].search([('code', '=', line.get('account_code'))])
                        if not account:
                            request.cr.rollback()
                            return invalid_response('account.account', "Account does not exit in Finance System.")
                        line['account_id'] = account.id
                        analytic_account = request.env["account.analytic.account"].search(
                            [('code', '=', line.get('analytic_account_code'))])
                        if not analytic_account:
                            request.cr.rollback()
                            return invalid_response('account.analytic.tag',
                                                    "Analytic Account does not exit in Finance System.")
                        line['analytic_account_id'] = analytic_account.id
                        analytic_tag = request.env["account.analytic.tag"].search(
                            [('code', '=', line.get('analytic_tag_code'))])
                        if not analytic_tag:
                            request.cr.rollback()
                            return invalid_response('account.analytic.tag', "Analytic Tag does not exit in Finance System.")
                        line['analytic_tag_ids'] = [(4, analytic_tag.id)]
                        operating_unit = request.env["operating.unit"].search([('code', '=', line.get('ou_code'))])
                        if not operating_unit:
                            request.cr.rollback()
                            return invalid_response('operating.unit', "Operation Unit does not exit in Finance System.")
                        line['ou_id'] = operating_unit.id
                        line['name'] = line.get('name')
                        line['move_id'] = journal_entries.id
                        # try:
                        #     journal_line = request.env['account.move.line'].create(line)
                        #     print(journal_line)
                        # except Exception as e:
                        #     print(e)
                        journal_line_list.append(line)
                    else:
                        account = request.env["account.account"].search([('code', '=', line.get('account_code'))])
                        if not account:
                            request.cr.rollback()
                            return invalid_response('account.account', "Account does not exit in Finance System.")
                        line['account_id'] = account.id
                        line['move_id'] = journal_entries.id
                        journal_line_list.append(line)
                request.env['account.move.line'].create(journal_line_list)
                journal_entries.write({'name': payload.get('name')})

            except Exception as e:
                request.cr.rollback()
                return invalid_response('params', str(e))
            else:
                data = {'id': journal_entries.id}
                if journal_entries:
                    return valid_response(data)
                else:
                    return valid_response(data)
        return invalid_response('invalid object model', 'The model %s is not available in the registry.' % ioc_name)

    @validate_token
    @http.route(_routes, type='http', auth="none", methods=['PUT'], csrf=False)
    def put(self, model=None, id=None, **payload):
        """."""
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid literal %s for id with base ' % id)
        _model = request.env[self._model].sudo().search(
            [('model', '=', model)], limit=1)
        if not _model:
            return invalid_response('invalid object model', 'The model %s is not available in the registry.' % model, 404)
        try:
            domain, fields, offset, limit, order, context = extract_arguments(
                payload)
            if not context:
                context = request.env.context.copy()
            payload = extract_value(payload)
            request.env[_model.model].with_context(context).sudo().browse(_id).write(payload)
            # request.env[_model.model].sudo().browse(_id).write(request.jsonrequest)
        except Exception as e:
            request.cr.rollback()
            return invalid_response('exception', e.name)
        else:
            return valid_response('update %s record with id %s successfully!' % (_model.model, _id))

    @validate_token
    @http.route(_routes, type='http', auth="none", methods=['DELETE'], csrf=False)
    def delete(self, model=None, id=None, **payload):
        """."""
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid literal %s for id with base ' % id)
        try:
            record = request.env[model].sudo().search([('id', '=', _id)])
            if record:
                record.unlink()
            else:
                return invalid_response('missing_record', 'record object with id %s could not be found' % _id, 404)
        except Exception as e:
            request.cr.rollback()
            return invalid_response('exception', e.name, 503)
        else:
            return valid_response('record %s has been successfully deleted' % record.id)

    @validate_token
    @http.route(_routes, type='http', auth="none", methods=['PATCH'], csrf=False)
    def patch(self, model=None, id=None, action=None, **payload):
        """."""
        try:
            _id = int(id)
        except Exception as e:
            return invalid_response('invalid object id', 'invalid literal %s for id with base ' % id)
        try:
            domain, fields, offset, limit, order, context = extract_arguments(
                payload)
            if not context:
                context = request.env.context.copy()
            record = request.env[model].with_context(context).sudo().search([('id', '=', _id)])
            _callable = action in [method for method in dir(
                record) if callable(getattr(record, method))]
            if record and _callable:
                # action is a dynamic variable.
                getattr(record, action)()
            else:
                return invalid_response('missing_record',
                                        'record object with id %s could not be found or %s object has no method %s' % (_id, model, action), 404)
        except Exception as e:
            request.cr.rollback()
            return invalid_response('exception', e, 503)
        else:
            return valid_response('record %s has been successfully patched' % record.id)
