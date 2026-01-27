# A2I2 Monitoring & Observability Guide

Comprehensive guide for monitoring, logging, and observability of the A2I2 platform.

---

## Table of Contents

1. [Monitoring Overview](#monitoring-overview)
2. [Health Checks](#health-checks)
3. [Database Monitoring](#database-monitoring)
4. [API Monitoring](#api-monitoring)
5. [Voice Pipeline Monitoring](#voice-pipeline-monitoring)
6. [Cost Monitoring](#cost-monitoring)
7. [Alerting Setup](#alerting-setup)
8. [Logging Configuration](#logging-configuration)
9. [Performance Dashboards](#performance-dashboards)
10. [Troubleshooting Runbooks](#troubleshooting-runbooks)

---

## Monitoring Overview

### Key Metrics to Track

| Category | Metric | Target | Critical |
|----------|--------|--------|----------|
| **Availability** | Uptime | >99.9% | <99% |
| **Latency** | API P95 | <500ms | >2000ms |
| **Latency** | Voice E2E | <1500ms | >3000ms |
| **Errors** | Error rate | <1% | >5% |
| **Database** | Query time | <100ms | >1000ms |
| **Database** | Connection pool | <80% | >95% |
| **Cost** | Daily spend | Budget | 150% budget |

### Monitoring Stack Options

| Tool | Purpose | Cost | Complexity |
|------|---------|------|------------|
| **Vercel Analytics** | Frontend + Edge | Included | Low |
| **Neon Dashboard** | Database metrics | Included | Low |
| **Supabase Dashboard** | Database + Auth | Included | Low |
| **Axiom** | Logs + metrics | Free tier | Medium |
| **Datadog** | Full observability | $15+/host | High |
| **Grafana Cloud** | Metrics + dashboards | Free tier | Medium |

**Recommended**: Start with built-in tools (Vercel + Neon/Supabase), add Axiom for logs.

---

## Health Checks

### API Health Endpoint

Create `/api/health/route.ts`:

```typescript
import { sql } from '@/lib/db';

export async function GET() {
  const checks = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: process.env.npm_package_version || '1.0.0',
    checks: {} as Record<string, any>
  };

  // Database check
  try {
    const start = Date.now();
    await sql`SELECT 1`;
    checks.checks.database = {
      status: 'healthy',
      latency_ms: Date.now() - start
    };
  } catch (error) {
    checks.status = 'unhealthy';
    checks.checks.database = {
      status: 'unhealthy',
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }

  // Memory tables check
  try {
    const [episodic, semantic, procedural] = await Promise.all([
      sql`SELECT COUNT(*) as count FROM arcus_episodic_memory`,
      sql`SELECT COUNT(*) as count FROM arcus_semantic_memory`,
      sql`SELECT COUNT(*) as count FROM arcus_procedural_memory`
    ]);
    checks.checks.memory_tables = {
      status: 'healthy',
      episodic_count: episodic[0].count,
      semantic_count: semantic[0].count,
      procedural_count: procedural[0].count
    };
  } catch (error) {
    checks.checks.memory_tables = {
      status: 'degraded',
      error: error instanceof Error ? error.message : 'Unknown error'
    };
  }

  // Vector extension check
  try {
    await sql`SELECT '[1,2,3]'::vector`;
    checks.checks.pgvector = { status: 'healthy' };
  } catch {
    checks.checks.pgvector = { status: 'unhealthy', error: 'pgvector not enabled' };
  }

  const statusCode = checks.status === 'healthy' ? 200 : 503;
  return Response.json(checks, { status: statusCode });
}
```

### Cron Health Check

Set up a cron job to check health regularly:

```bash
# crontab -e
*/5 * * * * curl -s https://your-app.vercel.app/api/health | jq '.status' || echo "Health check failed" | mail -s "A2I2 Alert" you@email.com
```

### Vercel Cron (vercel.json)

```json
{
  "crons": [
    {
      "path": "/api/cron/health-check",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

---

## Database Monitoring

### Neon Monitoring

Access via Neon Dashboard → Monitoring:

**Key Metrics:**
- Active connections
- Compute time
- Storage size
- Query performance

**SQL Queries for Monitoring:**

```sql
-- Connection count
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Slow queries (last 24 hours)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- ms
ORDER BY total_exec_time DESC
LIMIT 20;

-- Table sizes
SELECT
    relname as table,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE relname LIKE 'arcus_%'
ORDER BY pg_total_relation_size(relid) DESC;

-- Index usage
SELECT
    indexrelname as index,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC
LIMIT 20;

-- Vector index performance
SELECT
    indexrelname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%embedding%';
```

### Supabase Monitoring

Access via Supabase Dashboard → Database → Reports:

**Key Metrics:**
- API requests/min
- Database size
- Auth users
- Realtime connections

### Database Alerts SQL

```sql
-- Create monitoring view
CREATE OR REPLACE VIEW arcus_monitoring AS
SELECT
    (SELECT COUNT(*) FROM arcus_episodic_memory WHERE created_at > NOW() - INTERVAL '1 hour') as episodic_1h,
    (SELECT COUNT(*) FROM arcus_semantic_memory WHERE created_at > NOW() - INTERVAL '1 hour') as semantic_1h,
    (SELECT COUNT(*) FROM arcus_procedural_memory WHERE created_at > NOW() - INTERVAL '1 hour') as procedural_1h,
    (SELECT COUNT(*) FROM arcus_autonomy_audit WHERE created_at > NOW() - INTERVAL '1 hour') as audit_1h,
    (SELECT AVG(confidence) FROM arcus_episodic_memory WHERE created_at > NOW() - INTERVAL '24 hours') as avg_confidence_24h,
    (SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active') as active_connections;

-- Query the view
SELECT * FROM arcus_monitoring;
```

---

## API Monitoring

### Request Logging Middleware

Create `src/middleware.ts`:

```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const start = Date.now();
  const requestId = crypto.randomUUID();

  // Add request ID header
  const response = NextResponse.next();
  response.headers.set('x-request-id', requestId);

  // Log request (in production, send to logging service)
  console.log(JSON.stringify({
    type: 'request',
    request_id: requestId,
    method: request.method,
    path: request.nextUrl.pathname,
    timestamp: new Date().toISOString(),
    user_agent: request.headers.get('user-agent'),
    ip: request.ip || request.headers.get('x-forwarded-for')
  }));

  return response;
}

export const config = {
  matcher: '/api/:path*'
};
```

### API Metrics Tracking

```typescript
// src/lib/metrics.ts
interface ApiMetric {
  endpoint: string;
  method: string;
  status: number;
  latency_ms: number;
  timestamp: string;
}

class MetricsCollector {
  private metrics: ApiMetric[] = [];

  record(metric: ApiMetric) {
    this.metrics.push(metric);

    // Flush to database/logging service periodically
    if (this.metrics.length >= 100) {
      this.flush();
    }
  }

  async flush() {
    if (this.metrics.length === 0) return;

    const batch = this.metrics.splice(0, 100);

    // Send to your logging service
    // await axiom.ingestEvents('api_metrics', batch);

    console.log(`Flushed ${batch.length} metrics`);
  }

  getStats() {
    const now = Date.now();
    const recent = this.metrics.filter(
      m => new Date(m.timestamp).getTime() > now - 60000
    );

    return {
      requests_per_minute: recent.length,
      avg_latency_ms: recent.reduce((a, b) => a + b.latency_ms, 0) / recent.length || 0,
      error_rate: recent.filter(m => m.status >= 400).length / recent.length || 0
    };
  }
}

export const metrics = new MetricsCollector();
```

### Vercel Analytics Integration

```typescript
// src/app/layout.tsx
import { Analytics } from '@vercel/analytics/react';
import { SpeedInsights } from '@vercel/speed-insights/next';

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
```

---

## Voice Pipeline Monitoring

### Voice Latency Tracking

```sql
-- Voice latency statistics (built into schema)
SELECT * FROM voice_latency_stats;

-- Custom latency analysis
SELECT
    DATE_TRUNC('hour', created_at) as hour,
    COUNT(*) as queries,
    AVG(latency_ms) as avg_total_ms,
    AVG(stt_latency_ms) as avg_stt_ms,
    AVG(tts_latency_ms) as avg_tts_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_ms,
    SUM(CASE WHEN latency_ms < 250 THEN 1 ELSE 0 END)::float / COUNT(*) as under_250ms_rate
FROM arcus_voice_queries
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;
```

### Voice Quality Metrics

```typescript
// Track voice quality indicators
interface VoiceMetric {
  session_id: string;
  stt_confidence: number;
  stt_latency_ms: number;
  tts_latency_ms: number;
  total_latency_ms: number;
  transcript_length: number;
  response_length: number;
  error?: string;
}

async function recordVoiceMetric(metric: VoiceMetric) {
  await sql`
    INSERT INTO arcus_voice_queries (
      query_text,
      latency_ms,
      stt_latency_ms,
      tts_latency_ms
    ) VALUES (
      ${metric.transcript_length + ' chars'},
      ${metric.total_latency_ms},
      ${metric.stt_latency_ms},
      ${metric.tts_latency_ms}
    )
  `;
}
```

---

## Cost Monitoring

### API Cost Tracking

```typescript
// src/lib/cost-tracker.ts

const PRICING = {
  // Anthropic Claude (per 1M tokens)
  'claude-opus-4': { input: 15.00, output: 75.00 },
  'claude-sonnet-4': { input: 3.00, output: 15.00 },

  // Google Gemini (per 1M tokens)
  'gemini-3-pro': { input: 1.25, output: 5.00 },
  'gemini-3-flash': { input: 0.075, output: 0.30 },

  // OpenAI
  'whisper': { per_minute: 0.006 },
  'tts-1': { per_1k_chars: 0.015 },
  'text-embedding-3-small': { per_1m_tokens: 0.02 }
};

interface CostEntry {
  service: string;
  model: string;
  input_tokens?: number;
  output_tokens?: number;
  duration_seconds?: number;
  characters?: number;
  cost_usd: number;
  timestamp: string;
}

class CostTracker {
  private entries: CostEntry[] = [];

  recordLLM(model: string, inputTokens: number, outputTokens: number) {
    const pricing = PRICING[model] || PRICING['gemini-3-flash'];
    const cost = (inputTokens / 1_000_000 * pricing.input) +
                 (outputTokens / 1_000_000 * pricing.output);

    this.entries.push({
      service: 'llm',
      model,
      input_tokens: inputTokens,
      output_tokens: outputTokens,
      cost_usd: cost,
      timestamp: new Date().toISOString()
    });
  }

  recordSTT(durationSeconds: number) {
    const cost = (durationSeconds / 60) * PRICING.whisper.per_minute;
    this.entries.push({
      service: 'stt',
      model: 'whisper',
      duration_seconds: durationSeconds,
      cost_usd: cost,
      timestamp: new Date().toISOString()
    });
  }

  recordTTS(characters: number) {
    const cost = (characters / 1000) * PRICING['tts-1'].per_1k_chars;
    this.entries.push({
      service: 'tts',
      model: 'tts-1',
      characters,
      cost_usd: cost,
      timestamp: new Date().toISOString()
    });
  }

  getDailyCost(): number {
    const today = new Date().toISOString().split('T')[0];
    return this.entries
      .filter(e => e.timestamp.startsWith(today))
      .reduce((sum, e) => sum + e.cost_usd, 0);
  }

  getMonthlyCost(): number {
    const thisMonth = new Date().toISOString().slice(0, 7);
    return this.entries
      .filter(e => e.timestamp.startsWith(thisMonth))
      .reduce((sum, e) => sum + e.cost_usd, 0);
  }
}

export const costTracker = new CostTracker();
```

### Cost Alerts

```typescript
// Check daily budget
const DAILY_BUDGET = 10; // USD

async function checkCostAlert() {
  const dailyCost = costTracker.getDailyCost();

  if (dailyCost > DAILY_BUDGET * 0.8) {
    console.warn(`Cost warning: $${dailyCost.toFixed(2)} (80% of daily budget)`);
    // Send alert
  }

  if (dailyCost > DAILY_BUDGET) {
    console.error(`Cost exceeded: $${dailyCost.toFixed(2)} > $${DAILY_BUDGET}`);
    // Send critical alert, consider rate limiting
  }
}
```

---

## Alerting Setup

### Alert Rules

| Alert | Condition | Severity | Channel |
|-------|-----------|----------|---------|
| API Down | Health check fails 3x | Critical | SMS, Slack |
| High Latency | P95 > 2s for 5 min | Warning | Slack |
| Error Spike | Error rate > 5% | Warning | Slack |
| Database Full | Storage > 90% | Critical | Email, Slack |
| Cost Exceeded | Daily > budget | Warning | Email |
| Voice Degraded | Latency > 3s | Warning | Slack |

### Slack Webhook Integration

```typescript
// src/lib/alerts.ts

const SLACK_WEBHOOK = process.env.SLACK_WEBHOOK_URL;

interface Alert {
  level: 'info' | 'warning' | 'critical';
  title: string;
  message: string;
  fields?: Record<string, string>;
}

async function sendSlackAlert(alert: Alert) {
  if (!SLACK_WEBHOOK) return;

  const colors = {
    info: '#36a64f',
    warning: '#ff9800',
    critical: '#f44336'
  };

  await fetch(SLACK_WEBHOOK, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      attachments: [{
        color: colors[alert.level],
        title: `[${alert.level.toUpperCase()}] ${alert.title}`,
        text: alert.message,
        fields: alert.fields ? Object.entries(alert.fields).map(([k, v]) => ({
          title: k,
          value: v,
          short: true
        })) : undefined,
        ts: Math.floor(Date.now() / 1000)
      }]
    })
  });
}

// Usage
sendSlackAlert({
  level: 'warning',
  title: 'High API Latency',
  message: 'P95 latency exceeded 2 seconds',
  fields: {
    'Current P95': '2.3s',
    'Threshold': '2.0s',
    'Affected Endpoint': '/api/recall'
  }
});
```

### Email Alerts (with Resend)

```typescript
import { Resend } from 'resend';

const resend = new Resend(process.env.RESEND_API_KEY);

async function sendEmailAlert(alert: Alert) {
  await resend.emails.send({
    from: 'alerts@a2i2.app',
    to: ['ops@yourcompany.com'],
    subject: `[A2I2 ${alert.level.toUpperCase()}] ${alert.title}`,
    text: alert.message
  });
}
```

---

## Logging Configuration

### Structured Logging

```typescript
// src/lib/logger.ts

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  service: string;
  [key: string]: any;
}

class Logger {
  private service: string;

  constructor(service: string) {
    this.service = service;
  }

  private log(level: LogLevel, message: string, meta?: Record<string, any>) {
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      service: this.service,
      ...meta
    };

    // Output as JSON for log aggregation
    console.log(JSON.stringify(entry));
  }

  debug(message: string, meta?: Record<string, any>) {
    if (process.env.NODE_ENV === 'development') {
      this.log('debug', message, meta);
    }
  }

  info(message: string, meta?: Record<string, any>) {
    this.log('info', message, meta);
  }

  warn(message: string, meta?: Record<string, any>) {
    this.log('warn', message, meta);
  }

  error(message: string, error?: Error, meta?: Record<string, any>) {
    this.log('error', message, {
      ...meta,
      error: error ? {
        name: error.name,
        message: error.message,
        stack: error.stack
      } : undefined
    });
  }
}

// Usage
export const apiLogger = new Logger('api');
export const dbLogger = new Logger('database');
export const voiceLogger = new Logger('voice');
```

### Axiom Integration

```typescript
// src/lib/axiom.ts
import { Axiom } from '@axiomhq/js';

const axiom = new Axiom({
  token: process.env.AXIOM_TOKEN!,
  orgId: process.env.AXIOM_ORG_ID!
});

export async function logToAxiom(dataset: string, events: any[]) {
  await axiom.ingest(dataset, events);
}

// Flush logs periodically
setInterval(() => axiom.flush(), 10000);
```

---

## Performance Dashboards

### Key Dashboard Panels

**1. Overview**
- Request rate (rpm)
- Error rate (%)
- P50/P95/P99 latency
- Active users

**2. API Performance**
- Latency by endpoint
- Error breakdown by type
- Request volume by endpoint

**3. Database**
- Query latency distribution
- Connection pool usage
- Storage growth rate
- Slow query log

**4. Voice**
- End-to-end latency
- STT/TTS breakdown
- Success rate
- Usage volume

**5. Cost**
- Daily spend by service
- Token usage
- Projected monthly cost

### Grafana Dashboard JSON

```json
{
  "dashboard": {
    "title": "A2I2 Overview",
    "panels": [
      {
        "title": "Request Rate",
        "type": "stat",
        "targets": [{
          "expr": "rate(http_requests_total[5m])"
        }]
      },
      {
        "title": "API Latency P95",
        "type": "timeseries",
        "targets": [{
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
        }]
      },
      {
        "title": "Error Rate",
        "type": "gauge",
        "targets": [{
          "expr": "rate(http_requests_total{status=~'5..'}[5m]) / rate(http_requests_total[5m])"
        }]
      }
    ]
  }
}
```

---

## Troubleshooting Runbooks

### Runbook: High API Latency

**Symptoms**: P95 latency > 2 seconds

**Investigation Steps**:
1. Check Vercel function logs for slow requests
2. Query database for slow queries:
   ```sql
   SELECT query, mean_exec_time
   FROM pg_stat_statements
   ORDER BY mean_exec_time DESC
   LIMIT 10;
   ```
3. Check if vector searches are causing delays
4. Review recent deployments for regressions

**Remediation**:
- Add database indexes if missing
- Implement caching for frequent queries
- Scale database compute (Neon: increase CU)

---

### Runbook: Database Connection Exhaustion

**Symptoms**: "too many connections" errors

**Investigation Steps**:
1. Check active connections:
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   ```
2. Find connection leaks:
   ```sql
   SELECT state, count(*)
   FROM pg_stat_activity
   GROUP BY state;
   ```

**Remediation**:
- Use connection pooling (PgBouncer or Neon pooler)
- Review code for unclosed connections
- Increase max_connections if needed

---

### Runbook: Voice Quality Degradation

**Symptoms**: Voice latency > 3 seconds, poor transcription

**Investigation Steps**:
1. Check voice metrics:
   ```sql
   SELECT * FROM voice_latency_stats ORDER BY hour DESC LIMIT 5;
   ```
2. Test STT/TTS APIs directly
3. Check network latency to API endpoints

**Remediation**:
- Switch to faster model (e.g., `tiny.en`)
- Enable streaming for STT/TTS
- Consider local voice processing

---

### Runbook: Cost Spike

**Symptoms**: Daily spend exceeds budget

**Investigation Steps**:
1. Check cost breakdown by service
2. Identify high-usage endpoints
3. Look for runaway processes or infinite loops

**Remediation**:
- Implement rate limiting
- Add cost caps to API calls
- Review and optimize prompts (reduce token usage)

---

## Quick Reference

### Environment Variables for Monitoring

```bash
# Logging
AXIOM_TOKEN="xaat-..."
AXIOM_ORG_ID="your-org"
LOG_LEVEL="info"

# Alerting
SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
RESEND_API_KEY="re_..."
ALERT_EMAIL="ops@yourcompany.com"

# Cost tracking
DAILY_BUDGET_USD="10"
MONTHLY_BUDGET_USD="300"
```

### Useful Commands

```bash
# Check health
curl -s https://your-app.vercel.app/api/health | jq

# View recent logs (Vercel)
vercel logs your-app --follow

# Database stats
psql "$DATABASE_URL" -c "SELECT * FROM arcus_monitoring;"

# Voice latency
psql "$DATABASE_URL" -c "SELECT * FROM voice_latency_stats LIMIT 5;"
```

---

**Last Updated**: 2026-01-27
