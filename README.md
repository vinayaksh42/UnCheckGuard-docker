# 🛡️ UnCheckGuard – SCAM 2025 Artifact

* **Authors:** Vinayak Sharma, Patrick Lam   
* **Persistent paper link:** [Detecting Exception-Related Behavioural Breaking Changes with UnCheckGuard](./main.pdf) (preprint)
* **Conference:** IEEE International Conference on Source Code Analysis and Manipulation (SCAM) 2025
* **DOI (Artifact):** [Zenodo DOI link](https://doi.org/10.5281/zenodo.16788650) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16788651.svg)](https://doi.org/10.5281/zenodo.16788650)
* **Abstract / Artifact Description:** This artifact is a Dockerized version of the research tool UnCheckGuard. It is a research tool for detecting newly added unchecked exceptions in upgraded Java libraries that may cause behavioral breaking changes (BBCs) in client applications. Given a client repository and commit (or a batch of repositories), it automatically clones, builds, and analyzes both the old and updated library versions, compares exception-throwing behavior, and identifies affected client call sites. The artifact includes all required Java code, Python scripts, datasets, and step-by-step instructions to fully reproduce the results reported in the associated paper, along with an automated summary report generated at the end of each run.

This repository contains the **Dockerized artifact** for UnCheckGuard, enabling easy setup and execution in a controlled environment.  
The original main repository is available at: [https://github.com/vinayaksh42/UncheckedException](https://github.com/vinayaksh42/UncheckedException)

---

## 🏷️ Badges Claimed

* **Open Research Object** – This artifact is publicly available in a persistent archival repository with a DOI, is released under an OSI-approved open-source license, and includes complete documentation and source code.

* **Research Object Reviewed** – This artifact is complete, consistent with the associated paper, well-documented, and fully exercisable via Docker. It includes all necessary data, code, and scripts to reproduce the results, along with clear step-by-step instructions and automated summary reporting.

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
  - Python3 (if running the summary python script manually)
  - Tested on:
    - Ubuntu 24.04 LTS
    - Windows 11
- **Skills & Knowledge:**
  - Docker Usage
  - Python 
  - Java

No proprietary software or special hardware is required.

---

## ⚙️ Installation

**1. Clone the repository**
```bash
git clone https://github.com/vinayaksh42/uncheckguard-docker.git
cd uncheckguard-docker
````

**2. Build the Docker image**

```bash
docker build -t artifactuncheckguard:latest .
mkdir results
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
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest analyzeClient <repoOwner/repoName> <commitHash>
```

**Example:**

```bash
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest analyzeClient a63881763/HttpAsyncClientUtils 4eff19ca23d587654ecb022c7178c29ab0aaca68
```

---

### 2️⃣ **Analysis on a List of Clients**

```bash
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run <path/to/list.txt>
```

The text file containing the list of clients should be placed within the `scripts/` folder before building the image.

**Example:**

```bash
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt
```

File format (`list.txt`):

```
repoOwner/repoName
```

---

## 📊 Reproducing Paper Results

The file `hasMatches.txt` contains all the clients showcased in the paper’s findings.
To reproduce them, from scratch:

```bash
docker build -t artifactuncheckguard:latest .
mkdir results
docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt
```

**Note:** The results in the summary may differ from those in the research paper because the tool analyzes the latest available library versions at runtime. A library may receive new updates after this artifact is published, which can change the analysis outcomes.

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
* Semantic Version Change Types — classification of each impactful LibraryOld → LibraryNew pair with > 0 matched methods as major, minor, patch, none, or unknown.

The same summary is also saved to `results/summary.json` for later reference.

---

## 📌 Mapping to Paper Results

| Paper Result                     | Command                                                                                                      | Output Location      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------- |
| Library-Client pairs, libraries, callsites       | `docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt`            | `results/` Summary.json |
| Table 1: Exception Analysis Funnel | `docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt` | `results/` Summary.json |
| Table 2:  Distribution of reachable newly-added exceptions across version types | `docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt` | `results/` Summary.json |
| Table 3: Clients, libraries,versions, andcountsofcallsitesreachingnewly-addedexceptions | `docker run --rm -v "$(pwd)/results:/app/results" artifactuncheckguard:latest run hasMatches.txt` | `results/`  results.csv |

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
The `src/` folder contains the Java application responsible for analyzing client applications as well as libraries.

---

## 📬 Contact

For questions or support, contact: 
- Vinayak Sharma – v236shar@uwaterloo.ca
- Patrick Lam – patrick.lam@uwaterloo.ca



