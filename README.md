# RouteLab — retrieval is a tool, not a mandatory step

A student-friendly selective-RAG application with four visible routing choices, local document retrieval, a restricted calculator, and downloadable routing records. The live agent uses your Euron endpoint through the OpenAI-compatible Python client.

## Run locally

Python 3.11 or newer recommended. From this project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and insert your key. Never commit it.
python -m streamlit run app.py
```

Open http://localhost:8501. Choose **Live Euron LLM** in the sidebar for real model responses. Offline mode works without credentials, but intentionally does not pretend to be an LLM.

```dotenv
EURON_API_KEY=your-real-key
EURON_MODEL=gemini-3.5-flash-lite
```

`EURI_API_KEY` is supported too, matching the supplied example. `EURON_API_KEY` takes precedence. The endpoint is `https://api.euron.one/api/v1/euri`. No key is included in source, logs, or submission artifacts.

Gemini 3.5 Flash-Lite is an appropriate starting model for this routing task: Google's [model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite) lists structured outputs and function calling. Euron availability and account access must be verified with a real key; this project does not assume Google's availability guarantees gateway availability. Change `EURON_MODEL` to an exact model ID enabled in your Euron account if necessary. No silent model substitutions occur.

## What happens for a query?

1. The live router receives the question and a boolean indicating document availability. It returns a validated JSON decision and a short explanation.
2. `answer_directly` generates an answer without searching. Simple arithmetic such as `10 × 20` uses this route.
3. `retrieve_documents` searches paragraph chunks using BM25-style lexical scoring. Only matching passages are sent to the answer model, with source IDs.
4. `use_another_tool` prepares an arithmetic expression and executes it with a bounded AST calculator. Python `eval` is never used.
5. `ask_for_clarification` returns a question without retrieval. Unsupported weather/account actions also request usable data or context.

A policy calculation uses `retrieve_documents` plus `needs_calculator=true`: retrieve → derive a supported expression → calculate. Missing price or eligibility triggers clarification after retrieval. The log separates **planned tools** from **actually executed tools**. A calculator flag does not mean a calculator was executed.

The application orchestrates these steps itself using chat completion JSON. It does not depend on the gateway implementing native function-calling parameters. Unparseable output fails visibly rather than switching to the offline baseline.

## Test and export routing results

```powershell
python -m pytest -q
python evaluation.py
python evaluation.py --live
```

- `results/offline_baseline.json` and `.csv`: 24 executed offline questions with independently labelled expected routes. These are **not live LLM results**.
- `results/live.json` and `.csv`: generated only when you run `--live` with a valid key. Live evaluation makes multiple paid API requests per question.
- `logs/queries.jsonl`: local append-only app records when logging is enabled. Includes timestamps, mode, model, route, rationale, actual tools, evidence, answer, status, and latency.
- The UI offers a session JSON download. Each question is independent; there is no hidden conversation memory. Re-enter complete context after clarification.

Evaluation accuracy measures agreement on route **and calculator intent**, not answer quality. Tests also exercise tool order, missing documents, missing calculation inputs, malformed decisions, calculator restrictions, and the Streamlit UI. Scripted test doubles test orchestration, not model intelligence.

## Project map

| File | Purpose |
| --- | --- |
| `app.py` | Three-tab classroom interface |
| `agent.py` | Router, Euron client, retrieval, calculator, executor, logging |
| `evaluation.py` | 24-question dataset and CSV/JSON evaluation runner |
| `documents/refund_policy.md` | Fictional teaching policy |
| `tests/test_agent.py` | Offline and integration-style checks |
| `docs/TEACHING_GUIDE.md` | Classroom lesson and exercises |
| `docs/YOUTUBE_SCRIPT.md` | Recording script and shot list |
| `docs/SUBMISSION.md` | GitHub and YouTube handoff steps |

## Teaching boundaries

Uploads support UTF-8 TXT/Markdown, not PDF. Paragraph retrieval is local and needs no embedding service, but lexical matching can miss synonyms or relevant exceptions. Retrieved scores are ranking scores, not confidence probabilities. Review all relevant policy sections before relying on a result; this is a classroom prototype, not a refund approval system.

The calculator guarantees execution of a restricted numeric expression, not correctness of an LLM-selected formula. Prompts instruct the model to treat documents as untrusted evidence; this reduces but does not eliminate prompt injection. Do not expose this local prototype as a public service without authentication, access controls, and operational hardening.

Questions and retrieved passages are sent to Euron in live mode. Query logs contain user content and are ignored by Git. Sample evaluation results contain only fictional public classroom examples. Review live output before sharing it.
