import os
from datetime import datetime
import pyspark

import utils.data_processing_bronze_table
import utils.data_processing_silver_table
import utils.data_processing_gold_table

# Initialize SparkSession
spark = pyspark.sql.SparkSession.builder \
    .appName("dev") \
    .master("local[*]") \
    .getOrCreate()

# Set log level to ERROR to hide warnings
spark.sparkContext.setLogLevel("ERROR")

# generate list of dates to process
def generate_first_of_month_dates(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    first_of_month_dates = []
    current_date = datetime(start_date.year, start_date.month, 1)
    while current_date <= end_date:
        first_of_month_dates.append(current_date.strftime("%Y-%m-%d"))
        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)

    return first_of_month_dates

def make_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

# set up config: each source's monthly snapshot range (from EDA in notebooks/01_source_inventory.ipynb)
sources = {
    # table name: (raw file, first snapshot, last snapshot)
    "attributes": ("data/features_attributes.csv", "2023-01-01", "2025-01-01"),
    "financials": ("data/features_financials.csv", "2023-01-01", "2025-01-01"),
    "clickstream": ("data/feature_clickstream.csv", "2023-01-01", "2024-12-01"),
    "loan_daily": ("data/lms_loan_daily.csv", "2023-01-01", "2025-11-01"),
}
dates = {name: generate_first_of_month_dates(start, end) for name, (_, start, end) in sources.items()}

# create bronze datalake
for name, (source_csv, _, _) in sources.items():
    bronze_directory = make_directory(f"datamart/bronze/{name}/")
    for date_str in dates[name]:
        utils.data_processing_bronze_table.process_bronze_table(date_str, source_csv, name, bronze_directory, spark)

# create silver datalake
silver_functions = {
    "attributes": utils.data_processing_silver_table.process_silver_attributes_table,
    "financials": utils.data_processing_silver_table.process_silver_financials_table,
    "clickstream": utils.data_processing_silver_table.process_silver_clickstream_table,
    "loan_daily": utils.data_processing_silver_table.process_silver_loan_table,
}
for name, process_silver_table in silver_functions.items():
    silver_directory = make_directory(f"datamart/silver/{name}/")
    for date_str in dates[name]:
        process_silver_table(date_str, f"datamart/bronze/{name}/", silver_directory, spark)

# create gold label store: one partition per LMS snapshot month
gold_label_store_directory = make_directory("datamart/gold/label_store/")
for date_str in dates["loan_daily"]:
    utils.data_processing_gold_table.process_labels_gold_table(
        date_str, "datamart/silver/loan_daily/", gold_label_store_directory, spark, dpd=30, mob=6)

# create gold feature store: one partition per application month
gold_feature_store_directory = make_directory("datamart/gold/feature_store/")
for date_str in dates["attributes"]:
    utils.data_processing_gold_table.process_features_gold_table(
        date_str, "datamart/silver/attributes/", "datamart/silver/financials/", "datamart/silver/clickstream/",
        gold_feature_store_directory, spark)

# summary
labels = spark.read.parquet(gold_label_store_directory + "*")
features = spark.read.parquet(gold_feature_store_directory + "*")
print("label store rows:", labels.count(), "feature store rows:", features.count(),
      "feature store columns:", len(features.columns))

spark.stop()



