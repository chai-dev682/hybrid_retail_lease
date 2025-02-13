from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from app.core.config import settings, ModelType
from app.db.vectordb import vector_db
from app.db.mysql import mysql_db
from app.core.logging import logger
from app.core.prompt_templates.query_transformation import query_transformation
from app.core.prompt_templates.sql_vector import sql_vector
from app.core.prompt_templates.generate_sql import generate_sql
from app.core.prompt_templates.generate_response import generate_response
from app.core.function_templates.sql_vector import sql_vector_tool
from .graph_state import GraphState, DatabaseEnum

model = ChatOpenAI(
    model=ModelType.gpt4o,
    openai_api_key=settings.OPENAI_API_KEY
)

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

def query_transformation_node(state: GraphState) -> GraphState:    
    response = model.invoke([{
        "role": "user",
        "content": query_transformation.format(
            conversation=format_conversation_history(state.messages),
            query=state.messages[-1]["content"]
        )
    }])
    
    state.query = response.content
    return state

def determine_database(state: GraphState) -> DatabaseEnum:
    is_sql = extract_function_params(prompt=sql_vector.format(query=state.query), function=sql_vector_tool)
    if is_sql == "yes":
        return DatabaseEnum.MYSQL
    else:
        return DatabaseEnum.VECTORDB

def txt2sql_node(state: GraphState) -> GraphState:
    state.database = DatabaseEnum.MYSQL
    response = model.invoke([SystemMessage(generate_sql.format(query=state.query))])
    state.sql_query = response.content.strip()
    return state

def data_retrieval_node(state: GraphState) -> GraphState:
    try:
        if state.database == DatabaseEnum.MYSQL:
            results = mysql_db.query(state.sql_query)
        else:
            results = vector_db.query(state.query, top_k=3)

        context = "\n\n".join(
            "\n".join([
                f"Start Date: {lease.start_date}",
                f"Expiry Date: {lease.expiry_date}",
                f"Rent: ${lease.current_rent_pa:,.2f}/year (in thousands)",
                f"Rent per sqm: ${lease.current_rent_sqm:,.2f}",
                f"Centre: {lease.centre_name}",
                f"Tenant: {lease.lessee}",
                f"Category: {lease.tenant_category}",
                f"Subcategory: {lease.tenant_subcategory}",
                f"Lessor: {lease.lessor}",
                f"Lessee: {lease.lessee}",
                f"Area: {lease.area} sqm"
            ]) for lease in results
        )

        prompt = generate_response.format(
            query=state.query,
            conversation_history=format_conversation_history(state.messages),
            context=context
        )

        response = model.invoke([SystemMessage(prompt)])
        state.messages.append({"role": "assistant", "content": response.content})

    except Exception as e:
        logger.error(f"Error in data retrieval: {str(e)}")
        state.messages.append({
            "role": "assistant",
            "content": "I apologize, but I encountered an error while retrieving the information. Could you please rephrase your question?"
        })

    return state