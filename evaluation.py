"""Reproducible routing evaluation; live results are never fabricated."""
import argparse
import csv
import json
from pathlib import Path

from agent import Agent, DocumentStore, EuronLLM, ROOT, sample_documents

# Expectations are hand-labelled requirements, independent of router output.
CASES = [
    ('What is 10 × 20?', 'answer_directly', False),
    ('What is the capital of France?', 'answer_directly', False),
    ('Explain photosynthesis to a student.', 'answer_directly', False),
    ('Write a haiku about the ocean.', 'answer_directly', False),
    ('What is retrieval augmented generation?', 'answer_directly', False),
    ('Give three tips for learning Python.', 'answer_directly', False),
    ('What does our uploaded policy say about refunds?', 'retrieve_documents', False),
    ('What is the return window in our policy?', 'retrieve_documents', False),
    ('Does our policy refund original shipping charges?', 'retrieve_documents', False),
    ('What does the policy say about downloaded digital products?', 'retrieve_documents', False),
    ('How long does refund processing take under our policy?', 'retrieve_documents', False),
    ('How can I contact our support according to the policy?', 'retrieve_documents', False),
    ('Calculate the refund under our policy for an unused product costing 2000 returned 10 days after delivery with a receipt.', 'retrieve_documents', True),
    ('Calculate the refund under our policy for a product costing 800 reported damaged on delivery within 3 days.', 'retrieve_documents', True),
    ('Calculate the refund based on this policy.', 'retrieve_documents', True),
    ('Calculate the total refund under our policy for two unused products priced 100 and 300 returned within 10 days with receipts.', 'retrieve_documents', True),
    ('Calculate (1250 * 0.9) - 20', 'use_another_tool', True),
    ('Calculate 18 percent of 2450.', 'use_another_tool', True),
    ('Calculate compound interest on 1000 at 5 percent annually for 3 years.', 'use_another_tool', True),
    ('Calculate (48 * 37) / 6', 'use_another_tool', True),
    ('Can you explain it?', 'ask_for_clarification', False),
    ('Do it for that one.', 'ask_for_clarification', False),
    ('What is the weather in Delhi right now?', 'ask_for_clarification', False),
    ('Translate this.', 'ask_for_clarification', False),
]


def evaluate(live=False, output=None):
    agent = Agent(DocumentStore(sample_documents()), EuronLLM() if live else None, log_path=None)
    results = []
    for query, route, calculator in CASES:
        result = agent.run(query)
        decision = result['decision'] or {}
        result.update(expected_route=route, expected_calculator=calculator)
        result['passed'] = result['status'] != 'error' and decision.get('route') == route and decision.get('needs_calculator') == calculator
        results.append(result)
        print(f"{'PASS' if result['passed'] else 'FAIL'} | {decision.get('route', 'error')} | {query}")
    passed = sum(r['passed'] for r in results)
    report = {'summary': {'mode': 'live' if live else 'offline_baseline', 'total': len(results), 'passed': passed,
                          'routing_accuracy': passed / len(results),
                          'scope': 'Route and calculator-intent agreement, not answer-quality accuracy. Offline mode does not validate LLM behavior.'},
              'results': results}
    output = Path(output or ROOT / 'results' / ('live.json' if live else 'offline_baseline.json'))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    with output.with_suffix('.csv').open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['question', 'expected_route', 'actual_route', 'expected_calculator', 'actual_calculator', 'tools_used', 'status', 'passed'])
        writer.writeheader()
        for result in results:
            d = result['decision'] or {}
            writer.writerow(dict(question=result['query'], expected_route=result['expected_route'], actual_route=d.get('route'),
                                 expected_calculator=result['expected_calculator'], actual_calculator=d.get('needs_calculator'),
                                 tools_used=','.join(t['name'] for t in result['tools']), status=result['status'], passed=result['passed']))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', help='Use real Euron API calls (may incur charges).')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = evaluate(args.live, args.output)
    print(json.dumps(report['summary'], indent=2))
    raise SystemExit(0 if report['summary']['passed'] == report['summary']['total'] else 1)
