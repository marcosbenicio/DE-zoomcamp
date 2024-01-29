import os
import argparse
from sqlalchemy import create_engine
import pandas as pd
import gzip

def main(params):
    
    try:
        # Get the parameters 
        user = params.user
        password = params.password
        host = params.host
        port = params.port
        database_name = params.database_name
        table_name = params.table_name
        url = params.url
        file_name = params.file_name
        file_extension = params.file_extension
        
        # Download csv file from url
        if os.system(f'wget {url} -O {file_name}') != 0:
            raise Exception(f"Failed to download file from {url}")

        # Check the file extension and process
        if file_extension == '.csv':
            df = pd.read_csv(file_name, low_memory=False) 
        
        elif file_extension == '.gz':
            with gzip.open(file_name, 'rb') as f:
                df = pd.read_csv(f, low_memory=False)
    
        else:
            raise Exception(f"File extension {file_extension} not supported")
        
        # Create a connection to the database
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database_name}')
        
        # Create a table in database from the pandas dataframe
        df.to_sql(name=table_name, con=engine, if_exists="replace")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":  

    parser = argparse.ArgumentParser(description='Ingest CSV data to Posgres')

    parser.add_argument("--user", help= 'user name for posgres' )
    parser.add_argument("--password", help= 'password for posgres' )
    parser.add_argument("--host", help= 'host for posgres')
    parser.add_argument("--port", help= 'port for posgres')
    parser.add_argument("--database_name", help= 'database name for posgres')
    parser.add_argument("--url", help= 'url for file csv or .gz file to ingest')
    parser.add_argument("--table_name", help= 'Table name to pass data')
    parser.add_argument("--file_name", help= 'Name to save data')
    parser.add_argument("--file_extension", help= 'Extension of the file to ingest (csv or .gz)')

    args = parser.parse_args()
    main(args)