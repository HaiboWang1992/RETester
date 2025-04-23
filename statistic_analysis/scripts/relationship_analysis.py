import json
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

cwd = os.getcwd()


def extract_and_merge_data(directory, level1, level2):
    all_data = []
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            # Load the CSV file
            file_path = os.path.join(directory, filename)
            data = pd.read_csv(file_path)

            # Filter columns and check for non-empty "root cause"
            if {'html_url', 'symptom', 'input property', 'refactoring type', 'root cause'}.issubset(data.columns):
                filtered_data = data[['html_url', 'symptom', 'input property', 'refactoring type', 'root cause']]
                if level1 == 'input property' or level2 == 'input property':
                    filtered_data = filtered_data[filtered_data['input property'].notna() & (filtered_data['input property'] != '')]
                if level1 == 'root cause' or level2 == 'root cause':
                    filtered_data = filtered_data[filtered_data['root cause'].notna() & (filtered_data['root cause'] != '')]

                # Append to list if there are any valid rows
                if not filtered_data.empty:
                    all_data.append(filtered_data)

    # Merge all data into one DataFrame
    if all_data:
        merged_data = pd.concat(all_data, ignore_index=True)
    else:
        merged_data = pd.DataFrame()

    return merged_data


def run_chi_squared_test(data, level1, level2):
    # Create a contingency table
    contingency_table = pd.crosstab(data[level1], data[level2])

    # Perform the Chi-squared test
    chi2, p, dof, expected = stats.chi2_contingency(contingency_table)

    print("Chi-squared test results:")
    print("Chi-squared statistic:", chi2)
    print("p-value:", p)
    print("Degrees of freedom:", dof)

    # Check if we reject the null hypothesis
    if p < 0.05:
        print("Variables are related.")
        return contingency_table
    else:
        print("Variables are not related.")
        return None


def post_hoc_chi_squared(data, col1, col2):
    unique_col1 = data[col1].dropna().unique()
    unique_col2 = data[col2].dropna().unique()
    results = []

    # Iterate over all pairs of category values
    for value1 in unique_col1:
        for value2 in unique_col2:
            # Construct a contingency table for the current pair
            observed = pd.crosstab(data[col1] == value1, data[col2] == value2)
            chi2, p, dof, _ = stats.chi2_contingency(observed, correction=False)

            # Store the results
            results.append(((value1, value2), p))

    # Adjust p-values for multiple testing using Bonferroni correction
    p_values = [p for _, p in results]
    reject, corrected_p_values, _, _ = multipletests(p_values, alpha=0.05, method='bonferroni')

    # Collect significant results
    significant_results = []
    for ((value1, value2), p), corrected_p, is_significant in zip(results, corrected_p_values, reject):
        if is_significant:
            significant_results.append((value1, value2, corrected_p))

    return significant_results


def perform_chi_squared_test_and_post_hoc_analysis():
    directory_path = 'source/'
    # replace the following two category names with the target category pair to be analyzed
    level1 = 'input property'
    level2 = 'symptom'
    data = extract_and_merge_data(directory_path, level1, level2)
    contingency_table = run_chi_squared_test(data, level1, level2)
    if contingency_table is not None:
        significant_relationships = post_hoc_chi_squared(data, level1, level2)

        # Output significant pairs
        for relation in significant_relationships:
            print(
                f"({relation[0]}, {relation[1]}) p-value: {relation[2]}")


perform_chi_squared_test_and_post_hoc_analysis()






