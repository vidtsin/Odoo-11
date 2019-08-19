# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################

{
    'name': 'Account Invoice Currency Rate',
    'version': '11.0.1.4',
    'category': 'Generic Modules/Accounting',
    'sequence': 1,
    'description': """
        App will add invocie currency rate on invocie screen to adjust currency rate 
        
Account Invoice Currency Rate
Odoo Account Invoice Currency Rate
Invoice Currency Rate 
Odoo Invoice Currency Rate 
add invocie currency rate on invocie screen to adjust currency rate
odoo add invocie currency rate on invocie screen to adjust currency rate
account invoice
odoo account invoice
account invoice screen
odoo account invoice screen
currency exchange rate 
odoo currency exchange rate
Currency Exchange Rate on Invoice
Odoo Currency Exchange Rate on Invoice
Currency Exchange Rate on payment
Odoo Currency Exchange Rate on payment
Currency Exchange Rate on sale
Odoo Currency Exchange Rate on sale
Odoo currency exchange rate on purchase
Currency exchange rate on purchase
Manual Currency Exchange Rate
Odoo Manual Currency Exchange Rate
Currency rate exchange
Odoo currency rate exchange
        
        
        
    """,
    'summary':"""App will add invocie currency rate on invocie screen to adjust currency rate""",
    'depends': ['account','currency_rate_inverted'],
    'data': [
        'views/account_invoice.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    #author and support Details
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':20.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
