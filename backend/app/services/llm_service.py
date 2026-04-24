import asyncio
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_TREND_EXPLANATION_TEMPLATE = """
You are a senior inventory analyst. Given the following demand data for a retail product,
provide a clear, concise explanation (3-4 sentences) of the demand trend and seasonality.

Product: {product_id} | Store: {store_id}
Trend direction: {trend_direction}
Average weekly demand: {avg_demand:.1f} units
Peak demand period: {peak_period}
Key demand drivers (SHAP): {top_drivers}
Seasonality pattern: {seasonality}

Explain what is driving demand and what the business should watch for.
""".strip()

_REORDER_REASONING_TEMPLATE = """
You are a supply chain expert. Explain the reorder recommendation below in plain business language (2-3 sentences).

Product: {product_id} | Store: {store_id}
Current inventory: {current_inventory} units
Forecasted demand (next {lead_time} days): {forecasted_demand:.0f} units
Reorder point: {reorder_point} units
Safety stock: {safety_stock} units
Recommended order quantity: {recommended_qty} units

Provide a clear business justification for this recommendation.
""".strip()

# Fallback explanations when LLM is unavailable
def _trend_fallback(ctx: dict) -> str:
    return (
        f"Demand for {ctx['product_id']} at {ctx['store_id']} shows a {ctx['trend_direction']} trend "
        f"with an average of {ctx['avg_demand']:.1f} units/day. "
        f"Peak demand is expected around {ctx['peak_period']}. "
        f"Key drivers are {ctx['top_drivers']}."
    )

def _reorder_fallback(ctx: dict) -> str:
    return (
        f"With {ctx['current_inventory']} units in stock and {ctx['forecasted_demand']:.0f} units "
        f"forecasted over the next {ctx['lead_time']} days, "
        f"ordering {ctx['recommended_qty']} units maintains the {ctx['safety_stock']}-unit safety stock buffer."
    )


class LLMService:
    LLM_TIMEOUT = 30  # seconds

    def __init__(self):
        settings = get_settings()
        self.llm = OllamaLLM(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
        )
        self._trend_chain = (
            PromptTemplate.from_template(_TREND_EXPLANATION_TEMPLATE)
            | self.llm
            | StrOutputParser()
        )
        self._reorder_chain = (
            PromptTemplate.from_template(_REORDER_REASONING_TEMPLATE)
            | self.llm
            | StrOutputParser()
        )

    async def explain_trend(self, context: dict) -> str:
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: self._trend_chain.invoke(context)),
                timeout=self.LLM_TIMEOUT,
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("LLM trend explanation timed out — using fallback")
            return _trend_fallback(context)
        except Exception as e:
            logger.error("LLM trend explanation failed: %s", e)
            return _trend_fallback(context)

    async def explain_reorder(self, context: dict) -> str:
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, lambda: self._reorder_chain.invoke(context)),
                timeout=self.LLM_TIMEOUT,
            )
            return result
        except asyncio.TimeoutError:
            logger.warning("LLM reorder explanation timed out — using fallback")
            return _reorder_fallback(context)
        except Exception as e:
            logger.error("LLM reorder explanation failed: %s", e)
            return _reorder_fallback(context)
