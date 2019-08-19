from odoo import models, fields, _, api


class res_partner(models.Model):
    _inherit = 'res.partner'

    rtn = fields.Char('RTN', translate=True)

    _sql_constraints = [('rtn_uniq', 'Check(1=1)', 'rtn1 must be unique!')]

