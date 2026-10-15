DATA CLASSIFICATION FRAMEWORK FOR AI/ML PROJECTS
====================================================

A fully offline Python + Pandas + Tkinter microproject.

WHAT IS INCLUDED
----------------
main.py
    Tkinter desktop application.

classifier.py
    Rule-based sensitivity scoring and classification engine.

datasets/
    Five intentionally different synthetic institutional datasets:
    1. public_institutional_data.csv
    2. academic_records.csv
    3. student_services.csv
    4. health_records.csv
    5. mixed_institutional_data.csv

reports/
    Empty folder for exported reports.

TECHNOLOGY
----------
Python
Pandas
Tkinter
Matplotlib
OpenPyXL

INSTALLATION
------------
pip install -r requirements.txt

RUN
---
python main.py

CLASSIFICATION LEVELS
---------------------
Public               : 0-25
Internal             : 26-50
Confidential         : 51-75
Highly Confidential  : 76-100

HOW IT WORKS
------------
1. User selects a CSV file.
2. Pandas reads the dataset.
3. The classifier examines each column.
4. Column names are compared against sensitivity rules.
5. Simple value-pattern checks detect emails and phone numbers.
6. A sensitivity score is assigned.
7. The column receives a classification.
8. A recommended usage level is generated.
9. Tkinter displays the results and a classification-distribution graph.
10. The report can be exported to Excel or CSV.

WHY THE DATASETS ARE DIFFERENT
------------------------------
The datasets deliberately have different schemas and purposes.

Public institutional data:
    General campus/program information.

Academic records:
    Marks, attendance, CGPA and academic performance.

Student services:
    Personal contact, scholarship, hostel and counselling information.

Health records:
    Medical conditions, medication and emergency contacts.

Mixed institutional data:
    Academic, personal, financial, health and placement information.

This allows the same classification framework to demonstrate
different sensitivity profiles across different institutional domains.

IMPORTANT
---------
All records are synthetic. No real student/institutional information is used.
The application is offline and does not require an API, database, cloud
service, or internet connection.
