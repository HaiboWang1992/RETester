from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import csv
import traceback



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

                id_link = "https://bz.apache.org/netbeans/" + id.find("a").get("href")
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

    pmd_url_list = ['https://bz.apache.org/netbeans/buglist.cgi?component=Refactoring&order=changeddate%20DESC%2Cbug_status%2Cpriority%2Cassigned_to%2Cbug_id&product=java&query_format=advanced&resolution=FIXED&short_desc=refactoring%20refactor&short_desc_type=anywordssubstr']
    result = []
    for pmd_url in pmd_url_list:
        result.extend(get_bug_content_from_page(driver, pmd_url))

    return result

# crawl_bugs()

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
    with open('netbeans_refactoring_bug_reports_from_bugzilla.csv', 'w+', encoding='utf-8', newline='') as file:
        print('static_tools_content.csv opened')
        writer = csv.writer(file)
        header = ['html_url', 'id_number', 'importance', 'product', 'component', 'assignee', 'status', 'resolution', 'summary', 'changeddate']
        # write csv head
        writer.writerow(header)
        # write the review data to csv file
        writer.writerows(result_list)
        print('static_tools_content.csv written')


save_static_tools_content_into_csv()