FROM mageai/mageai:latest

#  For a dynamic path based on environment variable inside .env 
ARG USER_CODE_PATH=/home/src/${PROJECT_NAME} 

# copy the requirements file to the container
COPY ["requirements.txt", "${USER_CODE_PATH}"]

# install the requirements
RUN pip3 install -r ${USER_CODE_PATH}/requirements.txt


