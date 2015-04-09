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

column_renames = {
    'account_invoice': [
        ('address_contact_id', None),
        # Il va garder le champ address_contact_id et ne pas le
        # dropper ; pour récupérer le champ en post, il faut faire
        # openupgrade.get_legacy_name('address_contact_id')
    ]
    }

@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return
    openupgrade.rename_columns(cr, column_renames)
