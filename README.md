# Centralized Logging and Metrics Collection using Sidecar Pattern

A modular microservices implementation demonstrating the **Sidecar Pattern** for observability. This project decouples logging and metrics collection from application logic, allowing core services to remain lightweight while ensuring robust monitoring infrastructure.

## 📋 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Services & Ports](#services--ports)
- [Verification & Testing](#verification--testing)
- [Configuration](#configuration)
- [Design Decisions](#design-decisions)

## 🔭 Overview

In modern cloud-native environments, applications should focus on business logic, not infrastructure concerns. This project implements three independent application services (User, Product, Order), each paired with two dedicated sidecar containers:

1.  **Logging Sidecar:** Tails local log files via a shared volume, enriches log entries with metadata (Service Name, Environment), and forwards them to a centralized Log Aggregator.
2.  **Metrics Sidecar:** Periodically scrapes the application's raw metrics endpoint, adds dimension labels, and exposes an enriched Prometheus-compatible metrics stream on a separate port.

## 🏗 Architecture

The system is composed of the following components orchestrated via Docker Compose:

* **Application Services:** Python Flask apps that write JSON logs to disk and expose a basic `/metrics` endpoint.
* **Sidecar Loggers:** Python processes that read from the shared volume and `POST` logs to the aggregator.
* **Sidecar Metrics:** Scrapers that fetch, parse, and re-expose metrics with added tags (`service_name`, `environment`).
* **Mock Aggregator:** A centralized service that ingests and stores logs for verification.

## 📂 Project Structure

```text
sidecar-assignment/
├── app-service/           # Generic application service code
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── sidecar-logger/        # Log forwarding sidecar
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── sidecar-metrics/       # Metrics enrichment sidecar
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── mock-aggregator/       # Central log storage service
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── docker-compose.yml     # Orchestration configuration
├── .env.example           # Environment variable documentation
└── README.md              # Project documentation

```

## 🛠 Prerequisites

* **Docker** and **Docker Compose** installed on your machine.
* **Git** for version control.
* **Curl** or a web browser for testing endpoints.

## 🚀 Getting Started

1. **Clone the repository:**
```bash
git clone https://github.com/venkateshmalakala/sidecar-assignment.git
cd sidecar-assignment

```


2. **Environment Setup:**
The project comes with a ready-to-use configuration. No manual `.env` file creation is required for default local execution, as variables are defined directly in `docker-compose.yml`.
3. **Build and Run:**
```bash
docker-compose up --build -d

```


4. **Wait for Healthchecks:**
The services employ health checks to ensure they are ready before accepting traffic. Wait approximately 30 seconds for all containers to reach the `healthy` state. You can check status with:
```bash
docker-compose ps

```



## 🔌 Services & Ports

| Service | Host Port | Internal Port | Description |
| --- | --- | --- | --- |
| **User Service** | `3000` | `3000` | Core Application |
| **Product Service** | `3002` | `3000` | Core Application |
| **Order Service** | `3003` | `3000` | Core Application |
| **Log Aggregator** | `8080` | `8080` | Log Verification API |
| **User Metrics** | `9101` | `9100` | Enriched Metrics |
| **Product Metrics** | `9102` | `9100` | Enriched Metrics |
| **Order Metrics** | `9103` | `9100` | Enriched Metrics |

## ✅ Verification & Testing

Follow these steps to validate the implementation:

### 1. Generate Traffic

Send a request to the User Service to generate logs and metrics data.

```bash
curl http://localhost:3000/
# Output: Hello from user-service

```

### 2. Verify Logging Pipeline

Check the centralized aggregator to confirm the log was received and enriched.

```bash
curl http://localhost:8080/logs

```

**Expected Output (JSON):**

```json
[
  {
    "message": "Root endpoint accessed on user-service",
    "level": "info",
    "service_name": "user-service",
    "environment": "production",
    "timestamp": "..."
  }
]

```

### 3. Verify Metrics Pipeline

Query the metrics sidecar to see enriched data.

```bash
curl http://localhost:9101/metrics

```

**Expected Output:**

```text
http_requests_total{method="GET", path="/",service_name="user-service",environment="production"} 42

```

## ⚙️ Configuration

Key configuration options found in `docker-compose.yml`:

* `SERVICE_NAME`: Tags logs and metrics with the specific service identity.
* `ENVIRONMENT`: Tags data with the deployment environment (e.g., production, staging).
* `LOG_AGGREGATOR_URL`: Destination for the logging sidecar.
* `APP_METRICS_URL`: Source endpoint for the metrics sidecar to scrape.

## 💡 Design Decisions

* **Shared Volumes:** Used for the logging pipeline to allow the sidecar to read files written by the main application without network overhead.
* **Network Scrapers:** Used for the metrics pipeline to simulate standard Prometheus scraping patterns.
* **Python Healthchecks:** Native Python libraries (`urllib`) are used for container health checks to keep Docker images lightweight and secure (removing the need for `curl` inside the image).
* **Loose Coupling:** The main application has zero knowledge of the aggregator or the final metrics format; it only cares about its local files and local endpoints.

## 🧹 Cleanup

To stop the services and remove the containers/networks:

```bash
docker-compose down

```

To remove the build cache and volumes (for a fresh start):

```bash
docker-compose down -v --rmi all --remove-orphans

```

