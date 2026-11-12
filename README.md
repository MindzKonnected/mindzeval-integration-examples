# MindzEval integration examples

Runnable examples that show how to connect a SQL agent built with a given framework to [MindzEval](https://github.com/MindzKonnected/mindzeval), so you can see a real score on a real agent.

Each example is a self-contained folder with its own README and `requirements.txt`. Pick the one that matches your framework, open its folder, and follow its README.

| Example | Framework | What it shows |
|---|---|---|
| [`langgraph/`](langgraph/) | LangGraph | A films SQL agent scored on single questions, a follow-up conversation, clarifying questions, refusals and a display limit |

More examples will be added here.

## How every example works

- The agent code stays as it is. The only MindzEval-specific code is a small adapter that turns MindzEval's question into the agent's input, and the agent's output into a result record.
- `mindzeval.yaml` points MindzEval at the adapter and the database. The test cases are in `cases/`.
- Run `mindzeval lint`, `mindzeval validate` and `mindzeval run` from the example's folder.

## Before you start

- Python 3.11 or newer.
- MindzEval is not on PyPI yet, so each example's `requirements.txt` installs it from GitHub. When it is published, that line becomes plain `mindzeval`.
- The examples call a hosted model, so you need an API key for it. Never commit a key. `.env` is already in `.gitignore`.
- The example databases are small and made up. No real data is involved.
