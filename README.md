# CS611 Assignment 1: Loan default data pipeline


## Context
You are a data scientist working at a financial institute (e.g. bank). Your company lends money to users in the form of cash loans. You are tasked to eventually build a machine learning model that can predict whether a user will default on their loan at the point of loan application. For this assignment, you will be preparing the data through production data pipelines in preparation for machine learning model training (in the next assignment). You have 2 tasks: prepare the feature and label data stores compliant to the Medallion Architecture, and prepare a presentation deck (max 10 slides) to present to your manager, other engineers and business users of what tables you will create under which parts of the Medallion Architecture.

## Data

Four raw CSV files:

| File | Contents |
|---|---|
| `features_attributes.csv` | Customer attributes |
| `features_financials.csv` | Customer financial information |
| `feature_clickstream.csv` | Customer clickstream activity |
| `lms_loan_daily.csv` | Daily loan records from the loan management system |

**NOTE:** The brief names the first two `feature_attributes` and `feature_financials`. My code will uses actual filenames.

The data is not stored in Git. After cloning, copy the four files into `data/`:

    data/
    ├── feature_clickstream.csv
    ├── features_attributes.csv
    ├── features_financials.csv
    └── lms_loan_daily.csv

`data/` and the generated `datamart/` folder are both listed in `.gitignore`.

## Source inventory

`notebooks/01_source_inventory.ipynb` examines the raw data files for size, candidate keys, date coverage and obvious data-quality problems.

## Status

Environment and source inventory; pipeline not yet implemented.
