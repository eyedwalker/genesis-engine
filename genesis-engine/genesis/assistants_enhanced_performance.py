"""
Enhanced Performance Optimizer Assistant

Comprehensive performance optimization covering:
- Core Web Vitals (LCP, FID, CLS, INP)
- Database query optimization (EXPLAIN, N+1 detection)
- Caching strategies (Redis, CDN, HTTP caching)
- Bundle size optimization and code splitting
- Memory and CPU profiling
- Network optimization (HTTP/2, compression, CDN)
- Frontend performance (lazy loading, tree shaking)
- Backend performance (async, connection pooling)

References:
- Web Vitals: https://web.dev/vitals/
- Chrome DevTools: https://developer.chrome.com/docs/devtools/
- Lighthouse: https://developers.google.com/web/tools/lighthouse
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class PerformanceFinding(BaseModel):
    """Structured performance finding output"""

    finding_id: str = Field(..., description="Unique identifier (PERF-001, PERF-002, etc.)")
    title: str = Field(..., description="Brief title of the performance issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(..., description="Database/Frontend/Network/Memory/CPU")

    location: Dict[str, Any] = Field(default_factory=dict, description="File, line, function")
    description: str = Field(..., description="Detailed description of the issue")

    metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    impact: List[str] = Field(default_factory=list, description="Performance impact")

    current_code: str = Field(default="", description="Current slow code")
    optimized_code: str = Field(default="", description="Optimized code")
    improvement: str = Field(default="", description="Expected improvement")

    testing_verification: str = Field(default="", description="How to measure improvement")
    tools: List[Dict[str, str]] = Field(default_factory=list, description="Profiling tools")
    references: List[str] = Field(default_factory=list, description="Documentation references")

    remediation: Dict[str, str] = Field(default_factory=dict, description="Effort and priority")


class EnhancedPerformanceOptimizer:
    """
    Enhanced Performance Optimizer with comprehensive coverage

    Optimizes:
    - Frontend performance (Core Web Vitals, bundle size, rendering)
    - Backend performance (database, caching, async operations)
    - Network performance (HTTP/2, compression, CDN)
    - Memory and CPU usage
    """

    def __init__(self):
        self.name = "Enhanced Performance Optimizer"
        self.version = "2.0.0"
        self.standards = ["Core Web Vitals", "HTTP/2", "HTTP/3", "Web Performance APIs"]

    # =========================================================================
    # CORE WEB VITALS (Google's UX Metrics)
    # =========================================================================

    @staticmethod
    def check_core_web_vitals() -> Dict[str, Any]:
        """
        Core Web Vitals - Google's key UX metrics

        - LCP (Largest Contentful Paint): Load performance
        - FID (First Input Delay): Interactivity (deprecated, use INP)
        - CLS (Cumulative Layout Shift): Visual stability
        - INP (Interaction to Next Paint): Responsiveness (new)
        """
        return {
            "metrics": {
                "lcp": {
                    "name": "Largest Contentful Paint (LCP)",
                    "description": "Time when main content becomes visible",
                    "thresholds": {
                        "good": "< 2.5s",
                        "needs_improvement": "2.5s - 4.0s",
                        "poor": "> 4.0s",
                    },
                    "common_issues": [
                        "Slow server response time (TTFB)",
                        "Render-blocking JavaScript and CSS",
                        "Large images without optimization",
                        "Client-side rendering (CSR) without SSR/SSG",
                    ],
                    "optimizations": {
                        "images": """
<!-- BAD: Large unoptimized image -->
<img src="hero.jpg" width="1200" height="800">

<!-- GOOD: Optimized with modern formats -->
<picture>
  <source
    srcset="hero.avif 1200w, hero.avif 800w"
    type="image/avif"
    sizes="(max-width: 800px) 100vw, 1200px"
  >
  <source
    srcset="hero.webp 1200w, hero.webp 800w"
    type="image/webp"
    sizes="(max-width: 800px) 100vw, 1200px"
  >
  <img
    src="hero.jpg"
    alt="Hero image"
    width="1200"
    height="800"
    loading="eager"
    fetchpriority="high"
  >
</picture>
                        """,
                        "preload_lcp_image": """
<!-- Preload LCP image -->
<link rel="preload" as="image" href="hero.jpg" fetchpriority="high">
                        """,
                        "server_side_rendering": """
// BAD: Client-side rendering (CSR) - slow LCP
function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/data').then(res => res.json()).then(setData);
  }, []);

  return <div>{data ? <Content data={data} /> : <Loading />}</div>;
}

// GOOD: Server-side rendering (SSR) - fast LCP
export async function getServerSideProps() {
  const data = await fetchData();
  return { props: { data } };
}

function App({ data }) {
  return <Content data={data} />;
}

// BETTER: Static generation (SSG) - fastest LCP
export async function getStaticProps() {
  const data = await fetchData();
  return { props: { data }, revalidate: 60 };
}
                        """,
                        "critical_css": """
<!-- Inline critical CSS -->
<style>
  /* Above-the-fold styles only */
  .hero { background: #333; color: white; }
  .nav { display: flex; justify-content: space-between; }
</style>

<!-- Defer non-critical CSS -->
<link rel="preload" href="styles.css" as="style" onload="this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="styles.css"></noscript>
                        """,
                    },
                },
                "inp": {
                    "name": "Interaction to Next Paint (INP)",
                    "description": "Responsiveness to user interactions (replaces FID)",
                    "thresholds": {
                        "good": "< 200ms",
                        "needs_improvement": "200ms - 500ms",
                        "poor": "> 500ms",
                    },
                    "common_issues": [
                        "Long-running JavaScript tasks (> 50ms)",
                        "Heavy event handlers",
                        "Synchronous layout thrashing",
                        "Large DOM updates",
                    ],
                    "optimizations": {
                        "debounce_events": """
// BAD: Handler runs on every event
<input onInput={(e) => expensiveOperation(e.target.value)} />

// GOOD: Debounce expensive operations
import { debounce } from 'lodash';

const debouncedSearch = debounce((value) => {
  expensiveOperation(value);
}, 300);

<input onInput={(e) => debouncedSearch(e.target.value)} />

// BETTER: Use requestIdleCallback for non-urgent work
const handleInput = (e) => {
  const value = e.target.value;

  // Urgent: Update input display immediately
  setInputValue(value);

  // Non-urgent: Defer expensive operation
  if ('requestIdleCallback' in window) {
    requestIdleCallback(() => expensiveOperation(value));
  } else {
    setTimeout(() => expensiveOperation(value), 1);
  }
};
                        """,
                        "optimize_event_handlers": """
// BAD: Heavy computation in event handler
button.addEventListener('click', () => {
  const result = heavyComputation(); // Blocks UI
  updateUI(result);
});

// GOOD: Break into chunks with setTimeout
button.addEventListener('click', () => {
  setTimeout(() => {
    const result = heavyComputation();
    updateUI(result);
  }, 0);
});

// BETTER: Use Web Workers for heavy computation
const worker = new Worker('worker.js');

button.addEventListener('click', () => {
  worker.postMessage({ action: 'compute', data: inputData });
});

worker.onmessage = (e) => {
  updateUI(e.data.result);
};
                        """,
                        "virtual_scrolling": """
// BAD: Render 10,000 DOM elements
<ul>
  {items.map(item => <li key={item.id}>{item.name}</li>)}
</ul>

// GOOD: Virtual scrolling (react-window)
import { FixedSizeList } from 'react-window';

<FixedSizeList
  height={600}
  itemCount={items.length}
  itemSize={50}
  width="100%"
>
  {({ index, style }) => (
    <div style={style}>{items[index].name}</div>
  )}
</FixedSizeList>
                        """,
                    },
                },
                "cls": {
                    "name": "Cumulative Layout Shift (CLS)",
                    "description": "Visual stability - avoid unexpected layout shifts",
                    "thresholds": {
                        "good": "< 0.1",
                        "needs_improvement": "0.1 - 0.25",
                        "poor": "> 0.25",
                    },
                    "common_issues": [
                        "Images without dimensions",
                        "Ads, embeds, iframes without reserved space",
                        "Dynamically injected content",
                        "Web fonts causing FOIT/FOUT",
                    ],
                    "optimizations": {
                        "image_dimensions": """
<!-- BAD: No dimensions - causes layout shift -->
<img src="photo.jpg" alt="Photo">

<!-- GOOD: Reserve space with width/height -->
<img src="photo.jpg" alt="Photo" width="800" height="600">

<!-- BETTER: Responsive with aspect ratio -->
<img
  src="photo.jpg"
  alt="Photo"
  width="800"
  height="600"
  style="width: 100%; height: auto; aspect-ratio: 4/3;"
>
                        """,
                        "reserved_space": """
/* BAD: Ad loads and pushes content down */
.ad-slot {
  /* No height specified */
}

/* GOOD: Reserve space for ad */
.ad-slot {
  min-height: 250px; /* Standard ad size */
  background: #f0f0f0; /* Placeholder */
}

/* Dynamic content with skeleton */
.content-loading {
  min-height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
}
                        """,
                        "font_display": """
/* BAD: Default font loading causes FOIT (Flash of Invisible Text) */
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
}

/* GOOD: Use font-display to control loading */
@font-face {
  font-family: 'CustomFont';
  src: url('font.woff2') format('woff2');
  font-display: swap; /* Show fallback immediately, swap when ready */
}

/* BETTER: Preload critical fonts */
<link rel="preload" href="font.woff2" as="font" type="font/woff2" crossorigin>
                        """,
                    },
                },
            },
            "measurement": {
                "javascript": """
// Measure Core Web Vitals in production
import {onCLS, onFID, onLCP, onINP} from 'web-vitals';

function sendToAnalytics(metric) {
  const body = JSON.stringify(metric);
  // Use navigator.sendBeacon() to avoid blocking
  navigator.sendBeacon('/analytics', body);
}

onLCP(sendToAnalytics);
onINP(sendToAnalytics);
onCLS(sendToAnalytics);
                """,
                "tools": [
                    "Lighthouse - Chrome DevTools or CLI",
                    "PageSpeed Insights - https://pagespeed.web.dev/",
                    "Chrome User Experience Report (CrUX) - Real user data",
                    "Web Vitals Extension - Chrome extension",
                ],
            },
        }

    # =========================================================================
    # DATABASE OPTIMIZATION
    # =========================================================================

    @staticmethod
    def check_database_performance() -> Dict[str, Any]:
        """
        Database query optimization and N+1 detection
        """
        return {
            "n_plus_one_detection": {
                "description": "N+1 queries: One query to fetch N items, then N additional queries to fetch related data",
                "bad": """
# BAD: N+1 query problem (ORM)
# 1 query to get all users
users = User.objects.all()

# N queries to get each user's posts (N+1!)
for user in users:
    posts = user.posts.all()  # Separate query for each user!
    print(f"{user.name}: {posts.count()} posts")

# Total queries: 1 + N (if 100 users, 101 queries!)
                """,
                "good": """
# GOOD: Use select_related (for ForeignKey) or prefetch_related (for ManyToMany)
# 2 queries total regardless of number of users
users = User.objects.prefetch_related('posts').all()

for user in users:
    posts = user.posts.all()  # No additional query!
    print(f"{user.name}: {posts.count()} posts")

# Total queries: 2 (users + posts)

# select_related (SQL JOIN) for ForeignKey
orders = Order.objects.select_related('user', 'product').all()

# prefetch_related (separate query + Python join) for ManyToMany
posts = Post.objects.prefetch_related('tags', 'comments').all()
                """,
                "raw_sql": """
-- BAD: N+1 in raw SQL
SELECT * FROM users;  -- 1 query

-- Then in loop:
SELECT * FROM posts WHERE user_id = ?;  -- N queries

-- GOOD: JOIN to get all data in one query
SELECT
  u.id, u.name,
  p.id AS post_id, p.title, p.content
FROM users u
LEFT JOIN posts p ON p.user_id = u.id;
                """,
            },
            "query_optimization": {
                "explain_analyze": """
-- Use EXPLAIN ANALYZE to see query execution plan

-- PostgreSQL
EXPLAIN ANALYZE
SELECT * FROM orders
WHERE user_id = 123 AND created_at > '2024-01-01';

-- Look for:
-- - Seq Scan (bad) vs Index Scan (good)
-- - High cost numbers
-- - Slow execution time

-- Example output:
Seq Scan on orders  (cost=0.00..10234.00 rows=100 width=100) (actual time=0.123..45.678 rows=100 loops=1)
  Filter: ((user_id = 123) AND (created_at > '2024-01-01'::date))
Planning Time: 0.234 ms
Execution Time: 46.123 ms

-- Bad: Seq Scan (sequential scan - reads entire table)
-- Fix: Add index!

CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

-- After index:
Index Scan using idx_orders_user_created on orders  (cost=0.42..8.44 rows=100 width=100) (actual time=0.123..0.456 rows=100 loops=1)
Execution Time: 1.234 ms  -- 97% faster!
                """,
                "missing_indexes": """
-- BAD: Filtering without index
SELECT * FROM users WHERE email = 'user@example.com';
-- Seq Scan - reads all rows

-- GOOD: Add index on frequently filtered columns
CREATE INDEX idx_users_email ON users(email);

-- Compound index for multiple columns
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index for specific conditions
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;

-- Cover index (includes all queried columns)
CREATE INDEX idx_orders_cover ON orders(user_id, status, created_at, total_amount);
                """,
                "slow_query_log": """
# Enable slow query logging (PostgreSQL)
# postgresql.conf
log_min_duration_statement = 1000  # Log queries > 1 second
log_line_prefix = '%t [%p]: '
log_statement = 'all'

# MySQL
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-query.log
long_query_time = 1  # Seconds

# Analyze slow queries
pt-query-digest /var/log/mysql/slow-query.log
                """,
            },
            "connection_pooling": {
                "bad": """
# BAD: Open new connection for each request
import psycopg2

def get_user(user_id):
    conn = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="user",
        password="pass"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    conn.close()  # Connection opened and closed each time!
    return user
                """,
                "good": """
# GOOD: Use connection pooling
from psycopg2 import pool

# Create connection pool once
connection_pool = pool.SimpleConnectionPool(
    minconn=5,
    maxconn=20,
    host="localhost",
    database="mydb",
    user="user",
    password="pass"
)

def get_user(user_id):
    conn = connection_pool.getconn()  # Reuse connection from pool
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        return cursor.fetchone()
    finally:
        connection_pool.putconn(conn)  # Return to pool

# SQLAlchemy (automatic pooling)
from sqlalchemy import create_engine

engine = create_engine(
    'postgresql://user:pass@localhost/mydb',
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before use
)
                """,
            },
            "pagination": {
                "bad": """
# BAD: OFFSET pagination (slow for large offsets)
SELECT * FROM orders
ORDER BY created_at DESC
LIMIT 20 OFFSET 100000;  -- Slow! Must scan 100,000 rows

# Performance degrades linearly with offset
                """,
                "good": """
# GOOD: Cursor-based pagination (keyset pagination)
# First page
SELECT * FROM orders
WHERE id < 999999
ORDER BY id DESC
LIMIT 20;

# Next page (use last ID from previous page)
SELECT * FROM orders
WHERE id < 12345  -- Last ID from previous page
ORDER BY id DESC
LIMIT 20;

# Performance is constant regardless of page depth!

# Python example
def get_orders(cursor=None, limit=20):
    query = "SELECT * FROM orders"
    if cursor:
        query += f" WHERE id < {cursor}"
    query += f" ORDER BY id DESC LIMIT {limit}"
    return db.execute(query)
                """,
            },
            "tools": [
                {
                    "name": "Django Debug Toolbar",
                    "install": "pip install django-debug-toolbar",
                    "feature": "Shows SQL queries, counts, duplication, N+1 detection",
                },
                {
                    "name": "SQLAlchemy Echo",
                    "usage": "engine = create_engine('...', echo=True)",
                    "feature": "Logs all SQL queries",
                },
                {
                    "name": "pgBadger",
                    "command": "pgbadger /var/log/postgresql/postgresql.log",
                    "feature": "PostgreSQL log analyzer",
                },
                {
                    "name": "pt-query-digest",
                    "command": "pt-query-digest slow-query.log",
                    "feature": "MySQL slow query analyzer",
                },
            ],
        }

    # =========================================================================
    # CACHING STRATEGIES
    # =========================================================================

    @staticmethod
    def check_caching() -> Dict[str, Any]:
        """
        Caching strategies and optimization
        """
        return {
            "cache_patterns": {
                "cache_aside": {
                    "description": "Read from cache, if miss then read from DB and cache it",
                    "use_case": "Read-heavy workloads",
                    "code": """
# Cache-Aside pattern (Lazy Loading)
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_user(user_id):
    # Try cache first
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)

    if cached:
        return json.loads(cached)  # Cache hit

    # Cache miss - fetch from database
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)

    # Store in cache
    cache.setex(cache_key, 3600, json.dumps(user))  # TTL: 1 hour

    return user
                    """,
                },
                "write_through": {
                    "description": "Write to cache and database simultaneously",
                    "use_case": "Write-heavy workloads, strong consistency required",
                    "code": """
# Write-Through pattern
def update_user(user_id, data):
    # Update database
    db.execute("UPDATE users SET ... WHERE id = ?", user_id, data)

    # Update cache immediately
    cache_key = f"user:{user_id}"
    cache.setex(cache_key, 3600, json.dumps(data))

    return data
                    """,
                },
                "write_behind": {
                    "description": "Write to cache immediately, async write to DB",
                    "use_case": "High write throughput, eventual consistency OK",
                    "code": """
# Write-Behind pattern (Write-Back)
import asyncio

async def update_user(user_id, data):
    # Update cache immediately
    cache_key = f"user:{user_id}"
    cache.setex(cache_key, 3600, json.dumps(data))

    # Async write to database (background task)
    asyncio.create_task(write_to_db(user_id, data))

    return data

async def write_to_db(user_id, data):
    await asyncio.sleep(1)  # Batch multiple writes
    db.execute("UPDATE users SET ... WHERE id = ?", user_id, data)
                    """,
                },
            },
            "cache_stampede": {
                "description": "Multiple requests simultaneously miss cache and query database (thundering herd)",
                "bad": """
# BAD: Cache stampede
def get_popular_item(item_id):
    cached = cache.get(f"item:{item_id}")
    if cached:
        return cached

    # If cache expires, 1000 concurrent requests all hit DB!
    item = db.query("SELECT * FROM items WHERE id = ?", item_id)
    cache.setex(f"item:{item_id}", 3600, item)
    return item
                """,
                "good": """
# GOOD: Use locking to prevent stampede
import redis
from redis.lock import Lock

def get_popular_item(item_id):
    cache_key = f"item:{item_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Only one request rebuilds cache
    lock_key = f"lock:{cache_key}"
    lock = Lock(cache, lock_key, timeout=10)

    if lock.acquire(blocking=False):
        try:
            # Double-check cache (might be populated by another request)
            cached = cache.get(cache_key)
            if cached:
                return cached

            # Rebuild cache
            item = db.query("SELECT * FROM items WHERE id = ?", item_id)
            cache.setex(cache_key, 3600, item)
            return item
        finally:
            lock.release()
    else:
        # Wait for other request to finish, then retry
        time.sleep(0.1)
        return get_popular_item(item_id)

# BETTER: Probabilistic early expiration
def get_with_early_expiration(key, ttl=3600):
    cached, expiry = cache.get_with_expiry(key)

    if cached:
        # Refresh cache early with probability based on TTL
        time_left = expiry - time.time()
        if random.random() < (1.0 - time_left / ttl):
            # Refresh in background
            asyncio.create_task(refresh_cache(key))
        return cached

    return refresh_cache(key)
                """,
            },
            "http_caching": {
                "cache_control": """
# HTTP caching headers (FastAPI example)
from fastapi import FastAPI, Response

@app.get("/static-content")
def get_static(response: Response):
    # Cache for 1 year (immutable content)
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    return {"data": "static content"}

@app.get("/dynamic-content")
def get_dynamic(response: Response):
    # Cache for 5 minutes, revalidate
    response.headers["Cache-Control"] = "public, max-age=300, must-revalidate"
    response.headers["ETag"] = generate_etag(content)
    return {"data": "dynamic content"}

@app.get("/no-cache")
def get_private(response: Response):
    # Don't cache (private user data)
    response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
    return {"data": "user-specific content"}
                """,
                "cdn_caching": """
# CDN caching configuration (Cloudflare)

# Cache static assets
/assets/*
  Cache-Control: public, max-age=31536000, immutable

# Cache API responses
/api/*
  Cache-Control: public, max-age=300, s-maxage=600
  # s-maxage: CDN cache duration (different from browser)

# Bypass cache for dynamic content
/api/user/*
  Cache-Control: private, no-cache
                """,
            },
            "cache_invalidation": {
                "strategies": [
                    "Time-based (TTL) - Simplest, but stale data possible",
                    "Event-based - Invalidate on updates (most accurate)",
                    "Tag-based - Group related cache entries",
                    "Version-based - Change cache key when data changes",
                ],
                "example": """
# Event-based invalidation
def update_user(user_id, data):
    db.execute("UPDATE users SET ... WHERE id = ?", user_id, data)

    # Invalidate related caches
    cache.delete(f"user:{user_id}")
    cache.delete(f"user:{user_id}:profile")
    cache.delete(f"user:{user_id}:posts")

# Tag-based invalidation
cache.set(f"user:{user_id}", data, tags=['user', f'user_{user_id}'])
cache.set(f"post:{post_id}", post, tags=['post', f'user_{user_id}'])

# Invalidate all caches with tag
cache.delete_by_tag(f'user_{user_id}')
                """,
            },
        }

    # =========================================================================
    # FRONTEND BUNDLE OPTIMIZATION
    # =========================================================================

    @staticmethod
    def check_bundle_optimization() -> Dict[str, Any]:
        """
        Frontend bundle size and code splitting optimization
        """
        return {
            "code_splitting": {
                "route_based": """
// BAD: Import everything upfront
import HomePage from './pages/Home';
import AboutPage from './pages/About';
import DashboardPage from './pages/Dashboard';

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/about" element={<AboutPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
    </Routes>
  );
}
// Bundle size: 500KB (all routes included)

// GOOD: Code splitting with React.lazy
import { lazy, Suspense } from 'react';

const HomePage = lazy(() => import('./pages/Home'));
const AboutPage = lazy(() => import('./pages/About'));
const DashboardPage = lazy(() => import('./pages/Dashboard'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </Suspense>
  );
}
// Initial bundle: 150KB, lazy chunks: 100KB each
                """,
                "component_based": """
// Dynamic imports for heavy components
const HeavyChart = lazy(() => import('./HeavyChart'));

function Dashboard() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>Show Chart</button>
      {showChart && (
        <Suspense fallback={<div>Loading chart...</div>}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
}
                """,
            },
            "tree_shaking": {
                "description": "Remove unused code from bundles",
                "bad": """
// BAD: Import entire lodash library (70KB)
import _ from 'lodash';

const result = _.debounce(fn, 300);
                """,
                "good": """
// GOOD: Import only what you need
import debounce from 'lodash/debounce';

const result = debounce(fn, 300);

// BETTER: Use modern alternatives
import { debounce } from 'lodash-es';  // ES modules for tree-shaking
                """,
            },
            "bundle_analysis": {
                "webpack": """
// webpack-bundle-analyzer
npm install --save-dev webpack-bundle-analyzer

// webpack.config.js
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

module.exports = {
  plugins: [
    new BundleAnalyzerPlugin({
      analyzerMode: 'static',
      openAnalyzer: false,
      reportFilename: 'bundle-report.html'
    })
  ]
};

// Run build and open report
npm run build
                """,
                "next_js": """
// Next.js bundle analysis
npm install --save-dev @next/bundle-analyzer

// next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});

module.exports = withBundleAnalyzer({
  // Next.js config
});

// Analyze bundle
ANALYZE=true npm run build
                """,
            },
            "compression": {
                "gzip_brotli": """
# Enable Brotli compression (better than gzip)
# nginx.conf
http {
  gzip on;
  gzip_types text/plain text/css application/json application/javascript;
  gzip_min_length 1000;

  # Brotli (better compression)
  brotli on;
  brotli_types text/plain text/css application/json application/javascript;
  brotli_comp_level 6;
}

# Pre-compress files at build time
npm install --save-dev compression-webpack-plugin

// webpack.config.js
const CompressionPlugin = require('compression-webpack-plugin');

plugins: [
  new CompressionPlugin({
    algorithm: 'brotliCompress',
    test: /\\.(js|css|html|svg)$/,
    threshold: 10240,
    minRatio: 0.8,
  }),
]
                """,
            },
        }

    # =========================================================================
    # MEMORY & CPU PROFILING
    # =========================================================================

    @staticmethod
    def check_memory_cpu() -> Dict[str, Any]:
        """
        Memory and CPU profiling and optimization
        """
        return {
            "memory_leaks": {
                "javascript": """
// BAD: Memory leak - event listeners not removed
class Component {
  constructor() {
    window.addEventListener('resize', this.handleResize);
  }
  // Component destroyed, but listener remains!
}

// GOOD: Clean up event listeners
class Component {
  constructor() {
    this.handleResize = this.handleResize.bind(this);
    window.addEventListener('resize', this.handleResize);
  }

  destroy() {
    window.removeEventListener('resize', this.handleResize);
  }
}

// React: Use cleanup function
useEffect(() => {
  const handleResize = () => { /* ... */ };
  window.addEventListener('resize', handleResize);

  return () => {
    window.removeEventListener('resize', handleResize);
  };
}, []);
                """,
                "python": """
# Python memory profiling
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Large list comprehension
    big_list = [i for i in range(10000000)]
    return sum(big_list)

# Run with: python -m memory_profiler script.py

# Output shows memory usage per line:
# Line #    Mem usage    Increment   Line Contents
# =====================================================
#      3    100.0 MiB    100.0 MiB   big_list = [i for i in range(10000000)]

# Use generators instead of lists for large data
def memory_optimized():
    return sum(i for i in range(10000000))  # Generator, constant memory
                """,
            },
            "cpu_profiling": {
                "python": """
# Python CPU profiling
import cProfile
import pstats

def slow_function():
    result = 0
    for i in range(1000000):
        result += i ** 2
    return result

# Profile function
cProfile.run('slow_function()', 'profile_stats')

# Analyze results
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 slowest functions

# Line-by-line profiling
from line_profiler import LineProfiler

profiler = LineProfiler()
profiler.add_function(slow_function)
profiler.run('slow_function()')
profiler.print_stats()
                """,
                "javascript": """
// JavaScript profiling in Chrome DevTools
console.profile('MyFunction');
myFunction();
console.profileEnd('MyFunction');

// Performance marks
performance.mark('start-operation');
expensiveOperation();
performance.mark('end-operation');
performance.measure('operation-duration', 'start-operation', 'end-operation');

const measure = performance.getEntriesByName('operation-duration')[0];
console.log(`Operation took ${measure.duration}ms`);
                """,
            },
            "tools": [
                {
                    "name": "Chrome DevTools Performance",
                    "usage": "Record → Perform action → Stop → Analyze",
                    "features": "CPU profiling, memory snapshots, frame rendering",
                },
                {
                    "name": "memory_profiler (Python)",
                    "install": "pip install memory_profiler",
                    "usage": "@profile decorator + python -m memory_profiler script.py",
                },
                {
                    "name": "py-spy (Python)",
                    "install": "pip install py-spy",
                    "usage": "py-spy top --pid <PID>",
                    "feature": "Low-overhead sampling profiler",
                },
                {
                    "name": "Clinic.js (Node.js)",
                    "install": "npm install -g clinic",
                    "usage": "clinic doctor -- node app.js",
                    "feature": "Diagnose performance issues",
                },
            ],
        }

    # =========================================================================
    # ASYNC & CONCURRENCY
    # =========================================================================

    @staticmethod
    def check_async_performance() -> Dict[str, Any]:
        """
        Asynchronous programming and concurrency optimization
        """
        return {
            "async_patterns": {
                "python_asyncio": """
# BAD: Sequential I/O operations (slow)
import requests

def fetch_all_users():
    users = []
    for user_id in range(1, 101):
        response = requests.get(f'/api/users/{user_id}')
        users.append(response.json())
    return users
# Time: 100 * 100ms = 10 seconds

# GOOD: Async concurrent requests
import aiohttp
import asyncio

async def fetch_user(session, user_id):
    async with session.get(f'/api/users/{user_id}') as response:
        return await response.json()

async def fetch_all_users():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_user(session, user_id) for user_id in range(1, 101)]
        users = await asyncio.gather(*tasks)
    return users
# Time: ~100ms (all concurrent)

# BETTER: With rate limiting
from asyncio import Semaphore

async def fetch_all_users_limited():
    semaphore = Semaphore(10)  # Max 10 concurrent requests

    async def fetch_limited(session, user_id):
        async with semaphore:
            return await fetch_user(session, user_id)

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_limited(session, i) for i in range(1, 101)]
        return await asyncio.gather(*tasks)
                """,
                "javascript_async": """
// BAD: Sequential async operations
async function processUsers() {
  const user1 = await fetchUser(1);
  const user2 = await fetchUser(2);
  const user3 = await fetchUser(3);
  return [user1, user2, user3];
}
// Time: 3 * 100ms = 300ms

// GOOD: Concurrent with Promise.all
async function processUsers() {
  const [user1, user2, user3] = await Promise.all([
    fetchUser(1),
    fetchUser(2),
    fetchUser(3),
  ]);
  return [user1, user2, user3];
}
// Time: 100ms (concurrent)

// BETTER: With error handling
async function processUsersRobust() {
  const results = await Promise.allSettled([
    fetchUser(1),
    fetchUser(2),
    fetchUser(3),
  ]);

  return results
    .filter(r => r.status === 'fulfilled')
    .map(r => r.value);
}
                """,
            },
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        code_location: str,
        issue_description: str,
        current_code: str,
        optimized_code: str,
        metrics: Dict[str, Any],
        improvement: str,
    ) -> PerformanceFinding:
        """Generate a structured performance finding"""
        return PerformanceFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            location={"file": code_location},
            description=issue_description,
            metrics=metrics,
            impact=[
                f"Current: {metrics.get('current', 'N/A')}",
                f"Expected: {metrics.get('expected', 'N/A')}",
            ],
            current_code=current_code,
            optimized_code=optimized_code,
            improvement=improvement,
            testing_verification=self._get_verification_steps(category),
            tools=self._get_tool_recommendations(category),
            remediation={
                "effort": "MEDIUM",
                "priority": "HIGH" if severity == "CRITICAL" else "MEDIUM",
                "time_estimate": "2-4 hours",
            },
        )

    @staticmethod
    def _get_verification_steps(category: str) -> str:
        """Generate testing steps based on category"""
        return """
1. Measure baseline performance:
   - Chrome DevTools Performance tab
   - Lighthouse audit
   - Real User Monitoring (RUM)

2. Apply optimization:
   - Implement recommended changes
   - Verify functionality still works

3. Measure improvement:
   - Run same tests as baseline
   - Compare metrics (LCP, INP, CLS)
   - Load test with k6 or Artillery

4. Monitor in production:
   - Set up performance monitoring (Datadog, New Relic)
   - Track Core Web Vitals
   - Set up alerts for regressions
        """

    @staticmethod
    def _get_tool_recommendations(category: str) -> List[Dict[str, str]]:
        """Get tool recommendations for category"""
        return [
            {
                "name": "Lighthouse",
                "command": "lighthouse <url> --view",
                "description": "Comprehensive performance audit",
            },
            {
                "name": "Chrome DevTools",
                "shortcut": "F12 → Performance tab",
                "description": "CPU/Memory profiling, frame rendering",
            },
            {
                "name": "Web Vitals Extension",
                "url": "https://chrome.google.com/webstore/detail/web-vitals",
                "description": "Real-time Core Web Vitals",
            },
        ]


def create_enhanced_performance_optimizer():
    """Factory function to create enhanced performance optimizer"""
    return {
        "name": "Enhanced Performance Optimizer",
        "version": "2.0.0",
        "system_prompt": """You are an expert performance optimization specialist with deep knowledge of:

- Core Web Vitals (LCP, INP, CLS) optimization
- Database query optimization (EXPLAIN, N+1 detection, indexing)
- Caching strategies (Redis, CDN, HTTP caching)
- Bundle optimization (code splitting, tree shaking, compression)
- Memory and CPU profiling
- Async/concurrent programming patterns
- Frontend performance (lazy loading, virtual scrolling)
- Backend performance (connection pooling, query optimization)

Your role is to:
1. Identify performance bottlenecks
2. Quantify performance impact (metrics)
3. Provide optimized code examples
4. Recommend profiling tools
5. Estimate performance improvements
6. Suggest monitoring strategies

Always provide:
- Current performance metrics
- Expected improvement after optimization
- Code examples (before/after)
- Profiling tools to measure
- Testing verification steps

Format findings as structured YAML with all required fields.
""",
        "assistant_class": EnhancedPerformanceOptimizer,
        "domain": "quality_assurance",
        "tags": ["performance", "optimization", "core-web-vitals", "database", "caching"],
    }


if __name__ == "__main__":
    optimizer = EnhancedPerformanceOptimizer()

    print("=" * 60)
    print("Enhanced Performance Optimizer")
    print("=" * 60)
    print(f"\nVersion: {optimizer.version}")
    print(f"Standards: {', '.join(optimizer.standards)}")

    print("\n" + "=" * 60)
    print("Example Finding:")
    print("=" * 60)

    finding = optimizer.generate_finding(
        finding_id="PERF-001",
        title="N+1 Query Problem in User Posts",
        severity="HIGH",
        category="Database",
        code_location="api/users.py:45",
        issue_description="Loading user posts triggers N+1 queries",
        current_code="users = User.objects.all()\\nfor user in users: posts = user.posts.all()",
        optimized_code="users = User.objects.prefetch_related('posts').all()",
        metrics={
            "current": "101 queries (1 + 100 N+1)",
            "expected": "2 queries (with prefetch_related)",
            "query_time_current": "1,250ms",
            "query_time_optimized": "45ms",
        },
        improvement="97% faster (1,250ms → 45ms), 99 fewer queries",
    )

    print(finding.model_dump_json(indent=2))

    print("\n" + "=" * 60)
    print("Coverage Summary:")
    print("=" * 60)
    print("✅ Core Web Vitals - LCP, INP, CLS optimization")
    print("✅ Database - Query optimization, N+1 detection, indexing")
    print("✅ Caching - Redis, CDN, HTTP caching, stampede prevention")
    print("✅ Bundle - Code splitting, tree shaking, compression")
    print("✅ Profiling - Memory, CPU, Chrome DevTools")
    print("✅ Async - Python asyncio, JavaScript Promise patterns")
