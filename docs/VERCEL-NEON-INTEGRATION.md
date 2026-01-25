# Vercel + Neon Integration Plan

**A2I2 Platform Deployment Guide**

This document outlines the complete integration plan for deploying the A2I2 platform on Vercel with Neon PostgreSQL as the database backend.

---

## Overview

| Component | Current | Target |
|:----------|:--------|:-------|
| **Database** | Supabase (PostgreSQL) | Neon (PostgreSQL) |
| **Hosting** | None (CLI-based) | Vercel |
| **API Layer** | Direct Supabase client | Next.js API routes |
| **Frontend** | None | Next.js App Router |

**Migration Complexity: LOW** - The current schema is pure PostgreSQL, making Neon migration straightforward.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        A2I2 ON VERCEL + NEON                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────────────────────────────────────────────────────────┐   │
│   │                         VERCEL PLATFORM                                  │   │
│   │                                                                          │   │
│   │   ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │   │
│   │   │   Next.js App    │    │   API Routes     │    │   Edge Runtime   │  │   │
│   │   │   (Frontend)     │    │   (/api/*)       │    │   (Middleware)   │  │   │
│   │   │                  │    │                  │    │                  │  │   │
│   │   │  • Dashboard     │    │  • /api/learn    │    │  • Auth check    │  │   │
│   │   │  • Chat UI       │    │  • /api/recall   │    │  • Rate limiting │  │   │
│   │   │  • Memory View   │    │  • /api/relate   │    │  • Routing       │  │   │
│   │   │  • Graph Viz     │    │  • /api/reflect  │    │                  │  │   │
│   │   │                  │    │  • /api/entities │    │                  │  │   │
│   │   └────────┬─────────┘    └────────┬─────────┘    └──────────────────┘  │   │
│   │            │                       │                                     │   │
│   │            └───────────────────────┼─────────────────────────────────────┤   │
│   └────────────────────────────────────┼─────────────────────────────────────┘   │
│                                        │                                         │
│                                        │ Neon Serverless Driver                  │
│                                        │ @neondatabase/serverless                │
│                                        │                                         │
│   ┌────────────────────────────────────▼─────────────────────────────────────┐   │
│   │                         NEON POSTGRESQL                                   │   │
│   │                                                                          │   │
│   │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  │   │
│   │   │  Episodic   │   │  Semantic   │   │ Procedural  │   │  Entities   │  │   │
│   │   │   Memory    │   │   Memory    │   │   Memory    │   │   + Rels    │  │   │
│   │   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘  │   │
│   │                                                                          │   │
│   │   ┌─────────────────────────────────────────────────────────────────┐   │   │
│   │   │                    pgvector Extension                            │   │   │
│   │   │              (Semantic search / embeddings)                      │   │   │
│   │   └─────────────────────────────────────────────────────────────────┘   │   │
│   │                                                                          │   │
│   │   Features:                                                              │   │
│   │   • Serverless scaling (scale to zero)                                  │   │
│   │   • Connection pooling built-in                                         │   │
│   │   • Branching for dev/staging                                           │   │
│   │   • pgvector native support                                             │   │
│   │                                                                          │   │
│   └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Neon Database Setup

### 1.1 Create Neon Project

1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project with these settings:
   - **Project name:** `a2i2-production` (or `a2i2-dev` for development)
   - **Region:** Choose closest to your users
   - **PostgreSQL version:** 16 (latest)
   - **Compute size:** Start with 0.25 CU (auto-scales)

### 1.2 Enable Required Extensions

Connect to your Neon database and run:

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Verify extensions
SELECT * FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector');
```

### 1.3 Run Schema Migration

The existing Supabase schema is 100% compatible with Neon. Run the schema from:
`.claude/skills/knowledge-repository/schemas/supabase-schema.sql`

**Minor modifications for Neon:**

```sql
-- The schema works as-is, but you may want to adjust RLS
-- Neon doesn't have Supabase's auth.uid() function
-- For now, use application-level auth instead of RLS

-- Option A: Disable RLS (simpler, use app-level auth)
ALTER TABLE arcus_episodic_memory DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_semantic_memory DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_procedural_memory DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_entities DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_relationships DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_session_state DISABLE ROW LEVEL SECURITY;
ALTER TABLE arcus_autonomy_audit DISABLE ROW LEVEL SECURITY;

-- Option B: Keep RLS with custom policies (implement later for multi-tenant)
-- This requires adding user_id column and custom auth handling
```

### 1.4 Connection String Setup

Neon provides two connection strings:

| Type | Use Case | Format |
|:-----|:---------|:-------|
| **Pooled** | Production API routes | `postgres://user:pass@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require` |
| **Direct** | Migrations, admin | `postgres://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require` |

**Environment Variables:**

```bash
# For Vercel
DATABASE_URL="postgres://user:pass@ep-xxx-pooler.region.aws.neon.tech/dbname?sslmode=require"

# For local development (direct connection)
DATABASE_URL_DIRECT="postgres://user:pass@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"
```

---

## Phase 2: Vercel Project Setup

### 2.1 Initialize Next.js Project

```bash
# Create Next.js app in the repo
npx create-next-app@latest app --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# Or add to existing structure
mkdir -p src/app src/lib src/components
```

**Recommended project structure:**

```
a2i2-beta-v1/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx              # Dashboard
│   │   ├── api/                  # API routes
│   │   │   ├── learn/route.ts
│   │   │   ├── recall/route.ts
│   │   │   ├── relate/route.ts
│   │   │   ├── reflect/route.ts
│   │   │   ├── entities/route.ts
│   │   │   └── health/route.ts
│   │   ├── memories/             # Memory browser
│   │   │   └── page.tsx
│   │   ├── graph/                # Knowledge graph viz
│   │   │   └── page.tsx
│   │   └── chat/                 # Chat interface
│   │       └── page.tsx
│   │
│   ├── lib/
│   │   ├── db.ts                 # Neon client
│   │   ├── knowledge.ts          # Knowledge operations
│   │   └── types.ts              # TypeScript types
│   │
│   └── components/
│       ├── MemoryCard.tsx
│       ├── GraphVisualization.tsx
│       └── ChatInterface.tsx
│
├── .claude/skills/               # Existing skill (unchanged)
├── docs/
├── package.json
├── next.config.js
├── tailwind.config.ts
└── vercel.json
```

### 2.2 Install Dependencies

> **Note**: `create-next-app` installs core dependencies (next, react, react-dom, typescript, tailwindcss).
> The packages below are **additional** dependencies for the A2I2 integration.

```bash
# Database driver (required)
npm install @neondatabase/serverless

# Input validation (required)
npm install zod

# Authentication (choose one - required for production)
npm install @clerk/nextjs         # Clerk (recommended for quick setup)
# OR
npm install next-auth             # NextAuth.js (more flexible)

# Optional integrations
npm install ai                    # Vercel AI SDK (if adding chat)
npm install @anthropic-ai/sdk     # Claude integration
npm install d3 @types/d3          # Graph visualization
```

### 2.3 Database Client Setup

**`src/lib/db.ts`:**

```typescript
import { neon } from '@neondatabase/serverless';

// Validate environment variable at startup
if (!process.env.DATABASE_URL) {
  throw new Error('DATABASE_URL environment variable is required');
}

// Serverless-optimized connection using tagged templates
// This is the idiomatic pattern for @neondatabase/serverless
export const sql = neon(process.env.DATABASE_URL);

// Usage example:
// const users = await sql`SELECT * FROM users WHERE id = ${userId}`;
//
// The neon() driver uses tagged template literals for parameterized queries.
// Values are automatically escaped and safe from SQL injection.
```

### 2.4 Knowledge Operations Port

> **SECURITY WARNING**: The code examples below are for demonstration purposes.
> Before deploying to production, you MUST:
> 1. Add authentication middleware (see Section 2.6)
> 2. Re-enable Row Level Security with proper policies
> 3. Validate and sanitize all user inputs
> 4. Never expose these endpoints without authentication

**`src/lib/knowledge.ts`:**

```typescript
import { sql } from './db';

// Type-safe memory types to prevent SQL injection
type MemoryType = 'episodic' | 'semantic' | 'procedural';

// Whitelist of allowed columns per memory type to prevent injection
// Column names must match the actual database schema (supabase-schema.sql)
const ALLOWED_COLUMNS: Record<MemoryType, readonly string[]> = {
  episodic: ['event_type', 'summary', 'detailed_content', 'participants', 'tags', 'outcome', 'confidence', 'importance'],
  semantic: ['category', 'statement', 'explanation', 'evidence', 'domain', 'tags', 'confidence'],
  procedural: ['procedure_type', 'name', 'description', 'steps', 'tags', 'confidence']
} as const;

export class KnowledgeRepository {

  // LEARN: Store new knowledge
  // Uses explicit table queries to prevent SQL injection
  async learn(
    memoryType: MemoryType,
    entry: Record<string, unknown>
  ): Promise<{ id: string }> {
    // Validate columns against whitelist
    const allowedCols = ALLOWED_COLUMNS[memoryType];
    const sanitizedEntry: Record<string, unknown> = {};

    for (const [key, value] of Object.entries(entry)) {
      if (allowedCols.includes(key)) {
        sanitizedEntry[key] = value;
      }
    }

    // Use explicit queries per table type to avoid dynamic SQL
    let result;
    if (memoryType === 'episodic') {
      result = await sql`
        INSERT INTO arcus_episodic_memory
          (event_type, summary, detailed_content, participants, tags, outcome, confidence, importance)
        VALUES (
          ${sanitizedEntry.event_type ?? null},
          ${sanitizedEntry.summary ?? null},
          ${JSON.stringify(sanitizedEntry.detailed_content ?? {})},
          ${sanitizedEntry.participants ?? []},
          ${sanitizedEntry.tags ?? []},
          ${sanitizedEntry.outcome ?? null},
          ${sanitizedEntry.confidence ?? 0.5},
          ${sanitizedEntry.importance ?? 'normal'}
        )
        RETURNING id
      `;
    } else if (memoryType === 'semantic') {
      result = await sql`
        INSERT INTO arcus_semantic_memory
          (category, statement, explanation, evidence, domain, tags, confidence)
        VALUES (
          ${sanitizedEntry.category ?? null},
          ${sanitizedEntry.statement ?? null},
          ${sanitizedEntry.explanation ?? null},
          ${sanitizedEntry.evidence ?? []},
          ${sanitizedEntry.domain ?? null},
          ${sanitizedEntry.tags ?? []},
          ${sanitizedEntry.confidence ?? 0.5}
        )
        RETURNING id
      `;
    } else {
      result = await sql`
        INSERT INTO arcus_procedural_memory
          (procedure_type, name, description, steps, tags, confidence)
        VALUES (
          ${sanitizedEntry.procedure_type ?? null},
          ${sanitizedEntry.name ?? null},
          ${sanitizedEntry.description ?? null},
          ${JSON.stringify(sanitizedEntry.steps ?? [])},
          ${sanitizedEntry.tags ?? []},
          ${sanitizedEntry.confidence ?? 0.5}
        )
        RETURNING id
      `;
    }

    return { id: result[0].id };
  }

  // RECALL: Retrieve knowledge
  // NOTE: For production semantic search, generate embeddings for the query
  // and use pgvector's similarity operators (e.g., `<->` for L2 distance).
  // This implementation uses text-based search as a fallback.
  async recall(options: {
    query: string;
    memoryTypes?: MemoryType[];
    limit?: number;
    minConfidence?: number;
    daysBack?: number;
  }): Promise<Record<string, unknown>[]> {
    const {
      query: searchQuery,
      memoryTypes = ['episodic', 'semantic', 'procedural'],
      limit = 10,
      minConfidence = 0.5,
      daysBack = 30
    } = options;

    // Validate numeric inputs to prevent injection
    const safeLimit = Math.min(Math.max(1, Math.floor(limit)), 100);
    const safeDaysBack = Math.min(Math.max(1, Math.floor(daysBack)), 365);
    const safeConfidence = Math.min(Math.max(0, minConfidence), 1);

    // Escape LIKE special characters to prevent wildcard injection
    const escapedQuery = searchQuery.replace(/[\\%_]/g, '\\$&');

    const results: Record<string, unknown>[] = [];

    // Use explicit queries per table to prevent SQL injection
    for (const type of memoryTypes) {
      let rows: Record<string, unknown>[] = [];

      if (type === 'episodic') {
        rows = escapedQuery
          ? await sql`
              SELECT * FROM arcus_episodic_memory
              WHERE summary ILIKE ${'%' + escapedQuery + '%'} ESCAPE '\\'
              AND confidence >= ${safeConfidence}
              AND created_at >= NOW() - (${safeDaysBack} * INTERVAL '1 day')
              ORDER BY created_at DESC
              LIMIT ${safeLimit}
            `
          : await sql`
              SELECT * FROM arcus_episodic_memory
              WHERE confidence >= ${safeConfidence}
              AND created_at >= NOW() - (${safeDaysBack} * INTERVAL '1 day')
              ORDER BY created_at DESC
              LIMIT ${safeLimit}
            `;
      } else if (type === 'semantic') {
        // Search by 'statement' column (matches schema)
        rows = escapedQuery
          ? await sql`
              SELECT * FROM arcus_semantic_memory
              WHERE statement ILIKE ${'%' + escapedQuery + '%'} ESCAPE '\\'
              AND confidence >= ${safeConfidence}
              AND created_at >= NOW() - (${safeDaysBack} * INTERVAL '1 day')
              ORDER BY created_at DESC
              LIMIT ${safeLimit}
            `
          : await sql`
              SELECT * FROM arcus_semantic_memory
              WHERE confidence >= ${safeConfidence}
              AND created_at >= NOW() - (${safeDaysBack} * INTERVAL '1 day')
              ORDER BY created_at DESC
              LIMIT ${safeLimit}
            `;
      } else if (type === 'procedural') {
        // Search by 'name' column (matches schema - not 'procedure_name')
        rows = escapedQuery
          ? await sql`
              SELECT * FROM arcus_procedural_memory
              WHERE name ILIKE ${'%' + escapedQuery + '%'} ESCAPE '\\'
              AND confidence >= ${safeConfidence}
              AND created_at >= NOW() - (${safeDaysBack} * INTERVAL '1 day')
              ORDER BY created_at DESC
              LIMIT ${safeLimit}
            `
          : await sql`
              SELECT * FROM arcus_procedural_memory
              WHERE confidence >= ${safeConfidence}
              AND created_at >= NOW() - (${safeDaysBack} * INTERVAL '1 day')
              ORDER BY created_at DESC
              LIMIT ${safeLimit}
            `;
      }

      results.push(...rows);
    }

    return results;
  }

  // RELATE: Create entity relationships
  async relate(
    sourceName: string,
    sourceType: string,
    relationship: string,
    targetName: string,
    targetType: string,
    properties?: Record<string, unknown>
  ): Promise<{ relationshipId: string }> {
    // Ensure entities exist
    const sourceId = await this.ensureEntity(sourceName, sourceType);
    const targetId = await this.ensureEntity(targetName, targetType);

    const result = await sql`
      INSERT INTO arcus_relationships
        (source_entity_id, target_entity_id, relationship, properties)
      VALUES (${sourceId}, ${targetId}, ${relationship}, ${JSON.stringify(properties || {})})
      ON CONFLICT (source_entity_id, relationship, target_entity_id)
      DO UPDATE SET
        properties = EXCLUDED.properties,
        observation_count = arcus_relationships.observation_count + 1,
        last_observed = NOW()
      RETURNING id
    `;

    return { relationshipId: result[0].id };
  }

  // REFLECT: Synthesize patterns
  async reflect(options: {
    days?: number;
    focusAreas?: string[];
    minEvidence?: number;
  }): Promise<{ patterns: Record<string, unknown>[] }> {
    const { days = 7, minEvidence = 3 } = options;

    // Validate numeric inputs
    const safeDays = Math.min(Math.max(1, Math.floor(days)), 90);
    const safeMinEvidence = Math.min(Math.max(1, Math.floor(minEvidence)), 100);

    // Aggregate patterns from recent memories
    const patterns = await sql`
      SELECT
        event_type,
        COUNT(*) as occurrence_count,
        AVG(confidence) as avg_confidence
      FROM arcus_episodic_memory
      WHERE event_timestamp >= NOW() - (${safeDays} * INTERVAL '1 day')
      GROUP BY event_type
      HAVING COUNT(*) >= ${safeMinEvidence}
      ORDER BY occurrence_count DESC
    `;

    return { patterns };
  }

  // Helper: Ensure entity exists
  private async ensureEntity(name: string, type: string): Promise<string> {
    const existing = await sql`
      SELECT id FROM arcus_entities
      WHERE name = ${name} AND entity_type = ${type}
    `;

    if (existing.length > 0) {
      return existing[0].id;
    }

    const result = await sql`
      INSERT INTO arcus_entities (name, entity_type)
      VALUES (${name}, ${type})
      RETURNING id
    `;

    return result[0].id;
  }
}

export const knowledge = new KnowledgeRepository();
```

### 2.5 API Routes

> **IMPORTANT**: These routes require authentication in production.
> See Section 2.6 for middleware setup.

**`src/app/api/learn/route.ts`:**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { knowledge } from '@/lib/knowledge';
import { z, ZodError } from 'zod';

const LearnSchema = z.object({
  memoryType: z.enum(['episodic', 'semantic', 'procedural']),
  entry: z.record(z.unknown())
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { memoryType, entry } = LearnSchema.parse(body);

    const result = await knowledge.learn(memoryType, entry);

    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    // Handle validation errors separately
    if (error instanceof ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.errors },
        { status: 400 }
      );
    }

    // Log error server-side only (don't expose details to client)
    console.error('Learn error:', error instanceof Error ? error.message : 'Unknown error');
    return NextResponse.json(
      { error: 'Failed to store knowledge' },
      { status: 500 }
    );
  }
}
```

**`src/app/api/recall/route.ts`:**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { knowledge } from '@/lib/knowledge';

// Valid memory types for type-safe filtering
const VALID_MEMORY_TYPES = ['episodic', 'semantic', 'procedural'] as const;
type MemoryType = typeof VALID_MEMORY_TYPES[number];

function parseMemoryTypes(typesParam: string | null): MemoryType[] | undefined {
  if (!typesParam) return undefined;

  return typesParam
    .split(',')
    .filter((t): t is MemoryType => VALID_MEMORY_TYPES.includes(t as MemoryType));
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    const results = await knowledge.recall({
      query: searchParams.get('q') || '',
      memoryTypes: parseMemoryTypes(searchParams.get('types')),
      limit: parseInt(searchParams.get('limit') || '10'),
      minConfidence: parseFloat(searchParams.get('confidence') || '0.5'),
      daysBack: parseInt(searchParams.get('days') || '30')
    });

    return NextResponse.json({ results });
  } catch (error) {
    console.error('Recall error:', error);
    return NextResponse.json(
      { error: 'Failed to retrieve knowledge' },
      { status: 500 }
    );
  }
}
```

**`src/app/api/health/route.ts`:**

```typescript
import { NextResponse } from 'next/server';
import { sql } from '@/lib/db';

export async function GET() {
  try {
    await sql`SELECT 1`;
    return NextResponse.json({
      status: 'healthy',
      database: 'connected',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      { status: 'unhealthy', error: 'Database connection failed' },
      { status: 500 }
    );
  }
}
```

**`src/app/api/relate/route.ts`:**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { knowledge } from '@/lib/knowledge';
import { z, ZodError } from 'zod';

const RelateSchema = z.object({
  sourceName: z.string().min(1),
  sourceType: z.string().min(1),
  relationship: z.string().min(1),
  targetName: z.string().min(1),
  targetType: z.string().min(1),
  properties: z.record(z.unknown()).optional()
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { sourceName, sourceType, relationship, targetName, targetType, properties } =
      RelateSchema.parse(body);

    const result = await knowledge.relate(
      sourceName,
      sourceType,
      relationship,
      targetName,
      targetType,
      properties
    );

    return NextResponse.json(result, { status: 201 });
  } catch (error) {
    if (error instanceof ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Relate error:', error instanceof Error ? error.message : 'Unknown error');
    return NextResponse.json(
      { error: 'Failed to create relationship' },
      { status: 500 }
    );
  }
}
```

**`src/app/api/reflect/route.ts`:**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { knowledge } from '@/lib/knowledge';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);

    const days = parseInt(searchParams.get('days') || '7', 10);
    const minEvidence = parseInt(searchParams.get('minEvidence') || '3', 10);

    // Validate parameters
    if (isNaN(days) || days < 1 || days > 90) {
      return NextResponse.json(
        { error: 'days must be between 1 and 90' },
        { status: 400 }
      );
    }

    const result = await knowledge.reflect({
      days,
      minEvidence: isNaN(minEvidence) ? 3 : minEvidence
    });

    return NextResponse.json(result);
  } catch (error) {
    console.error('Reflect error:', error instanceof Error ? error.message : 'Unknown error');
    return NextResponse.json(
      { error: 'Failed to generate reflection' },
      { status: 500 }
    );
  }
}
```

### 2.6 Authentication Middleware (Required for Production)

> **CRITICAL**: Never deploy API routes without authentication.
> The examples above will expose your entire knowledge base to the public internet.

**Option A: Clerk (Recommended for quick setup)**

**`src/middleware.ts`:**

```typescript
import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';

// Define which routes require authentication
const isProtectedRoute = createRouteMatcher([
  '/api/learn(.*)',
  '/api/recall(.*)',
  '/api/relate(.*)',
  '/api/reflect(.*)',
  '/api/entities(.*)',
]);

// Health check remains public
const isPublicRoute = createRouteMatcher([
  '/api/health',
  '/',
]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: ['/((?!.*\\..*|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

**Option B: Simple API Key Authentication**

**`src/lib/auth.ts`:**

```typescript
import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

// Timing-safe comparison to prevent timing attacks
function secureCompare(a: string, b: string): boolean {
  if (a.length !== b.length) {
    // Compare against itself to maintain constant time even on length mismatch
    crypto.timingSafeEqual(Buffer.from(a), Buffer.from(a));
    return false;
  }
  return crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
}

export function withAuth(
  handler: (req: NextRequest) => Promise<NextResponse>
) {
  return async (req: NextRequest) => {
    const apiKey = req.headers.get('x-api-key') || '';
    const validApiKey = process.env.API_SECRET_KEY || '';

    if (!apiKey || !validApiKey || !secureCompare(apiKey, validApiKey)) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    return handler(req);
  };
}
```

**Usage in API routes:**

```typescript
import { withAuth } from '@/lib/auth';

async function handler(request: NextRequest) {
  // Your route logic here
}

export const POST = withAuth(handler);
```

---

## Phase 3: Vercel Deployment

### 3.1 Vercel Configuration

**`vercel.json`:**

```json
{
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

> **Note**: For Next.js projects, Vercel automatically handles build configuration.
> Set `DATABASE_URL` and other secrets via Vercel Dashboard, not in `vercel.json`.

### 3.2 Environment Variables

In Vercel Dashboard → Settings → Environment Variables:

| Variable | Value | Environment |
|:---------|:------|:------------|
| `DATABASE_URL` | Neon pooled connection string | Production, Preview, Development |
| `ANTHROPIC_API_KEY` | Your Claude API key | Production, Preview |

### 3.3 Neon Integration (Recommended)

Vercel has a native Neon integration:

1. Go to Vercel Dashboard → Integrations
2. Search for "Neon"
3. Install and connect your Neon project
4. `DATABASE_URL` will be automatically configured

### 3.4 Deploy

```bash
# Install Vercel CLI
npm install -g vercel

# Link to your Vercel account
vercel link

# Deploy preview
vercel

# Deploy production
vercel --prod
```

---

## Phase 4: Frontend Implementation (Optional)

### 4.1 Dashboard Page

**`src/app/page.tsx`:**

```typescript
import { sql } from '@/lib/db';

interface DashboardStats {
  episodic_count: number;
  semantic_count: number;
  procedural_count: number;
  entity_count: number;
  relationship_count: number;
}

// Optimized query using UNION ALL to reduce database round trips
async function getStats(): Promise<DashboardStats> {
  const stats = await sql`
    SELECT
      SUM(CASE WHEN type = 'episodic' THEN count ELSE 0 END)::int as episodic_count,
      SUM(CASE WHEN type = 'semantic' THEN count ELSE 0 END)::int as semantic_count,
      SUM(CASE WHEN type = 'procedural' THEN count ELSE 0 END)::int as procedural_count,
      SUM(CASE WHEN type = 'entity' THEN count ELSE 0 END)::int as entity_count,
      SUM(CASE WHEN type = 'relationship' THEN count ELSE 0 END)::int as relationship_count
    FROM (
      SELECT 'episodic' as type, COUNT(*) as count FROM arcus_episodic_memory
      UNION ALL
      SELECT 'semantic' as type, COUNT(*) as count FROM arcus_semantic_memory
      UNION ALL
      SELECT 'procedural' as type, COUNT(*) as count FROM arcus_procedural_memory
      UNION ALL
      SELECT 'entity' as type, COUNT(*) as count FROM arcus_entities
      UNION ALL
      SELECT 'relationship' as type, COUNT(*) as count FROM arcus_relationships
    ) as counts
  `;
  return stats[0] as DashboardStats;
}

export default async function Dashboard() {
  const stats = await getStats();

  return (
    <main className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">A2I2 Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard title="Episodic Memories" count={stats.episodic_count} />
        <StatCard title="Semantic Memories" count={stats.semantic_count} />
        <StatCard title="Procedural Memories" count={stats.procedural_count} />
        <StatCard title="Entities" count={stats.entity_count} />
        <StatCard title="Relationships" count={stats.relationship_count} />
      </div>
    </main>
  );
}

function StatCard({ title, count }: { title: string; count: number }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
      <p className="text-3xl font-bold mt-2">{count.toLocaleString()}</p>
    </div>
  );
}
```

### 4.2 Memory Browser

**`src/app/memories/page.tsx`:**

```typescript
'use client';

import { useState, useEffect } from 'react';

// Define proper TypeScript interfaces for type safety
interface Memory {
  id: string;
  summary?: string;
  name?: string;
  procedure_name?: string;
  confidence: number;
  detailed_content?: { description?: string };
  definition?: string;
  steps?: string[];
  tags?: string[];
  created_at: string;
}

type MemoryType = 'episodic' | 'semantic' | 'procedural';

export default function MemoriesPage() {
  const [memories, setMemories] = useState<Memory[]>([]);
  const [memoryType, setMemoryType] = useState<MemoryType>('episodic');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    fetch(`/api/recall?types=${memoryType}&limit=50`)
      .then(res => res.json())
      .then(data => {
        setMemories(data.results || []);
        setIsLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch memories:', err);
        setIsLoading(false);
      });
  }, [memoryType]);

  return (
    <main className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Memory Browser</h1>

      <div className="flex gap-4 mb-6">
        {(['episodic', 'semantic', 'procedural'] as const).map(type => (
          <button
            key={type}
            onClick={() => setMemoryType(type)}
            className={`px-4 py-2 rounded ${
              memoryType === type
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 dark:bg-gray-700'
            }`}
          >
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </button>
        ))}
      </div>

      {isLoading ? (
        <p className="text-gray-500">Loading memories...</p>
      ) : (
        <div className="space-y-4">
          {memories.map((memory) => (
            <MemoryCard key={memory.id} memory={memory} />
          ))}
          {memories.length === 0 && (
            <p className="text-gray-500">No memories found.</p>
          )}
        </div>
      )}
    </main>
  );
}

function MemoryCard({ memory }: { memory: Memory }) {
  const title = memory.summary || memory.name || memory.procedure_name || 'Untitled';
  const description = memory.detailed_content?.description
    || memory.definition
    || memory.steps?.[0]
    || '';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div className="flex justify-between items-start">
        <h3 className="font-medium">{title}</h3>
        <span className="text-sm text-gray-500">
          {memory.confidence != null
            ? `${Math.round(memory.confidence * 100)}% confidence`
            : ''}
        </span>
      </div>
      {description && (
        <p className="text-gray-600 dark:text-gray-400 mt-2 text-sm">
          {description}
        </p>
      )}
      {memory.tags && memory.tags.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {memory.tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Cost Comparison

| Service | Supabase | Neon + Vercel |
|:--------|:---------|:--------------|
| **Database** | $25/mo (Pro) | Free tier → $19/mo (Launch) |
| **Hosting** | Not included | Free (Vercel Hobby) or $20/mo (Pro) |
| **Vector Search** | Included | Included (pgvector) |
| **Connection Pooling** | REST only | Native pooling |
| **Scaling** | Manual | Auto-scaling (serverless) |
| **Branching** | Via projects/migrations | Native instant branching |
| **Cold Start** | N/A | ~250ms (optimized) |

**Estimated Monthly Cost:**
- **Development:** $0 (both Neon and Vercel have free tiers)
- **Production:** $19-39/mo (Neon Launch + Vercel Hobby/Pro)

---

## Migration Checklist

### Pre-Migration
- [ ] Export existing Supabase data (if any)
- [ ] Create Neon project and run schema
- [ ] Test connection from local environment
- [ ] Create Vercel project

### Migration Steps
- [ ] Update environment variables in Vercel
- [ ] Deploy API routes
- [ ] Verify `/api/health` endpoint
- [ ] Import existing data (if applicable)
- [ ] Update Claude skill to use API endpoints

### Post-Migration
- [ ] Monitor Neon dashboard for query performance
- [ ] Set up Vercel Analytics
- [ ] Configure alerting for errors
- [ ] Update documentation

---

## Benefits of Vercel + Neon

### For Development
1. **Database Branching** - Create isolated database branches for features
2. **Preview Deployments** - Each PR gets its own deployment + database branch
3. **Instant Rollbacks** - Vercel's instant rollback capability
4. **Edge Functions** - Run API routes closer to users

### For Production
1. **Serverless Scaling** - Both Neon and Vercel scale automatically
2. **Cost Efficiency** - Scale to zero when not in use
3. **Global Distribution** - Vercel's edge network
4. **Native Integration** - Vercel + Neon work seamlessly together

### For the A2I2 Platform
1. **Web Interface** - Finally have a UI for the knowledge system
2. **API Access** - Claude and other clients can use REST endpoints
3. **Real-time Dashboard** - Monitor memory system health
4. **Future Growth** - Ready for team collaboration features

---

## Next Steps After Deployment

1. **Add Authentication** - Implement Clerk or NextAuth for user management
2. **Build Chat Interface** - Integrate Claude via Vercel AI SDK
3. **Knowledge Graph Visualization** - D3.js or React Flow for entity graphs
4. **Voice Integration** - Connect PersonaPlex to the web interface
5. **Mobile App** - Use the API to build mobile clients

---

## Support

- **Neon Documentation:** https://neon.tech/docs
- **Vercel Documentation:** https://vercel.com/docs
- **A2I2 Issues:** https://github.com/therealchandlerbing/a2i2-beta-v1/issues

---

*Last Updated: 2026-01-25*
