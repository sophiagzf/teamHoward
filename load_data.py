import pandas as pd

# College Scorecard
raw_scorecard = pd.read_csv("data/MERGED2018_19_PP.csv")

# IPEDS
raw_ipeds = pd.read_csv("data/hd2019.csv", encoding="cp1252")


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

# Check the output
print(data.head())