from typing import List
from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from config import ModelType, get_prompt_template, PromptTemplate
from src.tools.str_utils import messages_to_text

from .graph_state import GraphState, DatabaseEnum, Message
from .graph_nodes import query_transformation_node, txt2sql_node, data_retrieval_node, determine_database

from src.tools.db_utils import query_sql
from src.tools.vectordb_utils import query_pinecone

class Agent:

    def __init__(self):
        self.data_retrieval_graph = self._build_data_retrieval_graph()
        self.model = ChatOpenAI(
            model=ModelType.gpt4o,
        )

    @staticmethod
    def _get_initial_state(messages: List[Message], database: DatabaseEnum) -> GraphState:
        return GraphState(
            messages=messages,
            database=database
        )

    @staticmethod
    def _build_data_retrieval_graph():
        workflow = StateGraph(state_schema=GraphState)
        workflow.add_node("query_transformation_node", query_transformation_node)
        workflow.add_node("txt2sql_node", txt2sql_node)
        workflow.add_node("data_retrieval_node", data_retrieval_node)
        workflow.add_conditional_edges("query_transformation_node", determine_database, {
            DatabaseEnum.MYSQL: "txt2sql_node",
            DatabaseEnum.VECTORDB: "data_retrieval_node"
        })

        workflow.set_entry_point("query_transformation_node")
        workflow.set_finish_point("data_retrieval_node")
        workflow = workflow.compile()

        return workflow

    def generate_query(self, messages):
        init_state = self._get_initial_state([Message(role=message["role"], content=message["content"]) for message in messages], DatabaseEnum.VECTORDB)

        result = self.data_retrieval_graph.invoke(init_state)
        return result

    def retrieve_data(self, query, database : DatabaseEnum, conversation):
        result = ""
        if database == DatabaseEnum.MYSQL:
            result = query_sql(query)
        else:
            result = query_pinecone(query, top_k=1)
        prompt = get_prompt_template(PromptTemplate.ANSWER).format(content=result, conversation=messages_to_text(conversation))
        answer = self.model.invoke([SystemMessage(prompt)]).content
        return answer

    def invoke(self, messages):
        query_state = self.generate_query(messages)
        query_state = dict(query_state)
        if query_state["database"] == DatabaseEnum.MYSQL:
            return self.retrieve_data(query_state["sql_query"], DatabaseEnum.MYSQL, query_state["messages"])
        else:
            return self.retrieve_data(query_state["query"], DatabaseEnum.VECTORDB, query_state["messages"])
            