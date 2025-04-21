from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import csv
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd


def get_issue_detailed_content_from_url(driver, issue_url):
    if issue_url is None or len(issue_url) == 0:
        return ""
    try:

        # Wait until the page is fully loaded
        try:
            driver.get(issue_url)
            # Waiting for the presence of an element on the page
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'ring-ui-headingWrapperButton_d0d1'))
            WebDriverWait(driver, 5).until(element_present)
        except TimeoutException:
            print("Loading took too much time!")

        page = BeautifulSoup(driver.page_source, 'html.parser')
        title_button = page.find("h1", {'class': 'ring-ui-heading_d601'})
        title_text = title_button.get_text().strip()

        overall_text = title_text + "\n"

        comment_div = page.find("div", {'class': 'description__e030'})

        current_comment_text = comment_div.get_text().strip()

        overall_text = overall_text + current_comment_text + "\n"

        print('---overall_text---')
        print(overall_text.replace("Plain text", " ").replace("Java detected", " ").replace("C detected", " ").replace("C# detected", " ").replace("C++ detected", " ").replace("Java stack trace detected", " "))
    except Exception:
        overall_text = ""
        print('exception happens during test.')
        traceback.print_exc()

    return overall_text.replace("Plain text", " ").replace("Java detected", " ").replace("C detected", " ").replace("C# detected", " ").replace("C++ detected", " ").replace("Java stack trace detected", " ")




def crawl_detailed_information():


    issue_url_list = ['https://youtrack.jetbrains.com/issue/IDEA-362804/Pull-Members-Up-with-Lambda-Accessing-Super-Methods-produces-red-code']
    result = []
    for issue_url in issue_url_list:
        service = Service(executable_path='./geckodriver.exe')
        options = webdriver.FirefoxOptions()
        driver = webdriver.Firefox(service=service, options=options)
        get_issue_detailed_content_from_url(driver, issue_url)

    return result

# crawl_detailed_information()




def save_static_tools_content_into_csv():
    crawled_list = []
    # crawled_list.extend(crawl_bugs())

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



def get_issue_content(manual_analysis_file_path):
    manual_result_dataframe = pd.read_csv(manual_analysis_file_path, encoding='unicode_escape')
    service = Service(executable_path='./geckodriver.exe')
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=service, options=options)

    header = ['html_url', 'priority', 'type', 'state', 'subsystem', 'created_date', 'has_input_program',
              'input property', 'symptom', 'refactoring_type', 'commit_html_url', 'root_cause', 'content_text']
    target_file_path = 'target_data/idea.csv'

    total_issue_list = []
    for row_index, row_dict in manual_result_dataframe.iterrows():
        html_url = row_dict["url"]
        content_text = get_issue_detailed_content_from_url(driver, html_url)

        one_file_item = []
        one_file_item.append(html_url)
        one_file_item.append(str(row_dict["priority"]))
        one_file_item.append(str(row_dict["type"]))
        one_file_item.append(str(row_dict["state"]))
        one_file_item.append(str(row_dict["subsystem"]))

        one_file_item.append(str(row_dict["created date"]))
        one_file_item.append(str(row_dict["input program"]))
        one_file_item.append(str(row_dict["input property"]))
        one_file_item.append(str(row_dict["symptoms"]))
        one_file_item.append(str(row_dict["refactoring type"]))
        one_file_item.append(str(row_dict["commit_html_url"]))
        one_file_item.append(str(row_dict["root cause"]))
        one_file_item.append(content_text)

        # append this review to the list
        total_issue_list.append(one_file_item)



        print('-------------row_index---------------', str(row_index))

    save_data_into_csv_file(header, total_issue_list, target_file_path)

get_issue_content("source_data/IDEA_bug_reports.csv")