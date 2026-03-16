import requests

url = 'http://localhost:5000/api/process-application'
files = {
    'gst_file': open('credit_engine/data/gst_transactions.csv', 'rb'),
    'bank_file': open('credit_engine/data/bank_statements.csv', 'rb'),
}
data = {
    'applicant_name': 'Test Corp',
    'officer_notes': 'Testing upload'
}

try:
    r = requests.post(url, files=files, data=data, timeout=120)
    print('status', r.status_code)
    print(r.text)
except Exception as e:
    print('error', e)
finally:
    for f in files.values():
        f.close()
