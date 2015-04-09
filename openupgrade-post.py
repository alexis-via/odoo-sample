# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade, the free software migration tool for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com/)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

from openerp.openupgrade import openupgrade
from openerp import pooler, SUPERUSER_ID
import logging

logger = logging.getLogger('OpenUpgrade')

def migrate_invoice_addresses(cr, pool):
    # Contact id takes precedence over old partner id
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'account.invoice',
        'partner_id', openupgrade.get_legacy_name('address_contact_id'))

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    #migrate_invoice_addresses(cr, pool)
    migrate_invoice_names(cr, pool)
    lock_closing_reconciliations(cr, pool)
    migrate_payment_term(cr, pool)
    merge_account_cashbox_line(cr, pool)
    openupgrade.load_xml(
        cr, 'account',
        'migrations/7.0.1.1/data.xml')
