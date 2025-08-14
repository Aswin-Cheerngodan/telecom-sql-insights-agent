import os
from utils.logger import setup_logger
from dotenv import load_dotenv
import sqlite3
from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from langchain.chat_models import init_chat_model
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDatabaseTool,
)
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent


logger = setup_logger(__name__, "logs/app.log")

# Load environment variables from .env file
load_dotenv()
logger.info("Environment variables loaded")

# Get the API key from environment variable
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    logger.error(f"Google api key is not found in the .env file.")
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")


column_info = """
Table: roaming
Column Name	Description
imsi:	Unique subscriber identifier to identify a user
imsitac:	Device identifier or TAC associated with the IMSI
vmcc:	Visited Mobile Country Code
vmnc:	Visited Mobile Network Code
hmcc:	Home Mobile Country Code
hmnc:	Home Mobile Network Code
data_inbound_uploaded_bytes:	Data uploaded by the subscriber while roaming (inbound) in bytes
data_inbound_downloaded_bytes:	Data downloaded by the subscriber while roaming (inbound) in bytes
data_outbound_uploaded_bytes:	Data uploaded by the subscriber while in their home network (outbound) in bytes
data_outbound_downloaded_bytes:	Data downloaded by the subscriber while in their home network (outbound) in bytes
2G/3G Usage:	Boolean flag indicating 2G/3G network usage
4G/5G Usage:	Boolean flag indicating 4G/5G network usage
device_type:	Device type - IOT or NON-IOT
extract_date:	date of roaming

Mappings:
mcc	mnc	country	operator
202	1	Germany	Cosmote
204	2	UK	Airelo
206	3	India	Dolphin
302	5	US	Penguin
303	6	Ireland	Trek
"""

logger.info(f"Column info for the Prompt: \n{column_info}")

few_shots = """
### Example 1
User Question:
How much data was used by subscribers while roaming in January 2025?

SQL Query:
SELECT
    SUM(data_inbound_uploaded_bytes + data_inbound_downloaded_bytes) AS total_roaming_data_bytes
FROM usage_logs
WHERE strftime('%Y-%m', extract_date) = '2025-01';

Answer:
Total roaming data used in January 2025: 2,145,678,900 bytes.

Insight:
Roaming usage in January 2025 surged to over 2.1 GB, marking a 28% increase compared to the prior month, likely due to post-holiday international travel. This trend signals an opportunity to launch targeted "New Year Roaming Packs" to capture seasonal high-value usage.

---

### Example 2
User Question:
Which country had the highest inbound data usage by users?

SQL Query:
SELECT
    vmcc, vmnc,
    SUM(data_inbound_uploaded_bytes + data_inbound_downloaded_bytes) AS total_inbound_data_bytes
FROM usage_logs
GROUP BY vmcc, vmnc
ORDER BY total_inbound_data_bytes DESC
LIMIT 1;

Answer:
Germany (Cosmote) recorded the highest inbound data usage at 987,654,321 bytes.

Insight:
Germany's Cosmote network leads in inbound roaming traffic, indicating a lucrative partnership point for preferential bandwidth agreements. Strengthening capacity planning here could drive better service quality for high-value inbound roamers.

---

### Example 3
User Question:
How many IOT devices used 4G/5G networks while roaming?

SQL Query:
SELECT
    COUNT(DISTINCT imsi) AS iot_device_count
FROM usage_logs
WHERE device_type = 'IOT'
  AND "4G/5G Usage" = 1;

Answer:
4,230 IOT devices used 4G/5G networks while roaming.

Insight:
A growing IoT presence on high-speed roaming networks suggests untapped revenue in enterprise M2M services. This trend justifies investment in IoT-specific roaming bundles with guaranteed latency SLAs.
"""

logger.info(f"Few shots for the prompt: \n{few_shots}")

custom_system_prompt = PromptTemplate(
    input_variables=["dialect", "top_k", "column_info", "few_shots"],
    template="""You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct and very optimized {dialect} query to run, then look at the results of the query and return the answer along with some important 2–3 sentence insight summary for A telecom analytics company for Roaming Data Analytics .
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.
Then you should query the schema of the most relevant tables.

Schema information:
{column_info}

Few-shot examples:
{few_shots}

Follow these rules:
1. Only query the columns provided in the schema above.
2. Use the mappings when interpreting values.
3. Always check for correct column names before outputting SQL.
"""
)

logger.info(f"Custom system prompt for the Agent: \n{custom_system_prompt}")


def create_agent_executor(database_path: str, top_k: int = 5):
    """Set up and creates react agent for sql creation execution and 
    generating insights

    Args:
        database_path (str): Path name of the sql database
        top_k: Maximum number of rows that the ai generated sql query should return
    Returns:
        react_agent: langgraph react agent with llm, tools and prompt
    """
    try:
        # Creating DB connection
        engine = create_engine(f"sqlite:///{database_path}", echo=False)
        db = SQLDatabase(engine)
        logger.info(f"Database loaded for the agent")

        # Initializing model
        llm = init_chat_model(
            "gemini-2.5-flash",
            model_provider="google_genai"
        )
        logger.info(f"LLM created for the agent")

        # Creating Toolkit
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        logger.info(f"Database toolkit loaded for the agent")

        # Formatting prompt
        system_message = custom_system_prompt.format(
            dialect="SQLite",
            top_k=top_k,
            column_info=column_info,
            few_shots=few_shots
        )
        logger.info(f"system message updated for the agent")

        # Creating the react agent with llm, tookit and promt
        return create_react_agent(llm, toolkit.get_tools(), prompt=system_message)
    except Exception as e:
        logger.error(f"Error occured during react agent creation: {e}", exc_info=True)
        return None
