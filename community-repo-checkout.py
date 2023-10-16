#! /usr/bin/python3

import git
import os

GITHUB_LOGIN = 'alexis-via'
GITHUB_ORG = 'akretion'

proto_map = {
    '1': 'https',
    '2': 'ssh',
    }

proto_int = input('Github access: 1 for HTTPS, 2 for SSH : ')
if proto_int in proto_map:
    github_proto = proto_map[proto_int]
else:
    raise
assert github_proto in ('https', 'ssh')


version = input('Odoo version : ')
if len(version) == 2:
    assert version.isdigit()
    version = '%s.0' % version
elif len(version) == 4:
    assert version.endswith('.0')
    assert version[:2].isdigit()
else:
    raise

repos = {
        # base
        'partner-contact': 'https://github.com/OCA/partner-contact',
        'community-data-files': 'https://github.com/OCA/community-data-files',

        # technical
        'py3o-report-templates': 'https://github.com/akretion/odoo-py3o-report-templates',
        'viewer-groups': 'https://github.com/akretion/odoo-viewer-groups',
        'reporting-engine': 'https://github.com/OCA/reporting-engine',
        'server-auth': 'https://github.com/OCA/server-auth',  # from v8
        'server-backend': 'https://github.com/OCA/server-backend',  # from v11
        'server-brand': 'https://github.com/OCA/server-brand',  # from v11
        'server-env': 'https://github.com/OCA/server-env',  # from v11
        'server-tools': 'https://github.com/OCA/server-tools',
        'server-ux': 'https://github.com/OCA/server-ux',  # from v10
        'report-print-send': 'https://github.com/OCA/report-print-send',
        'web': 'https://github.com/OCA/web',
        'web-api': 'https://github.com/OCA/web-api',  # from v14
        'rest-framework': 'https://github.com/OCA/rest-framework',  # from v10

        # general
        'usability': 'https://github.com/akretion/odoo-usability',
        'purchase-workflow': 'https://github.com/OCA/purchase-workflow',
        'sale-workflow': 'https://github.com/OCA/sale-workflow',
        'l10n-france': 'https://github.com/OCA/l10n-france',
        'edi': 'https://github.com/OCA/edi',

        # stock/mrp
        'stock-logistics-barcode': 'https://github.com/OCA/stock-logistics-barcode',
        'stock-logistics-warehouse': 'https://github.com/OCA/stock-logistics-warehouse',
        'stock-logistics-workflow': 'https://github.com/OCA/stock-logistics-workflow',
        'stock-logistics-tracking': 'https://github.com/OCA/stock-logistics-tracking',
        'manufacture': 'https://github.com/OCA/manufacture',

        # accounting
        'account-move-import': 'https://github.com/akretion/account-move-import',
        'currency': 'https://github.com/OCA/currency',
        'mis-builder': 'https://github.com/OCA/mis-builder',
        'account-analytic': 'https://github.com/OCA/account-analytic',
        'account-closing': 'https://github.com/OCA/account-closing',
        'account-financial-reporting': 'https://github.com/OCA/account-financial-reporting',
        'account-financial-tools': 'https://github.com/OCA/account-financial-tools',
        'account-fiscal-rule': 'https://github.com/OCA/account-fiscal-rule',
        'account-invoicing': 'https://github.com/OCA/account-invoicing',
        'bank-statement-import': 'https://github.com/OCA/bank-statement-import',
        'account-reconcile': 'https://github.com/OCA/account-reconcile',
        'bank-statement-reconcile-simple': 'https://github.com/akretion/bank-statement-reconcile-simple',
        'bank-payment': 'https://github.com/OCA/bank-payment',
        'credit-control': 'https://github.com/OCA/credit-control',
        'intrastat': 'https://github.com/OCA/intrastat-extrastat',

        # MISC
        # 'mooncard': 'https://github.com/akretion/odoo-mooncard-connector',
        # 'telephony': 'https://github.com/OCA/connector-telephony',
        # 'donation': 'https://github.com/OCA/donation',
        # 'vertical-abbey': 'https://github.com/OCA/vertical-abbey',
        # 'contract': 'https://github.com/OCA/contract',
        # 'multi-company': 'https://github.com/OCA/multi-company',
        # 'ak-incubator': 'https://github.com/akretion/ak-odoo-incubator',
        # 'pos': 'https://github.com/OCA/pos',
        # 'delivery-carrier': 'https://github.com/OCA/delivery-carrier',

        # e-commerce / shopinvader
        # 'product-attribute': 'https://github.com/OCA/product-attribute',
        # 'product-variant': 'https://github.com/OCA/product-variant',
        # 'connector': 'https://github.com/OCA/connector',
        # 'queue': 'https://github.com/OCA/queue',
        # 'connector-ecommerce': 'https://github.com/OCA/connector-ecommerce',
        # 'ecommerce': 'https://github.com/OCA/e-commerce',
        # 'search-engine': 'https://github.com/OCA/search-engine',
        # 'storage': 'https://github.com/OCA/storage',
        # 'shopinvader': 'https://github.com/shopinvader/odoo-shopinvader',
        # 'shopinvader-payment': 'https://github.com/shopinvader/odoo-shopinvader-payment',
        # 'shopinvader-pim': 'https://github.com/shopinvader/odoo-pim',

        }

if not os.path.exists('symlink'):
    os.mkdir('symlink')
cur_dir = os.getcwd()
path = []
test_path = ['odoo/addons', 'addons', '../symlink']
path.append(os.path.join(cur_dir, 'odoo/odoo/addons'))
path.append(os.path.join(cur_dir, 'odoo/addons'))
path.append(os.path.join(cur_dir, 'symlink'))

oca_prefix = 'https://github.com/OCA/'
for repo_name, original_repo_url in repos.items():
    repo_url = original_repo_url
    if github_proto == 'ssh':
        if original_repo_url.startswith('https://github.com/'):
            repo_url = repo_url.replace('https://github.com/', 'git@github.com:')
    elif github_proto == 'https':
        repo_url = '%s.git' % repo_url
        if original_repo_url.startswith('https://github.com/') and not original_repo_url.startswith(oca_prefix):
            repo_url = repo_url.replace('https://', f'https://{GITHUB_LOGIN}@')
    path.append(os.path.join(cur_dir, repo_name))
    test_path.append('../' + repo_name)
    # skip if repo is already on filesystem
    if os.path.exists(repo_name):
        print('%s subdir already exists: skipping' % repo_name)
        continue
    print(repo_name)
    repo = git.Repo.clone_from(repo_url, repo_name, branch=version, single_branch=True)
    # Add Akretion remote repo
    if original_repo_url.startswith(oca_prefix):
        if github_proto == 'ssh':
            org_repo_url = original_repo_url.replace(oca_prefix, 'git@github.com:akretion/')
        elif github_proto == 'https':
            org_repo_url = original_repo_url.replace(oca_prefix, f'https://{GITHUB_LOGIN}@github.com/{GITHUB_ORG}/')
            org_repo_url = '%s.git' % org_repo_url
        repo.create_remote(GITHUB_ORG, org_repo_url)


for x in [path, test_path]:
    addons_path = 'addons_path = %s' % ','.join(x)
    print(addons_path)
