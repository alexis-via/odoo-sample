#! /usr/bin/python3

import argparse
import configparser
import git
import os

__author__ = "Alexis de Lattre <alexis.delattre@akretion.com>"
__date__ = "April 2024"
__version__ = "0.3"


def main(args):
    print('args.config_file=', args.config_file)
    if not os.path.exists(args.config_file):
        exit("File %s doesn't exist" % args.config_file)
    config = configparser.ConfigParser()
    config.read(args.config_file)
    # raise if Odoo section not found
    for required_section in ['odoo', 'repos', 'github']:
        if required_section not in config.sections():
            exit(f"Missing [{required_section}] section in the configuration file {args.config_file}")
    version = config['odoo'].get('version')
    if len(version) == 2:
        assert version.isdigit()
        version = '%s.0' % version
    elif len(version) == 4:
        assert version.endswith('.0')
        assert version[:2].isdigit()
    print(f'Odoo version={version}')
    github_org = config['github'].get('organization')
    if not github_org:
        exit("Missing 'organization' in [github] section of config file")
    github_login = config['github'].get('login')
    if not github_login:
        exit("Missing 'login' in [github'] section of config file")
    github_proto = config['github'].get('protocol')
    if not github_proto:
        exit("Missing 'protocol' in [github'] section of config file")
    if github_proto not in ('https', 'ssh'):
        exit("The 'protocol' in [github] section must be 'https' or 'ssh'")
    if not os.path.exists('symlink'):
        os.mkdir('symlink')
    cur_dir = os.getcwd()
    path = []
    test_path = ['odoo/addons', 'addons', '../symlink']
    path.append(os.path.join(cur_dir, 'odoo/odoo/addons'))
    path.append(os.path.join(cur_dir, 'odoo/addons'))
    path.append(os.path.join(cur_dir, 'symlink'))

    oca_prefix = 'https://github.com/OCA/'
    for repo_name in config['repos']:
        original_repo_url = repo_url = config['repos'][repo_name]
        if github_proto == 'ssh':
            if original_repo_url.startswith('https://github.com/'):
                repo_url = repo_url.replace('https://github.com/', 'git@github.com:')
        elif github_proto == 'https':
            repo_url = f'{repo_url}.git'
            if original_repo_url.startswith('https://github.com/') and not original_repo_url.startswith(oca_prefix):
                repo_url = repo_url.replace('https://', f'https://{github_login}@')
        path.append(os.path.join(cur_dir, repo_name))
        test_path.append('../' + repo_name)
        # skip if repo is already on filesystem
        if os.path.exists(repo_name):
            if args.noupdate:
                print(f'{repo_name} subdir already exists: skipping')
            else:
                print(f'{repo_name} subdir already exists: updating')
                repo = git.Repo(repo_name)
                if str(repo.active_branch) != version:
                    exit(f"Branch name is {repo.active_branch} on {repo_name}; should be {version}")
                repo.remotes.origin.pull()
        else:
            print(repo_name)
            repo = git.Repo.clone_from(repo_url, repo_name, branch=version, single_branch=True)
            # Add Akretion remote repo
            if original_repo_url.startswith(oca_prefix):
                if github_proto == 'ssh':
                    org_repo_url = original_repo_url.replace(oca_prefix, f'git@github.com:{github_org}/')
                elif github_proto == 'https':
                    org_repo_url = original_repo_url.replace(oca_prefix, f'https://{github_login}@github.com/{github_org}/')
                    org_repo_url = f'{org_repo_url}.git'
                repo.create_remote(github_org, org_repo_url)

    for x in [path, test_path]:
        addons_path = 'addons_path = %s' % ','.join(x)
        print(addons_path)

if __name__ == '__main__':
    usage = "community-repo-checkout.py"
    epilog = "Author: %s - Version: %s" % (__author__, __version__)
    description = "Checkout and update community repositories for Odoo."

    parser = argparse.ArgumentParser(
        usage=usage, epilog=epilog, description=description)
    parser.add_argument(
        '-c', '--config', dest='config_file', default='/home/odoo/erp/community-repo.conf',
        help="Configuration file."
             "Default value: /home/odoo/erp/odoo-community-repo.conf")
    parser.add_argument(
        '-n', '--no-update', dest='noupdate', action='store_true',
        help="Don't update existing repositories.")
    args = parser.parse_args()
    main(args)
