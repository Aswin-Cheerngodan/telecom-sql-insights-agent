# Telecom Roaming Data Analytics Agent

## Overview
This project is an **AI-powered Telecom Data Analytics tool** built using **LangChain**, **LangGraph**, and **Streamlit**.  
It uses a **Agentic approach** to:
- Generate **optimized SQL queries** from plain English.
- Execute those queries on a **SQLite database** (`telecom_data.db`).
- Provide **business insights** in natural language.

The system is tailored for **Roaming Data Analytics** in telecom, where quick and accurate insights are critical for decision-making.

---

## Project Structure
├── data/ # Data files
├── logs/ # logs
├── scripts/ # Extra scripts for project
├── src/ # Main source code
│ ├── utils/ # Helper modules
│ │ ├── init.py
│ ├── app.py # Streamlit web application
│ ├── main.py # Core agent creation and configuration
├── tests/ # Unit tests
├── venv/ # Python virtual environment
├── .env # Environment variables (not committed to Git)
├── telecom_data.db # SQLite database with telecom roaming data
├── requirements.txt # Python dependencies
├── README.md # Project documentation

---

## How It Works

1. **Environment Setup**
   - The `.env` file stores sensitive API keys, e.g., `GOOGLE_API_KEY`.
   - Loaded automatically in `main.py`.

2. **Agent Creation (`main.py`)**
   - Uses **LangChain** + **LangGraph** to create a **ReAct Agent**.
   - Agent is initialized.
   - Prompt includes:
     - Schema info (table + column descriptions).
     - MCC/MNC mappings for network names.
     - Few-shot examples for better SQL generation.

3. **Streamlit App (`app.py`)**
   - User enters a **natural language query**.
   - Agent:
     - Generates SQL.
     - Runs it on `telecom_data.db`.
     - Returns results + 2–3 sentence business insights.
   - Results shown in a table or chart.

4. **Business Focus**
   - Insights are **business-friendly**, not just technical.
   - Example: “Germany’s Cosmote network leads in inbound roaming traffic, indicating a lucrative partnership opportunity.”

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Aswin-Cheerngodan/telecom-sql-insights-agent.git
cd telecom-sql-insights-agent
```
### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```
### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
### 4. Setup Environment Variables
Create .env file
```bash
GOOGLE_API_KEY=your_google_gemini_api_key
```
---
### Running the Application
#### Run streamlit app
```bash
streamlit run src/app.py
```
## Example Queries

* "Which network had the highest inbound data usage in July 2025?"

* "What is the average inbound download for NON-IOT devices?"

* "Top 5 IMSIs with highest outbound uploads."

## Features

- Natural Language to SQL conversion.

- Business Insight Generation with context.

- MCC/MNC mapping to human-readable country & operator names.

- Few-shot examples for better query accuracy.

- Streamlit UI for easy interaction.

- SQLite database for portability.