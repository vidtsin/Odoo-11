# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, exceptions, _
import odoo.addons.decimal_precision as dp
from datetime import datetime

class FacturasVentas(models.Model):
    _name = 'libro.ventas.invoice'
    _description = 'Facturas de Clientes'
    _order = 'factura_id desc'

    treasury_id = fields.Many2one("libro.ventas.forecast", "Forecast")
    factura_id = fields.Integer("Id de factura")
    invoice_id = fields.Many2one("account.invoice", string="No. Documento")
    numero_factura = fields.Char("No. Factura")
    invoice_date = fields.Date("Fecha de Factura")
    date_due = fields.Date(string="Fecha de Vencimiento")
    partner_id = fields.Many2one("res.partner", string="Empresa")
    state = fields.Selection([('draft', 'Borrador'), ('proforma', 'Pro-forma'),
                              ('proforma2', 'Pro-forma'), ('open', 'Abierta'),
                              ('paid', 'Pagada'), ('cancel', 'Anulada')],
                             string="State")
    total_amount = fields.Float(string="Total de Factura",
                                digits_compute=dp.get_precision('Account'))
    subtotal = fields.Float(string="SubTotal",
                            digits_compute=dp.get_precision('Account'))
    isv = fields.Float(string="Impuesto",
                       digits_compute=dp.get_precision('Account'))

    tipo_factura = fields.Char("Tipo de Factura")


class AccountTreasuryForecast(models.Model):
    _name = 'libro.ventas.forecast'
    _description = 'Libro de Ventas'

    def get_currency(self):
        return self.env.user.company_id.currency_id.id

    currency_id = fields.Many2one("res.currency", "Moneda", required=True,
                                  readonly=True, domain=[('active', '=', True)],
                                  default=get_currency)
    name = fields.Char(string="Descripción")
    # Borrar
    total_incoming = fields.Float(string="Total de Ventas", readonly=True)
    sub_total = fields.Float("Neto Gravado", readonly=True)
    total_gravado = fields.Float("Total Gravado", readonly=True)
    total_impuesto = fields.Float("Impuestos", readonly=True)
    total_exento = fields.Float("Total Facturas Exentas")
    # Borrar
    state = fields.Selection([('draft', 'Borrador'), ('progress', 'Progreso'),
                              ('done', 'Finalizado')], string='Estado',
                             default='draft')
    start_date = fields.Date(string="Fecha de Inicio", required=True)
    end_date = fields.Date(string="Fecha Final", required=True)
    check_draft = fields.Boolean(string="Borrador")
    check_cancel = fields.Boolean(string="Anuladas", default=1)
    check_proforma = fields.Boolean(string="Esperando Aprobación")
    check_done = fields.Boolean(string="Pagadas", default=1)
    check_open = fields.Boolean(string="Abiertas", default=1)
    facturas_gravadas = fields.Integer("# Facturas Gravadas")
    facturas_exentas = fields.Integer("# Facturas Exentas")
    total_numero_facturas = fields.Integer("# Facturas")
    out_invoice_ids = fields.One2many("libro.ventas.invoice", "treasury_id",
                                      "Facturas de Clientes")
    regimen = fields.Boolean("Facturas con Regimen", default=1)
    month = fields.Char(string="Month",compute="get_month",store=True)
    year  = fields.Integer(string="Year",compute="get_month",store=True)

    @api.depends('start_date')
    def get_month(self):
        for sale in self:
            if sale.start_date:
                date = datetime.strptime(sale.start_date, '%Y-%m-%d')
                number_month = date.month
                print ("//////////////////")
                print (date.year)
                sale.month = self.months(number_month)
                sale.year = date.year

    def months(self,number):
        if number == 1:
            return _('January')
        elif number == 2:
            return _('February')
        elif number == 3:
            return _('March')
        elif number == 4:
            return _('April')
        elif number == 5:
            return _('May')
        elif number == 6:
            return _('June')
        elif number == 7:
            return _('July')
        elif number == 8:
            return _('August')
        elif number == 9:
            return _('September')
        elif number == 10:
            return _('October')
        elif number == 11:
            return _('November')
        elif number == 12:
            return _('December')

    @api.one
    @api.constrains('end_date', 'start_date')
    def check_date(self):
        if self.start_date > self.end_date:
            raise exceptions.Warning(
                _('Error!:: End date is lower than start date.'))

    @api.one
    @api.constrains('check_draft', 'check_proforma', 'check_open')
    def check_filter(self):
        if not self.check_draft and not self.check_proforma and \
                not self.check_open and not self.check_done:
            raise exceptions.Warning(
                _('Error!:: There is no any filter checked.'))

    @api.one
    def restart(self):
        self.out_invoice_ids.unlink()
        self.total_incoming = 0
        self.sub_total = 0
        self.total_impuesto = 0
        self.total_exento = 0
        self.total_gravado = 0
        self.facturas_gravadas = 0
        self.facturas_exentas = 0
        self.total_numero_facturas = 0
        return True

    @api.multi
    def button_calculate(self):
        self.restart()
        self.calculate_invoices()
        self.calculate_total()
        return True

    @api.one
    def calculate_total(self):
        if self.out_invoice_ids:
            amount = 0.0
            sub_total = 0.0
            isv = 0.0
            exento = 0.0
            contador = 0.0
            contador_exento = 0.0
            for line in self.out_invoice_ids:
                if line.state != 'cancel':
                    amount += line.total_amount
                    if line.isv == 0:
                        exento += line.subtotal
                        contador_exento += 1
                    else:
                        sub_total += line.subtotal
                        isv += line.isv
                        contador += 1
            self.total_incoming = amount
            self.sub_total = sub_total
            self.total_impuesto = isv
            self.total_exento = exento
            self.total_gravado = round((isv / 0.15), 2)
            self.facturas_gravadas = contador
            self.facturas_exentas = contador_exento
            self.total_numero_facturas = contador + contador_exento

    @api.one
    def calculate_invoices(self):
        invoice_obj = self.env['account.invoice']
        treasury_invoice_obj = self.env['libro.ventas.invoice']
        state = []
        invoice_ids = False
        self.total_incoming = 0
        if self.check_cancel:
            state.append("cancel")
        if self.check_open:
            state.append("open")
        if self.check_done:
            state.append("paid")

        invoice_ids = invoice_obj.search(
            [('date_invoice', '>=', self.start_date),
             ('date_invoice', '<=', self.end_date),
             ('state', 'in', tuple(state)), ('type', '=', 'out_invoice')])
        for invoice_o in invoice_ids:
            if self.regimen and invoice_o.cai_shot:
                values = {
                    'treasury_id': self.id,
                    'invoice_id': invoice_o.id,
                    'factura_id': invoice_o.id,
                    'date_due': invoice_o.date_due,
                    'numero_factura': invoice_o.move_name,
                    'invoice_date': invoice_o.date_invoice,
                    'partner_id': invoice_o.partner_id.id,
                    'state': invoice_o.state
                }
                if self.currency_id == invoice_o.currency_id:
                    if invoice_o.type == 'out_invoice':
                        self.total_incoming += invoice_o.amount_total
                    elif invoice_o.type == 'out_refund':
                        self.total_incoming -= invoice_o.amount_total
                    elif invoice_o.type in ("in_invoice", "in_refund"):
                        self.total_invoice_out += invoice_o.amount_total
                    values["subtotal"] = invoice_o.amount_untaxed
                    values['isv'] = invoice_o.amount_tax
                    values['total_amount'] = invoice_o.amount_total
                else:
                    if invoice_o.type == 'out_invoice':
                        self.total_incoming += invoice_o.amount_local
                    elif invoice_o.type == 'out_refund':
                        self.total_incoming -= invoice_o.amount_local
                    elif invoice_o.type in ("in_invoice", "in_refund"):
                        self.total_invoice_out += invoice_o.amount_local
                    values["subtotal"] = \
                        invoice_o.amount_untaxed * invoice_o.exch_rate
                    values['isv'] = invoice_o.amount_tax * invoice_o.exch_rate
                    values['total_amount'] \
                        = invoice_o.amount_total * invoice_o.exch_rate

                if invoice_o.amount_tax == 0:
                    values['tipo_factura'] = 'Exenta'
                else:
                    values['tipo_factura'] = 'Gravada'
                new_id = treasury_invoice_obj.create(values)

            if not self.regimen and not invoice_o.cai_shot:
                values = {
                    'treasury_id': self.id,
                    'invoice_id': invoice_o.id,
                    'factura_id': invoice_o.id,
                    'date_due': invoice_o.date_due,
                    'numero_factura': invoice_o.move_name,
                    'invoice_date': invoice_o.date_invoice,
                    'partner_id': invoice_o.partner_id.id,
                    'state': invoice_o.state
                }
                if self.currency_id == invoice_o.currency_id:
                    if invoice_o.type == 'out_invoice':
                        self.total_incoming += invoice_o.amount_total
                    elif invoice_o.type == 'out_refund':
                        self.total_incoming -= invoice_o.amount_total
                    elif invoice_o.type in ("in_invoice", "in_refund"):
                        self.total_invoice_out += invoice_o.amount_total
                    values["subtotal"] = invoice_o.amount_untaxed
                    values['isv'] = invoice_o.amount_tax
                    values['total_amount'] = invoice_o.amount_total
                else:
                    if invoice_o.type == 'out_invoice':
                        self.total_incoming += invoice_o.amount_local
                    elif invoice_o.type == 'out_refund':
                        self.total_incoming -= invoice_o.amount_local
                    elif invoice_o.type in ("in_invoice", "in_refund"):
                        self.total_invoice_out += invoice_o.amount_local
                    values["subtotal"] = \
                        invoice_o.amount_untaxed * invoice_o.exch_rate
                    values['isv'] = invoice_o.amount_tax * invoice_o.exch_rate
                    values['total_amount'] \
                        = invoice_o.amount_total * invoice_o.exch_rates
                if invoice_o.amount_tax == 0:
                    values['tipo_factura'] = 'Exenta'
                else:
                    values['tipo_factura'] = 'Gravada'

                new_id = treasury_invoice_obj.create(values)

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_progress(self):
        self.write({'state': 'progress'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})
