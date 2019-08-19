# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class account_invoice_ext(models.Model):
    _inherit = "account.invoice"

    cai_shot = fields.Char("Cai", readonly=True)
    cai_expires_shot = fields.Date("expiration_date", readonly=True)
    min_number_shot = fields.Char("min_number", readonly=True)
    max_number_shot = fields.Char("max_number", readonly=True)
    amount_total_text = fields.Char("Amount Total", compute='get_totalt', default='Cero')

    @api.multi
    def action_invoice_open(self):
        res = super(account_invoice_ext, self).action_invoice_open()
        if self.journal_id.sequence_id.fiscal_regime:
            if self.date_invoice > self.journal_id.sequence_id.expiration_date:
                self.journal_id.sequence_id.number_next_actual = self.journal_id.sequence_id.number_next_actual - 1
                raise Warning(_('la fecha de expiracion para esta secuencia es %s ') % (self.journal_id.sequence_id.expiration_date) )
            self.cai_shot = ''

            for regimen in self.journal_id.sequence_id.fiscal_regime:
                if regimen.selected:
                    self.cai_shot = regimen.cai.name
                    self.cai_expires_shot = regimen.cai.expiration_date
                    self.min_number_shot = self.journal_id.sequence_id.dis_min_value
                    self.max_number_shot = self.journal_id.sequence_id.dis_max_value

        return res

    @api.one
    @api.depends('journal_id')
    def get_totalt(self):
        self.amount_total_text = ''
        if self.currency_id:
            self.amount_total_text=self.to_word(self.amount_total,self.currency_id.name)
        else:
            self.amount_total_text =self.to_word(self.amount_total,self.user_id.company_id.currency_id.name)
        return True


    def to_word(self,number, mi_moneda):
        valor= number
        number=int(number)
        centavos=int((round(valor-number,2))*100)
        UNIDADES = (
            '',
            'UN ',
            'DOS ',
            'TRES ',
            'CUATRO ',
            'CINCO ',
            'SEIS ',
            'SIETE ',
            'OCHO ',
            'NUEVE ',
            'DIEZ ',
            'ONCE ',
            'DOCE ',
            'TRECE ',
            'CATORCE ',
            'QUINCE ',
            'DIECISEIS ',
            'DIECISIETE ',
            'DIECIOCHO ',
            'DIECINUEVE ',
            'VEINTE '
        )

        DECENAS = (
            'VENTI',
            'TREINTA ',
            'CUARENTA ',
            'CINCUENTA ',
            'SESENTA ',
            'SETENTA ',
            'OCHENTA ',
            'NOVENTA ',
            'CIEN ')

        CENTENAS = (
            'CIENTO ',
            'DOSCIENTOS ',
            'TRESCIENTOS ',
            'CUATROCIENTOS ',
            'QUINIENTOS ',
            'SEISCIENTOS ',
            'SETECIENTOS ',
            'OCHOCIENTOS ',
            'NOVECIENTOS '
        )
        MONEDAS = (
            {'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
            {'country': u'Honduras', 'currency': 'HNL', 'singular': u'Lempira', 'plural': u'Lempiras', 'symbol': u'L'},
            {'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR', 'plural': u'DÓLARES', 'symbol': u'US$'},
            {'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'€'},
            {'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
            {'country': u'Perú', 'currency': 'PEN', 'singular': u'NUEVO SOL', 'plural': u'NUEVOS SOLES', 'symbol': u'S/.'},
            {'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'£'}
            )
        if mi_moneda != None:
            try:
                moneda = filter(lambda x: x['currency'] == mi_moneda, MONEDAS)[0]
                if number < 2:
                    moneda = moneda['singular']
                else:
                    moneda = moneda['plural']
            except:
                return "Tipo de moneda inválida"
        else:
            moneda = ""
        converted = ''
        if not (0 < number < 999999999):
            return 'No es posible convertir el numero a letras'

        number_str = str(number).zfill(9)
        millones = number_str[:3]
        miles = number_str[3:6]
        cientos = number_str[6:]

        if(millones):
            if(millones == '001'):
                converted += 'UN MILLON '
            elif(int(millones) > 0):
                converted += '%sMILLONES ' % self.convert_group(millones)

        if(miles):
            if(miles == '001'):
                converted += 'MIL '
            elif(int(miles) > 0):
                converted += '%sMIL ' % self.convert_group(miles)

        if(cientos):
            if(cientos == '001'):
                converted += 'UN '
            elif(int(cientos) > 0):
                converted += '%s ' % self.convert_group(cientos)
        if(centavos)>0:
            converted+= "con %2i/100 "%centavos
        converted += moneda
        return converted.title()


    def convert_group(self,n):
        UNIDADES = (
            '',
            'UN ',
            'DOS ',
            'TRES ',
            'CUATRO ',
            'CINCO ',
            'SEIS ',
            'SIETE ',
            'OCHO ',
            'NUEVE ',
            'DIEZ ',
            'ONCE ',
            'DOCE ',
            'TRECE ',
            'CATORCE ',
            'QUINCE ',
            'DIECISEIS ',
            'DIECISIETE ',
            'DIECIOCHO ',
            'DIECINUEVE ',
            'VEINTE '
        )
        DECENAS = (
            'VENTI',
            'TREINTA ',
            'CUARENTA ',
            'CINCUENTA ',
            'SESENTA ',
            'SETENTA ',
            'OCHENTA ',
            'NOVENTA ',
            'CIEN '
        )

        CENTENAS = (
            'CIENTO ',
            'DOSCIENTOS ',
            'TRESCIENTOS ',
            'CUATROCIENTOS ',
            'QUINIENTOS ',
            'SEISCIENTOS ',
            'SETECIENTOS ',
            'OCHOCIENTOS ',
            'NOVECIENTOS '
        )
        MONEDAS = (
            {'country': u'Colombia', 'currency': 'COP', 'singular': u'PESO COLOMBIANO', 'plural': u'PESOS COLOMBIANOS', 'symbol': u'$'},
            {'country': u'Honduras', 'currency': 'HNL', 'singular': u'Lempira', 'plural': u'Lempiras', 'symbol': u'L'},
            {'country': u'Estados Unidos', 'currency': 'USD', 'singular': u'DÓLAR', 'plural': u'DÓLARES', 'symbol': u'US$'},
            {'country': u'Europa', 'currency': 'EUR', 'singular': u'EURO', 'plural': u'EUROS', 'symbol': u'€'},
            {'country': u'México', 'currency': 'MXN', 'singular': u'PESO MEXICANO', 'plural': u'PESOS MEXICANOS', 'symbol': u'$'},
            {'country': u'Perú', 'currency': 'PEN', 'singular': u'NUEVO SOL', 'plural': u'NUEVOS SOLES', 'symbol': u'S/.'},
            {'country': u'Reino Unido', 'currency': 'GBP', 'singular': u'LIBRA', 'plural': u'LIBRAS', 'symbol': u'£'}
        )
        output = ''

        if(n == '100'):
            output = "CIEN "
        elif(n[0] != '0'):
            output = CENTENAS[int(n[0]) - 1]

        k = int(n[1:])
        if(k <= 20):
            output += UNIDADES[k]
        else:
            if((k > 30) & (n[2] != '0')):
                output += '%sY %s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])
            else:
                output += '%s%s' % (DECENAS[int(n[1]) - 2], UNIDADES[int(n[2])])

        return output

    def addComa(self, snum ):
        s = snum;
        i = s.index('.') # Se busca la posición del punto decimal
        while i > 3:
            i = i - 3
            s = s[:i] +  ',' + s[i:]
        return s

