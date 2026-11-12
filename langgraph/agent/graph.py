"""A small LangGraph SQL agent over films.db. This is "your agent": MindzEval doesn't change it.

    plan --(answer)--> run_sql --> summarize --> END
      \\--(clarify / decline)--> END
"""

import re
import sqlite3
from pathlib import Path
from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from agent.llm import get_llm

DB_PATH = Path(__file__).parent.parent / "films.db"
ROW_LIMIT = 50  # the agent only ever shows 50 rows to the user

PROMPT = """You answer questions about a films database with SQLite SQL.
Table: films(id, title, genre, country, release_year, rating)
Genres: Sci-Fi, Drama, Comedy, Action, Documentary.

Decide what to do with the user's latest message, using the whole conversation:
- answer: write one read-only SELECT query that answers it. Counts and totals are fine
  (use COUNT or SUM). Follow-ups such as "just the ones from Spain" or "how many is that?"
  refer to the earlier questions.
- clarify: the request is too vague to query; ask one short question
- decline: the request is not about films in this database (for example the weather);
  say so politely
When listing films, select id and title, plus any column the question filters on."""


class Plan(BaseModel):
    status: Literal["answer", "clarify", "decline"]
    sql: str | None = None
    message: str = ""  # the clarifying question or the refusal text
    reason: str | None = None  # a short label, e.g. AMBIGUOUS_REQUEST


class AgentState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], add_messages]
    status: str
    reason: str | None
    sql: str | None
    columns: list[str]
    rows: list[list]


def plan(state: AgentState, config: RunnableConfig):
    model = config.get("configurable", {}).get("model")
    planner = get_llm(model).with_structured_output(Plan)
    result = planner.invoke([SystemMessage(PROMPT), *state["messages"]])
    status, message = result.status, result.message
    if status == "answer" and not result.sql:  # the model chose "answer" but wrote no query
        status, message = "clarify", "I couldn't turn that into a query. Could you rephrase it?"
    update = {"status": status, "reason": result.reason, "sql": result.sql}
    if status != "answer":
        update["messages"] = [AIMessage(message)]
    return update


def run_sql(state: AgentState):
    sql = state["sql"].strip().rstrip(";")
    if not re.search(r"\blimit\b", sql, re.IGNORECASE):
        sql = f"{sql} LIMIT {ROW_LIMIT}"
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        cursor = db.execute(sql)
        columns = [c[0] for c in cursor.description]
        rows = [list(r) for r in cursor.fetchall()]
    except sqlite3.Error:
        return {"sql": sql, "messages": [AIMessage("Sorry, I couldn't run that query.")]}
    finally:
        db.close()
    return {"sql": sql, "columns": columns, "rows": rows}


def summarize(state: AgentState, config: RunnableConfig):
    model = config.get("configurable", {}).get("model")
    capped = len(state["rows"]) >= ROW_LIMIT
    prompt = (
        f"Question: {state['messages'][-1].content}\n"
        f"Columns: {state['columns']}\nRows ({len(state['rows'])} returned): {state['rows']}\n"
        "A query has already applied the conditions in the question, so every row matches them. "
        "Answer in one or two sentences."
        + (f" Only the first {ROW_LIMIT} rows are shown; say the full list may be longer." if capped else "")
    )
    return {"messages": [AIMessage(get_llm(model).invoke(prompt).content)]}


def after_plan(state: AgentState):
    return "run_sql" if state["status"] == "answer" else END


def after_sql(state: AgentState):
    return "summarize" if state.get("rows") is not None else END


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan)
    graph.add_node("run_sql", run_sql)
    graph.add_node("summarize", summarize)
    graph.add_edge(START, "plan")
    graph.add_conditional_edges("plan", after_plan)
    graph.add_conditional_edges("run_sql", after_sql)
    graph.add_edge("summarize", END)
    return graph.compile()
