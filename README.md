# Team Howard: College Scorecard and IPEDS Data
Instructions for how to use our data pipeline. First, to load and update College Scorecard data supplemented by IPEDS data, and second to generate a financial report given year.

## How to Load Data into SQL Database

### 1. Set your credentials.
Make a file called "credentials.py". Don't worry, this will not be pushed to Github. 
Populate the file with the following:

DBNAME = "your_dbname"

HOST = "your_host"

USERNAME = "your_username"

PASSWORD = "your_password"


### 2. Download data.
Download the data you want to run on your computer.

The College Scorecard data should start with "MERGED" and be a csv file. The IPEDS data should be a zip file. Unzip this file. Do not rename these files. They must provide the year somewhre in the file name.

Example:

"MERGED2018_19_PP.csv" contains the College Scorecard data for 2019.

"hd2019.csv" contains the IPEDS data for 2019.

### 3. Insert data into the SQL database.
Make sure you have the table created into your SQL database.
The code for creating the table is in database-schema.ipynb. Run the code chunks to create the SQL table if you have not already.

Make sure you have the following Python libraries loaded: 
pandas, re, argparse, os, psycopg, numpy

Run the following command: 

python load_data.py {COLLEGE SCORECARD FILEPATH} {IPEDS FILEPATH}

Example: 

python load_data.py data/MERGED2018_19_PP.csv data/hd2019.csv

Congrats! Your data should be loaded into the SQL database!

## How to Generate the Report
Please make sure you have the following Python libraries:
pandas, papermill, nbconvert

Please make sure you have the following OS libraries for converting the report to a html file:

MacTex (for macOS): https://tug.org/mactex/mactex-download.html

XeLaTeX (for Linux & Ubuntu): sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-plain-generic

Latex Project (for Windows): https://www.latex-project.org/get/ 

There are two command line files to run:

papermill create_report.ipynb create_report.ipynb -p YEAR {YEAR FOR REPORT} -k python3

jupyter nbconvert --to html create_report.ipynb --output reports/report_{YEAR FOR REPORT}.html

Please make sure to rename the html file in the second command to the year that the report came from! The reports folder is in the gitignore.