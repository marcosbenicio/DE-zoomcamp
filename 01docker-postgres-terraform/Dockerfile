FROM python:3.9.1

RUN apt-get update && apt-get install -y wget
RUN pip install pandas sqlalchemy psycopg2 pyarrow

WORKDIR /app

# Copy the script directly into /app
COPY ["ingest-data.py", "./"]

# Execute ingest-data.py when the container starts
ENTRYPOINT [ "python", "ingest-data.py" ]