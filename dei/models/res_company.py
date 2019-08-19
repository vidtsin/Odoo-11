from odoo import models, fields, _, api


class res_company(models.Model):
    _inherit = 'res.company'

    cai = fields.Char('CAI')



