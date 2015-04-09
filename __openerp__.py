# -*- encoding: utf-8 -*-
##############################################################################
#
#    MODULE_NAME module for Odoo
#    Copyright (C) 2015 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Account Cut-off Prepaid',
    'version': '0.1',
    'category': 'Accounting & Finance',
    'license': 'AGPL-3',
    'summary': 'Prepaid Expense, Prepaid Revenue',  # v7: size=64, v8: no size limit
    'description': """
This module adds a **Start Date** and **End Date** field on invoice
lines. For example, if you have an insurance contrat for your company
that run from April 1st 2013 to March 31st 2014, you will enter these
dates as start and end dates on the supplier invoice line. If your
fiscal year ends on December 31st 2013, 3 months of expenses are part of
the 2014 fiscal year and should not be part of the 2013 fiscal year. So,
thanks to this module, you will create a *Prepaid Expense* on December
31st 2013 and OpenERP will identify this expense with the 3 months that
are after the cut-off date and propose to generate the appropriate
cut-off journal entry.

This module has been written by Alexis de Lattre from Akretion
<alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion,Odoo Community Association (OCA)',
    'contributors': '',  # text
    'website': 'http://www.akretion.com',
    'depends': ['account_cutoff_base'],
    'external_dependencies': {'python': ['phonenumbers', 'Asterisk']},
    'data': [
        'company_view.xml',
        'account_view.xml',
    ],
    'demo': ['product_demo.xml'],
    'test': ['test/sale_stock_users.yml'],
    'qweb': ['static/src/xml/*.xml'],
    'css': ['static/src/css/*.css'],  # only in v7 (replaced by XML file in v8
    'js': ['static/src/js/*.js'],  # only in v7 ! (replaced by XML file in v8
    'images': [ # only in V7 ?
        'images/prepaid_revenue_draft.jpg',
        'images/prepaid_revenue_journal_entry.jpg',
        'images/prepaid_revenue_done.jpg',
        ],
    # pour les screenshots en v8: mettre dans static/description/, sans déclaration
    # dans ce fichier
    # pour l'icone du module (PNG 64x64 ou 128x128): rien à mettre dans __openerp__.py
    # v7: ./static/src/img/icon.png
    # v8: ./static/description/icon.png
    'url': 'http://www.akretion.com/doc_du_module.html',  # ??
    'installable': True,
    'auto_install': False,
    'application': True,
}
