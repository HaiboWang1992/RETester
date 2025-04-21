from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import csv
import traceback
import pandas as pd
import re
from collections import defaultdict
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException


def get_bug_content_from_page(driver, pmd_html_url):
    if pmd_html_url is None or len(pmd_html_url) == 0:
        return []
    try:
        driver.get(pmd_html_url)
        page = BeautifulSoup(driver.page_source, 'html.parser')

        total_data_list = []

        target_table = page.find("table", {'class': 'bz_buglist'})
        for i, row in enumerate(target_table.find_all('tr')):
            if i == 0:
                header = [el.text.strip() for el in row.find_all('th')]
            else:

                importance = str(row["class"][2]).strip().split('_')[1]
                id = row.find('td', attrs={'class':'first-child bz_id_column'})
                product = row.find('td', attrs={'class': 'bz_product_column nowrap'})
                component = row.find('td', attrs={'class': 'bz_component_column nowrap'})
                assignee = row.find('td', attrs={'class': 'bz_assigned_to_column nowrap'})
                status = row.find('td', attrs={'class': 'bz_bug_status_column nowrap'})
                resolution = row.find('td', attrs={'class': 'bz_resolution_column nowrap'})
                summary = row.find('td', attrs={'class': 'bz_short_desc_column'})
                changeddate = row.find('td', attrs={'class': 'bz_changeddate_column nowrap'})

                id_link = "https://bugs.eclipse.org/bugs/" + id.find("a").get("href")
                id_number = id.find("a").get_text().strip()
                product_name = product.find("span").get_text().strip()
                component_name = component.find("span").get_text().strip()
                assignee_name = assignee.find("span").get_text().strip()
                status_text = status.find("span").get_text().strip()
                resolution_text = resolution.find("span").get_text().strip()
                summary_text = summary.find("a").get_text().strip()
                changeddate_text = changeddate.get_text().strip()

                item_dict = {}
                item_dict['html_url'] = id_link
                item_dict['id_number'] = id_number
                item_dict['importance'] = importance
                item_dict['product'] = product_name
                item_dict['component'] = component_name
                item_dict['assignee'] = assignee_name
                item_dict['status'] = status_text
                item_dict['resolution'] = resolution_text
                item_dict['summary'] = summary_text
                item_dict['changeddate'] = changeddate_text

                total_data_list.append(item_dict)
    except Exception as ex:
        total_data_list = []
        print('exception happens during test.')
        traceback.print_exc()
    for index, item in enumerate(total_data_list):
        print('!!!!------index-------', index)
        print('!!!------html_url-------', item.get('html_url'))
        print('------id_number-------', item.get('id_number'))
        print('------importance-------', item.get('importance'))
        print('------product-------', item.get('product'))
        print('------component-------', item.get('component'))
        print('------assignee-------', item.get('assignee'))
        print('------status-------', item.get('status'))
        print('------resolution-------', item.get('resolution'))
        print('------summary-------', item.get('summary'))
        print('------changeddate-------', item.get('changeddate'))
        print('!!!!------index-------', index)

    return total_data_list


def crawl_bugs():
    service = Service(executable_path='./geckodriver.exe')
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=service, options=options)

    pmd_url_list = ['https://bugs.eclipse.org/bugs/buglist.cgi?classification=Eclipse%20Project&limit=0&order=changeddate%20DESC%2Cbug_id&product=JDT&query_format=advanced&resolution=FIXED&short_desc=refactoring%20refactor&short_desc_type=anywordssubstr']
    result = []
    for pmd_url in pmd_url_list:
        result.extend(get_bug_content_from_page(driver, pmd_url))

    return result

# crawl_bugs()


def get_issue_detailed_content_from_github_url(driver, issue_url):
    if issue_url is None or len(issue_url) == 0:
        return ""
    try:
        # Wait until the page is fully loaded
        try:
            driver.get(issue_url)
            # Waiting for the presence of an element on the page
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'ring-ui-headingWrapperButton_d0d1'))
            WebDriverWait(driver, 3).until(element_present)
        except TimeoutException:
            print("Loading took too much time!")

        page = BeautifulSoup(driver.page_source, 'html.parser')

        title_h1 = page.find("h1", {'class': 'gh-header-title'})
        title_text = title_h1.find("bdi", {'class': 'js-issue-title'}).get_text().strip()
        title_issue_no = title_h1.find("span", {'class': 'f1-light'}).get_text().strip()

        overall_text = title_text + " " + title_issue_no + "\n"

        comment_div_list = page.find_all("div", {'class': 'edit-comment-hide'})
        for current_comment_index, comment_div in enumerate(comment_div_list):
            comment_body_td = comment_div.find("td", {'class': 'd-block'})
            current_comment_text = comment_body_td.get_text().strip()

            overall_text = overall_text + current_comment_text + "\n"

        print('---overall_text---')
        print(overall_text)
    except Exception:
        overall_text = ""
        print('exception happens during test.')
        traceback.print_exc()

    return overall_text



def get_issue_detailed_content_from_bugzilla_url(driver, issue_url):
    if issue_url is None or len(issue_url) == 0:
        return ""
    try:
        # Wait until the page is fully loaded
        try:
            driver.get(issue_url)
            # Waiting for the presence of an element on the page
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'ring-ui-headingWrapperButton_d0d1'))
            WebDriverWait(driver, 3).until(element_present)
        except TimeoutException:
            print("Loading took too much time!")


        page = BeautifulSoup(driver.page_source, 'html.parser')

        summary_div = page.find("div", {'class': 'bz_short_desc_container'})
        summary_a_text = summary_div.find("a").get_text().strip()
        summary_short_sum = summary_div.find("span").get_text().strip()

        overall_text = summary_a_text + " " + summary_short_sum + "\n"

        comment_div_list = page.find_all("div", {'class': 'bz_comment'})
        for current_comment_index, comment_div in enumerate(comment_div_list):
            if current_comment_index == 0:
                comment_head_div_class_name = 'bz_first_comment_head'
            else:
                comment_head_div_class_name = 'bz_comment_head'
            current_comment_head = comment_div.find("div", {'class': comment_head_div_class_name})

            current_comment_head_user = current_comment_head.find("span", {'class': 'bz_comment_user'}).get_text().strip()
            current_comment_head_time = current_comment_head.find("span", {'class': 'bz_comment_time'}).get_text().strip()

            current_comment_text = comment_div.find("pre", {'class': 'bz_comment_text'}).get_text().strip()

            overall_text = overall_text + current_comment_head_user + " " + current_comment_head_time + "\n" + current_comment_text + "\n"

        print(overall_text)
    except Exception:
        overall_text = ""
        print('exception happens during test.')
        traceback.print_exc()

    return overall_text




def save_static_tools_content_into_csv():
    crawled_list = []
    crawled_list.extend(crawl_bugs())

    result_list = []
    for content_item in crawled_list:
        # setup one review item's value
        one_file_item = []
        one_file_item.append(str(content_item.get('html_url')))
        one_file_item.append(str(content_item.get('id_number')))
        one_file_item.append(str(content_item.get('importance')))
        one_file_item.append(str(content_item.get('product')))
        one_file_item.append(str(content_item.get('component')))
        one_file_item.append(str(content_item.get('assignee')))
        one_file_item.append(str(content_item.get('status')))
        one_file_item.append(str(content_item.get('resolution')))
        one_file_item.append(str(content_item.get('summary')))
        one_file_item.append(str(content_item.get('changeddate')))
        # append this review to the list
        result_list.append(one_file_item)

    print('---len of result_list---', len(result_list))
    with open('static_tools_content_with_code_example.csv', 'w+', encoding='utf-8', newline='') as file:
        print('static_tools_content.csv opened')
        writer = csv.writer(file)
        header = ['html_url', 'id_number', 'importance', 'product', 'component', 'assignee', 'status', 'resolution', 'summary', 'changeddate']
        # write csv head
        writer.writerow(header)
        # write the review data to csv file
        writer.writerows(result_list)
        print('static_tools_content.csv written')


# save_static_tools_content_into_csv()

def save_data_into_csv_file(header, result_list, file_path):
    try:
        with open(file_path, 'w+', encoding='utf-8', newline='') as file:
            print('static_tools_content.csv opened')
            writer = csv.writer(file)
            # write csv head
            writer.writerow(header)
            # write the review data to csv file
            writer.writerows(result_list)
            print('static_tools_content.csv written')
    except Exception:
        print('exception happens during test.')
        traceback.print_exc()



def get_issue_content(bug_report_type, manual_analysis_file_path):
    manual_result_dataframe = pd.read_csv(manual_analysis_file_path, encoding='unicode_escape')
    service = Service(executable_path='./geckodriver.exe')
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=service, options=options)

    if bug_report_type == "bugzilla":
        header = ['html_url', 'id_number', 'importance', 'product', 'component', 'assignee', 'status', 'resolution',
                      'summary', 'changeddate','symptom', 'has_patch', 'has_input_program', 'input_program_property',
                      'refactoring_type', 'root_cause', 'content_text']
        target_file_path = 'target_data/eclipse_bugzilla.csv'
    else:
        header = ['html_url', 'title', 'state', 'created_at', 'closed_at', 'has_input', 'has_patch', 'refactoring_type',
                      'symptom', 'input_program_property', 'root_cause', 'content_text']
        target_file_path = 'target_data/eclipse_github.csv'

    total_issue_list = []
    for row_index, row_dict in manual_result_dataframe.iterrows():
        if bug_report_type == "bugzilla":
            html_url = row_dict["html_url"]
            content_text = get_issue_detailed_content_from_bugzilla_url(driver, html_url)

            one_file_item = []
            one_file_item.append(html_url)
            one_file_item.append(str(row_dict["id_number"]))
            one_file_item.append(str(row_dict["importance"]))
            one_file_item.append(str(row_dict["product"]))
            one_file_item.append(str(row_dict["component"]))
            one_file_item.append(str(row_dict["assignee"]))
            one_file_item.append(str(row_dict["status"]))
            one_file_item.append(str(row_dict["resolution"]))
            one_file_item.append(str(row_dict["summary"]))

            one_file_item.append(str(row_dict["changeddate"]))
            one_file_item.append(str(row_dict["symptom category"]))
            one_file_item.append(str(row_dict["author patch"]))
            one_file_item.append(str(row_dict["input program"]))
            one_file_item.append(str(row_dict["input property"]))
            one_file_item.append(str(row_dict["refactoring type"]))
            one_file_item.append(str(row_dict["root cause"]))
            one_file_item.append(content_text)

            # append this review to the list
            total_issue_list.append(one_file_item)

        else:
            html_url = row_dict["html_url"]
            content_text = get_issue_detailed_content_from_github_url(driver, html_url)

            one_file_item = []
            one_file_item.append(html_url)
            one_file_item.append(str(row_dict["title"]))
            one_file_item.append(str(row_dict["state"]))
            one_file_item.append(str(row_dict["created_at"]))
            one_file_item.append(str(row_dict["closed_at"]))
            one_file_item.append(str(row_dict["has_input"]))
            one_file_item.append(str(row_dict["has_patch"]))
            one_file_item.append(str(row_dict["refactoring type"]))
            one_file_item.append(str(row_dict["symptom category"]))

            one_file_item.append(str(row_dict["input property"]))
            one_file_item.append(str(row_dict["root cause"]))
            one_file_item.append(content_text)

            # append this review to the list
            total_issue_list.append(one_file_item)


        print('-------------row_index---------------', str(row_index))

    save_data_into_csv_file(header, total_issue_list, target_file_path)

get_issue_content("bugzilla", "source_data/Eclipse_bug_reports_from_bugzilla.csv")
get_issue_content("github", "source_data/Eclipse_bug_reports_from_github.csv")