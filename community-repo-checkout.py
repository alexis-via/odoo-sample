#! /usr/bin/python3

import git
import os

version = 12

repos = {

        # base
        'partner-contact': 'https://github.com/OCA/partner-contact',
        'community-data-files': 'https://github.com/OCA/community-data-files',

        # technical / general
        'contract': 'https://github.com/OCA/contract',
        'edi': 'https://github.com/OCA/edi',
        'intrastat': 'https://github.com/OCA/intrastat',
        'telephony': 'https://github.com/OCA/connector-telephony',
        'usability': 'https://github.com/akretion/odoo-usability',
        'viewer-groups': 'https://github.com/akretion/odoo-viewer-groups',
        'l10n-france': 'https://github.com/OCA/l10n-france',
        'procurement-suggest': 'https://github.com/akretion/procurement-suggest',
        'purchase-workflow': 'https://github.com/OCA/purchase-workflow',
        'sale-workflow': 'https://github.com/OCA/sale-workflow',
        'reporting-engine': 'https://github.com/OCA/reporting-engine',
        'server-auth': 'https://github.com/OCA/server-auth',
        'server-backend': 'https://github.com/OCA/server-backend',
        'server-brand': 'https://github.com/OCA/server-brand',
        'server-env': 'https://github.com/OCA/server-env',
        'server-tools': 'https://github.com/OCA/server-tools',
        'server-ux': 'https://github.com/OCA/server-ux',
        'web': 'https://github.com/OCA/web',

        # stock
        'stock-logistics-barcode': 'https://github.com/OCA/stock-logistics-barcode',
        'stock-logistics-warehouse': 'https://github.com/OCA/stock-logistics-warehouse',
        'stock-logistics-workflow': 'https://github.com/OCA/stock-logistics-workflow',
        'stock-logistics-tracking': 'https://github.com/OCA/stock-logistics-tracking',

        # accounting
        'account-move-import': 'https://github.com/akretion/account-move-import',
        'currency': 'https://github.com/OCA/currency',
        'mis-builder': 'https://github.com/OCA/mis-builder',
        'account-analytic': 'https://github.com/OCA/account-analytic',
        'account-closing': 'https://github.com/OCA/account-closing',
        'account-financial-reporting': 'https://github.com/OCA/account-financial-reporting',
        'account-financial-tools': 'https://github.com/OCA/account-financial-tools',
        'account-invoicing': 'https://github.com/OCA/account-invoicing',
        'bank-statement-import': 'https://github.com/OCA/bank-statement-import',
        'bank-statement-reconcile-simple': 'https://github.com/akretion/bank-statement-reconcile-simple',
        'bank-payment': 'https://github.com/OCA/bank-payment',
        }

os.mkdir('symlink')
cur_dir = os.getcwd()
path = []
test_path = ['odoo/addons', 'addons', '../symlink']
path.append(os.path.join(cur_dir, 'odoo/odoo/addons'))
path.append(os.path.join(cur_dir, 'odoo/addons'))
path.append(os.path.join(cur_dir, 'symlink'))

for repo_name, repo_url in repos.items():
    print(repo_name)
    remote_branch = '%d.0' % version
    repo = git.Repo.clone_from(repo_url, repo_name, branch=remote_branch)

    path.append(os.path.join(cur_dir, repo_name))
    test_path.append('../' + repo_name)

for x in [path, test_path]:
    addons_path = 'addons_path = %s' % ','.join(x)
    print(addons_path)
