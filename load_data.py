import pandas as pd
import re
# College Scorecard
raw_scorecard = pd.read_csv("MERGED2018_19_PP.csv")

# IPEDS
raw_ipeds = pd.read_csv("hd2019.csv", encoding="cp1252")


# Keep only the columns we want from College Scorecard data
scorecard = raw_scorecard.loc[:, ["UNITID", "ACCREDAGENCY", "PREDDEG", "HIGHDEG",
                                  "CONTROL", "REGION", "ADM_RATE",
                                  "CCBASIC", "ADM_RATE", "TUITIONFEE_IN", "TUITIONFEE_OUT",
                                  "TUITIONFEE_PROG", "TUITFTE", "AVGFACSAL", "CDR2", "CDR3",
                                  "SAT_AVG", "PCTFLOAN"]]

# Rename UNITID to OPEID to match the IPEDS data
scorecard = scorecard.rename(columns={"UNITID": "OPEID"})

# Keep only the columns we want from the IPEDS data
ipeds = raw_ipeds.loc[:, ["INSTNM", "ADDR", "ZIP", "FIPS", "CITY", "STABBR",
                          "OPEID", "CBSA", "CSA", "LONGITUD", "LATITUDE"]]

# Join the datasets together
data = pd.merge(scorecard, ipeds, on="OPEID")


data = data.rename(columns={"OPEID": "oepid", "INSTNM": "name", "ADDR": "address", "STABBR": "state", "CITY": "city", "CCBASIC": "ccbasic", 
"LATITUDE": "latitude", "LONGITUDE": "longitude", "FIPS": "fips", "REGION": "region", "CBSA": "cbsa", "CSA": "csa", "ACCREDAGENCY": "accreditor", "PREDDEG": "pred_degree",
"HIGHDEG": "highest_degree", "CONTROL": "control", "ADM_RATE": "admission_rate", "TUITIONFEE_IN": "in_state_tuit", "TUITIONFEE_OUT": "out_state_tuit",
"TUITIONFEE_PROG": "prog_year_tuit", "TUITFTE": "revenue_tuit", "AVGFACSAL": "avg_faculty_salary", "CDR2": "two_yr_default", "CDR3": "three_yr_default", 
"SAT_AVG": "sat_avg", "PCTFLOAN": "prop_loan"})
# combining the state and city together into address
data['address'] = data.apply(lambda row: f"{row['city']}, {row['state']} - {row['address']}", axis=1)

file_name1 = "MERGED2018_19_PP.csv"
file_name2 = "hd2019.csv"


def extract_year_from_filename(file_name):
    if "MERGED" in file_name:
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
    print("Year not found in file name")

numeric_columns = ["opeid", "ccbasic", "latitude", "longitude", "fips", "cbsa", "csa",
"admission_rate", "in_state_tuit", "out_state_tuit",
"prog_year_tuit", "revenue_tuit", "avg_faculty_salary", "two_yr_default", "three_yr_default", 
"sat_avg", "prop_loan"]

# Replace -999 with None in numeric columns
for col in numeric_columns:
    if col in data.columns:
        data[col] = data[col].replace(-999, None)

data['extracted_year'] = pd.to_datetime(data["extracted_year"].astype(str) + '-01-01')

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
