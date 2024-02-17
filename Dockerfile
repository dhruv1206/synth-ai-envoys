# Set base image (host OS)
FROM python:3.11.0

# Install necessary system packages for OpenGL support
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# By default, listen on port 5000
EXPOSE 5000/tcp

# Set the working directory in the container
WORKDIR /app

# Copy all files and directories from the current directory to the working directory in the container
COPY . .

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Install MongoDB
RUN apt-get update && apt-get install -y gnupg
RUN wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/debian bullseye/mongodb-org/5.0 main" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
RUN apt-get update && apt-get install -y mongodb-org

# Specify the command to run on container start
CMD [ "python", "./app.py" ]
