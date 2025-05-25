import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon=":robot:")
st.title("LangChain: Chat with SQL DB")

## connect to sqlite database
LocalDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

# radio options 
radio_option = ["Select the database you want to connect to SQLite 3 Database- Student.db", "Connect to your MySQL Database"]
selected_opt = st.sidebar.radio(label="Select the database you want to connect to", options=radio_option)

# Initialize variables
mysql_host = mysql_user = mysql_password = mysql_db = None

if radio_option.index(selected_opt) == 1:  # MySQL option selected
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("Enter the host name of your MySQL database")
    mysql_user = st.sidebar.text_input("Enter the user name of your MySQL database")
    mysql_password = st.sidebar.text_input("Enter the password of your MySQL database", type="password")
    mysql_db = st.sidebar.text_input("Enter the name of your MySQL database")
else:
    db_uri = LocalDB

api_key = st.sidebar.text_input("Enter your Groq API key", type="password")

# Validation checks
if db_uri == MYSQL and not all([mysql_host, mysql_user, mysql_password, mysql_db]):
    st.info("Please enter all MySQL connection details")
    st.stop()

if not api_key:
    st.info("Please enter your Groq API key")
    st.stop()

# llm
llm = ChatGroq(groq_api_key=api_key, model_name="meta-llama/llama-4-scout-17b-16e-instruct", streaming=True)

@st.cache_resource(ttl="2h")  # ttl = total time limit
def configure_db(db_uri, mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_uri == LocalDB:
        dbfilepath = (Path(__file__).parent/"student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    
    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            return None
        try:
            # Using pymysql as specified in your original db_uri construction
            engine = create_engine(f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}")
            return SQLDatabase(engine)
        except Exception as e:
            st.error(f"Error connecting to MySQL database: {str(e)}")
            return None

# Configure database connection
try:
    if db_uri == MYSQL:
        db = configure_db(db_uri, mysql_host, mysql_user, mysql_password, mysql_db)
    else:
        db = configure_db(db_uri)
    
    if db is None:
        st.error("Failed to configure database connection")
        st.stop()
        
except Exception as e:
    st.error(f"Database configuration error: {str(e)}")
    st.stop()

## ToolKit
try:
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    
    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION  # Fixed typo: agent_Type -> agent_type
    )
except Exception as e:
    st.error(f"Error creating agent: {str(e)}")
    st.stop()

# Initialize chat messages
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
    
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        try:
            streamlit_callback = StreamlitCallbackHandler(st.container())
            response = agent.run(user_query, callbacks=[streamlit_callback])
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.write(response)
        except Exception as e:
            st.error(f"Error processing query: {str(e)}")