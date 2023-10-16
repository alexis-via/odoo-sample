# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# This file should be placed in the "tests" subdir of the module
# and its name should start with "test_".
# It should be imported in the __init__.py of the "tests" subdir
# but the __init__.py of the "tests" subdir mustn't be imported from
# the main __init__.py file of the module
# To run the test : ./odoo.py -u module --test-enable


# https://docs.python.org/2/library/unittest.html?highlight=unittest2

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, SavepointCase
from odoo.tests import tagged

# @tagged is used to avoid bugs such as:
# null value in column "sale_line_warn" violates not-null constraint
@tagged('post_install', '-at_install')
class TestFrIntrastatService(TransactionCase):  # v16: TransactionCase

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # create data

    # WARNING: the name of the method must start with test ?
    def test_generate_des(self):
        # Set company country to France
        company = self.env.ref('base.main_company')
        company.country_id = self.env.ref('base.fr')
        des = self.env['l10n.fr.intrastat.service.declaration'].create({
            'company_id': company.id})
        # We use the demo invoice provided by this module
        des.generate_service_lines()
        precision = self.env['decimal.precision'].precision_get('Account')
        self.assertEqual(float_compare(
            des.total_amount, 540.0, precision_digits=precision), 0)
        self.assertEqual(des.num_decl_lines, 3)
        des.done()
        self.assertEqual(des.state, 'done')
        des.generate_xml()
        xml_des_files = self.env['ir.attachment'].search([
            ('res_id', '=', des.id),
            ('res_model', '=', 'l10n.fr.intrastat.service.declaration'),
            ('type', '=', 'binary'),
            ])
        self.assertEqual(len(xml_des_files), 1)
        xml_des_file = xml_des_files[0]
        self.assertEqual(xml_des_file.datas_fname[-4:], '.xml')
        xml_root = etree.fromstring(xml_des_file.datas.decode('base64'))
        company_vat_xpath = xml_root.xpath(
            '/fichier_des/declaration_des/num_tvaFr')
        self.assertEqual(company_vat_xpath[0].text, company.vat)
        lines_xpath = xml_root.xpath('/fichier_des/declaration_des/ligne_des')
        self.assertEqual(len(lines_xpath), des.num_decl_lines)

assertEqual(a, b)   a == b
assertNotEqual(a, b)    a != b
assertTrue(x)   bool(x) is True
assertFalse(x)  bool(x) is False
assertIs(a, b)  a is b
assertIsNot(a, b)   a is not b
assertIsNone(x)     x is None
assertIsNotNone(x)  x is not None
assertIn(a, b)  a in b
assertNotIn(a, b)   a not in b
assertIsInstance(a, b)  isinstance(a, b)
assertNotIsInstance(a, b)   not isinstance(a, b)
self.assertGreater(a, b)
# to test a report
res = self.env['ir.actions.report']._render(
    "account.report_invoice_with_payments", self.invoice.ids)
self.assertRegex(str(res[0]), self.product.hs_code_id.hs_code)

from odoo.exceptions import ValidationError
self._set_analytic_policy('never')
with self.assertRaises(ValidationError):
    self._create_move(with_analytic=True)

with self.assertRaises(UserError):
    self.partner.sudo(self.user.id).open_map()

from freezegun import freeze_time
with freeze_time("2022-01-01"):
    move = self.env["account.move"].create({})

from odoo.tests.common import Form
wiz_form = Form(self.env["account.move.renumber.wizard"])
wiz_form.my_char_field = 'Tutu'
wiz = wiz_form.save()
wiz.run()

invoice_form = Form(
    cls.account_move.with_context(default_move_type="in_invoice")
    )
invoice_form.partner_id = cls.env["res.partner"].create(
    {"name": "test partner"}
    )
invoice_form.check_total = 1.19
with invoice_form.invoice_line_ids.new() as line_form:
    line_form.name = "Test invoice line"
    line_form.price_unit = 2.99
    line_form.tax_ids.clear()
cls.invoice = invoice_form.save()
