from langchain_community.utilities.sql_database import SQLDatabase
import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyDTXKlJq27fF0AiTvw7rK302TLCzNVwFQw"
from langchain.chains import create_sql_query_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
 
 
def chat_with_sql(query):
 
    # db= SQLDatabase.from_uri("mysql+mysqlconnector://root:root123@192.119568.0.:3306/antony")
    db= SQLDatabase.from_uri("mysql+mysqlconnector://root:root123@localhost:3306/antony")
    llm = ChatGoogleGenerativeAI(model='gemini-pro',temperature=0)
    generate_query = create_sql_query_chain(llm,db)
 
    answer_prompt = PromptTemplate.from_template(
     """Given the following user question, corresponding SQL query, and SQL result, answer the user question with some neat description.
 
 Question: {question}
 SQL Query: {query}
 SQL Result: {result}
 Answer: """
)
    rephrase_answer = answer_prompt|llm|StrOutputParser()
    execute_query = QuerySQLDataBaseTool(db=db)
    chain = (RunnablePassthrough.assign(query=generate_query).assign(
    result = itemgetter('query')|execute_query
    )|rephrase_answer
    )
 
    return chain.invoke({'question':f'Provide me only the query dont give any other additional words such as sql to the human {query}'})