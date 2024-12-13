"""Common methods"""
import ast
import json
import werkzeug.wrappers
from datetime import date, datetime
from json import dumps


def json_serial(obj):
    """ JSON serializer for objects not serializable by default json code """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, bytes):
        return obj.decode("utf-8")
    raise TypeError("Type %s not serializable" % type(obj))

def valid_response(data, status=200):
    """Valid Response
    This will be return when the http request was successfully processed."""
    '''
    data = {
        'count': len(data),
        'data': data
    }
    '''
    return werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=dumps(data, default=json_serial),
    )
    return data


def invalid_response(typ, message=None, status=400):
    """Invalid Response
    This will be the return value whenever the server runs into an error
    either from the client or the server."""
    if isinstance(message, Exception):
        message = message.name
        status = 500
    return werkzeug.wrappers.Response(
        status=status,
        content_type='application/json; charset=utf-8',
        response=json.dumps({
            'type': typ,
            'message': message if message else 'wrong arguments (missing validation)',
        }),
    )
    '''
    return {
        'type': typ,
            'message': message if message else 'wrong arguments (missing validation)',
    }
    '''


def extract_arguments(payload, offset=0, limit=0, order=None):
    """."""
    fields, domain = [], []
    context = {}
    if payload.get('domain'):
        domain += ast.literal_eval(payload.get('domain'))
    if payload.get('fields'):
        fields += ast.literal_eval(payload.get('fields'))
    if payload.get('offset'):
        offset = int(payload['offset'])
    if payload.get('limit'):
        limit = int(payload['limit'])
    if payload.get('order'):
        order = payload.get('order')
    if payload.get('context'):
        context = ast.literal_eval(payload.get('context'))
    return [domain, fields, offset, limit, order, context]


def extract_value(payload):
    for key, value in list(payload.items()):
        try:
            if key in ['login', 'password', 'db', 'domain', 'context']:
                del payload[key]
            payload.update({key: ast.literal_eval(value)})
        except:
            pass
    return payload
