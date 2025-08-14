import os
from utils.logger import setup_logger
from dotenv import load_dotenv
import streamlit as st
from main import create_agent_executor


logger = setup_logger(__name__, "logs/app.log")

# Load environment variables
load_dotenv()
logger.info("Enviroment variables loaded")


# Get API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("GOOGLE_API_KEY is not set in the .env file.")
    logger.error("GOOGLE_API_KEY is not found in the .env file")
    st.stop()


# Database path and top_k results
database_path = "telecom_data.db"
top_k = 5


# Streamlit UI
st.set_page_config(page_title="Telecom Roaming Data Analytics", layout="wide")
st.title("Telecom Roaming Data Analytics Agent")
st.write("Ask questions in natural language, and the AI will query the database, return results, and provide business insights.")

# Create agent executor dynamically
try:
    if "agent_executor" not in st.session_state:
        st.session_state.agent_executor = create_agent_executor(database_path, top_k)
        st.session_state.db_path = database_path
        st.session_state.top_k = top_k
        logger.info("Agent executor created sucessfully")

except Exception as e:
    logger.error(f"Error occured during creating agent executer: {e}", exc_info=True)
    st.error(f"Error: {e}")


# Query input
user_query = st.text_area("Enter your question")

if st.button("Run Query"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        logger.info(f"User query updated for the telecom data analytics with: {user_query}")
        try:
            # Run query
            with st.spinner("Creating Response..."):
                response = st.session_state.agent_executor.invoke({"messages": [("user", user_query)]})
                logger.info(f"Query response is generated \n {response}")
            
            # Fetch the final answer ans show
            final_answer = response["messages"][-1].content
            logger.info(f"Response generated with final answer as: \n {final_answer}")
            st.markdown("### **Answer**")
            st.write(final_answer)
        
        except Exception as e:
            logger.error(f"Error occured during agent execution: {e}", exc_info=True)
            st.error(f"Error: {e}")
