# SAP BTP Monitoring - Endpoint Details

## 🎯 Main Endpoint for SAP BTP Monitoring

### `/metrics` Endpoint

**This is the ONLY endpoint SAP BTP Monitoring reads from.**

```
URL: http://your-app-url/metrics
Method: GET
Content-Type: text/plain
Format: Prometheus exposition format
```

---

## 📊 What SAP BTP Monitoring Does

1. **SAP BTP Monitoring** connects to your app
2. It **scrapes** (reads) the `/metrics` endpoint every 15-30 seconds
3. The endpoint returns **all metrics in Prometheus format**
4. SAP BTP **stores** these metrics in its time-series database
5. You can **view** the metrics in **SAP BTP Metrics Explorer**

---

## 🔍 Metrics Exposed at `/metrics` Endpoint

When SAP BTP calls `GET /metrics`, it receives:

### Example Response:
```
# HELP tokens_generated_total Total tokens processed
# TYPE tokens_generated_total counter
tokens_generated_total{token_type="input",model_name="mistral"} 1500.0
tokens_generated_total{token_type="output",model_name="mistral"} 3000.0

# HELP gpu_memory_usage_bytes GPU memory usage in bytes
# TYPE gpu_memory_usage_bytes gauge
gpu_memory_usage_bytes{gpu_index="0"} 4294967296.0

# HELP guardrail_rejections_total Total requests rejected by guardrails
# TYPE guardrail_rejections_total counter
guardrail_rejections_total{guardrail_type="empty_input",model_name="mistral"} 5.0
guardrail_rejections_total{guardrail_type="prohibited_content",model_name="mistral"} 12.0

# HELP request_queue_size Current number of requests waiting
# TYPE request_queue_size gauge
request_queue_size{model_name="mistral"} 3.0

# HELP model_load_status Model load status (1=loaded, 0=error)
# TYPE model_load_status gauge
model_load_status{model_name="mistral"} 1.0

# HELP request_duration_seconds Request processing time
# TYPE request_duration_seconds gauge
request_duration_seconds{model_name="mistral",status="success"} 2.345
request_duration_seconds{model_name="mistral",status="rejected"} 0.001
request_duration_seconds{model_name="mistral",status="error"} 1.234

# HELP active_requests Currently processing requests
# TYPE active_requests gauge
active_requests{model_name="mistral"} 2.0
```

---

## 📈 How Metrics Appear in SAP BTP Metrics Explorer

### In SAP BTP Cockpit:

1. Go to **Monitoring** → **Metrics Explorer**
2. Select your application
3. You'll see these metrics available:

#### Counter Metrics (Always Increasing):
| Metric Name | Labels | What It Shows in BTP |
|------------|--------|---------------------|
| `tokens_generated_total` | token_type, model_name | Total tokens processed over time - line graph showing growth |
| `guardrail_rejections_total` | guardrail_type, model_name | Total rejections over time - line graph showing growth |

#### Gauge Metrics (Current Values):
| Metric Name | Labels | What It Shows in BTP |
|------------|--------|---------------------|
| `gpu_memory_usage_bytes` | gpu_index | Current GPU memory usage - real-time line graph |
| `request_queue_size` | model_name | Current queue size - real-time line graph |
| `model_load_status` | model_name | Is model loaded (1) or not (0) - binary status |
| `request_duration_seconds` | model_name, status | Latest request duration - real-time value |
| `active_requests` | model_name | Current active requests - real-time count |

---

## 🔧 How to Configure SAP BTP to Read `/metrics`

### Step-by-Step Configuration:

#### 1. Deploy Your App to SAP BTP
```bash
cf push metric-monitoring
```

#### 2. Get Your App URL
```bash
cf apps
# Example output: metric-monitoring.cfapps.sap.hana.ondemand.com
```

#### 3. Configure Monitoring in SAP BTP Cockpit

**Option A: Using SAP BTP Cockpit UI**
1. Navigate to your Space in SAP BTP Cockpit
2. Go to **Services** → **Service Instances**
3. Create **Application Logging Service** instance (if not exists)
4. The service automatically discovers the `/metrics` endpoint
5. Metrics appear in **Monitoring** → **Metrics Explorer**

**Option B: Using manifest.yml**
Add to your `manifest.yml`:
```yaml
applications:
  - name: metric-monitoring
    memory: 512M
    instances: 1
    buildpack: python_buildpack
    command: uvicorn main:app --host 0.0.0.0 --port 8080
    env:
      METRICS_PORT: "8080"
    routes:
      - route: metric-monitoring.cfapps.sap.hana.ondemand.com
    health-check-type: http
    health-check-http-endpoint: /health
```

#### 4. Verify Metrics Are Being Scraped

Test locally first:
```bash
curl http://localhost:8080/metrics
```

After deployment, test on BTP:
```bash
curl https://your-app.cfapps.sap.hana.ondemand.com/metrics
```

#### 5. View in Metrics Explorer

1. Go to **SAP BTP Cockpit**
2. Navigate to **Monitoring** → **Metrics Explorer**
3. Select your application: `metric-monitoring`
4. Choose metric to visualize:
   - `tokens_generated_total`
   - `request_queue_size`
   - `gpu_memory_usage_bytes`
   - etc.
5. Apply filters using labels (e.g., `model_name="mistral"`)

---

## 📊 Creating Dashboards in SAP BTP

### Example Dashboard Queries:

**1. Token Usage Over Time**
```
Query: tokens_generated_total{model_name="mistral"}
Visualization: Line Chart
Shows: Input vs Output token growth
```

**2. Request Queue Size**
```
Query: request_queue_size{model_name="mistral"}
Visualization: Line Chart
Shows: Real-time queue depth
Alert: Set threshold at 10 requests
```

**3. Guardrail Rejection Rate**
```
Query: rate(guardrail_rejections_total[5m])
Visualization: Line Chart
Shows: Rejections per minute
```

**4. Model Availability**
```
Query: model_load_status{model_name="mistral"}
Visualization: Status Widget
Shows: 1 = Up, 0 = Down
Alert: Trigger if value = 0
```

**5. Request Duration**
```
Query: request_duration_seconds{status="success"}
Visualization: Line Chart
Shows: Response time trend
Alert: Set threshold at 5 seconds
```

---

## 🎯 Quick Summary

### For SAP BTP Monitoring:

**Endpoint:** `GET /metrics`  
**Location in your code:** `main.py` line 108-119  
**What it returns:** All 7 metrics in Prometheus format  
**Scrape interval:** Every 15-30 seconds (BTP default)  
**Where to view:** SAP BTP Cockpit → Monitoring → Metrics Explorer

### Other Endpoints (NOT for monitoring):

- `POST /v1/generate` - Application endpoint (generates text)
- `GET /health` - Health check endpoint (used by BTP for app status)

**Only `/metrics` is used for metrics collection by SAP BTP Monitoring.**
