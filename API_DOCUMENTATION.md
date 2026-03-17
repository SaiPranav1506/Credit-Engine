# API Documentation - Credit Engine

## Base URL

**Development**: `http://localhost:5000`  
**Production**: `https://api.yourdomain.com`

---

## Endpoints

### 1. Health Check ✅

**Endpoint**: `GET /api/health`

**Description**: Check if the API is running and healthy

**Parameters**: None

**Response**:
```json
{
  "status": "healthy",
  "message": "Credit Engine API is running"
}
```

**Example**:
```bash
curl http://localhost:5000/api/health
```

---

### 2. Process Credit Application 📋

**Endpoint**: `POST /api/process-application`

**Description**: Process a credit application with optional document uploads

**Content-Type**: `multipart/form-data`

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| applicant_name | string | Yes | Name of the applicant |
| revenue | number | No | Annual revenue in dollars |
| net_profit | number | No | Net profit in dollars |
| debt_to_equity | number | No | Debt to equity ratio |
| fraud_score | number | No | Fraud risk score (0-1) |
| avg_balance | number | No | Average account balance |
| bank_statements | file | No | Bank statements (PDF/CSV, max 16MB) |
| gst_transactions | file | No | GST transactions (CSV, max 16MB) |

**Response**:
```json
{
  "application_id": "APP_20260317_001",
  "applicant_name": "John Doe",
  "decision": "APPROVE",
  "confidence": 0.78,
  "risk_score": 0.22,
  "summary": "Application approved with high confidence based on financial metrics",
  "detailed_analysis": {
    "financial_health": "STRONG",
    "fraud_risk": "LOW",
    "credit_worthiness": "HIGH"
  },
  "recommendation": "Proceed with loan approval up to $X amount",
  "timestamp": "2026-03-17T14:30:00Z",
  "processing_time_ms": 245
}
```

**Error Responses**:
```json
{
  "error": "Invalid file format",
  "message": "Only PDF and CSV files are allowed",
  "status": 400
}
```

**Example - Simple Request**:
```bash
curl -X POST http://localhost:5000/api/process-application \
  -F "applicant_name=John Doe" \
  -F "revenue=50000" \
  -F "net_profit=5000" \
  -F "debt_to_equity=0.5" \
  -F "fraud_score=0.2" \
  -F "avg_balance=10000"
```

**Example - With File Upload**:
```bash
curl -X POST http://localhost:5000/api/process-application \
  -F "applicant_name=John Doe" \
  -F "bank_statements=@path/to/statements.pdf" \
  -F "gst_transactions=@path/to/gst.csv"
```

**Example - Python**:
```python
import requests

url = "http://localhost:5000/api/process-application"
files = {
    'bank_statements': open('statements.pdf', 'rb'),
    'gst_transactions': open('gst.csv', 'rb')
}
data = {
    'applicant_name': 'John Doe',
    'revenue': 50000,
    'net_profit': 5000,
    'debt_to_equity': 0.5,
    'fraud_score': 0.2,
    'avg_balance': 10000
}

response = requests.post(url, files=files, data=data)
result = response.json()
print(f"Decision: {result['decision']}")
print(f"Confidence: {result['confidence']:.2%}")
```

**Example - JavaScript/TypeScript**:
```typescript
const formData = new FormData();
formData.append('applicant_name', 'John Doe');
formData.append('revenue', '50000');
formData.append('net_profit', '5000');
formData.append('debt_to_equity', '0.5');
formData.append('fraud_score', '0.2');
formData.append('avg_balance', '10000');

// Add files if available
if (bankStatementsFile) {
  formData.append('bank_statements', bankStatementsFile);
}
if (gstFile) {
  formData.append('gst_transactions', gstFile);
}

const response = await fetch('http://localhost:5000/api/process-application', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Decision: ${result.decision}`);
console.log(`Confidence: ${(result.confidence * 100).toFixed(2)}%`);
```

---

## Error Handling

### Common HTTP Status Codes

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Application processed successfully |
| 400 | Bad Request | Missing required parameters |
| 413 | File Too Large | Uploaded file exceeds 16MB limit |
| 415 | Unsupported Media | File format not supported |
| 500 | Server Error | Internal server error |

### Error Response Format

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "status": 400,
  "timestamp": "2026-03-17T14:30:00Z",
  "request_id": "REQ_20260317_001"
}
```

---

## Rate Limiting

**Default Limits** (Production):
- 100 requests per minute per IP
- 10 concurrent requests per IP
- 5 requests per second

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1234567890
```

---

## Authentication (Optional for Production)

**Header**: `Authorization: Bearer <token>`

**Example**:
```bash
curl -H "Authorization: Bearer YOUR_API_TOKEN" \
  http://localhost:5000/api/process-application
```

---

## Response Codes & Meanings

### Decision Values
- **APPROVE**: Application recommended for approval
- **REJECT**: Application recommended for rejection
- **REVIEW**: Application requires manual review

### Risk Levels
- **LOW**: 0.0 - 0.33
- **MEDIUM**: 0.33 - 0.66
- **HIGH**: 0.66 - 1.0

### Financial Health
- **STRONG**: Healthy financial metrics
- **MODERATE**: Acceptable financial metrics
- **WEAK**: Concerning financial metrics

---

## Model Information

**Model Type**: Ensemble Voting Classifier

**Components**:
- XGBoost (weight: 1.2)
- Random Forest (weight: 1.0)
- Gradient Boosting (weight: 1.0)
- Logistic Regression (weight: 0.8)

**Accuracy**: 77.98%  
**Precision**: 92.99% (low false positives)  
**Recall**: 27.48% (conservative approvals)  
**ROC-AUC**: 0.7360

**Features Used**:
1. Revenue
2. Net Profit
3. Debt-to-Equity Ratio
4. Fraud Score
5. Average Balance

---

## Rate Limit Example Response

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60,
  "status": 429
}
```

---

## CORS Configuration

**Allowed Origins** (Development):
- `http://localhost:3000`
- `http://localhost:5173`

**Allowed Origins** (Production):
- Configure in environment

**Allowed Methods**:
- GET
- POST
- OPTIONS

**Allowed Headers**:
- Content-Type
- Authorization

---

## Webhook Support (Future)

Coming soon:
- Application status updates
- Processing completion notifications
- Error notifications

---

## Testing the API

### Using curl
```bash
# Health check
curl http://localhost:5000/api/health

# Process application (minimal)
curl -X POST http://localhost:5000/api/process-application \
  -F "applicant_name=Test User"
```

### Using Postman
1. Import collection: [postman_collection.json](postman_collection.json)
2. Set environment: Development or Production
3. Run requests with sample data

### Using Thunder Client (VS Code)
Extension: Thunder Client  
Collection included in workspace

---

## SDK/Library Support

### Python
```python
from credit_engine import CreditEngineAPI

api = CreditEngineAPI(base_url="http://localhost:5000")
result = api.process_application(
    applicant_name="John Doe",
    revenue=50000,
    net_profit=5000
)
```

### JavaScript/TypeScript
```typescript
import { CreditEngineClient } from '@credit-engine/client';

const client = new CreditEngineClient({
  baseURL: 'http://localhost:5000'
});

const result = await client.processApplication({
  applicantName: 'John Doe',
  revenue: 50000,
  netProfit: 5000
});
```

---

## Best Practices

### Request Optimization
1. **Batch Processing**: Send multiple applications in one request
2. **Async Handling**: Don't wait for synchronous responses
3. **Caching**: Cache results for identical applications
4. **Error Handling**: Implement retry logic with exponential backoff

### Response Handling
```python
import requests
import time

def call_api_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url, 
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 429:  # Rate limit
                wait_time = int(response.headers.get('Retry-After', 60))
                time.sleep(wait_time)
                continue
                
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
    
    raise Exception(f"API call failed after {max_retries} attempts")
```

---

## Support & Documentation

- **Full Stack Guide**: [DEPLOYMENT_FULL_STACK.md](DEPLOYMENT_FULL_STACK.md)
- **Quick Start**: [DEPLOYMENT_QUICK_START.md](DEPLOYMENT_QUICK_START.md)
- **Model Info**: [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md)
- **GitHub**: https://github.com/SaiPranav1506/Credit-Engine

---

**API Version**: 3.0  
**Last Updated**: March 17, 2026  
**Status**: ✅ Production Ready
