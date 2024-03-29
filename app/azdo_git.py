from collections import namedtuple
import json
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth

Commit = namedtuple(
    "Commit", "commit_id repo comment author_name author_email author_date committer_name committer_email committer_date")
Change = namedtuple("Change", "commit_id path change_type")


class AZDOGit():
    BASE_URL_FORMAT = 'https://dev.azure.com/{}/{}/_apis/git'
    PAGE_SIZE = 50

    def __init__(self, org, project, token):
        self.org = org
        self.project = project
        self.token = token
        self.base_url = self.BASE_URL_FORMAT.format(org, project)

    def repos(self, filter=None):
        url = f'{self.base_url}/repositories?api-version=7.0'
        response = self.__get_data(url)
        data = response['value']
        if filter:
            return [r['name'] for r in data if filter.lower() in r['name'].lower()]
        else:
            return [r['name'] for r in data]

    def commits(self, repo, date_from=None):
        hasMore = True
        skip = 0
        url = self.__get_url(repo, self.PAGE_SIZE, skip, date_from)
        while hasMore:
            data = self.__get_data(url)
            item_count = data['count']
            if item_count > 0:
                for commit in data['value']:
                    yield self.__parse_commit_data(repo, commit)
                skip += item_count
                url = self.__get_url(repo, self.PAGE_SIZE, skip, date_from)
            else:
                hasMore = False

    def changes(self, repo, commit_id):
        url = f'{self.base_url}/repositories/{repo}/commits/{commit_id}/changes'
        data = self.__get_data(url)
        return [
            Change(commit_id=cr['item']['commitId'], path=cr['item']
                   ['path'], change_type=cr['changeType'])
            for cr in data['changes']
            if cr['item']['gitObjectType'] == 'blob']

    def __get_url(self, repo, pagesize, skip, since):
        url = f'{self.base_url}/repositories/{repo}/commits?api-version=7.0&$top={pagesize}&$skip={skip}&searchCriteria.showOldestCommitsFirst=true'
        if since:
            formatted_date = datetime.strftime(since, '%Y-%m-%dT%H:%M:%SZ')
            url = f'{url}&searchCriteria.fromDate={formatted_date}'
        return url

    def __get_data(self, url):
        response = requests.get(url, auth=HTTPBasicAuth('user', self.token))
        if response.status_code != 200:
            raise Exception(
                f'Got Status Code {response.status_code}.  Message: {response.reason}')
        return json.loads(response.content.decode('utf-8'))

    def __parse_commit_data(self, repo, ci):
        id = ci['commitId']
        comment = ci['comment']
        author = ci['author']
        author_name = author['name']
        author_email = author['email']
        author_date = self.__clean_date_string(author['date'])
        committer = ci['committer']
        committer_name = committer['name']
        committer_email = committer['email']
        committer_date = self.__clean_date_string(committer['date'])
        return Commit(id, repo, comment, author_name, author_email, author_date, committer_name, committer_email, committer_date)

    def __clean_date_string(self, date_string):
        return " ".join(date_string.split('T'))[:-1]
