# Monitoring & Observability Guide

## Overview

This guide covers monitoring, logging, and observability setup for the TMG Market Research Platform.

## Health Check Endpoints

The application provides several health check endpoints:

### `/api/health` - Basic Health Check
- **Purpose**: Liveness probe for containers and load balancers
- **Authentication**: Public
- **Response Time**: < 100ms
- **Use Case**: Kubernetes liveness probe, uptime monitoring

```bash
curl https://your-api.com/api/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T10:30:00Z",
  "service": "TMG Market Research API"
}
```

### `/api/health/ready` - Readiness Check
- **Purpose**: Verify service is ready to accept traffic
- **Authentication**: Public
- **Checks**: Database connectivity, GCP credentials, GCS bucket
- **Use Case**: Kubernetes readiness probe, deployment verification

```bash
curl https://your-api.com/api/health/ready
```

### `/api/health/detailed` - Detailed Status
- **Purpose**: Comprehensive system health information
- **Authentication**: Requires `X-API-Key` header
- **Use Case**: Administrative monitoring, debugging

```bash
curl -H "X-API-Key: your-api-key" https://your-api.com/api/health/detailed
```

## Kubernetes Health Probes

Add to your Kubernetes deployment:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: market-research-backend
spec:
  template:
    spec:
      containers:
      - name: backend
        image: gcr.io/project/backend:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /api/health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /api/health/ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

## Logging

### Application Logging

The application uses Python's built-in `logging` module with structured logging:

**Log Levels:**
- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages for recoverable issues
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical issues requiring immediate attention

**Configuration** (backend/app/main.py):
```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Cloud Logging (GCP)

For production, use Google Cloud Logging:

```bash
# Install Cloud Logging handler
pip install google-cloud-logging

# Add to main.py
import google.cloud.logging
client = google.cloud.logging.Client()
client.setup_logging()
```

### Log Aggregation

Query logs in Cloud Console:

```sql
-- All errors in last hour
resource.type="cloud_run_revision"
severity="ERROR"
timestamp>"2025-10-21T09:00:00Z"

-- API endpoint performance
resource.type="cloud_run_revision"
httpRequest.requestUrl=~"*/api/*"
httpRequest.latency>1s

-- Authentication failures
resource.type="cloud_run_revision"
jsonPayload.message=~".*Invalid API key.*"
```

## Metrics & Monitoring

### Key Metrics to Monitor

1. **Application Performance**
   - Request rate (requests/second)
   - Response time (p50, p95, p99)
   - Error rate (4xx, 5xx responses)
   - Database connection pool usage

2. **Database Performance**
   - Query response time
   - Connection count
   - Slow query count (> 1s)
   - Deadlock count

3. **Infrastructure**
   - CPU utilization (< 70% average)
   - Memory usage (< 80%)
   - Disk I/O
   - Network throughput

4. **Business Metrics**
   - Survey submissions per hour
   - Media uploads per hour
   - AI analysis queue depth
   - User engagement rate

### Google Cloud Monitoring Setup

```bash
# Create alert for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=$CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s \
  --condition-resource-type=cloud_run_revision \
  --condition-metric=run.googleapis.com/request_count \
  --condition-filter='metric.response_code_class="5xx"'

# Create alert for slow response times
gcloud alpha monitoring policies create \
  --notification-channels=$CHANNEL_ID \
  --display-name="Slow Response Times" \
  --condition-display-name="P95 latency > 2s" \
  --condition-threshold-value=2000 \
  --condition-threshold-duration=300s \
  --condition-resource-type=cloud_run_revision \
  --condition-metric=run.googleapis.com/request_latencies \
  --aggregation-alignment-period=60s \
  --aggregation-per-series-aligner=ALIGN_PERCENTILE_95

# Create alert for database connection pool exhaustion
gcloud alpha monitoring policies create \
  --notification-channels=$CHANNEL_ID \
  --display-name="DB Connection Pool Exhausted" \
  --condition-display-name="Connections > 25" \
  --condition-threshold-value=25 \
  --condition-threshold-duration=60s \
  --condition-resource-type=cloudsql_database \
  --condition-metric=cloudsql.googleapis.com/database/postgresql/num_backends
```

### Custom Metrics

Add custom metrics to your application:

```python
from google.cloud import monitoring_v3
import time

# Create custom metric client
client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project_id}"

def record_survey_submission(survey_slug: str):
    """Record a survey submission as a custom metric"""
    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/survey/submissions"
    series.resource.type = "global"
    series.metric.labels["survey_slug"] = survey_slug

    point = monitoring_v3.Point()
    point.value.int64_value = 1
    point.interval.end_time.seconds = int(time.time())
    series.points = [point]

    client.create_time_series(name=project_name, time_series=[series])
```

## Error Tracking

### Centralized Error Handling

The application includes centralized error handlers (app/core/error_handlers.py):

- HTTP exceptions (400s, 500s)
- Validation errors (422)
- Database errors
- Unhandled exceptions

All errors are logged with:
- Request path and method
- Error type and message
- Full stack trace (for 500 errors)
- Timestamp and request ID

### Error Tracking Service (Optional)

For advanced error tracking, integrate Sentry:

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]

# Add to main.py
import sentry_sdk
sentry_sdk.init(
    dsn="https://your-sentry-dsn",
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
    environment=os.getenv("ENVIRONMENT", "development")
)
```

## Performance Monitoring

### Database Query Monitoring

Enable query logging for slow queries:

```python
# Add to database.py
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={
        "options": "-c statement_timeout=30000"  # 30 second timeout
    }
)

# Log slow queries
@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop()
    if total > 1.0:  # Log queries > 1 second
        logger.warning(f"Slow query ({total:.2f}s): {statement[:100]}...")
```

### API Endpoint Performance

Monitor endpoint performance using middleware:

```python
import time
from starlette.middleware.base import BaseHTTPMiddleware

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Log slow requests
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.2f}s"
            )

        # Add performance header
        response.headers["X-Process-Time"] = str(process_time)
        return response

app.add_middleware(PerformanceMiddleware)
```

## Alerting Strategy

### Alert Levels

1. **Critical (P0)** - Immediate response required
   - Service completely down
   - Database connection failure
   - Data loss detected

2. **High (P1)** - Response within 1 hour
   - High error rate (> 10%)
   - Slow response times (p95 > 5s)
   - Disk space critically low (> 90%)

3. **Medium (P2)** - Response within 4 hours
   - Moderate error rate (> 5%)
   - Elevated response times (p95 > 2s)
   - Database connection pool usage high (> 80%)

4. **Low (P3)** - Response within 1 day
   - Minor errors
   - Unusual patterns detected
   - Non-critical warnings

### Alert Channels

Configure multiple notification channels:

```bash
# Email
gcloud alpha monitoring channels create \
  --type=email \
  --display-name="DevOps Email" \
  --channel-labels=email_address=devops@example.com

# Slack
gcloud alpha monitoring channels create \
  --type=slack \
  --display-name="DevOps Slack" \
  --channel-labels=channel_name=alerts,url=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# PagerDuty (for critical alerts)
gcloud alpha monitoring channels create \
  --type=pagerduty \
  --display-name="PagerDuty Critical" \
  --channel-labels=service_key=YOUR_PAGERDUTY_KEY
```

## Monitoring Dashboard

Create a custom monitoring dashboard in Google Cloud Console:

**Widgets to include:**
1. Request rate over time (line chart)
2. Error rate by endpoint (bar chart)
3. P50/P95/P99 latency (line chart)
4. Database connection pool usage (gauge)
5. CPU and memory usage (line chart)
6. Top 10 slowest endpoints (table)
7. Recent errors (log viewer)
8. Active user sessions (number)

## Incident Response Playbook

### When an alert fires:

1. **Acknowledge the alert**
   - Respond in PagerDuty or alert channel
   - Assign incident owner

2. **Assess the situation**
   ```bash
   # Check service health
   curl https://your-api.com/api/health/detailed -H "X-API-Key: key"

   # Check recent logs
   gcloud logging read "severity>=ERROR" --limit=50

   # Check current traffic
   gcloud monitoring read run.googleapis.com/request_count --limit=10
   ```

3. **Diagnose the issue**
   - Review error logs
   - Check database connectivity
   - Verify external dependencies (GCP services)
   - Check recent deployments

4. **Mitigate the issue**
   - Roll back recent deployment if needed
   - Scale up resources if capacity issue
   - Restart service if deadlocked

5. **Document and follow up**
   - Write incident report
   - Identify root cause
   - Create action items to prevent recurrence

## Uptime Monitoring

Set up external uptime monitoring using Google Cloud Monitoring Uptime Checks:

```bash
gcloud monitoring uptime-checks create \
  --display-name="API Health Check" \
  --resource-type=uptime-url \
  --monitored-resource=host=your-api.com,project_id=your-project \
  --http-check-path=/api/health \
  --period=60 \
  --timeout=10s
```

## Cost Monitoring

Monitor GCP costs to prevent surprises:

```bash
# Set budget alert
gcloud billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Monthly Budget" \
  --budget-amount=500USD \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=90 \
  --threshold-rule=percent=100
```

## Checklist

### Daily
- [ ] Review error logs
- [ ] Check alert status
- [ ] Verify backup completion
- [ ] Monitor response times

### Weekly
- [ ] Review performance trends
- [ ] Check resource utilization
- [ ] Review slow query logs
- [ ] Test alert channels

### Monthly
- [ ] Review and update dashboards
- [ ] Audit alert thresholds
- [ ] Review incident reports
- [ ] Update monitoring documentation

---

**Last Updated**: 2025-10-21
**Document Owner**: DevOps Team
**Review Frequency**: Quarterly
