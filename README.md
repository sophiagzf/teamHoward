# Team Howard: College Scorecard and IPEDS Data
Instructions for how to use our data pipeline. First, to load and update College Scorecard data supplemented by IPEDS data, and second to generate a financial report given year.

### Required Directory Structure
'data' folder
'reports' folder 
in the same directory as create_report.ipynb, database_schema.ipynb, load_data.py, and credentials.py.

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

### Example:

"MERGED2018_19_PP.csv" contains the College Scorecard data for 2019.

"hd2019.csv" contains the IPEDS data for 2019.

### 3. Create the SQL table: institutions
This step will only need to be completed once and if you drop the institutions table in your SQL database.
Make sure you have the 'institutions' table created in your SQL database.
The code for creating the table is in database-schema.ipynb. Run the two code chunks to create the SQL table and proper datatypes required for the institutions table.

### 4. Insert data into the SQL database.
Make sure you have the following Python libraries loaded: 
pandas, re, argparse, os, psycopg2, numpy

### Run the following command: 

python load_data.py {COLLEGE SCORECARD FILEPATH} {IPEDS FILEPATH}

It is important that you run the command with the College Scorecard filepath BEFORE the IPEDS filepath. Also, it is important that you run the command with data from the same year.

### Example: 

python load_data.py data/MERGED2018_19_PP.csv data/hd2019.csv

The above command will load 2019 College Scorecard and IPEDS data into the SQL database 'institutions' table.

Congrats! Your data should be loaded into the SQL database!

## How to Generate the Report
Please make sure you have the credentials.py file filled out from part 1 of loading the SQL database.

Please make sure you have the following Python libraries:
pandas, papermill, nbconvert, jupyter, plotly, IPython.display

Some interactive plots in the report are generated and called in to the larger report file. Please make sure you have a 'reports' folder in the same directory as create_report.ipynb.

### There are two command line files to run:

papermill create_report.ipynb create_report.ipynb -p YEAR {YEAR FOR REPORT}

jupyter nbconvert --to html create_report.ipynb --output reports/report_{YEAR FOR REPORT}.html --no-input

### Example:
papermill create_report.ipynb create_report.ipynb -p YEAR 2022

jupyter nbconvert --to html create_report.ipynb --output reports/report_2022.html --no-input

The above commands will create the data report with information from 2022 College Scorecard and IPEDS data along with visualizations to see change over time for all years in your database before and including 2022.

Please make sure to rename the html file in the second command to the year that the report came from! The reports folder is in the gitignore. 

### Converting the Report to PDF

From the html file, you can download it as a pdf by opening the html file in a web browser, such as Chrome, and selecting 'Save to PDF' when you print the page. When you export the html as a pdf this way, make sure to click 'More Settings' and set 'Scale' value to 'Custom'. Here, use 85 instead of 100. This will ensure that plots are properly sized and no legends are cut off.
