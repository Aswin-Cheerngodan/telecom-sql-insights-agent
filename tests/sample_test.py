import pandas as pd
from src.utils.logger import setup_logger
from src.main import create_agent_executor

logger = setup_logger(__name__, "logs/tests.log")

# Create the agent
agent_executor = create_agent_executor(database_path="telecom_data.db", top_k=5)
logger.info(f"Agent executor created for the testing")

# Define test business queries
test_queries = [
    "What is the average downloaded data volume for NON-IOT devices on 2G/3G networks?",
    "What percentage of roaming users used 4G/5G networks versus 2G/3G?",
    "Which visited network (vmcc/vmnc) had the highest number of active roamers?",
    "List the top 5 IMSIs with the highest data outbound uploads.",
    "What is the ratio of data upload to download for inbound sessions?",
]
logger.info(f"Test queries updated for the testing \n{test_queries}")


for i, query in enumerate(test_queries, start=1):
    logger.info(f"--- Query {i} ---")
    logger.info(f"**Input Prompt:** \n{query}")

    # Stream events from the agent
    sql_query = None
    final_answer = None

    events = agent_executor.stream(
        {"messages": [("user", query)]},
        stream_mode="values",
    )

    for event in events:
        last_msg = event["messages"][-1].content

        # detect SQL inside the message
        if "SELECT" in last_msg.upper():
            sql_query = last_msg.strip()
        else:
            final_answer = last_msg.strip()

    # Display generated SQL
    if sql_query:
        logger.info(f"**Generated SQL:**\n {sql_query}")
    else:
        logger.info("**Generated SQL:** Could not detect SQL in output.")

    # Display answer & insights
    if final_answer:
        # Separate answer from insight if formatted
        parts = final_answer.split("Insight:")
        answer_part = parts[0].strip()
        insight_part = parts[1].strip() if len(parts) > 1 else None

        logger.info(f"**Query Result:** \n{answer_part}")

        if insight_part:
            logger.info(f"**Insight Summary:** \n{insight_part}")

    print("\n--------------------\n\n\n\n")
