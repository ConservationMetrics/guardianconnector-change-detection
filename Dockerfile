FROM python:3.10-slim-bullseye

# Install tippecanoe
RUN apt-get update && \
    apt-get install -y git build-essential libsqlite3-dev zlib1g-dev && \
    git clone https://github.com/felt/tippecanoe.git && \
    cd tippecanoe && \
    make -j && \
    make install

# Install GDAL
RUN apt-get install -y binutils libproj-dev gdal-bin

# Download and install go-pmtiles
RUN apt-get install -y wget && \
    wget https://github.com/protomaps/go-pmtiles/releases/download/v1.11.0/go-pmtiles_1.11.0_Linux_x86_64.tar.gz && \
    tar -xzf go-pmtiles_1.11.0_Linux_x86_64.tar.gz && \
    rm go-pmtiles_1.11.0_Linux_x86_64.tar.gz && \
    mv pmtiles /usr/local/bin

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install gccd library
RUN pip install -e gccd_pkg

# Make port 80 available to the world outside this container
EXPOSE 80

# Run this command when the container launches
CMD ["python", "generate.py"]
