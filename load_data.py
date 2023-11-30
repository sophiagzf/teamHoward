import pandas as pd
import re
import argparse
import os
import time
from credentials import DBNAME, HOST, USERNAME, PASSWORD
import psycopg
import numpy as np

############################################
# Load raw csv files from the command line #
############################################
# Take in user input: one College Scorecard csv file (starts with 'MERGED') and
# one IPEDS data file (starts with 'hd')

# Run command:
# python3 load_data.py {COLLEGE SCORECARD FILEPATH} {IPEDS FILEPATH}
# Example: python3 load_data.py data/MERGED2018_19_PP.csv data/hd2019.csv

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

########################
# Merge raw csv files #
########################

# College Scorecard
raw_scorecard = pd.read_csv(args.college_scorecard, low_memory=False)

# IPEDS
raw_ipeds = pd.read_csv(args.ipeds, encoding='cp1252', low_memory=False)

# Keep only the columns we want from College Scorecard data
scorecard = raw_scorecard.loc[:, ['OPEID', 'INSTNM', 'ACCREDAGENCY',
                                  'PREDDEG', 'HIGHDEG',
                                  'CONTROL', 'REGION', 'ADM_RATE',
                                  'CCBASIC', 'TUITIONFEE_IN',
                                  'TUITIONFEE_OUT',
                                  'TUITIONFEE_PROG', 'TUITFTE', 'AVGFACSAL',
                                  'CDR2', 'CDR3',
                                  'SAT_AVG', 'PCTFLOAN']]

scorecard = scorecard.dropna(subset=['OPEID', 'INSTNM'])

# Keep only the columns we want from the IPEDS data
ipeds = raw_ipeds.loc[:, ['INSTNM', 'ADDR', 'ZIP', 'FIPS', 'CITY', 'STABBR',
                          'OPEID', 'CBSA', 'CSA', 'LONGITUD', 'LATITUDE']]
ipeds = ipeds.dropna(subset=['OPEID', 'INSTNM'])

# Make sure the OPEID (column we merge on) are both 
# of type object and same format
scorecard['OPEID'] = scorecard['OPEID'].astype('float')
ipeds['OPEID'] = scorecard['OPEID'].astype('float')
scorecard['OPEID'] = scorecard['OPEID'].astype('object')
ipeds['OPEID'] = ipeds['OPEID'].astype('object')

# Join the datasets together
data = pd.merge(scorecard, ipeds, on='OPEID', how='left')
# Drop duplicate column
data = data.drop(['INSTNM_y'], axis=1)

###################
# Clean the data #
###################

# Rename columns
data = data.rename(columns={'OPEID': 'opeid',
                            'INSTNM_x': 'name',
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
extracted_year = None

if year1:
    data['extracted_year'] = year1
    extracted_year = year1
elif year2:
    data['extracted_year'] = year2
    extracted_year = year2
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

# Cast floats to ints for a few columns
data['fips'] = data['fips'].astype('Int64')
data['ccbasic'] = data['ccbasic'].astype('Int64')
data['cbsa'] = data['cbsa'].astype('Int64')
data['csa'] = data['csa'].astype('Int64')

# Cast to object
data['accreditor'] = data['accreditor'].astype('object')

# NAs to None types
data = data.where(pd.notnull(data), None)
data = data.astype("object").replace(np.nan, None)

###############################
# Connect to the SQL database #
###############################

# Connnect, create conn connection object
# Connect to the database using parameters from credentials.py
conn = psycopg.connect(
    dbname=DBNAME,
    host=HOST,
    user=USERNAME,
    password=PASSWORD)

# Create a cursor and use it to submit/execute a query
cur = conn.cursor()

# Check if you have already inserted this year's data
# If you have, exit the script immediately
check_cmd = """
    SELECT * FROM institutions
    WHERE extracted_year = %s
    LIMIT 10;
"""

extracted_year = str(extracted_year) + '-01-01 00:00:00'
check_inserted = pd.DataFrame(cur.execute(check_cmd, [extracted_year]))

if check_inserted.shape[0] > 0:
    print(f"You have already inserted data for: {extracted_year}")
    print("Quitting now.")
    exit()

print("Preview of the data being loaded: \n\n")
print(data.head())

############################
# Data loading and summary #
############################

# To keep track of how much data has been read
# and inserted into the database
successful_inserts = 0
# Create a file to store invalid rows
invalid_rows_file = "invalid_rows.csv"

insert_cmd = """
        INSERT INTO institutions
        (opeid, name, accreditor, pred_degree, highest_degree,
        control, region, admission_rate, ccbasic,
        in_state_tuit, out_state_tuit, prog_year_tuit, revenue_tuit,
        avg_faculty_salary, two_yr_default, three_yr_default, sat_avg,
        prop_loan, address, ZIP,
        fips, city, state, cbsa,
        csa, longitude, latitude, extracted_year)
        VALUES
        (%s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s);
    """

invalid_rows = pd.DataFrame(columns=data.columns)

start_time = time.time()

for index, row in data.iterrows():
    try:
        # Insert data into the database
        cur.execute(insert_cmd, tuple(row))
        successful_inserts += 1
        conn.commit()
    # Handling errors & invalid rows rejected
    except Exception as e:
        # Print the error message
        print(f"Error during data insertion: {e}")
        print(f"Error is at this index: {index}")

        # Roll back the transaction upon error
        conn.rollback()

        # Store the invalid row in a data frame
        invalid_rows.loc[len(invalid_rows)] = row

end_time = time.time()

inserted_rows = successful_inserts
omitted_rows = len(data) - successful_inserts
difference = len(invalid_rows)
total_time = (end_time - start_time) / 60

# Print the summary after data insertion
print("\n \n \nData loading complete.")
print(f"Rows successfully inserted into the database: {inserted_rows}")
print(f"Rows omitted (due to errors, etc.): {omitted_rows}")
print(f"Number of rows in: {len(data)}")
print(f"Number of rows out: {inserted_rows}")
print(f"Difference in number of rows in vs. out: {difference}")
print(f"This process took {total_time} minutes.")

# Write invalid rows to a separate CSV file
invalid_rows.to_csv(invalid_rows_file, index=False)
print(f"Invalid rows written to: {invalid_rows_file}")

# Close the cursor and connection
cur.close()
conn.close()
