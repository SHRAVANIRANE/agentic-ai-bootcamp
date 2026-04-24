from langchain_ollama import OllamaLLM
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from app.agents.tools.inventory_tools import (
    get_forecast_summary,
    get_reorder_recommendation,
    list_available_products,
)
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """You are an expert inventory management AI assistant.
You help supply chain managers make data-driven decisions about stock levels and reordering.

You have access to the following tools:
{tools}

Use this format:
Question: the input question
Thought: think about what to do
Action: the action to take, one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Question: {input}
{agent_scratchpad}"""


def build_inventory_agent() -> AgentExecutor:
    settings = get_settings()
    llm = OllamaLLM(
        model=settings.OLLAMA_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=settings.LLM_TEMPERATURE,
    )
    tools = [get_forecast_summary, get_reorder_recommendation, list_available_products]
    prompt = PromptTemplate.from_template(_SYSTEM_PROMPT)
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)
