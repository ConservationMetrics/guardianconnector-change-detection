FROM python:3

# Install tippecanoe
RUN apt-get update && \
    apt-get install -y build-essential libsqlite3-dev zlib1g-dev && \
    git clone https://github.com/felt/tippecanoe.git && \
    cd tippecanoe && \
    make -j && \
    make install

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["python", "generate.py"]