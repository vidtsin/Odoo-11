# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

MONTH_GROUP = [('january', 'January'),
               ('february', 'February'),
               ('march', 'March'),
               ('april', 'April'),
               ('may', 'May'),
               ('june', 'June'),
               ('july', 'July'),
               ('august', 'August'),
               ('september', 'September'),
               ('november', 'November'),
               ('december', 'December')]

class wizardISVReport(models.TransientModel):
    _name = 'nahuiik_report.wizard_isv_report'

    month = fields.Selection(MONTH_GROUP, string="Month", track_visibility='onchange')
    fiscal_credit = fields.Float(string="Previous Period Tax Credit")
    pos = fields.Float(string="POS Retained Tax")

    @api.multi
    def print_report(self):
        """Call when button 'Get Report' clicked."""
        context = self._context
        data = {'ids': context.get('active_ids', []),'month':self.month,'fiscal_credit':self.fiscal_credit,'pos':self.pos}
        data['model'] = 'nahuiik_report.wizard_isv_report'
        data['form'] = self.read()[0]
        for field in data['form'].keys():
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
            report = self.env.ref("nahuiik_report.report_isv").report_action(self, data=data)
            if self.env.context.get('xls_export'):
                return self.env.ref('nahuiik_report.isv_report_xls').report_action(self, data=data)
            return report