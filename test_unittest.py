# Copyright 2022 Akretion France (http://www.akretion.com/)
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
from odoo.tests.common import TransactionCase
from odoo.tests import tagged

# @tagged is used to avoid bugs such as:
# null value in column "sale_line_warn" violates not-null constraint
@tagged('post_install', '-at_install')
class TestFrIntrastatService(TransactionCase):

    def setUp(self):
        super().setUp()
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

from odoo.exceptions import ValidationError
self._set_analytic_policy('never')
with self.assertRaises(ValidationError):
    self._create_move(with_analytic=True)

with self.assertRaises(UserError):
    self.partner.sudo(self.user.id).open_map()
