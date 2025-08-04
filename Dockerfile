FROM ubuntu:20.04

# Prevent interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# Install system packages: Python, Java 8/11, Maven, and tools
RUN apt-get update && \
    apt-get install -y \
    openjdk-8-jdk \
    openjdk-11-jdk \
    python3.10 \
    python3-pip \
    maven \
    bash \
    git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Environment variables
ENV JAVA8_HOME=/usr/lib/jvm/java-8-openjdk-amd64 \
    JAVA11_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
    JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64 \
    PATH=$JAVA_HOME/bin:$PATH \
    RESULTS_DIR=../results \
    MATCH_DIR=../Match \
    LIBRARY_RESULT_DIR=../LibraryResult \
    COMPARE_RESULT_DIR=../CompareResult \
    CLIENT_DIR=../client

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Build Java using Maven
RUN mvn clean package

# Default command
ENTRYPOINT ["bash", "run.sh"]