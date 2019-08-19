# -*- coding: utf-8 -*-
{
    'name': 'Facturacion Honduras',
    'version': '1.1',
    'author': 'ERP Labz, Mario Matamoros -Grupo Nahuiik',
    'website': 'http://erplabz.com',
    'description': """
                    Nuevo Regimen de facturacion en Honduras 2018
    """,
    'depends': ['base',
                'account',
                'account_voucher'],
    'data': [
        'views/cai_view.xml',
        'views/ir_sequence_view.xml',
        'views/res_partner_view.xml',
        'views/account_invoice_view.xml',
        'reports/report_sales_receipt.xml',
        'security/groups.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}

