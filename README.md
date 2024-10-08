# Bedrock Knowledge Base Interface

The **Bedrock Knowledge Base Interface** is a foundational system designed to interact with a knowledge base, enabling seamless access and management of data. This project uses Python, containerized with Docker, for portability and ease of deployment.

## Table of Contents

- [Bedrock Knowledge Base Interface](#bedrock-knowledge-base-interface)
  - [Table of Contents](#table-of-contents)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Running the Application](#running-the-application)
  - [Usage](#usage)

## Getting Started

This project provides a simple interface to access and manage knowledge base data, designed to be easy to set up with Docker. Whether you're a developer or a DevOps engineer, this repository includes everything needed to get up and running quickly.

### Prerequisites

Before you begin, ensure you have met the following requirements:

- Docker installed ([Installation guide](https://docs.docker.com/engine/install/))
- Docker Compose installed ([Installation guide](https://docs.docker.com/compose/install/))

Optionally, to run the application outside of Docker:

- Python 3.8+ installed
- Pip (Python package installer)

### Installation

1. **Clone the Repository**

Clone this repository to your local machine:

```bash
git clone https://github.com/diegoasp10/bedrock-knowledge-base-interface.git
cd bedrock-knowledge-base-interface
```

2. **Docker Setup** <!-- markdownlint-disable MD029 -->

Build the Docker image and start the container using Docker Compose:

```bash
docker compose up --build
```

This will build the Docker image and start the application based on the Dockerfile and ```compose.yml``` configuration.

3. **Python Setup (Optional)**

If you prefer to run the application locally without Docker, install the required Python packages:

```bash
cd app
pip install -r requirements.txt
```

## Running the Application

- **Docker (Recommended)**: Once the containers are up, the application will be accessible at ```http://localhost:8000``` (or the configured port in ```compose.yml```).
- **Python (Without Docker)**: You can run the application directly by executing the ```app.py``` file:

```bash
python app/app.py
```

## Usage

Once the application is running, you can:

- Access the knowledge base interface through your browser at ```http://localhost:8000```.
- Follow any specific documentation or guides provided in the app to interact with the knowledge base.
