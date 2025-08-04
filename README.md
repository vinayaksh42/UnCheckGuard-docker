# UncheckedExceptionChangeDetector

A tool to identify and compare unchecked exceptions in Java applications and libraries.
![image](https://github.com/user-attachments/assets/94236f3e-c39c-45b4-a911-7f331934eed3)

---

## 📋 Overview

**UncheckedException** is a powerful utility designed to:

1. Detect unchecked exceptions that may cause *behavioral breaking changes* (BBCs) in Java applications.  
2. Compare two versions of a Java library to identify newly added unchecked exceptions.

---

## 🚀 Getting Started

This guide helps you build and run the tool using Docker.

---

## 🛠 Prerequisites

- **Docker**: Ensure Docker is installed and running on your system.

---

## 🐳 Docker Commands

### 1. **Build the Docker image**

```bash
docker build -t artifactuncheckguard:latest .
```

This creates a Docker image named `artifactuncheckguard` with the `latest` tag.

---

### 2. **Run targeted analysis on a specific client**

```bash
mkdir results
docker run --rm -v "${PWD}\results:/app/results" artifactuncheckguard:latest analyzeClient <repoOwner/repoName> <commitHash>
```

#### 🔍 Example:
```bash
docker run --rm -v "${PWD}\results:/app/results" artifactuncheckguard:latest analyzeClient a63881763/HttpAsyncClientUtils 4eff19ca23d587654ecb022c7178c29ab0aaca68
```

---

### 3. **Run analysis on a list of clients**

```bash
mkdir results
docker run --rm -v "${PWD}\results:/app/results" artifactuncheckguard:latest run <path/to/file.txt>
```

The text file needs to be placed within the scripts folder before building the docker image.

#### 🔍 Example:
```bash
docker run --rm -v "${PWD}\results:/app/results" artifactuncheckguard:latest run hasMatches.txt
```

The `file.txt` must contain a list of GitHub repositories, one per line, in the format:

```
repoOwner/repoName
```

---

## 📁 Output

All results will be stored in the mounted `results` directory on your host machine.

You may also mount the following directories to inspect additional outputs:

- `Match/`
- `LibraryResult/`
- `CompareResult/`

---

