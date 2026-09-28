"""Run with: python -m streamlit run app.py"""
import json
import os

from dotenv import load_dotenv
import streamlit as st

from agent import Agent, DocumentStore, EuronLLM, LABELS, ROOT, sample_documents

st.set_page_config(page_title='RouteLab • Selective RAG', page_icon='🧭', layout='wide')
st.markdown('''<style>
.stApp {background: #0b1120; color: #e5edf9;}
h1,h2,h3 {letter-spacing: -.035em;}
[data-testid="stMetric"] {background: #162136; border: 1px solid #293a56; padding: 18px; border-radius: 14px;}
[data-testid="stSidebar"] {background: #111b2d;}
</style>''', unsafe_allow_html=True)
st.caption('ROUTELAB / AN INTERACTIVE AGENT CLASSROOM')
st.title('A good agent knows when to look things up.')
st.write('Ask a question. Inspect the route. See exactly which tools were used.')

with st.sidebar:
    st.header('Your classroom')
    mode = st.radio('Execution mode', ['Offline teaching baseline', 'Live Euron LLM'])
    model = st.text_input('Euron model', os.getenv('EURON_MODEL', 'gemini-3.5-flash-lite'))
    st.caption('Live mode reads EURON_API_KEY or EURI_API_KEY from your local .env. No key is embedded in the app.')
    include_sample = st.checkbox('Include fictional refund policy', value=True)
    uploads = st.file_uploader('Add lesson documents (.txt / .md)', type=['txt', 'md'], accept_multiple_files=True)
    st.caption('Supported: UTF-8 text and Markdown, up to 1 MB each. Uploaded documents stay in memory; retrieved passages are sent to Euron in live mode.')
    persist = st.checkbox('Save query logs on this computer', value=True)
    st.caption('Logs contain questions, answers, and retrieved passages. Keep classroom examples free of personal data.')

documents = sample_documents() if include_sample else {}
for index, upload in enumerate(uploads):
    if upload.size > 1_000_000:
        st.sidebar.error(f'{upload.name}: exceeds 1 MB.')
        continue
    try:
        documents[f'upload-{index + 1}-{upload.name}'] = upload.getvalue().decode('utf-8')
    except UnicodeDecodeError:
        st.sidebar.error(f'{upload.name}: save the file as UTF-8 text.')
store = DocumentStore(documents)
if 'history' not in st.session_state:
    st.session_state.history = []

learn, ask, results = st.tabs(['01 / Understand the routes', '02 / Try the agent', '03 / Routing results'])
with learn:
    columns = st.columns(4)
    cards = [
        ('01 · Answer directly', 'General knowledge or simple arithmetic.', 'What is 10 × 20?'),
        ('02 · Retrieve documents', 'The answer depends on your documents.', 'What does our policy say about refunds?'),
        ('03 · Use another tool', 'A calculator can compute a precise result.', 'Calculate (1250 * 0.9) - 20'),
        ('04 · Ask for clarification', 'The agent needs context or a supported task.', 'Can you explain it?'),
    ]
    for column, (title, description, example) in zip(columns, cards):
        with column:
            st.subheader(title)
            st.write(description)
            st.caption(example)
    st.divider()
    st.subheader('Retrieval is a choice, not a prerequisite')
    st.write('Question → routing decision → selected tools → answer + recorded evidence')
    st.info('A policy-based calculation follows two steps: retrieve the policy, then use the calculator. It is recorded under Retrieve Documents with an additional calculator flag.')
    st.write('The live router sees your question and whether documents are available. It chooses one of four routes and provides a short explanation. Only the retrieval route searches the document collection.')
    st.warning('Offline mode uses simple rules to demonstrate the interface. It is not a live LLM and does not generate policy interpretations. Lexical retrieval matches words, so synonyms and conflicting policies may require clarification.')
    with st.expander('Read the teaching policy'):
        st.markdown(next(iter(sample_documents().values())))

with ask:
    examples = ['What is 10 × 20?', 'What does our uploaded policy say about refunds?',
                'Calculate the refund under our policy for an unused product costing 2000 returned 10 days after delivery with a receipt.',
                'Calculate (1250 * 0.9) - 20', 'Can you explain it?']
    selected = st.selectbox('Start with an example', examples)
    with st.form('question'):
        question = st.text_area('Your question', value=selected, max_chars=8000, height=110)
        submitted = st.form_submit_button('Run agent →', type='primary')
    if submitted:
        load_dotenv(override=True)
        try:
            llm = EuronLLM(model) if mode == 'Live Euron LLM' else None
        except ValueError as error:
            st.error(str(error))
        else:
            with st.spinner('Choosing a route and running the selected tools…'):
                outcome = Agent(store, llm, ROOT / 'logs' / 'queries.jsonl' if persist else None).run(question)
            st.session_state.history.append(outcome)
    if st.session_state.history:
        outcome = st.session_state.history[-1]
        decision = outcome['decision'] or {}
        a, b, c = st.columns(3)
        a.metric('Selected route', LABELS.get(decision.get('route'), 'Routing failed'))
        b.metric('Tool calls', len(outcome['tools']))
        c.metric('Elapsed', f"{outcome['latency_ms']:,.0f} ms")
        st.caption(f"Recorded mode: {outcome['mode']} · Model: {outcome['model'] or 'rule baseline'} · Status: {outcome['status']}")
        st.write(decision.get('reason', 'No valid routing decision was returned.'))
        st.subheader('Answer')
        st.markdown(outcome['answer'])
        with st.expander('Inspect retrieved evidence and tool calls', expanded=bool(outcome['tools'])):
            for source in outcome['sources']:
                st.caption(f"{source['id']} · lexical score {source['score']}")
                st.text(source['text'])
            st.json(outcome['tools'])
        with st.expander('Full routing record'):
            st.json(outcome)

with results:
    st.subheader('Every question leaves a routing record')
    history = st.session_state.history
    st.caption('This table contains this browser session. Persistent JSONL logs are stored separately in logs/ when enabled.')
    if history:
        st.dataframe([{'question': x['query'], 'route': (x['decision'] or {}).get('route', 'error'),
                       'mode': x['mode'], 'tools': ', '.join(t['name'] for t in x['tools']),
                       'status': x['status']} for x in history], hide_index=True, use_container_width=True)
        st.download_button('Download session JSON', json.dumps(history, indent=2), 'routing-session.json', 'application/json')
    else:
        st.info('Run a question in the second tab to start your own routing log.')
    baseline = ROOT / 'results' / 'offline_baseline.json'
    if baseline.exists():
        with st.expander('View the included 24-question offline evaluation'):
            report = json.loads(baseline.read_text(encoding='utf-8'))
            st.write(report['summary'])
            st.dataframe([{'question': r['query'], 'expected': r['expected_route'],
                           'actual': (r['decision'] or {}).get('route'), 'passed': r['passed']} for r in report['results']], hide_index=True)
