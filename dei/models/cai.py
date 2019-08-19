# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import time
from odoo.exceptions import Warning


class fiscal_regime(models.Model):
    _name = "dei.fiscal_regime"

    cai = fields.Many2one('dei.cai', required=True)
    sequence = fields.Many2one('ir.sequence')
    selected = fields.Boolean('selected')
    desde = fields.Integer('From')
    hasta = fields.Integer('to')
#    next            = fields.Integer('next', related='sequence.number_next_actual')

#    _sql_constraints = [
#    ('cai_unique', 'unique(cai)', 'cai already exists!')
#    ]

   

#    @api.onchange('estado')
#    def verify_active_cai(self):
#        print 'verify_active_cai'
#        if self.estado:
#            if not self.cai.active:
#                self.write({'estado':0})
#                raise Warning(_('this cai is inactive ' ))


class cai(models.Model):
    _name = "dei.cai"

    name = fields.Char('CAI', help='Clave de Autorización de Impresión ', required=True, select=True)
    expiration_date = fields.Date('Expiration Date', required=True, select=True)
    # active = fields.Boolean('active')
    company = fields.Many2one('res.company', required=True)
    fiscal_regimes = fields.One2many('dei.fiscal_regime', 'cai')


#    @api.onchange('active')
#    def inactive_fiscal_regimes(self):
#        if not self.active:
#            for regime in self.fiscal_regimes:
#                regime.estado=False

