import json

import pytest

from agent import Agent, DocumentStore, ROOT, calculate, sample_documents
from evaluation import CASES


class FakeLLM:
    model = 'scripted-test-double'

    def __init__(self, *responses):
        self.responses = iter(responses)

    def complete(self, *args):
        return next(self.responses)


def decision(route, calculator=False):
    return {'route': route, 'reason': 'Test decision', 'needs_calculator': calculator,
            'retrieval_query': 'refund calculation product price', 'clarification': 'Which product?'}


@pytest.mark.parametrize('query,route,calculator', CASES)
def test_offline_routing(query, route, calculator):
    result = Agent(DocumentStore(sample_documents()), log_path=None).run(query)
    assert result['status'] != 'error'
    assert result['decision']['route'] == route
    assert result['decision']['needs_calculator'] == calculator
    assert bool(result['sources']) == (route == 'retrieve_documents')


@pytest.mark.parametrize('expression', ['__import__("os")', '(1).__class__', '2 ** 1000000', '[1]', 'True', '1e309', '9' * 201])
def test_calculator_rejects_unsafe_input(expression):
    with pytest.raises((ValueError, SyntaxError)):
        calculate(expression)


def test_calculator():
    assert calculate('(1250 * 0.9) - 20') == 1105
    assert calculate('-4 + 2 ** 3') == 4
    with pytest.raises(ZeroDivisionError):
        calculate('1/0')


def test_direct_never_searches(monkeypatch):
    store = DocumentStore(sample_documents())
    monkeypatch.setattr(store, 'search', lambda *a: pytest.fail('Direct answers must not retrieve'))
    result = Agent(store, FakeLLM(decision('answer_directly'), '200'), None).run('What is 10 × 20?')
    assert result['answer'] == '200'
    assert result['tools'] == []


def test_policy_calculator_order():
    llm = FakeLLM(decision('retrieve_documents', True), {'expression': '2000 * 0.9', 'explanation': '90% refund'})
    result = Agent(DocumentStore(sample_documents()), llm, None).run('Calculate eligible policy refund for 2000')
    assert [t['name'] for t in result['tools']] == ['retrieve_documents', 'calculator']
    assert result['tools'][1]['result'] == 1800


def test_missing_amount_does_not_calculate():
    llm = FakeLLM(decision('retrieve_documents', True), {'expression': None, 'clarification': 'What was the product price?'})
    result = Agent(DocumentStore(sample_documents()), llm, None).run('Calculate policy refund')
    assert result['status'] == 'needs_clarification'
    assert len(result['tools']) == 1


def test_missing_documents():
    result = Agent(DocumentStore({}), FakeLLM(decision('retrieve_documents')), None).run('Explain our policy')
    assert result['sources'] == []
    assert result['status'] == 'needs_clarification'


def test_calculator_only():
    llm = FakeLLM(decision('use_another_tool', True), {'expression': '48*37/6'})
    result = Agent(DocumentStore({}), llm, None).run('Calculate 48*37/6')
    assert [t['name'] for t in result['tools']] == ['calculator']
    assert result['tools'][0]['result'] == 296


def test_error_is_logged_without_provider_details(tmp_path):
    log = tmp_path / 'queries.jsonl'
    result = Agent(DocumentStore({}), FakeLLM({'route': 'invented'}), log).run('Hello there')
    assert result['status'] == 'error'
    assert json.loads(log.read_text())['query'] == 'Hello there'
    assert result['decision'] is None


def test_unrelated_document_not_returned():
    assert DocumentStore({'recipe.txt': 'Bananas and mangoes make a smoothie.'}).search('refund eligibility') == []


def test_ui_smoke():
    from streamlit.testing.v1 import AppTest
    app = AppTest.from_file(ROOT / 'app.py', default_timeout=15).run()
    assert not app.exception
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state['history'][-1]['answer'] == '200'
