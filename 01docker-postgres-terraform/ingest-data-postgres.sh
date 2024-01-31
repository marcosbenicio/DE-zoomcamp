URL1="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/green/green_tripdata_2019-09.csv.gz"
URL2="https://s3.amazonaws.com/nyc-tlc/misc/taxi+_zone_lookup.csv"

# Define parameters
USER="marcosbenicio"
PASSWORD="0102"
HOST="pg-database"
PORT="5432"
DATABASE_NAME="ny_taxi"
TABLE_NAME1="green_taxi_trip"
TABLE_NAME2="taxi_zone_lookup"
FILE_NAME1="green-tripdata-2019-09"
FILE_NAME2="taxi-zone-lookup"
FILE_EXTENSION1=".gz"
FILE_EXTENSION2=".csv"

# Ingest first dataset
docker run -it --rm\
    --network pg-network \
    ingest-data:v01 \
        --user=${USER} \
        --password=${PASSWORD} \
        --host=${HOST} \
        --port=${PORT} \
        --database_name=${DATABASE_NAME} \
        --table_name=${TABLE_NAME1} \
        --url=${URL1} \
        --file_name=${FILE_NAME1} \
        --file_extension=${FILE_EXTENSION1}

# Ingest second dataset
docker run -it --rm\
    --network pg-network \
    ingest-data:v01 \
        --user=${USER} \
        --password=${PASSWORD} \
        --host=${HOST} \
        --port=${PORT} \
        --database_name=${DATABASE_NAME} \
        --table_name=${TABLE_NAME2} \
        --url=${URL2} \
        --file_name=${FILE_NAME2} \
        --file_extension=${FILE_EXTENSION2}

        