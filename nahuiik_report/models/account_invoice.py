# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import except_orm
# from itertools import ifilter


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    cai_shot_compras = fields.Char("CAI")
    excluir_compra = fields.Boolean("Excluir Compras")
    is_importation = fields.Boolean(string="Is Importation")

    @api.onchange('type', 'partner_id')
    def onchange_partner_id_cai(self):
        if self.partner_id and self.type != 'out_invoice':
            self.cai_shot_compras = self.partner_id.cai_shot_compras

    @api.onchange('payment_term_id', 'date_invoice')
    def _onchange_payment_term_date_invoice(self):
        res = super(AccountInvoice,
                       self)._onchange_payment_term_date_invoice()
        if self.date_invoice and self.partner_id and \
                self.type != 'out_invoice' and not self.partner_id.customer:
            if self.partner_id.fecha_expiracion:
                if self.date_invoice > self.partner_id.fecha_expiracion and \
                        self.partner_id.cai_shot_compras:
                    raise except_orm(_('Error!'), _(
                        'La fecha de expiración del CAI  es inferior a '
                        'la fecha de factura'))
        return res


class ResPartner(models.Model):
    _inherit = 'res.partner'

    cai_shot_compras = fields.Char("CAI", domain="[('supplier', '=', True)]")
    fecha_expiracion = fields.Date("Fecha de expiración")
