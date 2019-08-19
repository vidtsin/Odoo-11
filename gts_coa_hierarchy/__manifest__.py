# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'GTS COA',
    'version' : '11.0.0.1',
    'summary': 'GTS COA',
    'sequence': 30,
    'description': """ Chart of Accounts with hierarchy.
        This module create parent and child relation in account""",
    'category' : 'Accounting & Finance',
    'price': 19.99,
    'currency': 'EUR',
    'license': 'OPL-1',
    'author': 'Geo Technosoft',
    'website': 'http://www.geotechnosoft.com',
    'company': 'Geo Technosoft Solutions Pvt Ltd.',
    'depends' : ['account', 'account_invoicing'],
    'data': [
        'views/account_account_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
