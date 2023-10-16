# Copyright 2023 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

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
