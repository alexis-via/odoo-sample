# -*- coding: utf-8 -*-
# © 2016 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

def migrate(cr, version):
    if not version:
        return

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
