# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class Reporte(models.AbstractModel):
    _name = 'report.nahuiik_report.report_ventas_invoice'

    @api.multi
    def get_report_values(self, docids, data=None):
        report = self.env['ir.actions.report']._get_report_from_name(
            'nahuiik_report.report_ventas_invoice')
        records = report.browse(self.ids)
        return {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': records,
        }
