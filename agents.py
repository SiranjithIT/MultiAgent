from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass
from typing import List, Dict, Any
from abc import ABC, abstractmethod

@dataclass
class WorkflowState:
  user_message: str = ""
  messages: List[Any] = None
  current_state: str = ""
  data: Dict[str, Any] = None
  
class BaseAgent:
  pass

class RouterAgent(BaseAgent):
  pass

class WebSearchAgent(BaseAgent):
  pass

class NL2SQL(BaseAgent):
  pass

class WorkflowManager():
  pass