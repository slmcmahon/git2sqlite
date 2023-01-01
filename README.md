git2sqlite
==

Extracts commit data from an Azure DevOps Git repo and stores it in an SQLite database

```
usage: git2sqlite [-h] [-o ORG] [-p PROJECT] [-r REPO] [-d DB_FILE] [-f FROM_DATE] [-t PAT_TOKEN] [-s]

Extracts data from an AZDO git repo and loads it into a SQLite file

options:
  -h, --help            show this help message and exit
  -o ORG, --org ORG     The Azure DevOps Organization. Defaults to 'slb-it' if not omitted.
  -p PROJECT, --project PROJECT
                        The Azure DevOps Project.
  -r REPO, --repo REPO  The Git Repository.
  -d DB_FILE, --db-file DB_FILE
                        The SQLITE Database File to write to. This file is created if it doesn't exist.
  -f FROM_DATE, --from-date FROM_DATE
                        The date from which to load commits (e.g. 2022-02-01)
  -t PAT_TOKEN, --pat-token PAT_TOKEN
                        A Personal Access Token that allows read access to the Azure DevOps Project. If this is not provided, then an 'AZDO_PAT' environment variable must be set.
  -s, --synchronize     Specifies that all repositories will be updated since the last moddified value of the committer_date value in the commits table. If set, then --from-date and --repo are ignored.
  ```

Examples:
==
## Extract data for a repository and add it to a new or existing database:

Get all commits from the ```webapp``` repository in the ```big-project``` project in the ```my-division``` organization:

```
git2sqlite -o my-division -p big-project -r webapp -f 2022-01-01 -d c:\data\big-project.sqlite3 -t <your-PAT>
```
or
```
git2sqlite --org my-division --project big-project --repo webapp --from-date 2022-01-01 -db-file c:\data\big-project.sqlite3 --pat-token <your-PAT>
```

**NOTE:** You can omit the -t / --pat-token argument if you have an environment variable named ```AZDO_PAT``` set with the appropriate value.


Subsequent calls with different repo names will add new records to an existing database.

## Update all repos in an existing database from last-modified date

Update all of the repos from the ```big-project``` project from the ```my-division``` project:

```
git2sqlite --org my-division --project big-project -d c:\data\big-project.sqlite3 --pat-token <your-PAT> --synchronize
```

Installation
==

For now:
```
python -m pip install 'git2sqlite @ git+https://github.com/slmcmahon/git2sqlite@9a17c72a0be4e9e4c758999464d27b31a90aa711'
```

Known Issues
==
* Nothing prevents adding commits to a database that was created for a different project.
* Others, I'm sure

## Near-term TODO:
* Improve error handling

This is a work in progress