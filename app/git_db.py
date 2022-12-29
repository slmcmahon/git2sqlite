from collections import namedtuple
import sqlite3
from .azdo_git import Commit, Change
import moment

COMMITS_TABLE = """create table if not exists commits (
    id text unique, 
    repo_name text, 
    summary text, 
    author_name text, 
    author_email text, 
    author_date datetime,
    committer_name text,
    committer_email text,
    committer_date datetime
);
"""
FILES_TABLE = """create table if not exists commit_files (
    id text, 
    path text, 
    change_type,
    constraint fk_id
        foreign key (id)
        references commits (id)
        on delete cascade
);
"""

INSERT_COMMIT = """insert into commits (
    id, repo_name, summary, author_name, author_email, author_date, 
    committer_name, committer_email, committer_date) 
values (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""
INSERT_CHANGE = """insert into commit_files (
    id, path, change_type) 
values (?, ?, ?)
"""
EXISTING_REPOS = """
select 
    repo_name, 
    max(committer_date) 
from commits 
group by repo_name 
order by repo_name
"""
REPO_LAST_MODIFIED = """
select max(committer_date) 
from commits 
where repo_name = ?
"""

DbRepo = namedtuple("DbRepo", "name last_commit")


class GitDB():
    def __init__(self, db_path):
        self.db_path = db_path
        self.__init_db()

    def add_commit(self, commit: Commit):
        conn = self._get_connection()
        csr = conn.cursor()
        csr.execute(INSERT_COMMIT,
                    (commit.commit_id, commit.repo,
                     commit.comment, commit.author_name,
                     commit.author_email, commit.author_date,
                     commit.committer_name,
                     commit.committer_email, commit.committer_date))
        conn.commit()
        conn.close()
        
    def add_change(self, change: Change):
        conn = self._get_connection()
        csr = conn.cursor()
        csr.execute(INSERT_CHANGE,
                (change.commit_id, change.path, change.change_type))
        conn.commit()
        conn.close()
        
    def existing_repos(self):
        conn = self._get_connection()
        csr = conn.cursor()
        csr.execute(EXISTING_REPOS)
        rows = csr.fetchall()
        repos = [DbRepo(row[0], moment.date(row[1]).add(seconds=1).date) for row in rows]
        conn.close()
        return repos
    
    def get_last_modified(self, repo):
        conn = self._get_connection()
        csr = conn.cursor()
        csr.execute(REPO_LAST_MODIFIED, (repo,))
        lmd = csr.fetchone()[0]
        conn.close()
        if not lmd:
            return lmd
        return moment.date(lmd).add(seconds=1).date
        
        
    def __init_db(self):
        conn = self._get_connection()
        csr = conn.cursor()
        csr.execute(COMMITS_TABLE)
        csr.execute(FILES_TABLE)
        conn.commit()
        conn.close()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)
