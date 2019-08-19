# -*- coding: utf-8 -*-
import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, api, fields, _
from datetime import datetime

class SalesXlsx(models.AbstractModel):
    _name = 'report.nahuiik_report.report_libro_ventas_invoice_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        cont = 1
        company_name = self.env.user.company_id.name
        for sale in lines:
            sheet = workbook.add_worksheet(_('Libro ventas ' + str(cont)))
            cont+=1
            format1 = workbook.add_format({'font_size': 14, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True})
            format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'right': True, 'left': True, 'bottom': True, 'top': True, 'bold': True})
            format22 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': False, 'left': False,'bottom': False, 'top': False, 'bold': False})
            format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'right': True, 'left': True,'bottom': True, 'top': True, 'bold': True,'bg_color':'#F3F781'})
            format23 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': False, 'left': False,'bottom': False, 'top': False, 'bold': True})
            format24 = workbook.add_format({'font_size': 10, 'align': 'left', 'right': False, 'left': False,'bottom': False, 'top': False, 'bold': False})
            ########### NUMBER FORMAT #######################################
            format3 = workbook.add_format({'align':'right','left':False,'right':False,'bottom': False, 'top': False, 'font_size': 10,'num_format': '#,##0.00'})
            format4 = workbook.add_format({'align':'left','left':False,'right':False,'bottom': False, 'top': False, 'bold':False ,'font_size': 10,'num_format': '#,##0.00'})
            format5 = workbook.add_format({'align':'left','left':False,'right':False,'bottom': False, 'top': False, 'bold':False ,'font_size': 10,'num_format': 'L '+'#,##0.00'})
            font_size_8 = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8})
            red_mark = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 8,
                                            'bg_color': 'red'})
            justify = workbook.add_format({'bottom': True, 'top': True, 'right': True, 'left': True, 'font_size': 12})
            font_size_8.set_align('center')
            justify.set_align('justify')
            format1.set_align('center')
            red_mark.set_align('center')

            sheet.set_column(0, 0, 5)
            sheet.set_column(1, 1, 13)
            sheet.set_column(2, 2, 35)
            sheet.set_column(3, 3, 20)
            sheet.set_column(4, 4, 35)
            sheet.set_column(5, 5, 25)
            sheet.set_column(6, 6, 15)
            sheet.set_column(7, 7, 15)
            sheet.set_column(8, 8, 15)

            #sheet.merge_range('A1:I1', company_name, format1)
            sheet.merge_range('B2:J2', company_name, format11)
            
            sheet.write(3, 1, _('Sales book'), format23)
            sheet.merge_range('B5:C5', _('Expressed in Lempiras of Honduras').upper(), format23)
            #sheet.write(4, 1, _('Expressed in Lempiras of Honduras'), format23)

            sheet.write(6, 1, _('Start Date'), format23)
            sheet.write(6, 2, self.change_format(sale.start_date), format24)
            sheet.write(6, 3, _('End Date'), format23)
            sheet.write(6, 4, self.change_format(sale.end_date), format24)

            sheet.write(7, 1, _('Total sales'), format23)
            sheet.write_number(7, 2, sale.total_incoming, format5)
            sheet.write(7, 3, _('Taxable sales'), format23)
            sheet.write_number(7, 4, sale.total_gravado, format5)

            sheet.write(8, 3, _('Ventas Exentas'), format23)
            sheet.write_number(8, 4, sale.total_exento, format5)
            
            sheet.write(9, 3, _('Total taxes'), format23)
            sheet.write_number(9, 4, sale.total_impuesto, format5)
            
            pos = 12
            sheet.write(11, 1, _('Date'), format21)
            sheet.write(11, 2, _('Client'), format21)
            sheet.write(11, 3, _('RTN'), format21)
            sheet.write(11, 4, _('CAI'), format21)
            sheet.write(11, 5, _('Invoice Number'), format21)
            sheet.write(11, 6, _('Subt Total'), format21)
            sheet.write(11, 7, _('Taxes'), format21)
            sheet.write(11, 8, _('Total'), format21)
            sheet.write(11, 9, _('Type'), format21)
            for invoice in sale.out_invoice_ids:
                sheet.write(pos, 1, self.change_format(invoice.invoice_date), format22)
                sheet.write(pos, 2, invoice.partner_id.name, format22)
                sheet.write(pos, 3, invoice.partner_id.rtn or '', format22)
                sheet.write(pos, 4, invoice.invoice_id.cai_shot or '', format22)
                sheet.write(pos, 5, invoice.numero_factura, format22)
                sheet.write_number(pos, 6, invoice.subtotal, format3)
                sheet.write_number(pos, 7, invoice.isv, format3)
                sheet.write_number(pos, 8, invoice.total_amount, format3)
                sheet.write(pos, 9, invoice.tipo_factura, format22)
                pos+=1

    def change_format(self,date):
        return datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
