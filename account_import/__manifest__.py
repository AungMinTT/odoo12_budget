# Copyright 2015-TODAY Eficent
# - Jordi Ballester Alomar
# Copyright 2015-TODAY Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License: LGPL-3 or later (https://www.gnu.org/licenses/lgpl.html).
{
    "name": "Account Import",
    "summary": "Custom for account.",
    "version": "12.0.0.1.0",
    "author": "Royal Express",
    "website": "",
    "category": "Generic",
    "depends": ["base", "account", "analytic", "operating_unit"],
    "data": [
        'security/ir.model.access.csv',
        'views/draft_bill_view.xml',
        'wizard/draft_bill_import_wizard_view.xml'
    ],
    "license": "LGPL-3",
    'installable': True,
}
