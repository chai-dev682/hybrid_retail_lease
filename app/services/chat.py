from typing import List, Dict
from langgraph.graph import StateGraph, START
from langchain_openai import ChatOpenAI
from app.core.config import settings, ModelType
from app.services.graph.graph_state import GraphState
from app.services.graph.graph_nodes import (
    write_query,
    execute_query,
    generate_answer,
    visualization_node
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
        workflow.add_node("write_query", write_query)
        workflow.add_node("execute_query", execute_query)
        workflow.add_node("generate_answer", generate_answer)
        workflow.add_node("visual_show", visualization_node)
        
        # Add edges
        workflow.add_edge(START, "write_query")
        workflow.add_edge("write_query", "execute_query")
        workflow.add_edge("execute_query", "generate_answer")
        workflow.add_edge("generate_answer", "visual_show")
        
        workflow.set_finish_point("visual_show")
        
        return workflow.compile()

    def process_message(self, query: str, conversation_history: List[Dict[str, str]]) -> str:
        messages = conversation_history + [{"role": "user", "content": query}]
        initial_state = GraphState(messages=messages, query=query)
        
        final_state = self.data_retrieval_graph.invoke(initial_state)
        
        return {"response": final_state["messages"][-1]["content"],
                "visualization": final_state["visualization"]}

chat_service = ChatService()