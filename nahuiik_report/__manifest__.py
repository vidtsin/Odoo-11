# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Libro de Ventas y Compras",
    "version": "1.1",
    "category": "Tools",
    "complexity": "Alta",
    "license": "AGPL-3",
    "author": "ERP Labz, Mario Matamoros",
    'website': "http://erplabz.com",
    "depends": ["base", "account", "purchase", "dei",
                "pro_templates_multi_currency","account_invoice_supplier_ref_unique","report_xlsx"],
    "summary": "Libro de Ventas y Compras",
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/menu_view.xml",
        "views/cubo_ventas_view.xml",
        "views/libro_compras_view.xml",
        "report/nahuiik_report.xml",
        "report/report_libro_ventas_invoice_view.xml",
        "report/report_libro_compras_invoice_view.xml",
        "report/isv_report.xml",
        "views/account_invoice_view.xml",
        "views/res_partner_view.xml",
        "wizard/wizard_isv_view.xml",
    ],
    "application": True,
    "installable": True
}
