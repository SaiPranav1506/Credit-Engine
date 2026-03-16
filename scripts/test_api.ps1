$gst = Get-Item 'credit_engine/data/gst_transactions.csv'
$bank = Get-Item 'credit_engine/data/bank_statements.csv'
$form = @{applicant_name = 'Test Corp'; officer_notes = 'Testing'; gst_file = $gst; bank_file = $bank}
$response = Invoke-RestMethod -Uri 'http://localhost:5000/api/process-application' -Method Post -Form $form -TimeoutSec 120
$response | ConvertTo-Json -Depth 5
