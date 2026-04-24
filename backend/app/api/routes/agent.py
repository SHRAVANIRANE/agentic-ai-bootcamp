import asyncio
from fastapi import APIRouter
from app.models.schemas import AgentChatRequest, AgentChatResponse
from app.agents.inventory_agent import build_inventory_agent

router = APIRouter(prefix="/agent", tags=["Agent"])

_agent_executor = None


def _get_agent():
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = build_inventory_agent()
    return _agent_executor


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(req: AgentChatRequest) -> AgentChatResponse:
    agent = _get_agent()
    context = req.message
    if req.store_id:
        context += f" (Store: {req.store_id})"
    if req.product_id:
        context += f" (Product: {req.product_id})"

    # AgentExecutor.invoke is sync — run in thread pool to avoid blocking event loop
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: agent.invoke({"input": context}))
    return AgentChatResponse(
        response=result["output"],
        actions_taken=[str(step) for step in result.get("intermediate_steps", [])],
    )
