import pandas as pd
import re
import argparse
import os
from credentials import DBNAME, HOST, USERNAME, PASSWORD
# ^ see comments at the end in connection object creation
import psycopg

# Load raw csv files from the command line #
# Take in user input: one College Scorecard csv file (starts with 'MERGED') and
# one IPEDS data file (starts with 'hd')

# Run command:
# python3 load_data.py {COLLEGE SCORECARD FILEPATH} {IPEDS FILEPATH}
# python3 load_data.py data/MERGED2018_19_PP.csv data/hd2019.csv

file_name1 = None
file_name2 = None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get data files')
    parser.add_argument('college_scorecard',
                        nargs="?")
    parser.add_argument('ipeds',
                        nargs="?")

    args = parser.parse_args()

    # Save the filepath names for future use
    file_name1 = args.college_scorecard
    file_name2 = args.ipeds

# Format the filepath names so it is just the name of the file
file_name1 = os.path.basename(file_name1)
file_name2 = os.path.basename(file_name2)

# Merge raw csv files #

# College Scorecard
raw_scorecard = pd.read_csv(args.college_scorecard, low_memory=False)

# IPEDS
raw_ipeds = pd.read_csv(args.ipeds, encoding='cp1252', low_memory=False)

# Keep only the columns we want from College Scorecard data
scorecard = raw_scorecard.loc[:, ['OPEID', 'ACCREDAGENCY',
                                  'PREDDEG', 'HIGHDEG',
                                  'CONTROL', 'REGION', 'ADM_RATE',
                                  'CCBASIC', 'ADM_RATE', 'TUITIONFEE_IN',
                                  'TUITIONFEE_OUT',
                                  'TUITIONFEE_PROG', 'TUITFTE', 'AVGFACSAL',
                                  'CDR2', 'CDR3',
                                  'SAT_AVG', 'PCTFLOAN']]

# Keep only the columns we want from the IPEDS data
ipeds = raw_ipeds.loc[:, ['INSTNM', 'ADDR', 'ZIP', 'FIPS', 'CITY', 'STABBR',
                          'OPEID', 'CBSA', 'CSA', 'LONGITUD', 'LATITUDE']]

# Join the datasets together
data = pd.merge(scorecard, ipeds, on='OPEID', how='left')

# Clean the data #

# Rename columns
data = data.rename(columns={'OPEID': 'oepid',
                            'INSTNM': 'name',
                            'ADDR': 'address',
                            'STABBR': 'state',
                            'CITY': 'city',
                            'CCBASIC': 'ccbasic',
                            'LATITUDE': 'latitude',
                            'LONGITUD': 'longitude',
                            'FIPS': 'fips',
                            'REGION': 'region',
                            'CBSA': 'cbsa',
                            'CSA': 'csa',
                            'ACCREDAGENCY': 'accreditor',
                            'PREDDEG': 'pred_degree',
                            'HIGHDEG': 'highest_degree',
                            'CONTROL': 'control',
                            'ADM_RATE': 'admission_rate',
                            'TUITIONFEE_IN': 'in_state_tuit',
                            'TUITIONFEE_OUT': 'out_state_tuit',
                            'TUITIONFEE_PROG': 'prog_year_tuit',
                            'TUITFTE': 'revenue_tuit',
                            'AVGFACSAL': 'avg_faculty_salary',
                            'CDR2': 'two_yr_default',
                            'CDR3': 'three_yr_default',
                            'SAT_AVG': 'sat_avg',
                            'PCTFLOAN': 'prop_loan'})

# Combining the state and city together into address
data['address'] = data.apply(
    lambda row:
        f'{row["city"]}, {row["state"]} - {row["address"]}', axis=1)


def extract_year_from_filename(file_name):
    if 'MERGED' in file_name:
        match = re.search(r'\d{4}_\d{2}', file_name)
        if match:
            year_str = match.group().split('_')[1]
            year = int('20' + year_str)
            return year
    else:
        match = re.search(r'\d{4}', file_name)
        if match:
            year = int(match.group())
            return year
    return None


year1 = extract_year_from_filename(file_name1)
year2 = extract_year_from_filename(file_name2)

if year1:
    data['extracted_year'] = year1
elif year2:
    data['extracted_year'] = year2
else:
    print('Year not found in file name')

numeric_columns = ['opeid', 'ccbasic', 'latitude',
                   'longitude', 'fips', 'cbsa',
                   'csa', 'admission_rate',
                   'in_state_tuit', 'out_state_tuit',
                   'prog_year_tuit', 'revenue_tuit',
                   'avg_faculty_salary', 'two_yr_default',
                   'three_yr_default',
                   'sat_avg', 'prop_loan']

# Replace -999 with None in numeric columns
for col in numeric_columns:
    if col in data.columns:
        data[col] = data[col].replace(-999, None)

data['extracted_year'] = pd.to_datetime(
    data['extracted_year'].astype(str) + '-01-01')

# Mapping for degree
degree_mapping = {
    0: 'NA',
    1: 'Certificate',
    2: 'Associate',
    3: 'Bachelor',
    4: 'Graduate'
}

# Mapping for region (assuming you have a similar column)
region_mapping = {
    0: 'US Service',
    1: 'New England',
    2: 'Mid East',
    3: 'Great Lakes',
    4: 'Plains',
    5: 'Southeast',
    6: 'Southwest',
    7: 'Rocky Mountains',
    8: 'Far West',
    9: 'Outlying Areas'
}

# Mapping for ownership
ownership_mapping = {
    1: 'Public',
    2: 'Private Non-Profit',
    3: 'Private For-Profit'
}

# Apply the mappings
data['pred_degree'] = data['pred_degree'].map(degree_mapping)
data['highest_degree'] = data['highest_degree'].map(degree_mapping)
data['region'] = data['region'].map(region_mapping)
data['control'] = data['control'].map(ownership_mapping)

# Check the output
print(data.head())


# Push data to the SQL database #
# Connnect, create conn connection object
conn = psycopg.connect(
    host="pinniped.postgres.database.azure.com",
    # if the host name is the same, can't we just
    # include that in the README,
    # And then directly import the other variables
    # created in credentials.py like DBNAME, USERNAME,
    # into here?
    # Example:
    #  Connect to the database using parameters from credentials.py
    # conn = psycopg.connect(
    #       dbname=DBNAME,
    #       host=HOST,
    #       user=USERNAME,
    #       password=PASSWORD)
    dbname="yourusername",
    user="yourusername", 
    password="yourpassword"
)

# Create a cursor and use it to submit/execute a query:
cur = conn.cursor()

# SQL commands to create types and table
create_types = """
    CREATE TYPE degree AS ENUM(
        'NA','Certificate', 'Associate', 'Bachelor', 'Graduate');
    CREATE TYPE region_type AS ENUM(
        'US Service', 'New England', 'Mid East', 'Great Lakes',
        'Plains', 'Southeast', 'Southwest', 'Rocky Mountains',
        'Far West', 'Outlying Areas');
    CREATE TYPE ownership AS ENUM(
        'Public', 'Private Non-Profit', 'Private For-Profit');
"""

create_table = """
    CREATE TABLE institutions (
        opeid VARCHAR(10) PRIMARY KEY,
        name TEXT,
        location TEXT,
        address TEXT,
        latitude FLOAT,
        longitude FLOAT,
        fips INT,
        region region_type,
        ccbasic INT,
        cbsa FLOAT,
        csa FLOAT,
        accreditor TEXT,
        pred_degree degree,
        highest_degree degree,
        control ownership,
        admission_rate FLOAT CHECK (
            admission_rate <= 1 AND admission_rate >= 0),
        in_state_tuit INT,
        out_state_tuit INT,
        prog_year_tuit INT,
        revenue_tuit INT,
        two_yr_default FLOAT,
        three_yr_default FLOAT,
        avg_faculty_salary INT,
        avg_sat FLOAT,
        pct_loan FLOAT,
        extracted_year TEXT
    );
"""

# Execute the commands to create types and the table
cur.execute(create_types)
cur.execute(create_table)

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
