# -*- coding: utf-8 -*-
{
    'name': "Módulo de Tesoreria y Caja",
    'summary': """
        Módulo de Gestión de Bancos Multicompañia
        """,
    'description': """
        Gestión de banco y caja
    """,
    'author': "ERP Labz, César Alejandro Rodriguez Castillo",
    "website": "http://erplabz.com", 
    'category': 'Accounting',
    'version': '1.9',
    'depends': ['base', 'account', 'analytic', 'account_pdc', 'purchase', 'sh_amount_in_words'],
    'data': [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "wizard/wizard_plantilla_view.xml",
        #"views/factura_proveedor.xml",
        "views/main_menu_view.xml", 
        "wizard/journal_settings_view.xml",
        "views/ir_sequence_view.xml",
        "views/debit_view.xml",
        #"views/banks_transferences_view.xml",
        "views/config_journal_view.xml",
        "views/check_view.xml",
        "views/payment_view.xml",
        "views/account_payment_view.xml",
        "views/banks_transferences_view.xml",
        "views/plantilla_banks_view.xml",
        'views/date_filter.xml',
        "reports/cheqck_paper_format.xml", 
        "reports/check_report.xml",
        "reports/check_print.xml",
        "reports/deposit_report.xml",
        "reports/deposit_print.xml",
        
        'reports/write_cheqck_paper_format.xml',
        'reports/write_checks_report.xml',
        'reports/reporte2.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
