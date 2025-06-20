# Copyright 2025 Akretion France (https://www.akretion.com/)
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

# ===================================
# accounting test that create a new company v16
from odoo.addons.account.tests.common import AccountTestInvoicingCommon

@tagged("post_install", "-at_install")
class TestAccountInvoiceChangeCurrency(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        # cf addons/account/tests/common.py
        # si on laisse chart_template_ref à None, Odoo prend l10n_generic_coa.configurable_chart_template
        # Après ça, on a 2 company bien setupée en country US et currency USD:
        # - cls.company_data
        # - cls.company_data_2
        # Si on veut une company FR avec currency EUR:
        # les arguments après "chart_template" sont passés au create() de res.company
        cls.fr_test_company = cls.setup_company_data('Akretion France', chart_template=chart_template_ref, country_id=cls.env.ref("base.fr").id)
        pprint(cls.fr_test_company)
        cls.company = cls.fr_test_company['company']
        print('country=', cls.company.country_id.code)
        print('currency=', cls.company.currency_id.name)
        # On a bien une société avec country FR et devise EUR
        cls.user.write({
            'company_ids': [Command.link(cls.company.id)],
            'company_id': cls.company.id,
        })


{'company': res.company(18,),
 'currency': res.currency(1,),
 'default_account_assets': account.account(863,),
 'default_account_deferred_expense': account.account(853,),
 'default_account_deferred_revenue': account.account(865,),
 'default_account_expense': account.account(882,),
 'default_account_payable': account.account(866,),
 'default_account_receivable': account.account(858,),
 'default_account_revenue': account.account(876,),
 'default_account_tax_purchase': account.account(860,),
 'default_account_tax_sale': account.account(871,),
 'default_journal_bank': account.journal(33,),
 'default_journal_cash': account.journal(34,),
 'default_journal_misc': account.journal(30,),
 'default_journal_purchase': account.journal(29,),
 'default_journal_sale': account.journal(28,),
 'default_tax_purchase': account.tax(74,),
 'default_tax_sale': account.tax(73,)}
cls.company_data_2=============
{'company': res.company(17,),
 'currency': res.currency(1,),
 'default_account_assets': account.account(816,),
 'default_account_deferred_expense': account.account(806,),
 'default_account_deferred_revenue': account.account(818,),
 'default_account_expense': account.account(835,),
 'default_account_payable': account.account(819,),
 'default_account_receivable': account.account(811,),
 'default_account_revenue': account.account(829,),
 'default_account_tax_purchase': account.account(813,),
 'default_account_tax_sale': account.account(824,),
 'default_journal_bank': account.journal(24,),
 'default_journal_cash': account.journal(25,),
 'default_journal_misc': account.journal(21,),
 'default_journal_purchase': account.journal(20,),
 'default_journal_sale': account.journal(19,),
 'default_tax_purchase': account.tax(72,),
 'default_tax_sale': account.tax(71,)}

# ==============================
# accounting test v18
# Modèle : account_check_deposit, l10n_fr_intrastat_service

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestFrIntrastatService(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_country("fr")
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # 2 options:
        # 1) we can use the default company created by AccountTestInvoicingCommon
        # => cls.company = cls.company_data['company']
        # 2) we need a new company with specific values: we call setup_other_company() and we
        # can put any field of res.company as argument
        cls.fr_test_company_dict = cls.setup_other_company(
            name="Akretion France TEST DES",
            vat="FR86792377731",
        )
        cls.company = cls.fr_test_company_dict["company"]
        cls.env.user.write({'groups_id': [Command.link(cls.env.ref('account_payment_order.group_account_payment').id)], 'company_ids': [Command.link(cls.company.id)]})

        pprint(cls.fr_test_company_dict)

        {'company': res.company(168,),
 'currency': res.currency(125,),
 'default_account_assets': account.account(8201,),
 'default_account_deferred_expense': account.account(8189,),
 'default_account_deferred_revenue': account.account(8203,),
 'default_account_expense': account.account(8221,),
 'default_account_payable': account.account(8204,),
 'default_account_receivable': account.account(8195,),
 'default_account_revenue': account.account(8215,),  # =income
 'default_account_tax_purchase': account.account(8198,),
 'default_account_tax_sale': account.account(8210,),
 'default_journal_bank': account.journal(1213,),
 'default_journal_cash': account.journal(1214,),
 'default_journal_credit': account.journal(1215,),
 'default_journal_misc': account.journal(1210,),
 'default_journal_purchase': account.journal(1209,),
 'default_journal_sale': account.journal(1208,),
 'default_tax_purchase': account.tax(759,),
 'default_tax_sale': account.tax(758,)}
