# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from num2words import num2words
from odoo.exceptions import UserError


class Debit(models.Model):
    _name = 'banks.debit'
    _inherit = ['mail.thread']
    _description = "Management Debits"
    _order = 'date desc'

    def get_sequence(self):
        if self.journal_id:
            for seq in self.journal_id.secuencia_ids:
                if seq.move_type == self.doc_type:
                    return seq.id

    @api.onchange("currency_id")
    def onchangecurrency(self):
        if self.currency_id:
            if self.currency_id != self.company_id.currency_id:
                tasa = self.currency_id.with_context(date=self.date)
                self.currency_rate = tasa.rate 
                self.es_moneda_base = False
            else:
                self.currency_rate = 1
                self.es_moneda_base = True

    def get_char_seq(self, journal_id, doc_type):
        jr = self.env["account.journal"].search([('id', '=', journal_id)])
        for seq in jr.secuencia_ids:
            if seq.move_type == doc_type:
                return (seq.prefix + '%%0%sd' % seq.padding % seq.number_next_actual)

    def get_msg_number(self):
        if self.journal_id and self.state == 'draft':
            flag = False
            for seq in self.journal_id.secuencia_ids:
                if seq.move_type == self.doc_type:
                    if self.is_journal_change or not self.old_journal_id:
                        self.number_calc = seq.prefix + '%%0%sd' % seq.padding % seq.number_next_actual
                    else:
                        self.number_calc = self.old_number
                    flag = True
            if not flag:
                self.msg = "No existe numeración para este banco, verifique la configuración"
                self.number_calc = ""
            else:
                self.msg = ""

    def update_seq(self):
        deb_obj = self.env["banks.debit"].search([('state', '=', 'draft'), ('doc_type', '=', self.doc_type)])
        n = ""
        for seq in self.journal_id.secuencia_ids:
            if seq.move_type == self.doc_type:
                n = seq.prefix + '%%0%sd' % seq.padding % (seq.number_next_actual + 1)
        for db in deb_obj:
            db.write({'number': n})

    @api.model
    def create(self, vals):
        vals["number"] = self.get_char_seq(vals.get("journal_id"), vals.get("doc_type"))
        debit = super(Debit, self).create(vals)
        return debit

    @api.multi
    def unlink(self):
        for move in self:
            if move.state == 'validated':
                raise Warning(_('No puede eliminar registros contabilizados'))
        return super(Debit, self).unlink()

    @api.one
    @api.depends('debit_line.amount', 'total')
    def _compute_rest_credit(self):
        debit_line = 0
        credit_line = 0
        if self.doc_type == 'debit':
            for lines in self.debit_line:
                if lines.move_type == 'debit':
                    debit_line += lines.amount
                elif lines.move_type == 'credit':
                    credit_line += lines.amount
                else:
                    credit_line += 0
                    debit_line += 0
            self.total_debitos = debit_line
            self.total_creditos = credit_line
            self.rest_credit = self.total - (debit_line - credit_line)
        else:
            for lines in self.debit_line:
                if lines.move_type == 'debit':
                    debit_line += lines.amount
                elif lines.move_type == 'credit':
                    credit_line += lines.amount
                else:
                    credit_line += 0
                    debit_line += 0
            self.total_debitos = debit_line
            self.total_creditos = credit_line
            self.rest_credit = round(self.total - (credit_line - debit_line), 2)

    def get_currency(self):
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one("res.currency", "Moneda", domain=[('active', '=', True)])
    journal_id = fields.Many2one("account.journal", "Banco", required=True, domain="[('type', 'in',['bank','cash'])]")
    date = fields.Date(string="Fecha", help="Effective date for accounting entries", required=True)
    total = fields.Float(string='Total', required=True)
    name = fields.Text(string="Descripción", required=True)
    debit_line = fields.One2many("banks.debit.line", "debit_id", "Detalle de debito/credito", copy=True)
    rate = fields.Float("Tasa de Cambio")
    state = fields.Selection([('draft', 'Borrador'), ('validated', 'Validado'), ('anulated', "Anulado")], string="Estado", default='draft')
    number_calc = fields.Char("Número de Transacción", compute=get_msg_number)
    msg = fields.Char("Error de configuración", compute=get_msg_number)
    rest_credit = fields.Float('Diferencia', compute=_compute_rest_credit)
    move_id = fields.Many2one('account.move', 'Apunte Contable')
    number = fields.Char("Número", copy=False)
    doc_type = fields.Selection([('debit', 'Débito'), ('credit','Crédito'), ('deposit','Depósito')], string='Tipo', required=True)
    es_anticipo = fields.Boolean("Anticipo de Cliente")
    nombre_cliente = fields.Char("Cliente")
    company_id = fields.Many2one("res.company", "Empresa", default=lambda self: self.env.user.company_id, required=True)
    es_moneda_base = fields.Boolean("Es moneda base")
    total_debitos = fields.Float("Total débitos", compute=_compute_rest_credit)
    total_creditos = fields.Float("Total créditos", compute=_compute_rest_credit)
    plantilla_id = fields.Many2one("banks.template", "Plantilla")

    currency_rate = fields.Float("Tasa de Cambio", digits=(12, 6))

    amount_total_text = fields.Char("Amount Total", compute = 'get_totalt', default='Cero')

    amount_in_words = fields.Char(compute='amount_word', string='Amount', readonly=True)
    old_number = fields.Char(string="Old Number", copy=False, help="hold value of number field")
    old_journal_id = fields.Many2one('account.journal', string="Old Journal")
    is_journal_change = fields.Boolean(compute='_check_journal_change', string="Is Journal Change")
    
    @api.depends('journal_id')
    def _check_journal_change(self):
        for rec in self:
            if rec.old_number and rec.old_journal_id != rec.journal_id:
                rec.is_journal_change = True
            else:
                rec.is_journal_change = False
    
    @api.depends('total')
    def amount_word(self):

        if self.total:
            language = 'en'

            list_lang = [['en', 'en_US'], ['en', 'en_AU'], ['en', 'en_GB'], ['en', 'en_IN'],
                         ['fr', 'fr_BE'], ['fr', 'fr_CA'], ['fr', 'fr_CH'], ['fr', 'fr_FR'],
                         ['es', 'es_ES'], ['es', 'es_AR'], ['es', 'es_BO'], ['es', 'es_CL'], ['es', 'es_CO'],
                         ['es', 'es_CR'], ['es', 'es_DO'],
                         ['es', 'es_EC'], ['es', 'es_GT'], ['es', 'es_MX'], ['es', 'es_PA'], ['es', 'es_PE'],
                         ['es', 'es_PY'], ['es', 'es_UY'], ['es', 'es_VE'],
                         ['lt', 'lt_LT'], ['lv', 'lv_LV'], ['no', 'nb_NO'], ['pl', 'pl_PL'], ['ru', 'ru_RU'],
                         ['dk', 'da_DK'], ['pt_BR', 'pt_BR'], ['de', 'de_DE'], ['de', 'de_CH'],
                         ['ar', 'ar_SY'], ['it', 'it_IT'], ['he', 'he_IL'], ['id', 'id_ID'], ['tr', 'tr_TR'],
                         ['nl', 'nl_NL'], ['nl', 'nl_BE'], ['uk', 'uk_UA'], ['sl', 'sl_SI'], ['vi_VN', 'vi_VN']]

            cnt = 0
            for rec in list_lang[cnt:len(list_lang)]:
                if self.company_id.partner_id:
                    if rec[1] == self.company_id.partner_id.lang:
                        language = rec[0]
                    cnt += 1
            if self.total > 0:
                amount_total = self.total
            else:
                amount_total = self.total
            amount_str = str('{:2f}'.format(amount_total))
            amount_str_splt = amount_str.split('.')
            before_point_value = amount_str_splt[0]
            after_point_value = amount_str_splt[1][:2]
            after_float = int(amount_str_splt[1][:2])

            before_amount_words = num2words(int(before_point_value), lang=language)
            after_amount_words = ''

            if after_float > 0.01:
                after_amount_words = num2words(int(after_point_value), lang=language)

            if language:
                amount = before_amount_words.title()
            else:
                amount = before_amount_words

            currency = self.currency_id
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
            self.amount_in_words = amount


    @api.one
    @api.depends('journal_id')
    def get_totalt(self):
        self.amount_total_text = ''
        if self.currency_id:
            if self.currency_id.name == 'HNL':  
                self.amount_total_text = self.to_word(self.total, 'HNL')
            if self.currency_id.name == 'NIO':
                self.amount_total_text = self.to_word(self.total, 'NIO')
            if self.currency_id.name == 'USD':
                self.amount_total_text = self.to_word(self.total, 'USD')
        return True

    def to_word(self, number, mi_moneda):
        valor = number
        number = int(number)
        centavos = int((round(valor - number, 2)) * 100)
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
                moneda = list(filter(lambda x: x['currency'] == mi_moneda, MONEDAS))
                moneda = moneda[0]
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
            'VEINTI',
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

    @api.onchange("plantilla_id")
    def onchangeplantilla(self):
        if self.plantilla_id:
            self.company_id = self.plantilla_id.company_id.id
            self.journal_id = self.plantilla_id.journal_id.id
            self.name = self.plantilla_id.pagar_a
            self.total = self.plantilla_id.total
            self.doc_type = self.plantilla_id.doc_type
            self.currency_id = self.plantilla_id.currency_id.id
            self.es_moneda_base = self.plantilla_id.es_moneda_base
            lineas = []
            for line in self.plantilla_id.detalle_lines:
                lineas.append((0, 0, {
                    'partner_id': line.partner_id.id,
                    'account_id': line.account_id.id,
                    'name': line.name,
                    'amount': line.amount,
                    'currency_id': line.currency_id.id,
                    'analytic_id': line.analytic_id.id,
                    'move_type': line.move_type,
                    'debit_id': self.id,
                }))
            self.debit_line = lineas

    @api.onchange("journal_id")
    def onchangejournal(self):
        self.get_msg_number()
        if self.journal_id:
            if self.journal_id.currency_id:
                self.currency_id = self.journal_id.currency_id.id
            else:
                self.currency_id = self.company_id.currency_id.id

    @api.multi
    def action_validate(self):
        if not self.number_calc:
            raise Warning(_("El banco no cuenta con configuraciones/parametros para registrar débitos bancarios"))
        if not self.debit_line:
            raise Warning(_("No existen detalles de movimientos a registrar"))
        if self.total < 0:
            raise Warning(_("El total debe de ser mayor que cero"))
        if not round(self.rest_credit, 2) == 0.0:
            raise Warning(_("Existen diferencias entre el detalle y el total de la transacción a realizar"))
        
        self.write({'state': 'validated'})
        if self.is_journal_change or not self.old_journal_id:
            self.number = self.env["ir.sequence"].search([('id', '=', self.get_sequence())]).next_by_id()
            self.old_number = self.number
            self.old_journal_id = self.journal_id.id
        #check sequence duplication - code start
        find_ids = self.env['banks.debit'].search([('number', '=', self.number),('id', '!=', self.id),
                                                   ('state', '=', 'validated')])
        if find_ids:
            raise UserError("Record with sequence %s is already validated."%(self.number))
        
        is_installed_multi_payment = self.env['ir.module.module'].sudo().search([
                                        ('name', '=', 'invoice_multi_payment'), ('state', '=', 'installed')])
        if is_installed_multi_payment:
            payment_ids = self.env['account.payment'].search([('name', '=', self.number),
                                                              ('state', '=', 'posted')])
            if payment_ids:
                raise UserError("Record with sequence %s is already validated."%(self.number))
        #code end
        
        self.write({'move_id': self.generate_asiento()})
        self.update_seq()

    def generate_asiento(self):
        account_move = self.env['account.move']
        lineas = []
        if self.doc_type == 'debit':
            vals_haber = {
                'debit': 0.0,
                'credit': self.total * self.currency_rate,
                'name': self.name,
                'account_id': self.journal_id.default_credit_account_id.id,
                'date': self.date,
            }
            if self.journal_id.currency_id:
                if not self.company_id.currency_id == self.currency_id:
                    vals_haber["currency_id"] = self.currency_id.id
                    vals_haber["amount_currency"] = self.total * -1
                else:
                    vals_haber["amount_currency"] = 0.0
            for line in self.debit_line:
                # LINEA DE DEBITO
                if line.move_type == 'debit':
                    vals_debe = {
                        'debit': line.amount * self.currency_rate,
                        'credit': 0.0,
                        'name': line.name or self.name,
                        'account_id': line.account_id.id,
                        'date': self.date,
                        'partner_id': line.partner_id.id,
                        'analytic_account_id': line.analytic_id.id,
                    }
                    if self.journal_id.currency_id:
                        if not self.company_id.currency_id == self.currency_id:
                            vals_debe["currency_id"] = self.currency_id.id
                            vals_debe["amount_currency"] = line.amount
                        else:
                            vals_debe["amount_currency"] = 0.0
                    lineas.append((0, 0, vals_debe))
                if line.move_type == 'credit':
                    vals_credit = {
                        'debit': 0.0,
                        'credit': line.amount * self.currency_rate,
                        'name': line.name or self.name,
                        'account_id': line.account_id.id,
                        'date': self.date,
                        'partner_id': line.partner_id.id,
                        'analytic_account_id': line.analytic_id.id,
                    }
                    if self.journal_id.currency_id:
                        if not self.company_id.currency_id == self.currency_id:
                            vals_credit["currency_id"] = self.currency_id.id
                            vals_credit["amount_currency"] = line.amount * -1
                        else:
                            vals_credit["amount_currency"] = 0.0
                    lineas.append((0, 0, vals_credit))
            lineas.append((0, 0, vals_haber))
        else:
            vals_credit = {
                'debit': self.total * self.currency_rate,
                'credit': 0.0,
                'name': self.name,
                'account_id': self.journal_id.default_credit_account_id.id,
                'date': self.date,
            }
            if self.journal_id.currency_id:
                if not self.company_id.currency_id == self.currency_id:
                    vals_credit["currency_id"] = self.currency_id.id
                    vals_credit["amount_currency"] = self.total
                else:
                    vals_credit["amount_currency"] = 0.0
            for line in self.debit_line:
                if line.move_type == 'credit':
                    vals_debe = {
                        'debit': 0.0,
                        'credit': line.amount * self.currency_rate,
                        'amount_currency': 0.0,
                        'name': line.name or self.name,
                        'account_id': line.account_id.id,
                        'date': self.date,
                        'partner_id': line.partner_id.id,
                        'analytic_account_id': line.analytic_id.id,
                    }
                    if self.journal_id.currency_id:
                        if not self.company_id.currency_id == self.currency_id:
                            vals_debe["currency_id"] = self.currency_id.id
                            vals_debe["amount_currency"] = line.amount*-1
                        else:
                            vals_debe["amount_currency"] = 0.0
                    lineas.append((0, 0, vals_debe))
                if line.move_type == 'debit':
                    vals_credit = {
                        'debit': line.amount * self.currency_rate,
                        'credit': 0.0,
                        'amount_currency': 0.0,
                        'name': line.name or self.name,
                        'account_id': line.account_id.id,
                        'date': self.date,
                        'partner_id': line.partner_id.id,
                        'analytic_account_id': line.analytic_id.id,
                    }
                    if self.journal_id.currency_id:
                        if not self.company_id.currency_id == self.currency_id:
                            vals_credit["currency_id"] = self.currency_id.id
                            vals_credit["amount_currency"] = line.amount  * -1
                        else:
                            vals_credit["amount_currency"] = 0.0
                    lineas.append((0, 0, vals_credit))
            lineas.append((0, 0, vals_credit))
        values = {
            'journal_id': self.journal_id.id,
            'date': self.date,
            'ref': self.name,
            'line_ids': lineas,
            'state': 'posted',
        }
        id_move = account_move.create(values)
        self.generate_analytic_entry(id_move)
        id_move.write({'name': str(self.number)})
        return id_move.id

    def generate_analytic_entry(self,move):
        analytic_line = self.env['account.analytic.line']
        for line in move.line_ids:
            if line.debit != 0:
                amount = line.debit
            elif line.credit != 0:
                amount = line.credit

            if line.analytic_account_id:
                vals = {
                    'name': line.name or self.name,
                    'account_id': line.analytic_account_id.id,
                    'date': self.date,
                    'amount': amount,
                    'partner_id':line.partner_id.id,
                    'ref':line.name or self.name,
                    'move_id':line.id
                }
                analytic_line.create(vals)
        return True

    @api.multi
    def action_anulate_debit(self):
        for move in self.move_id:
            move.write({'state': 'draft'})
            move.unlink()
        self.write({'state': 'anulated'})

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_anulate(self):
        self.write({'state': 'anulated'})
        self.update_seq()
        self.number = self.env["ir.sequence"].search([('id', '=', self.get_sequence())]).next_by_id()


class Debitline(models.Model):
    _name = 'banks.debit.line'



    @api.onchange("account_id")
    def onchangecuenta(self):
        if self.debit_id.doc_type == 'credit' or self.debit_id.doc_type == 'deposit':
            self.move_type = 'credit'

    debit_id = fields.Many2one('banks.debit', 'Check')
    partner_id = fields.Many2one('res.partner', 'Empresa')
    account_id = fields.Many2one('account.account', 'Cuenta', required=True)
    name = fields.Char('Descripción')
    amount = fields.Float('Monto', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    analytic_id = fields.Many2one("account.analytic.account", string="Cuenta Analitica")
    move_type = fields.Selection([('debit', 'Débito'), ('credit', 'Crédito')], 'Débito/Crédito', default='debit', required=True)
