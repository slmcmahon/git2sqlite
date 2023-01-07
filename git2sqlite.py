from collections import namedtuple
import sys
import os
from os.path import exists
from datetime import datetime
import argparse
from app.azdo_git import AZDOGit
from app.git_db import GitDB, DbRepo


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
            f'The proposed path {proposed_path} is not a valid path.')
        return None
    return actual_path


def check_env_default(arg_value, arg_name, env_name):
    if arg_value:
        return arg_value.strip()
    if env_name in os.environ:
        return os.environ[env_name]
    raise ValueError(f'No value provided for --{arg_name}.')


def parse_args():
    parser = argparse.ArgumentParser(prog="git2sqlite",
                                     description="Extracts data from an AZDO git repo and loads it into a SQLite file")
    parser.add_argument('-o', '--org',
                        help="The Azure DevOps Organization. Will check for AZDO_ORG environment variable if omitted.")
    parser.add_argument('-p', '--project',
                        help="The Azure DevOps Project.  Will check for AZDO_PROJECT environment variable if omitted")
    parser.add_argument('-r', '--repo',
                        help="The Git Repository.")
    parser.add_argument('-d', '--db-file',
                        help="The SQLITE Database File to write to. This argument is required.",
                        required=True)
    parser.add_argument('-f', '--from-date',
                        help='The date from which to load commits (e.g. 2022-02-01)')
    parser.add_argument('-t', '--pat-token',
                        help="""A Personal Access Token that allows read access to the Azure DevOps Project. 
                                Will check for AZDO_PAT environment variable if omitted.""")
    parser.add_argument('-s', '--synchronize',
                        action='store_true',
                        help="""Specifies that all repositories will be updated since the last modified 
                                value of the committer_date value in the commits table. If set, then 
                                --from-date and --repo are ignored.""")

    args = parser.parse_args()

    proposed_path = None

    org = check_env_default(args.org, 'org', 'AZDO_ORG')
    project = check_env_default(args.project, 'project', 'AZDO_PROJECT')
    token = check_env_default(args.pat_token, 'token', 'AZDO_PAT')

    repo = args.repo.lstrip() if args.repo else None
    from_date = args.from_date.lstrip() if args.from_date else None
    if args.db_file:
        proposed_path = args.db_file.lstrip()

    return Args(org, project, repo, from_date, proposed_path, token, args.synchronize)


def main():
    args = None
    try:
        args = parse_args()
    except ValueError as e:
        print(e)
        exit(1)

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
            from_date = datetime.strptime(args.from_date, '%Y-%m-%d')
        else:
            from_date = gitdb.get_last_modified(args.repo)
        repo_list.append(DbRepo(args.repo, from_date))

    for repo in repo_list:
        print(f'Checking for updates to {repo.name}...')
        for commit in git.commits(repo.name, repo.last_commit):
            changes = git.changes(repo.name, commit.commit_id)
            print(
                f'Adding commit {commit.commit_id} from {commit.author_email} on {commit.author_date}.')
            gitdb.add_commit(commit, changes)

        print(f'Database is up to date for {repo.name}.')


if __name__ == '__main__':
    main()
