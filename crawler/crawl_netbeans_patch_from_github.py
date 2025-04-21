import calendar
import time

import pandas as pd
from urllib.parse import urlparse
from github import Github
from collections import defaultdict
import csv
import requests
from tempfile import NamedTemporaryFile
import shutil
from github import RateLimitExceededException
import traceback


# the token of GitHub User, meant to crawl the GitHub API
g = Github("")




## write the header of the test_crawl_data.csv
def write_header_to_csv(file_name):
    header = ['bug_report_id', 'commit_html_url']
    with open(file_name, 'w+', encoding='utf-8', newline='') as file:
        print('open file')
        writer = csv.writer(file)
        writer.writerow(header)
        print('headers written')



def read_raw_info_from_csv(file_path, row_name):
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        column = [row[row_name] for row in reader]
    return column






def crawl_bug_reports_from_repo(current_line, bug_id_url_list, repo_name, checkDict):
    bug_report_id = str(bug_id_url_list[current_line])
    search_string = 'repo:' + repo_name + ' ' + bug_report_id
    print(search_string)

    try:
        print('------------bug_report_id--------------------', bug_report_id)
        target_commits = g.search_commits(search_string)

        print('total searched commits number is ', target_commits.totalCount)

        commit_html_url = ''
        for each_commit in target_commits:
            if len(commit_html_url) == 0:
                commit_html_url = each_commit.html_url
            else:
                commit_html_url = commit_html_url + ';' + each_commit.html_url

        dict_key = str(bug_report_id)

        print('------combined_key------', dict_key)
        # if it is not in the checkDict, put it into checkDict
        if checkDict.get(dict_key) == None:
            issue_content = {}
            issue_content['bug_report_id'] = bug_report_id
            issue_content['commit_html_url'] = commit_html_url

            checkDict[dict_key] = issue_content

        print('------------bug_report_id--------------------', bug_report_id)

    # this is for the github.GithubException.RateLimitExceededException: 403
    except Exception:
        search_rate_limit = g.get_rate_limit().search
        print('search remaining', format(search_rate_limit.remaining))
        reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
        # add 10 seconds to be sure the rate limit has been reset
        sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10

        if sleep_time <= 0:
            sleep_time = 61

        time.sleep(sleep_time)
        print('!!!!!!!!!!!!!!!there are exceptions!')
        traceback.print_exc()
        return current_line

    return current_line + 1


def test_crawl_idea_patch():
    repo_name = "apache/netbeans"
    source_file_path = 'source_file/netbeans_bugzilla.csv'
    row_name = 'id_number'


    target_file_path = 'target_file/' + str(repo_name).split('/')[-1] + '_refactoring_bug_reports.csv'
    print('target_file_path is ', target_file_path)

    # write header to csv file
    write_header_to_csv(target_file_path)
    bug_id_url_list = read_raw_info_from_csv(source_file_path, row_name)
    total_len = len(bug_id_url_list)



    repo = g.get_repo(repo_name)
    print('repo name is ', repo.name.strip())

    # create a dict to save data
    checkDict = {}


    current_line = 0
    while current_line < total_len:
        error_at = crawl_bug_reports_from_repo(current_line, bug_id_url_list, repo_name, checkDict)
        current_line = error_at


    with open(target_file_path, 'a+', encoding='utf-8', newline='') as file:
        print(target_file_path, ' opened')
        writer = csv.writer(file)

        data_list = []
        for key in checkDict.keys():
            one_data_list = []
            value = checkDict.get(key)
            one_data_list.append(str(value.get('bug_report_id')))
            one_data_list.append(str(value.get('commit_html_url')))
            data_list.append(one_data_list)
        print('---data_list--', data_list)
        # write the data of one pull request to csv file
        writer.writerows(data_list)
        print(target_file_path, ' written')

test_crawl_idea_patch()