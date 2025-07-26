from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from langchain_core.prompts import ChatPromptTemplate
from model import *

@dataclass
class WorkflowState:
  user_message: str = ""
  messages: List[Any] = None
  current_state: str = ""
  data: Dict[str, Any] = None
  
class BaseAgent:
  def __init__(self, name):
    self.name = name
    self.role = "BaseAgent"
    self.llm = llm
  
  @abstractmethod
  def process(self,state: WorkflowState)->WorkflowState:
    pass
  
  def add_message(self, state: WorkflowState, msg: str):
    msg = f"{self.name}: {msg}"
    state.messages.append(msg)

class RouterAgent(BaseAgent):
  def __init__(self, name):
    super().__init__(name)
    self.role = "Routing"
    
  def process(self, state: WorkflowState)->WorkflowState:
    prompt = ChatPromptTemplate.from_messages([
      ("system", """You are an helpful routing agent. Use the question for analysis and give a single word routing decision. The routing options are as follows,
        1) web(For searching the web to solve the user's query).
        2) nl2sql(For accessing the database).
        3) general(For llm based reply).
      """),
      ("human","""
      Query: {query}
      
      Please provide the appropriate result based on the user query.
      """)
    ])
    
    chain = prompt | self.llm
    
    response = chain.invoke({
      "query" : state.user_message
    })
    
    web = ['web', 'web search', 'search']
    sql = ['nl2sql', 'sql']
    decision = "general"
    if any(web_token in response.content.lower() for web_token in web):
      decision = "web"
    elif any(sql_token in response.content.lower() for sql_token in sql):
      decision = "nl2sql"
      
    state.current_state = decision
    self.add_message(state, f"Router has decided to go to {decision} agent")
    return state

class WebSearchAgent(BaseAgent):
  def __init__(self, name):
    super().__init__(name)
    self.role = "Web Search"
    
  def process(self, state: WorkflowState)->WorkflowState:
    from websearch import search
    prompt = ChatPromptTemplate.from_messages([
      ("system", """You are an helpful agent. Use the user's query and web search result to give appropriate result.
      """),
      ("human","""
      Query: {query}
      Web Result: {web_result}
      
      Please provide the appropriate result based on the user query and web search result.
      """)
    ])
    
    web_result = search.invoke(state.user_message)
    chain = prompt | self.llm
    response = chain.invoke({
      "query" : state.user_message,
      "web_result": web_result
    })

    state.data['result'] = response.content
    self.add_message(state, response.content)
    state.current_state = "Response"
    return state

class NL2SQLAgent(BaseAgent):
  def __init__(self, name):
    super().__init__(name)
    self.role = "Natural Language Querying"
    
  def process(self, state: WorkflowState)->WorkflowState:
    from db_connection import DatabaseConnect
    from nl2sql import SQLChain
    db = DatabaseConnect()
    chain = SQLChain(db, llm)
    response = chain.invoke({"question":state.user_message})
    state.data['result'] = response
    self.add_message(state, response)
    state.current_state = "Response"
    return state
  
class General(BaseAgent):
    def __init__(self, name):
      super().__init__(name)
      self.role = "General Agent"
      
    def process(self, state: WorkflowState)->WorkflowState:
      prompt = ChatPromptTemplate.from_messages([
          ("system", """You are an helpful assistant providing response to user's query.
          Provide only the data that you have, do not hallucinate and generate fake data.
          """),
          ("human","""
          Query: {query}
          Please provide the appropriate result based on the user query.
          """)
        ])
      
      chain = prompt | self.llm
      
      response = chain.invoke({
          "query" : state.user_message
        })
      state.data['result'] = response.content
      self.add_message(state, response.content)
      state.current_state = "Response"
      return state
      
class RespondAgent(BaseAgent):
  def __init__(self, name):
    super().__init__(name)
    self.role = "Final Response"
    
  def process(self, state: WorkflowState)->WorkflowState:
    state.current_state = "End"
    return state

class WorkflowManager():
  def __init__(self):
    self.router = RouterAgent("RouterAgent")
    self.web_search = WebSearchAgent("WebSearchAgent")
    self.nl2sql = NL2SQLAgent("NL2SQLAgent")
    self.respond = RespondAgent("RespondAgent")
    self.workflow = self._build_workflow()
    
  def _build_workflow(self)->StateGraph:
    workflow = StateGraph(WorkflowState)
    workflow.add_node("router", self._router_node)
    workflow.add_node("web", self._websearch_node)
    workflow.add_node("nl2sql", self._nl2sql_node)
    workflow.add_node("respond", self._respond_node)
    
    workflow.add_edge(START, "router")
    workflow.add_conditional_edges(
      "router",
      lambda state: state.current_state.lower()
    )
    
    workflow.add_edge("web", "respond")
    workflow.add_edge("nl2sql", "respond")
    workflow.add_edge("respond", END)
    
    return workflow.compile()
  
    
  def _router_node(self, state: WorkflowState)->WorkflowState:
    return self.router.process(state)
  
  def _nl2sql_node(self, state: WorkflowState)->WorkflowState:
    return self.nl2sql.process(state)
  
  def _websearch_node(self, state: WorkflowState)->WorkflowState:
    return self.web_search.process(state)
  
  def _respond_node(self, state: WorkflowState)->WorkflowState:
    return self.respond.process(state)
  
  
  def run(self, query: str)->WorkflowState:
    print("Multi-agent System started processing this query", query)
    
    initial_state = WorkflowState(
      user_message=query,
      messages=[],
      current_state="Start(Orchestration)",
      data={}
    )
    result = self.workflow.invoke(initial_state)
    return result