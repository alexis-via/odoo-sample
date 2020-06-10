# -*- coding: utf-8 -*-
# © 2018 Akretion (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# In post migration script:
# - we can access the registry
# - the new fields are created
# - the old fields are still readable
from odoo import pooler, SUPERUSER_ID


def migrate(cr, version):
    if not version:
        return

    pool = pooler.get_pool(cr.dbname)
    pto = pool['product.template']

    cr.execute(
        'ALTER TABLE "account_cutoff_line" RENAME "after_cutoff_days" '
        'TO "prepaid_days"')

    cr.execute(
        "UPDATE payment_line SET communication = communication2, "
        "communication2 = null "
        "FROM payment_order "
        "WHERE payment_line.order_id = payment_order.id "
        "AND payment_order.state in ('draft', 'open') "
        "AND payment_line.state = 'normal' "
        "AND communication2 is not null")

# Explications :
# Il faut créer un sous-répertoire "migrations/7.0.0.2/" et mettre ce script dedans:
# le script sera alors exécuté pour openerp 7.0, quand on met à jour le module vers la version 0.2
