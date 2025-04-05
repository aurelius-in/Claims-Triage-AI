# Claims Triage AI System

> **TL;DR**: This AI-powered system automates the classification and routing of insurance claims.  
> It uses natural language processing and machine learning to evaluate incoming claim descriptions and recommend triage paths based on urgency, complexity, and risk.

---

### Non-technical Summary:

Imagine hundreds of health insurance claims coming in daily, each needing to be reviewed and routed to the right team — some to clinicians, some for fraud review, and others to be auto-approved. This system acts like a digital claims assistant: it reads claim descriptions, evaluates risk and urgency, and recommends where each claim should go. This reduces delays, prevents errors, and helps healthcare teams focus on what matters most.

---

## Features

- Accepts raw or structured health insurance claim data
- Uses an ML model to classify:
  - Urgency (High, Medium, Low)
  - Risk Level (High, Medium, Low)
  - Triage Destination (Clinical Review, Auto-Approval, Escalation)
- Provides rationale for each decision
- RESTful API built with FastAPI for integration
- Logs triage results and writes them to Excel or database

---

## Architecture

![Architecture Diagram](architecture-diagram.png)

---

## Tech Stack

- **Python 3.10+**
- **FastAPI** (for the triage API service)
- **Scikit-learn / HuggingFace** (for ML model)
- **Pandas & NumPy** (for data handling)
- **OpenAI/LLMs** (optional for explainability or reasoning)
- **Excel or SQLite** (for output logging)
- **Docker-ready** (optional)

---

## How to Run

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/yourusername/Claims-Triage-AI.git
cd Claims-Triage-AI/api
pip install -r requirements.txt
```

```
Claims-Triage-AI/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── api/
│   ├── main.py
│   ├── model/
│   │   ├── classifier.py
│   │   └── __init__.py
│   ├── utils/
│   │   ├── router.py
│   │   └── __init__.py
│   └── requirements.txt
│
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   ├── test_classifier.py
│   └── test_router.py
│
├── data/
│   ├── claims_sample.csv
│   └── processed_outputs.xlsx
│
├── notebook/
│   └── training_pipeline.ipynb
│
├── demo/
│   ├── run_demo.gif
│   └── screenshots/
│       └── triage_output.png
│
├── logs/
│   └── triage_log.txt
│
├── Dockerfile
├── README.md
├── LICENSE
└── .gitignore
```

