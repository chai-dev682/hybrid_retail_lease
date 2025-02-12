from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from config import ModelType, get_prompt_template, PromptTemplate, get_function_template, FunctionTemplate
from .graph_state import DatabaseEnum, GraphState
from src.tools.str_utils import messages_to_text

model = ChatOpenAI(
    model=ModelType.gpt4o,
)

def extract_function_params(prompt, function):
    function_name = function[0]["function"]["name"]
    arg_name = list(function[0]["function"]["parameters"]['properties'].keys())[0]
    model_ = model.bind_tools(function, tool_choice=function_name)
    messages = [SystemMessage(prompt)]
    tool_call = model_.invoke(messages).tool_calls
    prop = tool_call[0]['args'][arg_name]

    return prop


def query_transformation_node(state: GraphState) -> GraphState:
    prompt = get_prompt_template(PromptTemplate.QUERY_TRANSFER).format(conversation=messages_to_text(state.messages))
    messages = [SystemMessage(prompt)]
    summarized_content = model.invoke(messages).content
    state.query = summarized_content

    return state


def determine_database(state: GraphState) -> DatabaseEnum:
    prompt = get_prompt_template(PromptTemplate.SQL_VECTOR).format(query=state.query, conversation=messages_to_text(state.messages))
    sql_or_vector = get_function_template(FunctionTemplate.SQL_VECTOR)
    is_sql = extract_function_params(prompt=prompt, function=sql_or_vector)
    if is_sql == "yes":
        return DatabaseEnum.MYSQL
    else:
        return DatabaseEnum.VECTORDB


def txt2sql_node(state: GraphState) -> GraphState:
    state.database = DatabaseEnum.MYSQL
    prompt = get_prompt_template(PromptTemplate.GEN_SQL_QUERY).format(query=state.query, conversation=messages_to_text(state.messages))
    messages = [SystemMessage(prompt)]
    generated_sql_query = model.invoke(messages).content
    state.sql_query = generated_sql_query

    return state


def data_retrieval_node(state: GraphState) -> GraphState:
    return state