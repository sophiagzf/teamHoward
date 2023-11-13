import pandas as pd

# College Scorecard
raw_scorecard = pd.read_csv("data/MERGED2018_19_PP.csv")

# IPEDS
#raw_ipeds = pd.read_csv("data/hd2019.csv")


# Keep only the columns we want from College Scorecard data
scorecard = raw_scorecard.loc[:, ["UNITID", "ACCREDAGENCY", "PREDDEG", "HIGHDEG",
                                  "CONTROL", "REGION", "CCBASIC", "ADM_RATE", 
                                  "CCBASIC", "ADM_RATE", "TUITIONFEE_IN", "TUITIONFEE_OUT",
                                  "TUITIONFEE_PROG", "TUITFTE", "AVGFACSAL", "CDR2", "CDR3",
                                  "SAT_AVG", "PCTFLOAN"]]

# Rename UNITID to OPEID to match the IPEDS data
scorecard.rename(columns={"UNITID": "OPEID"})

# Check the output
scorecard.head()

# Keep only the columns we want from the IPEDS data
ipeds = raw_ipeds.loc[:, ["INSTNM", "ADDR", "ZIP", "FIPS", "CITY", "STABBR",
                          "OPEID", "CBSA", "CSA", "LONGITUD", "LATITUDE"]]

ipeds.head()

# Join the datasets together
#data = 