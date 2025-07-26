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
        1) web search(For searching the web to solve the user's query).
        2) nl2sql(For accessing the database).
        3) general(For llm based reply).
      """),
      ("human","""
      Question: {query}
      
      Please provide the comprehensive answer for the question based on the context.
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
      decision = "web search"
    elif any(sql_token in response.content.lower() for sql_token in sql):
      decision = "nl2sql"
      
    state.current_state = decision
    self.add_message(state, f"Router has decided to go to {decision} agent")
    return state

class WebSearchAgent(BaseAgent):
  pass

class NL2SQLAgent(BaseAgent):
  pass

class FormatAgent(BaseAgent):
  pass

class WorkflowManager():
  pass