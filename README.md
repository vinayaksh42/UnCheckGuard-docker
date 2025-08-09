# 🛡️ UnCheckGuard – ICSME 2025 Artifact

**Authors:** Vinayak Sharma, Patrick Lam   
**Associated Paper:** [Detecting Exception-Related Behavioural Breaking Changes with UnCheckGuard](./main.pdf)  
**Conference:** IEEE International Conference on Software Maintenance and Evolution (ICSME) 2025  
**DOI (Artifact):** [Zenodo DOI link]  
---

## 📝 Overview

**UnCheckGuard** is a tool designed to:

1. Detect unchecked exceptions that may cause *behavioral breaking changes* (BBCs) in Java applications.  
2. Compare two versions of a Java library to identify newly added unchecked exceptions.

This repository contains the **Dockerized artifact** for UnCheckGuard, enabling easy setup and execution in a controlled environment.  
The original main repository is available at: [https://github.com/vinayaksh42/UncheckedException](https://github.com/vinayaksh42/UncheckedException)

---

## 📄 License

This artifact is released under the **MIT License** license. See [LICENSE.md](LICENSE.md) for details.  
OSI-approved license ✔ — requirement for the *Open Research Object* badge.

---

## 🖥 Requirements

- **Hardware:**
  - CPU: 2+ cores
  - RAM: 8 GB minimum
  - Disk: 10 GB free space
- **Software:**
  - Docker ≥ 20.10
  - Tested on:
    - Ubuntu 22.04 LTS
    - macOS 14 (Apple Silicon)
    - Windows 11

No proprietary software or special hardware is required.

---

## ⚙️ Installation

**1. Clone the repository**
```bash
git clone https://github.com/vinayaksh42/uncheckguard-docker.git
cd artifact-uncheckguard
````

**2. Build the Docker image**

```bash
docker build -t artifactuncheckguard:latest .
```

**3. Verify installation**

```bash
docker run --rm artifactuncheckguard:latest --help
```

Expected output:

```
Usage:
  docker run ... run  <file.txt>          # Full pipeline
  docker run ... find <repo> <commit>     # Targeted analysis
```

---

## 🚀 Running the Tool

### 1️⃣ **Targeted Analysis on a Specific Client**

```bash
mkdir results
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest analyzeClient <repoOwner/repoName> <commitHash>
```

**Example:**

```bash
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest analyzeClient a63881763/HttpAsyncClientUtils 4eff19ca23d587654ecb022c7178c29ab0aaca68
```

---

### 2️⃣ **Analysis on a List of Clients**

```bash
mkdir results
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run <path/to/file.txt>
```

The text file should be placed within the `scripts/` folder before building the image.

**Example:**

```bash
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt
```

File format (`file.txt`):

```
repoOwner/repoName
```

---

## 📊 Reproducing Paper Results

The file `hasMatches.txt` contains all the clients showcased in the paper’s findings.
To reproduce them:

```bash
docker build -t artifactuncheckguard:latest .
mkdir results
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt
```

---

### 📊 Automatic Run Summary

At the end of both Docker commands —

```bash
docker run ... analyzeClient <repo> <commit>
docker run ... run <file.txt>
```

the [`scripts/summarize_results.py`](./scripts/summarize_results.py) script is executed automatically.

It reads `results/results.csv` from the run and prints a summary that includes:

* Unique libraries analyzed
* Unique Client–Library pairs
* Total matched methods (possible BBC call sites)
* Libraries with at least one matched method
* Total library usage calls
* Total unique clients

The same summary is also saved to `results/summary.json` for later reference.

You can also run this script manually, but it requires **Python 3** and the **pandas** library to be installed:

```bash
python3 scripts/summarize_results.py --csv ./results/results.csv --out ./results/summary.json
```

---

## 📌 Mapping to Paper Results

| Paper Result                     | Command                                                                                                      | Output Location      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------- |
| Library-Client pairs, libraries, callsites       | `docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt`            | `results/` Summary.json |

---

## 📁 Output

All results are stored in the mounted `results/` directory on your host machine.
Additional outputs:

* `Match/`
* `LibraryResult/`
* `CompareResult/`

---

## 📂 Repository Structure

```
.
├── Dockerfile               # Docker build instructions
├── LICENSE.md               # License information
├── README.md                # This file
├── scripts/                 # Helper scripts for running the Java-based analysis
├── results/                 # Output directory (contains csv files)
├── main.pdf/                # SCAM 2025 research paper
├── requirements.txt/        # Python requirements
├── run.sh/                  # shell script commands for running analysis
├── src/                     # Java program (client-library analysis)
```
More information about each script can be found in the [`scripts/`](./scripts) folder’s README.

---

## 📬 Contact

For questions or support, contact: 
- Vinayak Sharma – [v236shar@uwaterloo.ca](mailto:v236shar@uwaterloo.ca)
- 



