# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError,UserError

class isvReport(models.AbstractModel):
    _name = 'report.nahuiik_report.isv_report_view'

    @api.model
    def get_report_values(self, docids, data=None):
        month = self.get_month(data.get('month'))
        info_data = self.get_data(month,data.get('fiscal_credit'),data.get('pos'))
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            #'date_start': date_start,
            #'date_end': date_end,
            'docs': info_data,
        }

    def get_month(self,month):
        if month == 'january':
            return 'Enero'
        elif month == 'february':
            return 'Febrero'
        elif month == 'march':
            return 'Marzo'
        elif month == 'april':
            return 'April'
        elif month == 'may':
            return 'Mayo'
        elif month == 'june':
            return 'June'
        elif month == 'july':
            return 'Julio'
        elif month == 'august':
            return 'Agosto'
        elif month == 'september':
            return 'Septiembre'
        elif month == 'october':
            return 'Octubre'
        elif month == 'november':
            return 'Noviembre'
        elif month == 'december':
            return 'Diciembre'

    def get_data(self,month,credit,pos):
        sales = self.env['libro.ventas.forecast'].search([('month','=',month)])
        purchase = self.env['libro.compras.forecast'].search([('month','=',month)])
        info = {}
        tax_sale = 0
        tax_purchase = 0
        year = 0
        info = {
            'net_sale':0,
            'taxed_sale':0,
            'exonerated_sale':0,
            'total_sale':0,
            'net_purchase':0,
            'taxed_purchase':0,
            'exonerated_purchase':0,
            'total_purchase':0,
            'credit_fiscal':float(credit),
            'pos':float(pos)
        }
        for sale in sales:
            info.update({
                'net_sale':sale.sub_total,
                'taxed_sale':sale.sub_total*0.15,
                'exonerated_sale':sale.total_exento,
                'total_sale':sale.total_incoming
            })
            tax_sale = sale.sub_total*0.15
            year = sale.year
        for pur in purchase:
            info.update({
                'net_purchase':pur.sub_total,
                'taxed_purchase':pur.sub_total*0.15,
                'exonerated_purchase':pur.total_exento,
                'total_purchase':pur.total_incoming
            })
            tax_purchase = pur.sub_total*0.15
            year = purchase.year
        tax_total = tax_sale-tax_purchase
        info.update({
            'to_pay':tax_total,
            'total':tax_total-credit-pos,
            'year':year,
            'month':month
        })
        return [info]