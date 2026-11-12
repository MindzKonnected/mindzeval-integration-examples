"""The only new code: translate between MindzEval and the LangGraph agent."""

from agent.graph import build_graph

graph = build_graph()  # build once, reuse for every case


async def answer(question, history, params):
    # MindzEval sends earlier turns of the same case in `history`. This graph has no
    # checkpointer, so we pass the whole conversation ourselves.
    messages = [(m["role"], m["content"]) for m in history] + [("user", question)]
    state = await graph.ainvoke(
        {"messages": messages},
        config={"configurable": {"model": params.get("model")}},
    )
    return {
        "answer": state["messages"][-1].content,
        "sql": state.get("sql"),
        "status": state["status"],  # answer | clarify | decline
        "reason": state.get("reason"),
    }
