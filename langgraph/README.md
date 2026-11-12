# MindzEval + LangGraph example

Part of [MindzEval integration examples](../README.md). Run every command below from this `langgraph/` folder.

A small LangGraph SQL agent over a films database, and the few files that connect it to [MindzEval](https://github.com/MindzKonnected/mindzeval). Run it to see MindzEval score a real agent on single questions, a follow-up conversation, and questions the agent should ask about or decline.

The agent code (`agent/`) knows nothing about MindzEval. The only file added for it is `eval_adapter.py`, about 15 lines.

## What you need

- Python 3.11 or newer
- An OpenAI API key (a run makes at most 18 calls to `gpt-4o-mini` and takes about 30 seconds)

## Run it

**macOS / Linux**

```bash
git clone https://github.com/MindzKonnected/mindzeval-integration-examples.git
cd mindzeval-integration-examples/langgraph
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key"
python setup_db.py
mindzeval run
```

**Windows (PowerShell)**

```powershell
git clone https://github.com/MindzKonnected/mindzeval-integration-examples.git
cd mindzeval-integration-examples/langgraph
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:OPENAI_API_KEY = "your-key"
python setup_db.py
mindzeval run
```

`setup_db.py` creates `films.db` with 200 made-up films, so no real data is involved.

## What you should see

Results vary a little between runs because the model's wording changes. Typically:

- 9 turns, 7 pass, 2 fail
- Both failures have the cause `truncated`: the agent shows at most 50 rows, and two questions have more matching films (107 and 76). The agent's SQL was right, and MindzEval reports that (`uncapped accuracy 100%`, `correct but capped 2`).
- Behaviour accuracy 100%: it asks for clarification on "Show me the data", declines the weather question, and answers the clear question about Japanese films.
- The run exits with code 0, because the thresholds in `mindzeval.yaml` are met.

Open the HTML report in `mindzeval-results/` to see every turn, the SQL, and why each verdict was given.

## What is in the box

| File | What it is |
|---|---|
| `agent/graph.py` | The LangGraph agent: plan, run SQL, summarise. This is "your agent" |
| `agent/llm.py` | The model it uses. Swap in any LangChain chat model |
| `eval_adapter.py` | The only MindzEval-specific code. Turns a question and history into graph input, and the graph state into a result record |
| `mindzeval.yaml` | Points MindzEval at the adapter and the database, and sets pass thresholds |
| `cases/films.yaml` | The test cases: single turn, multi-turn, clarify, decline, and a negative control |
| `setup_db.py` | Builds the sample database |

## Try changing things

- **Check the setup without calling the model:** `mindzeval lint` checks the config and cases. `mindzeval validate` runs each reference query against the database.
- **See what would run:** `mindzeval run --list`
- **Run one case:** `mindzeval run --case scifi_from_spain`
- **Compare models:** add this to `mindzeval.yaml`, then run again. Every combination runs and the report compares them.

  ```yaml
  matrix:
    model: [gpt-4o-mini, gpt-4o]
  ```
- **Break the agent on purpose:** edit the prompt in `agent/graph.py` and see which cases change.
- **Use your own agent:** replace the graph, keep the adapter's shape, and point `database.url` at a read-only login.

## Troubleshooting

- **Every turn fails with `agent_crash`, mentioning the API key:** `OPENAI_API_KEY` isn't set in the terminal you ran `mindzeval` from.
- **`mindzeval: command not found`:** the virtual environment isn't active.
- **`SQLite database file not found`:** run `python setup_db.py` first.

## Notes

- MindzEval is not on PyPI yet, which is why `requirements.txt` installs it from GitHub.
- Never commit your API key. `.env` and the generated files are already in `.gitignore`.
