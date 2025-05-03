# Towards Understanding Refactoring Engine Bugs

### dataset
The dataset is in this folder. The corresponding raw data is in dataset/raw folder.
There are five files, each represents the bug reports from different refactoring tools and bug tracker systems.
1. Eclipse_bug_reports_from_bugzilla.csv: Eclipse refactoring bug reports from Bugzilla.
2. Eclipse_bug_reports_from_github.csv: Eclipse refactoring bug reports from GitHub.
3. IDEA_bug_reports.csv: IntelliJ IDEA refactoring bug reports from IntelliJ IDEA issue tracker.
4. Netbeans_bug_reports_from_bugzilla.csv: NetBeans refactoring bug reports from Bugzilla.
5. Netbeans_bug_reports_from_github.csv: NetBeans refactoring bug reports from GitHub.

### transferability_study
Bugs found by our transferability study (Section 5 in our paper) are in this folder.

### auto_labeling
The scripts for auto_labeling the bug reports using LLM.
- auto_labeling.py: the script for auto-labeling.
- source/few_shot_example: human constructed examples for few-shot-learning.
- target: evaluation dataset and labeling result.

### statistic_analysis
The scripts and results for the statistic analysis (RQ5).
Please read the readme.md in its folder for more detailed information.

### crawler
The scripts for the bug reports collection.


