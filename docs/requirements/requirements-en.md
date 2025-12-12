# Problem Space

## Background
Telecom network engineers follow a formal troubleshooting workflow during network outages.  
However, the required steps are documented across long and fragmented manuals, making it difficult to quickly locate and execute the correct procedures under time pressure.

## Core Pain Point
**In high-pressure outage situations, engineers must search through large volumes of documentation to find the correct troubleshooting steps, which is time-consuming and error-prone.**

This leads to delayed recovery, procedural mistakes, and increased operational risk.

## Key Problems (as stated in the problem description)
- **Troubleshooting steps are scattered across large manuals**
  - Engineers spend excessive time searching for relevant sections.
- **Engineers struggle to remember which diagnostic tests must be executed first**
  - Troubleshooting steps are order-dependent, but recall-based execution leads to mistakes.
- **Safety checks and prerequisite validations are often skipped**
  - Missing these steps can compromise system stability and operational safety.

## Problem Characterization
- The issue is **not lack of knowledge**, but **inability to retrieve and structure the correct information quickly**.
- The problem is primarily an **information retrieval and structuring challenge**, not a reasoning or automation problem.

---

# Solution Space (Requirements)

## Solution Overview
Build a retrieval-based assistant that converts a natural-language description of a network issue into **structured, guide-compliant troubleshooting steps**, following the official troubleshooting workflow.

The system focuses on **accurate retrieval, correct ordering, and safety-first execution**.

---

## Functional Requirements

### 1. User Interface (UI)
The UI must:
- Allow engineers to input:
  - Alarm patterns
  - Error messages
  - Symptom descriptions  
  using natural language.
- Display troubleshooting results as:
  - A **clearly structured step-by-step procedure**
  - Organized according to the official troubleshooting phases:
    1. Identification  
    2. Localization  
    3. Analysis  
    4. Corrective Action  
    5. Validation and Documentation
- Highlight:
  - Required **safety checks**
  - **Logical test execution order**
- Provide references to the original guide sections to ensure trust and traceability.

---

### 2. Backend
The backend must:
- Ingest and process the troubleshooting guide document.
- Store guide content in a **vector database** for semantic retrieval.
- Retrieve relevant guide sections based on the user’s input.
- Structure retrieved content into:
  - The five troubleshooting phases
  - Ordered diagnostic and corrective steps
  - Mandatory safety and stability checks
- Ensure that:
  - Steps are presented in the correct logical sequence
  - No required phase or safety step is omitted.

---

## Non-Goals (Out of Scope for MVP)
- Automatic execution of diagnostic commands or configuration changes.
- Generating new troubleshooting procedures not present in the guide.
- Root-cause inference beyond what is explicitly documented.
- User authentication and historical query storage (considered **additional features**, not part of MVP).

---

## Optional / Additional Features (Future Work)
- User login and role-based access.
- Storage and search of past troubleshooting queries.
- Retrieval of similar historical incidents.
- Feedback loop to improve retrieval accuracy.
