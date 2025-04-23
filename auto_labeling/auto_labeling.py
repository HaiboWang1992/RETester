import json
from openai import OpenAI
import re
import csv
import traceback
import pandas as pd
from datetime import datetime
from collections import defaultdict
import os
import random

client = OpenAI(api_key="")
model_type = "gpt-4o-mini"
gpt_folder_name = "4o_mini"


def write_method_list_into_txt(file_path, data_list):
    with open(file_path, 'w', encoding='utf-8') as f:
        for method_str in data_list:
            f.write(str(method_str).strip())
            f.write('\n')
    f.close()


def remove_huanhang(original_method):
    original_method_str = str(original_method).strip()
    splited_original_method_str = original_method_str.split('\n')
    new_str = ''
    for line in splited_original_method_str:
        line = line.strip()
        new_str = new_str + line + ' '

    return new_str.strip()

def write_raw_methods_into_txt(target_file_path, method_data_list):
    method_data_list_after_remove_huanhang = []
    total_data_len = len(method_data_list)
    total_index_list = range(total_data_len)

    for filter_item_id in total_index_list:
        method_data_list_after_remove_huanhang.append(remove_huanhang(str(method_data_list[filter_item_id])))

    write_method_list_into_txt(target_file_path, method_data_list_after_remove_huanhang)


def get_target_list_from_txt(file_path):
    f = open(file_path, "r", encoding="utf-8")
    lines = f.readlines()
    str_list = []

    for line in lines:
        line_str = str(line).strip()
        if len(line_str) != 0:
            str_list.append(line_str)

    return str_list



def send_request_to_gpt(request_string):
    completion = client.chat.completions.create(
        model=model_type,
        messages=[
            {"role": "user", "content": request_string}
        ]
    )

    response_content = completion.choices[0].message.content.strip()
    print(response_content)
    return response_content



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




def send_extract_request_to_gpt(messages_list):
    completion = client.chat.completions.create(
        model=model_type,
        messages=messages_list
    )

    response_content = completion.choices[0].message.content.strip()
    print('response_content')
    print(response_content)
    return response_content


def write_data_list_into_txt(file_path, data_list):
    with open(file_path, 'w', encoding='utf-8') as f:
        for method_str in data_list:
            f.write(json.dumps(method_str))
            f.write('\n')
    f.close()


def get_data_from_txt(file_path):
    json_list = []
    with open(file_path, 'r', encoding="utf-8") as f:
        for jsonstr in f.readlines():
            json_list.append(json.loads(jsonstr))

    return json_list



def build_extraction_prompt():
    # Define the first and last multi-line strings
    first_string = """
    You are a software testing expert. I will give you some historical bug
    reports for the refactoring engines. You need to extract the following
    information from the bug reports:
    1. Refactoring type;
    2. Bug symptom;
    3. Input program characteristic.
    The following are examples:
    """

    last_string = """You should only give me the extracted information in json format, not any natural language. Just give me the json, nothing else. Don't include any ```json or ``` to surround with the extracted json."""

    # Define the directory where the text files are stored
    directory = "source/few_shot_example/"  # Change this to your actual directory

    # Read the contents of the ten text files
    middle_strings = []
    for i in range(1, 12):  # Assuming the files are named 1.txt, 2.txt, ..., 10.txt
        file_path = os.path.join(directory, f"example_{i}.txt")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                middle_strings.append(file.read().strip())  # Read and strip any extra spaces

    # Concatenate all parts together
    final_string = first_string + "\n".join(middle_strings) + "\n" + last_string

    # # Print or use the final string
    # print(final_string)

    return final_string


def parse_extracted_information(extracted_information_str):
    print('parse_extracted_information')
    try:
        # Parse the 'response_content' from string to dictionary
        extracted_content = json.loads(extracted_information_str, strict=False)

        # Extract the 'classes' list
        RefactoringType = extracted_content["RefactoringType"]
        Symptom = extracted_content["Symptom"]
        InputProgramCharacteristic = extracted_content["InputProgramCharacteristic"]

        return RefactoringType, Symptom, InputProgramCharacteristic
    except:
        traceback.print_exc()
        return "", "", ""



def build_labeling_pipeline(current_bug_report_content):
    extraction_start_time = datetime.now()
    refactoring_information_extraction_prompt = build_extraction_prompt()
    # Create a conversation with a system message followed by the first user message
    completion1 = client.chat.completions.create(
        model=model_type,
        messages=[
            {"role": "system", "content": refactoring_information_extraction_prompt},
            {"role": "user", "content": current_bug_report_content}
        ]
    )

    # Get response to the first message
    extracted_information = completion1.choices[0].message.content.strip()

    extraction_end_time = datetime.now()

    extraction_time = extraction_end_time - extraction_start_time

    print('---------------extracted_information----------------------')
    print(extracted_information)
    print('---------------extracted_information----------------------')


    print('-----------------extraction_time--------------------')
    print(extraction_time)
    print('-----------------extraction_time--------------------')


    return extracted_information, extraction_time



def get_unmatched_bug_report_content(target_html_url_list, matched_bug_report_file_path, total_data_list):
    with open(matched_bug_report_file_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader)  # This reads the first line which is the header
        # Read each row after the header
        for row in reader:
            current_html_url = str(row[0])
            if current_html_url not in target_html_url_list:
                current_dict = {}
                current_dict["html_url"] = current_html_url
                current_dict["bug_report_content_text"] = str(row[-1])
                total_data_list.append(current_dict)


def get_bug_report_information(sampled_bug_report_file_path, eclipse_github_content_file_path, eclipse_bugzilla_content_file_path, idea_content_file_path):
    sampled_bug_list = get_data_from_txt(sampled_bug_report_file_path)
    sampled_bug_html_url_list = []
    for sampled_bug in sampled_bug_list:
        sampled_bug_html_url_list.append(sampled_bug["html_url"])

    total_data_list = []

    get_unmatched_bug_report_content(sampled_bug_html_url_list, eclipse_github_content_file_path, total_data_list)
    get_unmatched_bug_report_content(sampled_bug_html_url_list, eclipse_bugzilla_content_file_path, total_data_list)
    get_unmatched_bug_report_content(sampled_bug_html_url_list, idea_content_file_path, total_data_list)

    return total_data_list



def execute_pipeline(target_result_file_path, sampled_bug_report_list):
    total_result_list = []
    total_count = len(sampled_bug_report_list)
    for current_bug_report_index, current_bug_report in enumerate(sampled_bug_report_list):
        current_bug_report_html_url = current_bug_report["html_url"]
        print('start---current_bug_report_index---', current_bug_report_index, '---total_count---', total_count, '---current_bug_report_html_url---', current_bug_report_html_url)
        extracted_information, extraction_time = build_labeling_pipeline(current_bug_report["bug_report_content_text"])
        each_iteration_dict = {}
        each_iteration_dict["html_url"] = current_bug_report_html_url
        each_iteration_dict["extracted_information"] = extracted_information
        each_iteration_dict["extraction_time"] = str(extraction_time)

        total_result_list.append(each_iteration_dict)
        print('end---current_bug_report_index---', current_bug_report_index, '---total_count---', total_count, '---current_bug_report_html_url---', current_bug_report_html_url)

    write_data_list_into_txt(target_result_file_path, total_result_list)




def setup_execute_pipeline():
    sampled_few_shot_bug_report_file_path = 'source/few_shot_learning_sampled_bug_reports.txt'
    eclipse_github_content_file_path = 'source/source_with_content/eclipse_github.csv'
    eclipse_bugzilla_content_file_path = 'source/source_with_content/eclipse_bugzilla.csv'
    idea_content_file_path = 'source/source_with_content/idea.csv'
    other_bug_report_list = get_bug_report_information(sampled_few_shot_bug_report_file_path, eclipse_github_content_file_path, eclipse_bugzilla_content_file_path, idea_content_file_path)

    target_result_file_path = 'target/labeling_result.txt'

    execute_pipeline(target_result_file_path, other_bug_report_list)



# setup_execute_pipeline()






def get_random_sampled_response(original_file_path, random_sampled_response_file_path, sample_size = 100):
    parsed_list = get_data_from_txt(original_file_path)
    random_sampled_list = random.sample(parsed_list, sample_size)
    write_data_list_into_txt(random_sampled_response_file_path, random_sampled_list)
    print('random sample finished')


def test_get_random_sampled_response():
    original_file_path = 'target/labeling_result.txt'
    random_sampled_response_file_path = 'target/random_sampled_labeling_result.txt'
    get_random_sampled_response(original_file_path, random_sampled_response_file_path, sample_size=100)


# test_get_random_sampled_response()



def test_parse_results():
    result_list = get_data_from_txt('target/random_sampled_labeling_result.txt')
    for each_item in result_list:
        print("html_url: ", each_item["html_url"])

        extracted_content = json.loads(each_item["extracted_information"], strict=False)
        print("RefactoringType: ", extracted_content["RefactoringType"])
        print("Symptom: ", extracted_content["Symptom"])
        print("InputProgramCharacteristic: ", extracted_content["InputProgramCharacteristic"])

        print("extraction_time: ", each_item["extraction_time"])

# test_parse_results()


def start_calculate_total_time(result_list):
    extraction_time_list = []
    for each_item in result_list:
        extraction_time = each_item["extraction_time"]
        extraction_time_list.append(extraction_time)

    total_extraction_time = pd.to_timedelta(extraction_time_list).sum()
    average_extraction_time = pd.to_timedelta(extraction_time_list).mean()
    print('total_extraction_time: ', total_extraction_time)
    print('average_extraction_time: ', average_extraction_time)


def test_start_calculate_total_time():
    target_file_path = 'target/random_sampled_labeling_result.txt'
    result_list = get_data_from_txt(target_file_path)
    start_calculate_total_time(result_list)

# test_start_calculate_total_time()

def write_repo_pr_to_csv(list_contains_dict, result_file_path):
    # Writing to CSV file
    with open(result_file_path, mode="w", newline="") as file:
        # Get the field names from the keys of the first dictionary
        fieldnames = list_contains_dict[0].keys()
        # Create a writer object
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Write the header
        writer.writeheader()
        # Write the data
        writer.writerows(list_contains_dict)

    print(f"CSV file '{result_file_path}' has been created successfully.")



def merge_compilable_with_meta_information(target_file_path,
                                          eclipse_bugzilla_meta_information_csv_file_path,
                                          eclipse_github_meta_information_csv_file_path,
                                          idea_meta_information_csv_file_path, result_file_path):
    target_data_list = get_data_from_txt(target_file_path)

    overall_result_list = []

    for each_item_index, each_item in enumerate(target_data_list):
        target_item = {}
        target_html_url = each_item["html_url"]
        target_item["html_url"] = target_html_url

        extracted_content = json.loads(each_item["extracted_information"], strict=False)
        target_item["extracted_refactoring_type"] =  extracted_content["RefactoringType"]
        target_item["extracted_symptom"] = extracted_content["Symptom"]
        target_item["extracted_input_program_characteristic"] = extracted_content["InputProgramCharacteristic"]

        is_found = False

        with open(eclipse_bugzilla_meta_information_csv_file_path, newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            # Read each row after the header
            for row in reader:
                if row.get("html_url") == target_html_url:
                    target_item["ground_refactoring_type"] = row.get("refactoring type")
                    target_item["ground_symptom"] = row.get("symptom")
                    target_item["ground_input_program_characteristic"] = row.get("input property")
                    overall_result_list.append(target_item)
                    is_found = True
                    break

        if is_found:
            continue

        with open(eclipse_github_meta_information_csv_file_path, newline='', encoding="utf-8") as csvfile1:
            reader1 = csv.DictReader(csvfile1)
            # Read each row after the header
            for row1 in reader1:
                if target_html_url == row1.get("html_url"):
                    target_item["ground_refactoring_type"] = row1.get("refactoring type")
                    target_item["ground_symptom"] = row1.get("symptom")
                    target_item["ground_input_program_characteristic"] = row1.get("input property")
                    overall_result_list.append(target_item)
                    is_found = True
                    break

        if is_found:
            continue

        with open(idea_meta_information_csv_file_path, newline='', encoding="utf-8") as csvfile2:
            reader2 = csv.DictReader(csvfile2)
            for row2 in reader2:
                if target_html_url == row2.get("html_url"):
                    target_item["ground_refactoring_type"] = row2.get("refactoring type")
                    target_item["ground_symptom"] = row2.get("symptom")
                    target_item["ground_input_program_characteristic"] = row2.get("input property")
                    overall_result_list.append(target_item)
                    break

    # Writing to CSV file
    write_repo_pr_to_csv(overall_result_list, result_file_path)

def test_merge_compilable_with_meta_information():
    eclipse_bugzilla_meta_information_csv_file_path = "source/Eclipse_bug_reports_from_bugzilla.csv"
    eclipse_github_meta_information_csv_file_path = "source/Eclipse_bug_reports_from_github.csv"
    idea_meta_information_csv_file_path = "source/IDEA_bug_reports.csv"

    original_file_path = 'target/labeling_result.txt'
    random_sampled_response_file_path = 'target/random_sampled_labeling_result.txt'
    get_random_sampled_response(original_file_path, random_sampled_response_file_path, sample_size=100)

    result_file_path = "target/sampled_data_with_ground_truth.csv"
    merge_compilable_with_meta_information(random_sampled_response_file_path,
                                          eclipse_bugzilla_meta_information_csv_file_path,
                                          eclipse_github_meta_information_csv_file_path,
                                          idea_meta_information_csv_file_path, result_file_path)

# test_merge_compilable_with_meta_information()

