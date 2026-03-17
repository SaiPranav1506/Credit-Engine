import requests
import json

payload = {
    'company_name': 'Test Company LLC',
    'revenue': 50000,
    'net_profit': 10000,
    'debt_to_equity': 0.5,
    'fraud_score': 10
}

try:
    response = requests.post('http://localhost:5000/api/process-application', json=payload, timeout=30)
    print(f'Status: {response.status_code}')
    print(f'Content Type: {response.headers.get("content-type")}')
    if response.status_code == 200:
        result = response.json()
        print(f'\nDecision: {result.get("decision", "N/A")}')
        print(f'Score: {result.get("credit_score", "N/A")}')
        print(f'Status: {result.get("status", "N/A")}')
        print(f'\nFull Response:')
        print(json.dumps(result, indent=2))
    else:
        print(f'Error: {response.text[:500]}')
except Exception as e:
    print(f'Error: {e}')
