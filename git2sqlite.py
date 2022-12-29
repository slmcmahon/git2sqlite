from collections import namedtuple
import sys
import os
from os.path import exists
import moment
import argparse
from app.azdo_git import AZDOGit
from app.git_db import GitDB, DbRepo

DEFAULT_PAT = os.environ['AZDO_PAT']
DEFAULT_ORG = 'slb-it'
DEFAULT_PROJECT = 'es-delivery-platform'
DEFAULT_DB_PATH = os.path.join(os.path.expanduser('~'), 'gitlog.sqlite3')


Args = namedtuple(
    "Args", "org project, repo from_date db_path token synchronize")


def get_db_path(proposed_path):
    if exists(proposed_path):
        return proposed_path

    actual_path = None
    try:
        with open(proposed_path, 'x') as _:
            actual_path = proposed_path
    except:
        print(
            f'The proposed path {proposed_path} is not a valid path.  Using default: {DEFAULT_DB_PATH}.')
        return None
    return actual_path


def parse_args():
    parser = argparse.ArgumentParser(prog="git2sqlite",
                                     description="Extracts data from an AZDO git repo and loads it into a SQLite file")
    parser.add_argument('-o', '--org',
                        help="The Azure DevOps Organization. Defaults to 'slb-it' if not omitted.")
    parser.add_argument('-p', '--project',
                        help="The Azure DevOps Project.")
    parser.add_argument('-r', '--repo',
                        help="The Git Repository.")
    parser.add_argument('-d', '--db-file',
                        help="The SQLITE Database File to write to.  This file is created if it doesn't exist.")
    parser.add_argument('-f', '--from-date',
                        help='The date from which to load commits (e.g. 2022-02-01)')
    parser.add_argument('-t', '--pat-token',
                        help="A Personal Access Token that allows read access to the Azure DevOps Project.  If this is not provided, then an 'AZDO_PAT' environment variable must be set.")
    parser.add_argument('-s', '--synchronize',
                        action='store_true',
                        help='Specifies that all repositories will be updated since the last moddified value of the committer_date value in the commits table. If set, then --from-date and --repo are ignored.')

    args = parser.parse_args()

    proposed_path = None
    org = args.org.lstrip() if args.org else DEFAULT_ORG
    project = args.project.lstrip() if args.project else DEFAULT_PROJECT
    token = args.pat_token.lstrip() if args.pat_token else DEFAULT_PAT
    repo = args.repo.lstrip() if args.repo else None
    from_date = args.from_date.lstrip() if args.from_date else None
    if args.db_file:
        proposed_path = args.db_file.lstrip()

    return Args(org, project, repo, from_date, proposed_path, token, args.synchronize)


def main():
    args = parse_args()

    db_path = get_db_path(args.db_path)
    if not db_path:
        print(f'{args.db_path} is not a valid path.  Exiting')
        exit(1)

    print(f'Using DB Path: {db_path}')

    git = AZDOGit(args.org, args.project, args.token)
    gitdb = GitDB(args.db_path)

    repo_list = []

    if args.synchronize:
        repo_list = gitdb.existing_repos()
    else:
        from_date = None
        if args.from_date:
            from_date = moment.date(args.from_date).date
        else:
            from_date = gitdb.get_last_modified(args.repo)
        repo_list.append(DbRepo(args.repo,from_date))

    for repo in repo_list:
        print(f'Checking for updates to {repo.name}...')
        for commit in git.commits(repo.name, repo.last_commit):
            print(
                f'Adding commit {commit.commit_id} from {commit.author_email} on {commit.author_date}.')
            gitdb.add_commit(commit)
            for change in git.changes(repo.name, commit.commit_id):
                print(f'  {change.change_type} for file: {change.path}.')
                gitdb.add_change(change)
        print(f'Database is up to date for {repo.name}.')
        


if __name__ == '__main__':
    main()
