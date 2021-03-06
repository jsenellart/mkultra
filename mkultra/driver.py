import argparse

from . import commands
from . import git_utils
from . import mkdocs
from .app_version import version as app_version


def add_git_arguments(parser, commit=True):
    parser.add_argument('-r', '--remote', default='origin',
                        help='origin to push to (default: %(default)s)')
    parser.add_argument('-b', '--branch', default='gh-pages',
                        help='branch to commit to (default: %(default)s)')
    if (commit):
        parser.add_argument('-m', '--message',
                            help='commit message')
        parser.add_argument('-p', '--push', action='store_true',
                            help='push to {remote}/{branch} after commit')
        parser.add_argument('-f', '--force', action='store_true',
                            help='force push when pushing')


def deploy(args):
    git_utils.update_branch(args.remote, args.branch)
    mkdocs.build()
    commands.deploy(mkdocs.site_dir, args.version, args.alias, args.branch,
                    args.message)
    if args.push:
        git_utils.push_branch(args.remote, args.branch, args.force)


def delete(args):
    git_utils.update_branch(args.remote, args.branch)
    commands.delete(args.version, args.all, args.branch, args.message)
    if args.push:
        git_utils.push_branch(args.remote, args.branch, args.force)


def list_versions(args):
    git_utils.update_branch(args.remote, args.branch)
    all_versions = commands.list_versions(args.branch)
    for version, aliases in all_versions:
        if aliases:
            print("{version} ({aliases})".format(
                version=version, aliases=", ".join(aliases)
            ))
        else:
            print("{version}".format(version=version))


def install_extras(args):
    commands.install_extras('mkdocs.yml', args.theme)


def main():
    parser = argparse.ArgumentParser(prog='mkultra')
    subparsers = parser.add_subparsers()

    parser.add_argument('--version', action='version',
                        version='%(prog)s ' + app_version)

    deploy_p = subparsers.add_parser(
        'deploy', help='build docs and deploy them to a branch'
    )
    deploy_p.set_defaults(func=deploy)
    add_git_arguments(deploy_p)
    deploy_p.add_argument('version', metavar='VERSION',
                          help='version (directory) to deploy this build to')
    deploy_p.add_argument('alias', nargs='*', metavar='ALIAS',
                          help='alias for this build (e.g. "latest")')

    delete_p = subparsers.add_parser(
        'delete', help='delete docs from a branch'
    )
    delete_p.set_defaults(func=delete)
    add_git_arguments(delete_p)
    delete_p.add_argument('--all', action='store_true',
                          help='delete everything')
    delete_p.add_argument('version', nargs='*', metavar='VERSION',
                          help='version (directory) to delete')

    list_p = subparsers.add_parser(
        'list', help='list deployed docs on a branch'
    )
    list_p.set_defaults(func=list_versions)
    add_git_arguments(list_p, commit=False)

    install_extras_p = subparsers.add_parser(
        'install-extras', help='install extra files to your docs'
    )
    install_extras_p.set_defaults(func=install_extras)
    install_extras_p.add_argument('-t', '--theme',
                                  help='the theme to use for your docs')

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as e:
        parser.exit(1, '{prog}: {error}\n'.format(
            prog=parser.prog, error=str(e)
        ))
