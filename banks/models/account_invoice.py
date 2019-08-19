# -*- coding: utf-8 -*-
from odoo import api, fields, models
from num2words import num2words


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    numero_factura = fields.Char('Número de factura', help='Número de factura')
    cai_proveedor = fields.Char("Cai Proveedor")
    

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    
    @api.multi
    def get_aml_ids(self):
        aml_ids = self.env['account.move.line'].search([('payment_id', 'in', self.ids)])
        return aml_ids


    
    @api.multi  
    def amount_word(self):
        for inv in self:
            if inv.amount:            
                language = 'en'    
        
                list_lang=[['en','en_US'],['en','en_AU'],['en','en_GB'],['en','en_IN'],
                    ['fr','fr_BE'],['fr','fr_CA'],['fr','fr_CH'],['fr','fr_FR'],
                    ['es','es_ES'],['es','es_AR'],['es','es_BO'],['es','es_CL'],['es','es_CO'],['es','es_CR'],['es','es_DO'],
                    ['es','es_EC'],['es','es_GT'],['es','es_MX'],['es','es_PA'],['es','es_PE'],['es','es_PY'],['es','es_UY'],['es','es_VE'],            
                    ['lt','lt_LT'],['lv','lv_LV'],['no','nb_NO'],['pl','pl_PL'],['ru','ru_RU'],
                    ['dk','da_DK'],['pt_BR','pt_BR'],['de','de_DE'],['de','de_CH'],
                    ['ar','ar_SY'],['it','it_IT'],['he','he_IL'],['id','id_ID'],['tr','tr_TR'],
                    ['nl','nl_NL'],['nl','nl_BE'],['uk','uk_UA'],['sl','sl_SI'],['vi_VN','vi_VN']]
                
                cnt = 0           
                for rec in list_lang[cnt:len(list_lang)]:
                    if inv.partner_id:
                        if rec[1] == inv.partner_id.lang:
                            language = rec[0]
                        cnt+=1       
                if inv.amount > 0:
                    amount_total = inv.amount
                else:
                    amount_total = inv.amount
                amount_str =  str('{:2f}'.format(amount_total))
                amount_str_splt = amount_str.split('.')
                before_point_value = amount_str_splt[0]
                after_point_value = amount_str_splt[1][:2]
                after_float = int(amount_str_splt[1][:2]) 
                   
                before_amount_words = num2words(int(before_point_value),lang=language)
                after_amount_words = ''
                
                if after_float > 0.01:            
                    after_amount_words = num2words(int(after_point_value),lang=language)
        
                if language:
                    amount = before_amount_words.title()
                else :
                    amount = before_amount_words
                
                currency = inv.currency_id
                if currency and currency.currency_unit_label:
                    amount = amount + ' ' + currency.currency_unit_label 
                   
                if after_amount_words:
                    if currency and currency.amount_separator:
                        amount = amount + ' ' + currency.amount_separator 
                    
                    if language:
                        amount = amount + ' ' + after_amount_words.title()
                    else:        
                        amount = amount + ' ' + after_amount_words
                    
                    if currency and currency.currency_subunit_label:
                        amount = amount + ' ' + currency.currency_subunit_label
                         
                if currency and currency.close_financial_text:
                    amount = amount + ' ' + currency.close_financial_text
                return amount
                
                