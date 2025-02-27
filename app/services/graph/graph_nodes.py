from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
import pandas as pd

from app.core.config import settings, ModelType
from app.core.prompt_templates.generate_sql import generate_sql
from app.db.mysql import mysql_db
from .graph_state import GraphState, QueryOutput

model = ChatOpenAI(
    model=ModelType.gpt4o,
    openai_api_key=settings.OPENAI_API_KEY
)

db = SQLDatabase(mysql_db._get_engine())

def extract_function_params(prompt, function):
    function_name = function[0]["function"]["name"]
    arg_name = list(function[0]["function"]["parameters"]['properties'].keys())[0]
    model_ = model.bind_tools(function, tool_choice=function_name)
    messages = [SystemMessage(prompt)]
    tool_call = model_.invoke(messages).tool_calls
    prop = tool_call[0]['args'][arg_name]

    return prop

def format_conversation_history(messages: List[Dict[str, str]]) -> str:
    return "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

def write_query(state: GraphState) -> GraphState:
    """Generate SQL query to fetch information."""
    prompt = generate_sql.format(
        dialect=db.dialect,
        top_k=10,
        table_info=db.get_table_info(),
        input=state.query
    )
    structured_llm = model.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    state.sql_query = result["query"]
    print(state.sql_query)
    return state

def execute_query(state: GraphState) -> GraphState:
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    state.result = execute_query_tool.invoke(state.sql_query)
    print(state.result)
    return state

def generate_answer(state: GraphState) -> GraphState:
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state.query}\n'
        f'SQL Query: {state.sql_query}\n'
        f'SQL Result: {state.result}'
    )
    response = model.invoke(state.messages + [HumanMessage(prompt)])
    state.messages.append({"role": "assistant", "content": response.content})
    print(response.content)
    return state

def visualization_node(state: GraphState) -> GraphState:
    if not state.result:
        state.visualization = {"show": False}
        return state

    # Define visualization function
    visualization_function = {
        "name": "determine_visualization",
        "description": "Determine the best visualization type for the given data and query",
        "parameters": {
            "type": "object",
            "properties": {
                "visualization_type": {
                    "type": "string",
                    "enum": ["bar", "line", "table", "none"],
                    "description": "Type of visualization to show. 'bar' for comparisons, 'line' for trends, 'table' for raw data, 'none' for no visualization"
                },
                "x_axis": {
                    "type": "string",
                    "description": "Field to use for x-axis"
                },
                "y_axis": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Fields to use for y-axis"
                }
            },
            "required": ["visualization_type"]
        }
    }

    # Get visualization recommendation from LLM
    model_with_tools = model.bind_tools([visualization_function])
    response = model_with_tools.invoke(state.messages + [HumanMessage(f"Query: {state.query}\n SQL Query: {state.sql_query}")])

    # Parse the function call
    if response.tool_calls:
        args = response.tool_calls[0]['args']
        state.visualization = {
            "show": args["visualization_type"] != "none",
            "type": args["visualization_type"],
            "data": pd.DataFrame(state.result),
            "x": args.get("x_axis", ""),
            "y": args.get("y_axis", [])
        }
    else:
        state.visualization = {"show": False}
    print(state.visualization)
    return state