FROM apache/airflow:latest

# copy the requirements file to the container
COPY ["requirements.txt", "/"]

# install the requirements
RUN pip3 install --no-cache-dir -r /requirements.txt
