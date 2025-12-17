# Network Engineer Assistant

## Overview

This project implements a network troubleshooting retrieval assistant designed for network engineers.

During network incidents, engineers must follow a formal troubleshooting workflow, but the required steps are often scattered across long technical manuals.

Workflow is below:

1. Identifying the problem — interpreting alarms, symptoms, and error reports.
2. Locating the problem — isolating the fault using tests and narrowing down aAected components.
3. Analysing the problem — determining root cause from measurements and system behaviour.
4. Taking corrective action — applying fixes and verifying their eAectiveness.
5. Validating and documenting results — ensuring no secondary issues remain.

The guide also emphasizes **running tests in a logical sequence**, **verifying each step before proceeding**, and **applying strict system stability and safety precautions**. Engineers often struggle to remember which diagnostics must occur first or what checks are required before escalation. 

This system allows an engineer to input a natural-language problem description and receive structured troubleshooting steps grounded in the official guide.

The solution is based on [the Frontline LAN Troubleshooting Guide](https://assets.tequipment.net/assets/3/7/TroubleshootingGuide-FrontlineLAN.pdf) and strictly follows its prescribed diagnostic methodology.

## How to run

**Install Packages**

```
python -m venv .venv
pip install -r requirements.txt

cd frontend
npm i
```

**Create Vector DB**

Run below python notebook from top code block

- scripts\insert_vector_db.ipynb

- ※: This method is for local. The method of deployment environment is not yet.
- ※: After inserting by python notebook, restart python kernel. It is because due to connection to Qdrant, application fail. 

**Create RDB**

1. After login to postgres, create database

    ```
    CREATE DATEBASE netend
    ```

2. Change env file

    Copy .env.sample to .env and rewrite your settings. 

3. Run migration

    ```
    alembic upgrade head
    ```


**Backend**

```
fastapi dev main.py
```

**Frontend**

```
cd frontend
npm run dev
```


## Approach

### High Level Architecture

![](./docs/architecture.drawio.png)

### High Level Sequence

![](./docs/workflow-overview.drawio.png)

## Tech Stacks

### FrontEnd - React / React Router

| Category | tech stack | Reason |
| ---------| ---------- | -------|
| Base     | React      | This is a popular technology, so it is easy to find engineers to maintain. Also, separating from the backend allows for scalability. |
| Framework | React Router (Framework mode) | Routing and other settings are easy. There is little risk of vendor lock-in. |
| Component Library | Shadcn/ui | To unify the overall design in component files |

### Backend - FastAPI + OpenAI Agents SDK

| Category | tech stack | Reason |
| ---------| ---------- | -------|
| Framework | FastAPI | Routing and other settings are easy. There is little risk of vendor lock-in. |
| LLM Library | OpenAI Agents SDK | Considering future expansion to multi-turn. Ease of use of Conversation session. |
| Vector Search | Langchain | Well abstracted, so it can be implemented with less code. |

### DataStore - Qdrant / PostgreSQL

| Category | tech stack | Reason |
| ---------| ---------- | -------|
| VectorDB | Qdrant | It can be persisted locally and does not require Docker, making local development easy. It can be used for free for a wide range of purposes even after deployment. |
| RDB | PostgreSQL | Popular. |

## Main Topic / Tradeoffs

### 1. Why llm doing multi phase separately?

- I chose **multi phase** to execute LLM this procedure.

### 2. Why chose OpenAI Agents SDK?

### 3. Why chose determistic flow?

### 4. Why filter by category to retrieve vector store?

