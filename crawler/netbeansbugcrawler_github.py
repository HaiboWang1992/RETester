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


# if the repository and pull request is crawled, set the flag to 1, default is 0
def update_pr_to_crawled(pr_data_file, repo, pr_num):
    filename = pr_data_file
    tempfile = NamedTemporaryFile('w', newline='', delete=False)
    fields = ['repo', 'pr_num', 'is_crawled']

    with open(filename, 'r', newline='') as csvfile, tempfile:
        reader = csv.DictReader(csvfile, fieldnames=fields)
        writer = csv.DictWriter(tempfile, fieldnames=fields)
        for row in reader:
            # print('repo is : ', row['repo'], 'pr_num is : ', row['pr_num'], 'is_crawled is : ', row['is_crawled'])
            if row['repo'] == repo and str(row['pr_num']) == str(pr_num):
                row['is_crawled'] = "1"
            row = {'repo': row['repo'], 'pr_num': row['pr_num'], 'is_crawled': row['is_crawled']}
            writer.writerow(row)
    shutil.move(tempfile.name, filename)


# check the pull request is crawled, default is 0
def check_pr_is_crwaled(filename, repo, pr_num):
    df = pd.read_csv(filename)
    res = df.loc[(df['repo'] == repo) & (df['pr_num'] == pr_num) & (df['is_crawled'] == 1)]
    return len(res)


# write the parsed repository and pull request id into a csv file
def write_repo_pr_to_csv(filename, di):
    with open(filename, "w+", newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',')
        header = ['repo', 'pr_num', 'is_crawled']
        writer.writerow(header)
        keys = di.keys()
        for key in keys:
            values = di.get(key)
            for value in values:
                is_crawled = "0"
                print('key is : ', key, ', value is : ', value, 'is_crawled is : ', is_crawled)
                row_data = [key, value, is_crawled]
                writer.writerow(row_data)

## write the header of the test_crawl_data.csv
def write_header_to_csv(file_name):
    header = ['html_url', 'title', 'state', 'created_at', 'closed_at']
    with open(file_name, 'w+', encoding='utf-8', newline='') as file:
        print('open file')
        writer = csv.writer(file)
        writer.writerow(header)
        print('headers written')




def recursive_to_find_changed_commit(repo, comment_file_name, pr_commit_id_and_parent_id_dict, comment_original_commit_id):
    changed_in_this_commit = False
    for target_commit_id, target_commit_parent_id in pr_commit_id_and_parent_id_dict.items():
        if target_commit_parent_id == comment_original_commit_id:
            target_commit_files = repo.get_commit(sha=target_commit_id).files
            for target_commit_file in target_commit_files:
                if target_commit_file.filename == comment_file_name:
                    changed_in_this_commit = True
                    return changed_in_this_commit, target_commit_id
            return changed_in_this_commit, target_commit_id
    return changed_in_this_commit, None



# the main function to crawl the data according the repository and pull request number
# the data is crawled through GitHub public APIs V3, PyGitHub
def crawl_comment(current_line, df):
    print('--current line is-------', current_line)

    # each item contains three contents: repository name, pull request number and is_crawled flag
    current_line_data = df.loc[current_line, :].values.tolist()

    print('--current line data is--', current_line_data)

    repo_name = current_line_data[0]
    pr_num = current_line_data[1]
    pr_is_crawled = current_line_data[2]


    # if this pull request is crawled, move to the next PR
    if pr_is_crawled == 1:
        return current_line + 1
    try:
        # get the repository and pull request objects by PyGitHub's APIs
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(int(pr_num))

        pr_date = pr.created_at
        pr_title = pr.title
        pr_html_url = pr.html_url
        pr_body = pr.body

        print('--start--a--pull request--', pr_num)
        print('pull html url is : ', pr_html_url)

        # get the comments of the pull request
        comments = pr.get_comments()

        # the pull request does not have comments, ignore this pull request
        if comments.totalCount == 0:
            print('!!!!!!!!!!!!!!this pr has 0 comments, ignore it')
            return current_line + 1

        # create a dict to save data
        checkDict = {}

        pr_commits = pr.get_commits()
        pr_commits_id = []
        for pr_commit in pr_commits:
            pr_commit_id = pr_commit.commit.sha
            if pr_commit_id != None:
                pr_commits_id.append(pr_commit_id)

        print('this pr contains commit id are: ', pr_commits_id)

        # if this pr contains only one commit, ignore this pr
        if pr_commits.totalCount == 1:
            print('!!!!!!!!!!!!!!!this pr only has one commit, ignore it')
            return current_line + 1

        pr_commit_id_and_parent_id_dict = {}
        for pr_commit_id in pr_commits_id:
            pr_commit = repo.get_commit(sha=pr_commit_id)
            pr_commit_parent_list = pr_commit.parents
            print('----------pr_commit_parent_list----------', pr_commit_parent_list)
            print('----------pr_commit_parent_list[0].commit.sha----------', pr_commit_parent_list[0].commit.sha)
            if pr_commit_parent_list[0].commit.sha not in pr_commits_id:
                continue
            pr_commit_id_and_parent_id_dict[pr_commit_id] = pr_commit_parent_list[0].commit.sha

        print('-------pr_commit_id_and_parent_id_dict------', pr_commit_id_and_parent_id_dict)


        # loop the comments in the pull request to filter invalid data
        for comment in comments:

            print('--start a comment--')
            # calculate how many comments in total
            # comments_num = comments_num + 1

            print('comment html_url is : ', comment.html_url)
            # igore not .java files
            if '.java' not in comment.path:
                # calculate not java file number
                # total_not_java_files = total_not_java_files + 1
                # calculate invalid comment number
                # invalid_comments_num = invalid_comments_num + 1
                print('!!!!!!!!!this comment is not for a java file, pass through this')
                continue

            # the comment who's line = null can't be used
            # raw data is the comment's raw json data
            raw = comment.raw_data
            # line = raw.get("line")
            original_line = raw.get("original_line")
            # print("line is: ", line)
            # print("original_line is: ", original_line)

            # any of those two is null, this comment is invalid
            if original_line == None:
                # calculate the line null comment number
                # total_original_line_null_amount = total_original_line_null_amount + 1
                # calculate invalid comment number
                # invalid_comments_num = invalid_comments_num + 1
                print('!!!!!!!!!original_line is None')
                continue

            # if comment is not the first comment, ignore it
            # in some cases, comment has in_reply_to_id, it means this is not the first comment,
            # it is a reply to the first comment, so if this is the case, filter this comment

            if (comment.in_reply_to_id != None):
                # calculate invalid comment number
                # invalid_comments_num = invalid_comments_num + 1
                # calculate not first comment number
                # not_first_comment = not_first_comment + 1
                print('!!!!!!!!!in_reply_to_id is not None')
                continue

            # sometimes, the .java file is outdated, so we can not get it, ignore the comment if this happens
            comment_file_name = comment.path
            comment_commit_id = comment.commit_id
            comment_original_commit_id = comment.original_commit_id

            comment_original_commit_id_copy = comment_original_commit_id



            try:
                comment_original_commit = repo.get_commit(sha=comment_original_commit_id)
            except:
                print('!!!!!!!!!get commit from repo has something wrong, exception happens.')
                traceback.print_exc()
                return current_line + 1

            # get the changed files in the original commit
            comment_original_commit_files = comment_original_commit.files

            print('comment original_commit.files is: ', comment_original_commit_files)

            # comment body is the comment review
            comment_body = comment.body

            print('comment body is: ', comment_body)

            '''
            To judge if the reviewed file is changed in this commit.
            if not, find the parents commit, check the changed files in the parents commit, if it contains filename, then we get the commit that contains the file changed
            however, there are special occasions, for example, one file is changed many times, the nearest commit contains changed file, but this change is not relevant to
            this review comment, so we need to compare the code line (original code line number) is changed or not, if it is changed, this is relevant, otherwise, it is not relevant.
            '''
            changed_in_this_commit = False
            i_count = 0
            while changed_in_this_commit == False:
                try:
                    i_count = i_count + 1
                    print('---i_count--', i_count)
                    print('-----changed_in_this_commit-----', changed_in_this_commit)
                    print('-----comment_original_commit_id-----', comment_original_commit_id)
                    is_found, target_commit_id = recursive_to_find_changed_commit(repo, comment_file_name, pr_commit_id_and_parent_id_dict, comment_original_commit_id)
                    if target_commit_id == None:
                        break
                    changed_in_this_commit = is_found
                    comment_original_commit_id = target_commit_id
                except:
                    print('!!!!!!!!!!!!!!!!!get commit from repo has something wrong, exception happens.')
                    traceback.print_exc()
                    return current_line + 1

            print('--outer---changed_in_this_commit-----', changed_in_this_commit)
            print('--outer---comment_original_commit_id-----', comment_original_commit_id)
            if changed_in_this_commit == False:
                continue

            target_commit = repo.get_commit(sha=comment_original_commit_id)

            original_file_url = "https://raw.githubusercontent.com/" + repo_name + "/" + comment_original_commit_id_copy + "/" + comment_file_name
            changed_file_url = "https://raw.githubusercontent.com/" + repo_name + "/" + target_commit.commit.sha + "/" + comment_file_name
            changed_commit_message = target_commit.commit.message



            print("original_file_url is : ", original_file_url)
            print("changed_file_url is : ", changed_file_url)
            print("changed_commit_message is : ", changed_commit_message)
            # the content of the url
            original_file_content = requests.get(original_file_url).text
            changed_file_content = requests.get(changed_file_url).text

            print('--------404-----------', ("404: Not Found" == str(original_file_content)) or ("404: Not Found" == str(changed_file_content)))
            # if any of those is null, ignore this comment
            if ("404: Not Found" == str(original_file_content)) or ("404: Not Found" == str(changed_file_content)):
                # total_file_invalid_num = total_file_invalid_num + 1
                # invalid_comments_num = invalid_comments_num + 1
                continue
            # print("original_file_content is : ", original_file_content)
            # print("file_content is : ", file_content)

            # in some cases, comment does not have in_reply_to_id
            # to get the first comment, we should consider the create date of comment,
            # the same commit, original_commit, file, original line, line with different create_date should
            # only keep the earliest one
            combined_key = str(comment.commit_id) + str(comment.original_commit_id) + \
                           str(comment.path) + str(raw.get("original_line"))

            print('------combined_key------', combined_key)
            # if the comment is for the same commit_id, original_commit_id, file and original_line,
            # if it is not in the checkDict, put it into checkDict
            if checkDict.get(combined_key) == None:
                inside_comment = {}
                inside_comment['comment_html_url'] = comment.html_url
                inside_comment['comment_api_url'] = comment.url
                inside_comment['comment_author'] = comment.user.name
                inside_comment['diff_hunk'] = comment.diff_hunk
                inside_comment['review_comment'] = comment.body
                inside_comment['file_path'] = comment.path
                inside_comment['comment_id'] = comment.id
                inside_comment['commit_id'] = comment.commit_id
                inside_comment['original_commit_id'] = comment.original_commit_id
                inside_comment['changed_commit_id'] = target_commit.commit.sha
                inside_comment['original_commit_url'] = comment_original_commit.commit.url
                inside_comment['changed_commit_url'] = target_commit.commit.url
                inside_comment['original_commit_author'] = comment_original_commit.commit.committer.name
                inside_comment['changed_commit_author'] = target_commit.commit.committer.name
                inside_comment['original_commit_created_at'] = comment_original_commit.commit.committer.date
                inside_comment['changed_commit_created_at'] = target_commit.commit.committer.date
                inside_comment['comment_created_at'] = comment.created_at
                inside_comment['pull_request_url'] = comment.pull_request_url
                inside_comment['original_line'] = raw.get('original_line')
                inside_comment['line'] = raw.get('line')
                inside_comment['changed_file'] = changed_file_content
                inside_comment['original_file'] = original_file_content
                inside_comment['pull_request_title'] = pr.title
                inside_comment['pull_request_body'] = pr.body
                inside_comment['changed_commit_message'] = changed_commit_message
                inside_comment['start_line'] = raw.get('start_line')
                inside_comment['original_start_line'] = raw.get('original_start_line')

                checkDict[combined_key] = inside_comment
                print('----------------------------end a comment--')
            else:
                continue

        print('-------checkDict------', checkDict)

        with open('crawl_reviews_and_commits.csv', 'a+', encoding='utf-8', newline='') as file:
            print('crawl_reviews_and_commits.csv opened')
            writer = csv.writer(file)

            data_list = []
            for key in checkDict.keys():
                one_data_list = []
                value = checkDict.get(key)
                one_data_list.append(str(value.get('comment_html_url')))
                one_data_list.append(str(value.get('comment_api_url')))
                one_data_list.append(str(value.get('comment_author')))
                one_data_list.append(str(value.get('diff_hunk')))
                one_data_list.append(str(value.get('review_comment')))
                one_data_list.append(str(value.get('file_path')))
                one_data_list.append(str(value.get('comment_id')))
                one_data_list.append(str(value.get('commit_id')))
                one_data_list.append(str(value.get('original_commit_id')))
                one_data_list.append(str(value.get('changed_commit_id')))
                one_data_list.append(str(value.get('original_commit_url')))
                one_data_list.append(str(value.get('changed_commit_url')))
                one_data_list.append(str(value.get('original_commit_author')))
                one_data_list.append(str(value.get('changed_commit_author')))
                one_data_list.append(str(value.get('original_commit_created_at')))
                one_data_list.append(str(value.get('changed_commit_created_at')))
                one_data_list.append(str(value.get('comment_created_at')))
                one_data_list.append(str(value.get('pull_request_url')))
                one_data_list.append(str(value.get('original_line')))
                one_data_list.append(str(value.get('line')))
                one_data_list.append(str(value.get('changed_file')))
                one_data_list.append(str(value.get('original_file')))
                one_data_list.append(str(value.get('pull_request_title')))
                one_data_list.append(str(value.get('pull_request_body')))
                one_data_list.append(str(value.get('changed_commit_message')))
                one_data_list.append(str(value.get('start_line')))
                one_data_list.append(str(value.get('original_start_line')))

                data_list.append(one_data_list)
            print('---data_list--', data_list)
            # write the data of one pull request to csv file
            writer.writerows(data_list)
            print('crawl_reviews_and_commits.csv written')

        update_pr_to_crawled(repo_pr_file_name, repo_name, pr_num)
        print('-------------------------------------')
        print('--end--a--pull request--', pr_num)

        # this is for the github.GithubException.RateLimitExceededException: 403
    except RateLimitExceededException:
        search_rate_limit = g.get_rate_limit().search
        print('search remaining', format(search_rate_limit.remaining))
        reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
        # add 10 seconds to be sure the rate limit has been reset
        sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10
        time.sleep(sleep_time)
        return current_line
    except Exception as ex:
        print('!!!!!!!!!!!!!!!there are exceptions!')
        traceback.print_exc()
        return current_line + 1
    return current_line + 1



# # write_header_to_csv()
# repo_pr_data_frame = pd.read_csv(repo_pr_file_name)
# total_repo_pr_amount = len(repo_pr_data_frame)
# current_line = 0
# while current_line < total_repo_pr_amount:
#     error_at = crawl_comment(current_line, repo_pr_data_frame)
#     current_line = error_at





def crawl_bug_reports_from_repo(repo_name):
    print('--current repo is-------', repo_name)

    try:
        search_string = 'repo:' + repo_name + ' is:issue is:closed refactoring OR refactor'
        # print(search_string)

        target_issues = g.search_issues(search_string)

        print('total searched issues number is ', target_issues.totalCount)

        # create a dict to save data
        checkDict = {}

        for each_issue in target_issues:
            html_url = each_issue.html_url
            title = each_issue.title
            state = each_issue.state
            created_at = each_issue.created_at
            closed_at = each_issue.closed_at


            dict_key = str(html_url)

            print('------combined_key------', dict_key)
            # if it is not in the checkDict, put it into checkDict
            if checkDict.get(dict_key) == None:
                issue_content = {}
                issue_content['html_url'] = html_url
                issue_content['title'] = title
                issue_content['state'] = state
                issue_content['created_at'] = created_at
                issue_content['closed_at'] = closed_at

                checkDict[dict_key] = issue_content
            else:
                continue

        file_name = str(repo_name).split('/')[-1] + '_refactoring_bug_reports.csv'

        print('file_name is ', file_name)

        # write header to csv file
        write_header_to_csv(file_name)

        with open(file_name, 'a+', encoding='utf-8', newline='') as file:
            print(file_name, ' opened')
            writer = csv.writer(file)

            data_list = []
            for key in checkDict.keys():
                one_data_list = []
                value = checkDict.get(key)
                one_data_list.append(str(value.get('html_url')))
                one_data_list.append(str(value.get('title')))
                one_data_list.append(str(value.get('state')))
                one_data_list.append(str(value.get('created_at')))
                one_data_list.append(str(value.get('closed_at')))

                data_list.append(one_data_list)
            print('---data_list--', data_list)
            # write the data of one pull request to csv file
            writer.writerows(data_list)
            print(file_name, ' written')

        print('-------------------------------------')
    # this is for the github.GithubException.RateLimitExceededException: 403
    except RateLimitExceededException:
        search_rate_limit = g.get_rate_limit().search
        print('search remaining', format(search_rate_limit.remaining))
        reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
        # add 10 seconds to be sure the rate limit has been reset
        sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10
        time.sleep(sleep_time)
    except Exception:
        print('!!!!!!!!!!!!!!!there are exceptions!')
        traceback.print_exc()



repo_list = ["eclipse-jdt/eclipse.jdt.ui"]


for repo_name in repo_list:
    crawl_bug_reports_from_repo(repo_name)