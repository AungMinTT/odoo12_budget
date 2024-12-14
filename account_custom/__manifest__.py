# Copyright 2015-TODAY Eficent
# - Jordi Ballester Alomar
# Copyright 2015-TODAY Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License: LGPL-3 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Account Custom",
    "summary": "Custom for account.",
    "version": "12.0.0.1.0",
    "author": "Royal Express",
    "website": "",
    "category": "Generic",
    "depends": ["base", "account", "analytic", "operating_unit"],
    "data": [
        "views/account_invoice_view.xml",
        "views/account_move_view.xml",
        "views/analytic_account_view.xml"
    ],
    "license": "LGPL-3",
    'installable': True,
}
