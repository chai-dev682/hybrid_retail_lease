from typing import List, Dict
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from app.core.config import settings, ModelType
from app.services.graph.graph_state import GraphState, DatabaseEnum
from app.services.graph.graph_nodes import (
    query_transformation_node,
    determine_database,
    txt2sql_node,
    data_retrieval_node
)

class ChatService:
    def __init__(self):
        self.data_retrieval_graph = self._build_data_retrieval_graph()
        self.model = ChatOpenAI(
            model=ModelType.gpt4o,
            openai_api_key=settings.OPENAI_API_KEY
        )

    def _build_data_retrieval_graph(self):
        workflow = StateGraph(state_schema=GraphState)
        
        # Add nodes
        workflow.add_node("query_transformation", query_transformation_node)
        workflow.add_node("txt2sql", txt2sql_node)
        workflow.add_node("data_retrieval", data_retrieval_node)
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "query_transformation",
            determine_database,
            {
                DatabaseEnum.MYSQL: "txt2sql",
                DatabaseEnum.VECTORDB: "data_retrieval"
            }
        )

        # Add edges
        workflow.add_edge("txt2sql", "data_retrieval")

        workflow.set_entry_point("query_transformation")
        workflow.set_finish_point("data_retrieval")
        
        return workflow.compile()

    def process_message(self, query: str, conversation_history: List[Dict[str, str]]) -> str:
        messages = conversation_history + [{"role": "user", "content": query}]
        initial_state = GraphState(messages=messages)
        
        final_state = self.data_retrieval_graph.invoke(initial_state)
        return final_state["messages"][-1]["content"]

chat_service = ChatService()