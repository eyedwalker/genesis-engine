"""
Enhanced Caching Strategy Advisor

Comprehensive caching patterns covering:
- Eviction policies (LRU, LFU, FIFO, ARC, SLRU, W-TinyLFU)
- Cache stampede prevention (locking, probabilistic, lease-based)
- Multi-level caching (L1, L2, L3, near/far cache)
- Cache warming strategies
- Tag-based invalidation
- Cache sizing calculations
- HTTP caching (CDN, browser, conditional requests)
- Distributed caching patterns
- Cache consistency patterns
- Memory management and GC impact

References:
- Redis Documentation: https://redis.io/docs/
- HTTP Caching: https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
- RFC 7234: Caching: https://tools.ietf.org/html/rfc7234
- Caffeine Cache: https://github.com/ben-manes/caffeine
- Cache Consistency: https://martinfowler.com/articles/lmax.html
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class CachingFinding(BaseModel):
    """Structured caching finding output"""

    finding_id: str = Field(..., description="Unique identifier (CACHE-001, CACHE-002, etc.)")
    title: str = Field(..., description="Brief title of the issue")
    severity: str = Field(..., description="CRITICAL/HIGH/MEDIUM/LOW")
    category: str = Field(
        ..., description="eviction/stampede/consistency/sizing/invalidation/http"
    )

    location: Dict[str, Any] = Field(
        default_factory=dict, description="Cache key pattern, service, endpoint"
    )
    description: str = Field(default="", description="Detailed description of the issue")
    pattern_violated: str = Field(default="", description="Which caching pattern violated")

    current_implementation: str = Field(default="", description="Current caching code")
    improved_implementation: str = Field(default="", description="Improved caching code")
    explanation: str = Field(default="", description="Why the improvement is better")

    cache_metrics: Dict[str, Any] = Field(
        default_factory=dict, description="Hit rate, latency, memory usage"
    )
    performance_impact: str = Field(default="", description="Expected performance improvement")

    tools: List[Dict[str, str]] = Field(default_factory=list, description="Caching tools")
    references: List[str] = Field(default_factory=list, description="Documentation references")

    remediation: Dict[str, str] = Field(
        default_factory=dict, description="Step-by-step remediation guide"
    )


class EnhancedCachingAssistant:
    """
    Enhanced Caching Strategy Advisor

    Provides comprehensive caching guidance covering:
    - Eviction policies (LRU, LFU, ARC, W-TinyLFU)
    - Cache stampede prevention techniques
    - Multi-level caching architectures
    - Cache sizing and memory calculations
    - Distributed caching patterns
    - HTTP caching strategies
    - Cache invalidation patterns
    """

    def __init__(self):
        self.name = "Enhanced Caching Strategy Advisor"
        self.version = "2.0.0"
        self.standards = [
            "Redis Best Practices",
            "Memcached",
            "HTTP Caching (RFC 7234)",
            "CDN Caching",
            "Caffeine/Guava Cache",
        ]

    # =========================================================================
    # CACHE PATTERNS - Fundamental Strategies
    # =========================================================================

    @staticmethod
    def check_cache_aside_pattern() -> Dict[str, Any]:
        """
        Cache-Aside (Lazy Loading) Pattern

        Application manages both cache and database.
        Data is loaded into cache on demand.
        """
        return {
            "description": "Application loads data into cache on demand",
            "when_to_use": [
                "Read-heavy workloads",
                "When cache miss is acceptable occasionally",
                "Data that doesn't change frequently",
            ],
            "examples": {
                "bad": '''
# BAD: No caching - every request hits database
def get_user(user_id: str) -> dict:
    # Always queries database
    return db.query("SELECT * FROM users WHERE id = ?", user_id)

# BAD: No TTL - stale data forever
def get_user_bad_ttl(user_id: str) -> dict:
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    cache.set(cache_key, user)  # No TTL! Stale forever
    return user

# BAD: No error handling - cache failure breaks app
def get_user_no_error_handling(user_id: str) -> dict:
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)  # What if Redis is down?
    if cached:
        return cached
    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    cache.setex(cache_key, 3600, user)  # What if this fails?
    return user
''',
                "good": '''
# GOOD: Proper cache-aside with error handling and TTL
import json
import logging
from typing import Optional
from functools import wraps

logger = logging.getLogger(__name__)

class CacheAside:
    """Robust cache-aside implementation"""

    def __init__(self, cache_client, default_ttl: int = 3600):
        self.cache = cache_client
        self.default_ttl = default_ttl

    def get_or_load(
        self,
        key: str,
        loader: callable,
        ttl: Optional[int] = None,
        serialize: bool = True
    ):
        """
        Get from cache or load from source.

        Args:
            key: Cache key
            loader: Function to load data if cache miss
            ttl: Time to live in seconds
            serialize: Whether to JSON serialize/deserialize
        """
        ttl = ttl or self.default_ttl

        # Try cache first
        try:
            cached = self.cache.get(key)
            if cached is not None:
                logger.debug(f"Cache hit: {key}")
                return json.loads(cached) if serialize else cached
        except Exception as e:
            # Cache failure should not break the app
            logger.warning(f"Cache get failed for {key}: {e}")

        # Cache miss - load from source
        logger.debug(f"Cache miss: {key}")
        data = loader()

        # Update cache (best effort)
        try:
            value = json.dumps(data) if serialize else data
            self.cache.setex(key, ttl, value)
        except Exception as e:
            logger.warning(f"Cache set failed for {key}: {e}")

        return data


# Decorator version for cleaner code
def cached(
    key_pattern: str,
    ttl: int = 3600,
    cache_client = None
):
    """Decorator for cache-aside pattern"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key from pattern and arguments
            cache_key = key_pattern.format(*args, **kwargs)

            try:
                cached_value = cache_client.get(cache_key)
                if cached_value:
                    return json.loads(cached_value)
            except Exception as e:
                logger.warning(f"Cache get error: {e}")

            result = func(*args, **kwargs)

            try:
                cache_client.setex(cache_key, ttl, json.dumps(result))
            except Exception as e:
                logger.warning(f"Cache set error: {e}")

            return result
        return wrapper
    return decorator


# Usage
cache_aside = CacheAside(redis_client)

def get_user(user_id: str) -> dict:
    return cache_aside.get_or_load(
        key=f"user:{user_id}",
        loader=lambda: db.query("SELECT * FROM users WHERE id = ?", user_id),
        ttl=3600
    )

# Or with decorator
@cached(key_pattern="user:{0}", ttl=3600, cache_client=redis_client)
def get_user_decorated(user_id: str) -> dict:
    return db.query("SELECT * FROM users WHERE id = ?", user_id)
''',
            },
            "tools": [
                {
                    "name": "Redis",
                    "url": "https://redis.io/",
                    "install": "pip install redis",
                },
            ],
        }

    @staticmethod
    def check_write_through_pattern() -> Dict[str, Any]:
        """
        Write-Through Pattern

        Application writes to cache, cache synchronously writes to database.
        Ensures cache is always consistent with database.
        """
        return {
            "description": "Data is written to cache and database synchronously",
            "when_to_use": [
                "Write-heavy workloads where consistency is critical",
                "When stale reads are unacceptable",
                "Financial or transactional data",
            ],
            "examples": {
                "bad": '''
# BAD: Write to DB only, cache becomes stale
def update_user(user_id: str, data: dict):
    db.execute("UPDATE users SET name = ? WHERE id = ?", data["name"], user_id)
    # Cache still has old data!

# BAD: Write to cache first, then DB - inconsistent on failure
def update_user_bad_order(user_id: str, data: dict):
    cache.setex(f"user:{user_id}", 3600, json.dumps(data))
    # If DB write fails, cache has data that DB doesn't!
    db.execute("UPDATE users SET name = ? WHERE id = ?", data["name"], user_id)
''',
                "good": '''
# GOOD: Write-through with transaction-like behavior
class WriteThroughCache:
    """Write-through cache with consistency guarantees"""

    def __init__(self, cache_client, db_client, default_ttl: int = 3600):
        self.cache = cache_client
        self.db = db_client
        self.default_ttl = default_ttl

    def write(
        self,
        cache_key: str,
        db_operation: callable,
        data: any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Write data to both database and cache.

        Database write happens first to ensure consistency.
        If DB write succeeds but cache fails, we accept temporary inconsistency
        (cache will be updated on next read or TTL expiry).
        """
        ttl = ttl or self.default_ttl

        # Step 1: Write to database first (source of truth)
        try:
            db_operation()
        except Exception as e:
            logger.error(f"Database write failed: {e}")
            raise  # Don't update cache if DB failed

        # Step 2: Update cache (best effort)
        try:
            self.cache.setex(cache_key, ttl, json.dumps(data))
            logger.debug(f"Cache updated: {cache_key}")
        except Exception as e:
            # Log but don't fail - DB is source of truth
            logger.warning(f"Cache update failed (DB succeeded): {e}")
            # Optionally: invalidate stale cache entry
            try:
                self.cache.delete(cache_key)
            except:
                pass

        return True


# Usage
write_through = WriteThroughCache(redis_client, db_client)

def update_user(user_id: str, name: str, email: str):
    data = {"id": user_id, "name": name, "email": email}

    write_through.write(
        cache_key=f"user:{user_id}",
        db_operation=lambda: db.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            name, email, user_id
        ),
        data=data,
        ttl=3600
    )

    return data
''',
            },
            "tools": [
                {
                    "name": "Redis",
                    "url": "https://redis.io/",
                },
            ],
        }

    @staticmethod
    def check_write_behind_pattern() -> Dict[str, Any]:
        """
        Write-Behind (Write-Back) Pattern

        Application writes to cache, cache asynchronously writes to database.
        Improves write performance but risks data loss.
        """
        return {
            "description": "Data is written to cache immediately, database updated asynchronously",
            "when_to_use": [
                "High write throughput requirements",
                "When some data loss is acceptable",
                "Batch processing of writes",
                "Write coalescing needed",
            ],
            "examples": {
                "bad": '''
# BAD: Fire and forget - no guarantee of DB write
async def update_counter_bad(key: str, value: int):
    cache.set(f"counter:{key}", value)
    asyncio.create_task(db.execute(...))  # What if this fails?
    # No error handling, no retry, data could be lost
''',
                "good": '''
# GOOD: Write-behind with durability guarantees
import asyncio
from collections import defaultdict
from datetime import datetime
import json

class WriteBehindCache:
    """
    Write-behind cache with batching and durability.

    Writes are buffered in cache and periodically flushed to database.
    Uses write coalescing to reduce database operations.
    """

    def __init__(
        self,
        cache_client,
        db_client,
        flush_interval: int = 5,
        max_buffer_size: int = 1000
    ):
        self.cache = cache_client
        self.db = db_client
        self.flush_interval = flush_interval
        self.max_buffer_size = max_buffer_size
        self.write_buffer: Dict[str, dict] = {}
        self._running = False

    async def start(self):
        """Start background flush task"""
        self._running = True
        asyncio.create_task(self._flush_loop())

    async def stop(self):
        """Stop and flush remaining writes"""
        self._running = False
        await self._flush_to_db()

    async def write(self, key: str, data: dict):
        """Write to cache and buffer for DB"""
        # Immediate cache update
        self.cache.set(key, json.dumps(data))

        # Add to write buffer (coalesces multiple writes to same key)
        self.write_buffer[key] = {
            "data": data,
            "timestamp": datetime.utcnow(),
            "retries": 0
        }

        # Flush if buffer is full
        if len(self.write_buffer) >= self.max_buffer_size:
            await self._flush_to_db()

    async def _flush_loop(self):
        """Periodically flush buffer to database"""
        while self._running:
            await asyncio.sleep(self.flush_interval)
            await self._flush_to_db()

    async def _flush_to_db(self):
        """Flush all buffered writes to database"""
        if not self.write_buffer:
            return

        # Swap buffer for processing
        buffer = self.write_buffer
        self.write_buffer = {}

        failed = {}
        for key, entry in buffer.items():
            try:
                await self._write_to_db(key, entry["data"])
                logger.debug(f"Flushed to DB: {key}")
            except Exception as e:
                logger.error(f"DB write failed for {key}: {e}")
                entry["retries"] += 1
                if entry["retries"] < 3:
                    failed[key] = entry  # Retry later

        # Add failed writes back to buffer
        self.write_buffer.update(failed)

    async def _write_to_db(self, key: str, data: dict):
        """Write single entry to database"""
        # Implement based on your data model
        await self.db.execute(
            "INSERT INTO data (key, value) VALUES (?, ?) "
            "ON CONFLICT (key) DO UPDATE SET value = ?",
            key, json.dumps(data), json.dumps(data)
        )


# Usage with durability via Redis Streams (for crash recovery)
class DurableWriteBehind:
    """Write-behind with Redis Stream for durability"""

    def __init__(self, redis_client, db_client, stream_key: str = "write_queue"):
        self.cache = redis_client
        self.db = db_client
        self.stream_key = stream_key

    async def write(self, cache_key: str, data: dict):
        """Write to cache and durable queue"""
        # Update cache
        self.cache.set(cache_key, json.dumps(data))

        # Add to durable stream (persisted even on crash)
        self.cache.xadd(
            self.stream_key,
            {"key": cache_key, "data": json.dumps(data)},
            maxlen=100000  # Limit stream size
        )

    async def process_queue(self):
        """Process durable queue (run on startup and continuously)"""
        consumer_group = "db_writers"
        consumer_name = "worker_1"

        # Create consumer group if not exists
        try:
            self.cache.xgroup_create(self.stream_key, consumer_group, mkstream=True)
        except:
            pass  # Group already exists

        while True:
            # Read from stream
            messages = self.cache.xreadgroup(
                consumer_group, consumer_name,
                {self.stream_key: ">"},
                count=100,
                block=5000
            )

            for stream, entries in messages:
                for msg_id, fields in entries:
                    try:
                        await self._write_to_db(
                            fields["key"],
                            json.loads(fields["data"])
                        )
                        # Acknowledge message
                        self.cache.xack(self.stream_key, consumer_group, msg_id)
                    except Exception as e:
                        logger.error(f"Failed to process {msg_id}: {e}")
                        # Message will be re-delivered
''',
            },
            "tools": [
                {
                    "name": "Redis Streams",
                    "url": "https://redis.io/docs/data-types/streams/",
                },
            ],
        }

    @staticmethod
    def cache_patterns() -> Dict[str, Any]:
        """Common caching patterns summary"""
        return {
            "cache_aside": """
# Cache-Aside (Lazy Loading)
def get_user(user_id):
    cache_key = f"user:{user_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached  # Cache hit

    user = db.query("SELECT * FROM users WHERE id = ?", user_id)
    cache.setex(cache_key, 3600, user)  # TTL: 1 hour
    return user
            """,
            "write_through": """
# Write-Through
def update_user(user_id, data):
    db.execute("UPDATE users SET ... WHERE id = ?", user_id, data)
    cache.setex(f"user:{user_id}", 3600, data)
            """,
            "write_behind": """
# Write-Behind (Async)
async def update_user(user_id, data):
    cache.setex(f"user:{user_id}", 3600, data)
    asyncio.create_task(write_to_db(user_id, data))
            """,
            "refresh_ahead": """
# Refresh-Ahead (Proactive refresh before expiry)
def get_with_refresh_ahead(key, ttl=3600, refresh_threshold=0.2):
    data, remaining_ttl = cache.get_with_ttl(key)
    if data:
        if remaining_ttl < ttl * refresh_threshold:
            # Proactively refresh in background
            background_refresh(key)
        return data
    return load_and_cache(key, ttl)
            """,
        }

    # =========================================================================
    # CACHE STAMPEDE PREVENTION
    # =========================================================================

    @staticmethod
    def check_cache_stampede() -> Dict[str, Any]:
        """
        Cache Stampede Prevention

        When a popular cache key expires, many requests simultaneously
        try to regenerate it, overwhelming the database.
        """
        return {
            "description": "Prevent thundering herd when cache keys expire",
            "techniques": [
                "Locking (distributed mutex)",
                "Probabilistic early expiration (XFetch)",
                "Lease-based approach",
                "Background refresh",
                "Stale-while-revalidate",
            ],
            "examples": {
                "bad": '''
# BAD: Classic stampede-prone code
def get_popular_data(key: str) -> dict:
    cached = cache.get(key)
    if cached:
        return cached

    # 1000 requests hit this simultaneously when key expires!
    data = expensive_query()  # Database overloaded
    cache.setex(key, 3600, data)
    return data
''',
                "good": '''
# GOOD: Multiple stampede prevention techniques

import time
import random
import math
import threading
from typing import Optional, Tuple

class StampedeProtectedCache:
    """Cache with multiple stampede prevention strategies"""

    def __init__(self, cache_client, default_ttl: int = 3600):
        self.cache = cache_client
        self.default_ttl = default_ttl

    # === TECHNIQUE 1: Distributed Locking ===
    def get_with_lock(
        self,
        key: str,
        loader: callable,
        ttl: int = None,
        lock_timeout: int = 10
    ):
        """
        Use distributed lock to ensure only one request regenerates cache.
        Other requests wait or return stale data.
        """
        ttl = ttl or self.default_ttl

        # Try cache first
        cached = self.cache.get(key)
        if cached:
            return json.loads(cached)

        # Try to acquire lock
        lock_key = f"lock:{key}"
        lock_acquired = self.cache.set(lock_key, "1", nx=True, ex=lock_timeout)

        if lock_acquired:
            try:
                # We got the lock - regenerate cache
                data = loader()
                self.cache.setex(key, ttl, json.dumps(data))
                return data
            finally:
                self.cache.delete(lock_key)
        else:
            # Another request is regenerating - wait and retry
            for _ in range(50):  # Max 5 seconds
                time.sleep(0.1)
                cached = self.cache.get(key)
                if cached:
                    return json.loads(cached)

            # Fallback: load ourselves
            return loader()

    # === TECHNIQUE 2: Probabilistic Early Expiration (XFetch) ===
    def get_with_xfetch(
        self,
        key: str,
        loader: callable,
        ttl: int = None,
        beta: float = 1.0
    ):
        """
        XFetch algorithm: probabilistically refresh before expiry.

        Each request has a small chance of refreshing early, spreading
        the refresh load over time instead of all at once at expiry.

        Based on: "Optimal Probabilistic Cache Stampede Prevention"
        """
        ttl = ttl or self.default_ttl

        # Get value and TTL
        pipe = self.cache.pipeline()
        pipe.get(key)
        pipe.ttl(key)
        cached, remaining_ttl = pipe.execute()

        if cached is not None:
            # XFetch probability calculation
            # Higher probability as we approach expiry
            delta = ttl - remaining_ttl  # Time since cached

            # Probability increases exponentially as TTL decreases
            # P = delta * beta * ln(random()) where delta is age ratio
            if remaining_ttl > 0:
                age_ratio = delta / ttl
                # Refresh if random value falls below threshold
                threshold = age_ratio * beta * -math.log(random.random())
                if threshold < 1:
                    return json.loads(cached)

                # Probabilistic early refresh
                logger.debug(f"XFetch triggered early refresh for {key}")

        # Cache miss or early refresh triggered
        data = loader()
        self.cache.setex(key, ttl, json.dumps(data))
        return data

    # === TECHNIQUE 3: Lease-Based Approach ===
    def get_with_lease(
        self,
        key: str,
        loader: callable,
        ttl: int = None,
        lease_time: int = 10
    ):
        """
        Lease-based cache: returns stale data while one request refreshes.

        1. On miss, grant a "lease" to refresh
        2. Other requests get stale value with "refreshing" flag
        3. Lease holder updates cache
        """
        ttl = ttl or self.default_ttl
        stale_key = f"stale:{key}"
        lease_key = f"lease:{key}"

        # Try fresh cache
        cached = self.cache.get(key)
        if cached:
            return json.loads(cached), False  # fresh data

        # Try to acquire lease for refresh
        lease_acquired = self.cache.set(lease_key, "1", nx=True, ex=lease_time)

        if lease_acquired:
            try:
                # We have the lease - refresh
                data = loader()
                self.cache.setex(key, ttl, json.dumps(data))
                # Keep stale copy for grace period
                self.cache.setex(stale_key, ttl + 60, json.dumps(data))
                return data, False
            finally:
                self.cache.delete(lease_key)
        else:
            # No lease - return stale if available
            stale = self.cache.get(stale_key)
            if stale:
                return json.loads(stale), True  # stale but valid

            # No stale data - must wait
            time.sleep(0.1)
            return self.get_with_lease(key, loader, ttl, lease_time)

    # === TECHNIQUE 4: Background Refresh with Stale-While-Revalidate ===
    def get_with_background_refresh(
        self,
        key: str,
        loader: callable,
        ttl: int = None,
        stale_ttl: int = 60
    ):
        """
        Return stale data immediately while refreshing in background.
        Similar to HTTP stale-while-revalidate.
        """
        ttl = ttl or self.default_ttl
        meta_key = f"meta:{key}"

        # Get value and metadata
        pipe = self.cache.pipeline()
        pipe.get(key)
        pipe.hgetall(meta_key)
        cached, meta = pipe.execute()

        if cached is not None:
            # Check if we should refresh
            created = float(meta.get("created", 0))
            is_stale = (time.time() - created) > ttl
            is_refreshing = meta.get("refreshing") == "1"

            if is_stale and not is_refreshing:
                # Mark as refreshing and start background task
                self.cache.hset(meta_key, "refreshing", "1")
                threading.Thread(
                    target=self._background_refresh,
                    args=(key, loader, ttl, meta_key)
                ).start()

            return json.loads(cached)

        # Complete cache miss
        data = loader()
        pipe = self.cache.pipeline()
        pipe.setex(key, ttl + stale_ttl, json.dumps(data))
        pipe.hset(meta_key, mapping={"created": time.time(), "refreshing": "0"})
        pipe.expire(meta_key, ttl + stale_ttl)
        pipe.execute()
        return data

    def _background_refresh(self, key, loader, ttl, meta_key):
        """Background refresh task"""
        try:
            data = loader()
            pipe = self.cache.pipeline()
            pipe.setex(key, ttl + 60, json.dumps(data))
            pipe.hset(meta_key, mapping={"created": time.time(), "refreshing": "0"})
            pipe.execute()
            logger.debug(f"Background refresh completed for {key}")
        except Exception as e:
            self.cache.hset(meta_key, "refreshing", "0")
            logger.error(f"Background refresh failed: {e}")
''',
            },
            "tools": [
                {
                    "name": "Redis",
                    "url": "https://redis.io/",
                },
                {
                    "name": "Redlock",
                    "url": "https://redis.io/docs/reference/patterns/distributed-locks/",
                    "description": "Distributed locking algorithm",
                },
            ],
        }

    @staticmethod
    def stampede_prevention() -> Dict[str, Any]:
        """Cache stampede prevention techniques - summary"""
        return {
            "locking": """
# Prevent stampede with distributed lock
def get_with_lock(key):
    cached = cache.get(key)
    if cached:
        return cached

    lock_key = f"lock:{key}"
    if cache.set(lock_key, 1, nx=True, ex=10):  # Acquire lock
        try:
            data = fetch_from_db(key)
            cache.setex(key, 3600, data)
            return data
        finally:
            cache.delete(lock_key)
    else:
        time.sleep(0.1)
        return get_with_lock(key)
            """,
            "probabilistic_early_expiration": """
# Refresh before expiration probabilistically
import random

def get_with_early_refresh(key, ttl=3600, beta=1.0):
    data, expiry = cache.get_with_expiry(key)
    if data:
        time_left = expiry - time.time()
        # Random early refresh
        if random.random() < beta * math.log(random.random()) * -time_left / ttl:
            refresh_in_background(key)
        return data
    return refresh_and_cache(key, ttl)
            """,
        }

    # =========================================================================
    # EVICTION POLICIES
    # =========================================================================

    @staticmethod
    def check_eviction_policies() -> Dict[str, Any]:
        """
        Cache Eviction Policies

        When cache is full, which entries should be removed?
        Different policies optimize for different access patterns.
        """
        return {
            "description": "Strategies for removing entries when cache is full",
            "policies": {
                "LRU": {
                    "name": "Least Recently Used",
                    "description": "Evicts entries not accessed for longest time",
                    "best_for": "General purpose, temporal locality",
                    "weakness": "Scan resistance (one full scan evicts hot data)",
                },
                "LFU": {
                    "name": "Least Frequently Used",
                    "description": "Evicts entries with lowest access count",
                    "best_for": "Stable popularity patterns",
                    "weakness": "Slow to adapt to changing patterns",
                },
                "FIFO": {
                    "name": "First In First Out",
                    "description": "Evicts oldest inserted entries",
                    "best_for": "Simple, predictable behavior",
                    "weakness": "Ignores access patterns entirely",
                },
                "ARC": {
                    "name": "Adaptive Replacement Cache",
                    "description": "Dynamically balances recency and frequency",
                    "best_for": "Variable workloads",
                    "weakness": "More complex, higher overhead",
                },
                "W-TinyLFU": {
                    "name": "Window TinyLFU",
                    "description": "Admits to main cache based on frequency estimation",
                    "best_for": "Near-optimal hit rates",
                    "weakness": "Complex implementation",
                },
                "SLRU": {
                    "name": "Segmented LRU",
                    "description": "Separate segments for probation and protected entries",
                    "best_for": "Scan resistance",
                    "weakness": "More memory overhead",
                },
            },
            "examples": {
                "bad": '''
# BAD: Wrong eviction policy for workload

# Using noeviction when cache is bounded
# maxmemory-policy noeviction
# Result: OOM errors when cache fills up

# Using allkeys-random for hot data workload
# maxmemory-policy allkeys-random
# Result: Randomly evicts hot data, poor hit rate

# Using volatile-lru when no keys have TTL
# maxmemory-policy volatile-lru
# Result: No eviction happens, OOM errors
''',
                "good": '''
# GOOD: Choose eviction policy based on workload

# Redis configuration for different workloads

# === General web application ===
# Most items accessed recently should stay
maxmemory 2gb
maxmemory-policy allkeys-lru

# === Session storage ===
# All keys have TTL, evict oldest TTL first
maxmemory 1gb
maxmemory-policy volatile-ttl

# === Recommendation cache ===
# Some items consistently popular (LFU)
maxmemory 4gb
maxmemory-policy allkeys-lfu

# === Mixed workload with TTLs ===
# Prefer evicting keys with TTL
maxmemory 2gb
maxmemory-policy volatile-lru


# Python LRU cache implementation
from functools import lru_cache
from collections import OrderedDict
import threading

class LRUCache:
    """Thread-safe LRU cache implementation"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key):
        with self.lock:
            if key not in self.cache:
                return None
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            self.cache[key] = value
            if len(self.cache) > self.capacity:
                # Remove oldest (least recently used)
                self.cache.popitem(last=False)


# Caffeine-style W-TinyLFU (Java)
// Caffeine cache with W-TinyLFU eviction
Cache<String, Object> cache = Caffeine.newBuilder()
    .maximumSize(10_000)  // Uses W-TinyLFU automatically
    .expireAfterWrite(Duration.ofHours(1))
    .recordStats()  // Enable statistics
    .build();

// Access patterns analyzed for optimal eviction
Object value = cache.get(key, k -> loadFromDatabase(k));
''',
            },
            "sizing_formula": """
# Cache sizing calculations

# Memory per entry estimation:
# entry_size = key_size + value_size + overhead
# overhead ≈ 50-100 bytes per entry (pointers, metadata)

# Example: User profile cache
# - Key: "user:12345" ≈ 12 bytes
# - Value: JSON ≈ 500 bytes
# - Overhead: ≈ 100 bytes
# Total: ≈ 612 bytes per entry

# For 1M users:
# memory = 1,000,000 * 612 bytes ≈ 612 MB

# Hit rate estimation:
# For Zipf distribution (common in web):
# hit_rate ≈ 1 - (cache_size / total_items) ^ (1 - zipf_s)
# where zipf_s ≈ 0.7-0.8 for most web workloads

# Working set estimation:
# 80% of requests often hit 20% of data
# Cache that 20% for 80% hit rate
            """,
            "tools": [
                {
                    "name": "redis-cli INFO memory",
                    "description": "Monitor Redis memory usage",
                },
                {
                    "name": "Caffeine",
                    "url": "https://github.com/ben-manes/caffeine",
                    "description": "High-performance Java caching library with W-TinyLFU",
                },
            ],
        }

    @staticmethod
    def eviction_policies() -> Dict[str, Any]:
        """Cache eviction policies - summary"""
        return {
            "LRU": "Least Recently Used - evicts oldest accessed",
            "LFU": "Least Frequently Used - evicts least accessed",
            "FIFO": "First In First Out - evicts oldest inserted",
            "ARC": "Adaptive Replacement Cache - balances LRU/LFU",
            "redis_config": """
# Redis maxmemory policies
maxmemory 2gb
maxmemory-policy allkeys-lru  # LRU on all keys
# Options: volatile-lru, allkeys-lru, volatile-lfu, allkeys-lfu,
#          volatile-random, allkeys-random, volatile-ttl, noeviction
            """,
        }

    # =========================================================================
    # MULTI-LEVEL CACHING
    # =========================================================================

    @staticmethod
    def check_multi_level_caching() -> Dict[str, Any]:
        """
        Multi-Level Cache Architecture

        Layered caching with different characteristics at each level.
        Balances speed, capacity, and consistency.
        """
        return {
            "description": "Hierarchical caching with multiple layers",
            "levels": {
                "L1": {
                    "type": "In-process memory (local)",
                    "latency": "< 1 microsecond",
                    "size": "100MB - 1GB",
                    "consistency": "Per-instance only",
                    "examples": ["HashMap", "Caffeine", "functools.lru_cache"],
                },
                "L2": {
                    "type": "Distributed cache (shared)",
                    "latency": "< 1 millisecond",
                    "size": "1GB - 100GB",
                    "consistency": "Across all instances",
                    "examples": ["Redis", "Memcached", "Hazelcast"],
                },
                "L3": {
                    "type": "CDN edge cache",
                    "latency": "< 50 milliseconds",
                    "size": "Unlimited (distributed)",
                    "consistency": "Eventually consistent",
                    "examples": ["CloudFront", "Fastly", "Cloudflare"],
                },
            },
            "examples": {
                "bad": '''
# BAD: Only distributed cache - high latency for hot data
def get_user(user_id: str) -> dict:
    # Every request goes to Redis (network hop)
    cached = redis.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    user = db.query(user_id)
    redis.setex(f"user:{user_id}", 3600, json.dumps(user))
    return user

# Problems:
# 1. Network round-trip for every request (~1ms)
# 2. Redis becomes bottleneck for hot keys
# 3. Wasted bandwidth for unchanging data
''',
                "good": '''
# GOOD: Multi-level cache hierarchy
import time
import json
from threading import Lock
from typing import Optional, Tuple, Any
from functools import lru_cache
from cachetools import TTLCache

class MultiLevelCache:
    """
    Three-level cache hierarchy:
    - L1: Local memory (per-instance, fastest)
    - L2: Distributed (Redis, shared across instances)
    - L3: Origin (database, slowest)
    """

    def __init__(
        self,
        redis_client,
        l1_max_size: int = 10000,
        l1_ttl: int = 60,
        l2_ttl: int = 3600
    ):
        self.l1 = TTLCache(maxsize=l1_max_size, ttl=l1_ttl)
        self.l1_lock = Lock()
        self.l2 = redis_client
        self.l1_ttl = l1_ttl
        self.l2_ttl = l2_ttl

        # Metrics
        self.l1_hits = 0
        self.l2_hits = 0
        self.misses = 0

    def get(self, key: str, loader: callable = None) -> Optional[Any]:
        """
        Get value from cache hierarchy.

        Checks L1 -> L2 -> loader (L3) in order.
        Populates upper levels on miss.
        """
        # L1: Local memory (fastest)
        with self.l1_lock:
            if key in self.l1:
                self.l1_hits += 1
                return self.l1[key]

        # L2: Distributed cache
        try:
            cached = self.l2.get(key)
            if cached is not None:
                self.l2_hits += 1
                value = json.loads(cached)
                # Populate L1
                with self.l1_lock:
                    self.l1[key] = value
                return value
        except Exception as e:
            # L2 failure should not break the app
            pass

        # L3: Origin (database/API)
        if loader is None:
            self.misses += 1
            return None

        self.misses += 1
        value = loader()

        # Populate caches
        self.set(key, value)
        return value

    def set(self, key: str, value: Any):
        """Set value in all cache levels"""
        # L1
        with self.l1_lock:
            self.l1[key] = value

        # L2
        try:
            self.l2.setex(key, self.l2_ttl, json.dumps(value))
        except Exception:
            pass

    def invalidate(self, key: str):
        """Invalidate key at all levels"""
        # L1
        with self.l1_lock:
            self.l1.pop(key, None)

        # L2
        try:
            self.l2.delete(key)
        except Exception:
            pass

    def invalidate_pattern(self, pattern: str):
        """Invalidate keys matching pattern (L2 only, L1 by TTL)"""
        try:
            keys = self.l2.keys(pattern)
            if keys:
                self.l2.delete(*keys)
        except Exception:
            pass

    def get_stats(self) -> dict:
        """Get cache statistics"""
        total = self.l1_hits + self.l2_hits + self.misses
        return {
            "l1_hit_rate": self.l1_hits / total if total > 0 else 0,
            "l2_hit_rate": self.l2_hits / total if total > 0 else 0,
            "miss_rate": self.misses / total if total > 0 else 0,
            "l1_size": len(self.l1),
        }


# Usage
cache = MultiLevelCache(redis_client, l1_max_size=5000, l1_ttl=30, l2_ttl=3600)

def get_user(user_id: str) -> dict:
    return cache.get(
        key=f"user:{user_id}",
        loader=lambda: db.query("SELECT * FROM users WHERE id = ?", user_id)
    )

def update_user(user_id: str, data: dict):
    db.execute("UPDATE users SET ... WHERE id = ?", user_id, data)
    cache.invalidate(f"user:{user_id}")


# With HTTP CDN layer (L3)
from fastapi import FastAPI, Response

app = FastAPI()

@app.get("/api/users/{user_id}")
def get_user_api(user_id: str, response: Response):
    user = get_user(user_id)

    # CDN caching headers
    response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=30"
    response.headers["ETag"] = f'"{hash(json.dumps(user))}"'
    response.headers["Vary"] = "Accept"

    return user
''',
            },
            "consistency_patterns": '''
# Cache consistency across levels

class ConsistentMultiLevelCache(MultiLevelCache):
    """Multi-level cache with invalidation notifications"""

    def __init__(self, redis_client, pubsub_channel: str = "cache_invalidate"):
        super().__init__(redis_client)
        self.pubsub_channel = pubsub_channel
        self._setup_subscriber()

    def _setup_subscriber(self):
        """Listen for invalidation messages from other instances"""
        def listener():
            pubsub = self.l2.pubsub()
            pubsub.subscribe(self.pubsub_channel)
            for message in pubsub.listen():
                if message["type"] == "message":
                    key = message["data"].decode()
                    # Invalidate local cache
                    with self.l1_lock:
                        self.l1.pop(key, None)

        import threading
        threading.Thread(target=listener, daemon=True).start()

    def invalidate(self, key: str, broadcast: bool = True):
        """Invalidate with cross-instance notification"""
        super().invalidate(key)

        if broadcast:
            # Notify other instances
            self.l2.publish(self.pubsub_channel, key)
''',
            "tools": [
                {
                    "name": "cachetools",
                    "url": "https://cachetools.readthedocs.io/",
                    "install": "pip install cachetools",
                },
                {
                    "name": "Redis",
                    "url": "https://redis.io/",
                    "install": "pip install redis",
                },
            ],
        }

    @staticmethod
    def multi_level_caching() -> Dict[str, Any]:
        """Multi-level cache hierarchy - summary"""
        return {
            "levels": {
                "L1": "In-memory (application) - fastest, smallest",
                "L2": "Distributed (Redis) - fast, shared across instances",
                "L3": "CDN - slowest, global edge caching",
            },
            "implementation": """
class MultiLevelCache:
    def __init__(self):
        self.l1 = {}  # Local memory
        self.l2 = redis.Redis()  # Redis
        self.l1_ttl = 60  # 1 minute local
        self.l2_ttl = 3600  # 1 hour Redis

    def get(self, key):
        # Try L1
        if key in self.l1:
            return self.l1[key]

        # Try L2
        data = self.l2.get(key)
        if data:
            self.l1[key] = data  # Populate L1
            return data

        # Miss - fetch from source
        data = fetch_from_source(key)
        self.set(key, data)
        return data

    def set(self, key, value):
        self.l1[key] = value
        self.l2.setex(key, self.l2_ttl, value)
            """,
        }

    # =========================================================================
    # HTTP CACHING
    # =========================================================================

    @staticmethod
    def check_http_caching() -> Dict[str, Any]:
        """HTTP Caching Headers and CDN Configuration"""
        return {
            "description": "HTTP caching with Cache-Control, ETag, and CDN",
            "headers": {
                "Cache-Control": "Directives for caching behavior",
                "ETag": "Version identifier for conditional requests",
                "Last-Modified": "Timestamp of last change",
                "Vary": "Headers that affect cached response",
            },
            "examples": {
                "bad": '''
# BAD: No caching headers - every request goes to origin
@app.get("/api/products/{id}")
def get_product(id: str):
    return db.get_product(id)  # No Cache-Control!

# BAD: Wrong caching for dynamic content
@app.get("/api/users/me")
def get_current_user(response: Response):
    user = get_authenticated_user()
    # This caches user data for everyone!
    response.headers["Cache-Control"] = "public, max-age=3600"
    return user

# BAD: Missing Vary header
@app.get("/api/articles")
def get_articles(response: Response, accept_language: str = "en"):
    articles = get_articles_by_language(accept_language)
    response.headers["Cache-Control"] = "public, max-age=600"
    # Missing: Vary: Accept-Language
    # Wrong language may be served from cache!
    return articles
''',
                "good": '''
# GOOD: Proper HTTP caching

from fastapi import FastAPI, Response, Request, Header
from typing import Optional
import hashlib

app = FastAPI()

# Static assets - long cache with immutable
@app.get("/static/{path:path}")
def serve_static(path: str, response: Response):
    content = read_static_file(path)

    # Cache forever (use versioned URLs)
    response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    response.headers["ETag"] = hashlib.md5(content).hexdigest()

    return content


# API with conditional requests
@app.get("/api/products/{product_id}")
def get_product(
    product_id: str,
    response: Response,
    if_none_match: Optional[str] = Header(None)
):
    product = db.get_product(product_id)
    etag = f'"{product["version"]}"'

    # Check if client has current version
    if if_none_match == etag:
        response.status_code = 304  # Not Modified
        return None

    response.headers["ETag"] = etag
    response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=30"

    return product


# Private user data - no caching or private only
@app.get("/api/users/me")
def get_current_user(response: Response):
    user = get_authenticated_user()

    # Never cache in shared caches (CDN, proxy)
    response.headers["Cache-Control"] = "private, no-store"

    return user


# Varying by header
@app.get("/api/articles")
def get_articles(
    response: Response,
    accept_language: str = Header(default="en")
):
    articles = get_articles_by_language(accept_language)

    response.headers["Cache-Control"] = "public, max-age=600"
    response.headers["Vary"] = "Accept-Language, Accept"

    return articles


# Cache-Control directives reference:
CACHE_CONTROL_DIRECTIVES = {
    # Response directives
    "public": "Can be cached by any cache",
    "private": "Only browser cache, not CDN/proxy",
    "no-cache": "Must revalidate before using",
    "no-store": "Never cache",
    "max-age=N": "Fresh for N seconds",
    "s-maxage=N": "Fresh for N seconds in shared caches",
    "must-revalidate": "Must revalidate after stale",
    "proxy-revalidate": "Shared caches must revalidate",
    "immutable": "Will never change",
    "stale-while-revalidate=N": "Serve stale while refreshing for N seconds",
    "stale-if-error=N": "Serve stale if origin errors for N seconds",
}
''',
            },
            "cdn_config": '''
# CloudFront cache behavior configuration
cloudfront:
  distribution:
    origins:
      - id: api-origin
        domain_name: api.example.com
        custom_origin_config:
          http_port: 80
          https_port: 443
          origin_protocol_policy: https-only

    cache_behaviors:
      # Static assets - long cache
      - path_pattern: "/static/*"
        target_origin_id: api-origin
        viewer_protocol_policy: redirect-to-https
        cache_policy_id: "Managed-CachingOptimized"
        ttl:
          default: 86400
          max: 31536000

      # API - respect origin headers
      - path_pattern: "/api/*"
        target_origin_id: api-origin
        viewer_protocol_policy: redirect-to-https
        cache_policy_id: "Managed-CachingDisabled"  # Use origin Cache-Control
        origin_request_policy_id: "Managed-AllViewer"

    # Custom error responses
    custom_error_responses:
      - error_code: 503
        response_code: 503
        response_page_path: "/error/503.html"
        error_caching_min_ttl: 10  # Cache error briefly
''',
            "tools": [
                {
                    "name": "Chrome DevTools",
                    "description": "Inspect cache headers in Network tab",
                },
                {
                    "name": "curl",
                    "description": "curl -I https://example.com to see headers",
                },
                {
                    "name": "redbot",
                    "url": "https://redbot.org/",
                    "description": "HTTP cache header validator",
                },
            ],
        }

    # =========================================================================
    # CACHE INVALIDATION
    # =========================================================================

    @staticmethod
    def check_cache_invalidation() -> Dict[str, Any]:
        """Cache Invalidation Strategies"""
        return {
            "description": "Strategies for keeping cache consistent with source",
            "strategies": {
                "TTL": "Automatic expiration after time period",
                "explicit": "Manually delete when data changes",
                "tag_based": "Group related keys for batch invalidation",
                "event_driven": "Invalidate on data change events",
                "versioned_keys": "Include version in cache key",
            },
            "examples": {
                "bad": '''
# BAD: Only TTL - stale data for full TTL duration
def get_product(product_id: str) -> dict:
    cached = cache.get(f"product:{product_id}")
    if cached:
        return cached  # Could be stale!
    product = db.get_product(product_id)
    cache.setex(f"product:{product_id}", 3600, product)  # Stale for up to 1 hour
    return product

def update_product(product_id: str, data: dict):
    db.update_product(product_id, data)
    # Forgot to invalidate cache!
    # Users see stale data for up to 1 hour
''',
                "good": '''
# GOOD: Multiple invalidation strategies

import json
from typing import List, Set
from datetime import datetime

class CacheWithInvalidation:
    """Cache with tag-based invalidation"""

    def __init__(self, redis_client):
        self.cache = redis_client

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value: any, ttl: int = 3600, tags: List[str] = None):
        """Set with optional tags for group invalidation"""
        pipe = self.cache.pipeline()

        # Store value
        pipe.setex(key, ttl, json.dumps(value))

        # Track key in tag sets
        if tags:
            for tag in tags:
                pipe.sadd(f"tag:{tag}", key)
                pipe.expire(f"tag:{tag}", ttl + 60)

        pipe.execute()

    def invalidate(self, key: str):
        """Invalidate single key"""
        self.cache.delete(key)

    def invalidate_by_tag(self, tag: str):
        """Invalidate all keys with tag"""
        tag_key = f"tag:{tag}"
        keys = self.cache.smembers(tag_key)
        if keys:
            pipe = self.cache.pipeline()
            for key in keys:
                pipe.delete(key)
            pipe.delete(tag_key)
            pipe.execute()

    def invalidate_pattern(self, pattern: str):
        """Invalidate keys matching pattern (use sparingly)"""
        keys = self.cache.keys(pattern)
        if keys:
            self.cache.delete(*keys)


# Usage with tags
cache = CacheWithInvalidation(redis_client)

def get_product(product_id: str) -> dict:
    key = f"product:{product_id}"
    cached = cache.get(key)
    if cached:
        return json.loads(cached)

    product = db.get_product(product_id)
    cache.set(
        key=key,
        value=product,
        ttl=3600,
        tags=[
            f"category:{product['category_id']}",
            f"brand:{product['brand_id']}",
            "products"
        ]
    )
    return product

def update_product(product_id: str, data: dict):
    db.update_product(product_id, data)
    # Invalidate specific product
    cache.invalidate(f"product:{product_id}")

def update_category(category_id: str, data: dict):
    db.update_category(category_id, data)
    # Invalidate all products in category
    cache.invalidate_by_tag(f"category:{category_id}")


# Event-driven invalidation with pub/sub
class EventDrivenCache:
    """Cache invalidation via event bus"""

    def __init__(self, cache_client, event_bus):
        self.cache = cache_client
        self.event_bus = event_bus

        # Subscribe to data change events
        event_bus.subscribe("product.updated", self._on_product_updated)
        event_bus.subscribe("product.deleted", self._on_product_deleted)
        event_bus.subscribe("category.updated", self._on_category_updated)

    def _on_product_updated(self, event):
        self.cache.delete(f"product:{event.product_id}")

    def _on_product_deleted(self, event):
        self.cache.delete(f"product:{event.product_id}")

    def _on_category_updated(self, event):
        # Invalidate category and all products
        self.cache.delete(f"category:{event.category_id}")
        pattern = f"product:*:category:{event.category_id}"
        self.cache.invalidate_pattern(pattern)


# Versioned keys (for CDN-friendly invalidation)
class VersionedCache:
    """Use version in key to "invalidate" without deletion"""

    def __init__(self, cache_client):
        self.cache = cache_client

    def get_version(self, entity_type: str, entity_id: str) -> int:
        version = self.cache.get(f"version:{entity_type}:{entity_id}")
        return int(version) if version else 1

    def increment_version(self, entity_type: str, entity_id: str) -> int:
        return self.cache.incr(f"version:{entity_type}:{entity_id}")

    def get(self, entity_type: str, entity_id: str) -> any:
        version = self.get_version(entity_type, entity_id)
        key = f"{entity_type}:{entity_id}:v{version}"
        return self.cache.get(key)

    def set(self, entity_type: str, entity_id: str, value: any, ttl: int = 3600):
        version = self.get_version(entity_type, entity_id)
        key = f"{entity_type}:{entity_id}:v{version}"
        self.cache.setex(key, ttl, json.dumps(value))

    def invalidate(self, entity_type: str, entity_id: str):
        # Increment version - old cached value becomes orphan
        self.increment_version(entity_type, entity_id)
        # Old version will expire naturally via TTL
''',
            },
            "tools": [
                {
                    "name": "Redis SCAN",
                    "description": "For pattern-based invalidation without blocking",
                },
            ],
        }

    # =========================================================================
    # CACHE SIZING
    # =========================================================================

    @staticmethod
    def check_cache_sizing() -> Dict[str, Any]:
        """Cache Sizing Calculations"""
        return {
            "description": "How to calculate optimal cache size",
            "formulas": {
                "memory_per_entry": "key_size + value_size + overhead (~50-100 bytes)",
                "hit_rate_estimate": "Based on Zipf distribution of access patterns",
                "working_set": "Data accessed in typical time window",
            },
            "examples": {
                "bad": '''
# BAD: No capacity planning
redis_client = Redis()  # No maxmemory set
# Eventually: OOM killer terminates Redis

# BAD: Too small cache
# maxmemory 100mb
# Cache constantly evicting, poor hit rate
''',
                "good": '''
# GOOD: Data-driven cache sizing

def estimate_cache_size(
    entry_count: int,
    avg_key_size: int,
    avg_value_size: int,
    overhead_per_entry: int = 80
) -> int:
    """
    Estimate memory needed for cache.

    Args:
        entry_count: Number of entries to cache
        avg_key_size: Average key size in bytes
        avg_value_size: Average value size in bytes
        overhead_per_entry: Redis/system overhead per entry

    Returns:
        Estimated memory in bytes
    """
    entry_size = avg_key_size + avg_value_size + overhead_per_entry
    return entry_count * entry_size


def estimate_hit_rate(cache_size_ratio: float, zipf_s: float = 0.8) -> float:
    """
    Estimate hit rate based on cache size and access distribution.

    For Zipf distribution (common in web workloads):
    - zipf_s ~0.7-0.8 for most web traffic
    - Higher s = more skewed (fewer items get most access)

    Args:
        cache_size_ratio: cache_entries / total_entries
        zipf_s: Zipf distribution parameter

    Returns:
        Estimated hit rate
    """
    if cache_size_ratio >= 1:
        return 1.0
    return 1 - (1 - cache_size_ratio) ** (1 - zipf_s)


# Example calculation
print("=== Cache Sizing Example ===")

# Product catalog: 1M products
total_products = 1_000_000
avg_key = 20  # "product:12345678"
avg_value = 500  # JSON product data

# Working set: 20% gets 80% of traffic
working_set = int(total_products * 0.2)
cache_entries = working_set  # 200K entries

# Calculate memory
memory_bytes = estimate_cache_size(
    entry_count=cache_entries,
    avg_key_size=avg_key,
    avg_value_size=avg_value
)
memory_gb = memory_bytes / (1024**3)

print(f"Entries to cache: {cache_entries:,}")
print(f"Estimated memory: {memory_gb:.2f} GB")

# Estimate hit rate
hit_rate = estimate_hit_rate(cache_entries / total_products)
print(f"Expected hit rate: {hit_rate:.1%}")

# Redis config
print(f"""
# Redis configuration
maxmemory {int(memory_gb * 1.2)}gb  # 20% buffer
maxmemory-policy allkeys-lru
""")

# Output:
# Entries to cache: 200,000
# Estimated memory: 0.11 GB
# Expected hit rate: 80.0%
''',
            },
            "monitoring": '''
# Monitor cache effectiveness

def analyze_cache_performance(redis_client):
    """Analyze Redis cache performance"""
    info = redis_client.info()

    metrics = {
        "memory_used": info["used_memory_human"],
        "memory_peak": info["used_memory_peak_human"],
        "hit_rate": info["keyspace_hits"] / (info["keyspace_hits"] + info["keyspace_misses"]),
        "evicted_keys": info["evicted_keys"],
        "connected_clients": info["connected_clients"],
        "ops_per_sec": info["instantaneous_ops_per_sec"],
    }

    # Analysis
    if metrics["hit_rate"] < 0.9:
        print("WARNING: Hit rate below 90% - consider increasing cache size")

    if metrics["evicted_keys"] > 0:
        print(f"WARNING: {metrics['evicted_keys']} keys evicted - cache may be too small")

    return metrics
''',
            "tools": [
                {
                    "name": "redis-cli INFO",
                    "description": "Built-in Redis statistics",
                },
                {
                    "name": "Redis Memory Analyzer",
                    "url": "https://github.com/sripathikrishnan/redis-rdb-tools",
                    "install": "pip install rdbtools",
                },
            ],
        }

    def generate_finding(
        self,
        finding_id: str,
        title: str,
        severity: str,
        category: str,
        current: str,
        improved: str,
        explanation: str,
        **kwargs
    ) -> CachingFinding:
        """Generate a structured caching finding"""
        return CachingFinding(
            finding_id=finding_id,
            title=title,
            severity=severity,
            category=category,
            location=kwargs.get("location", {}),
            description=kwargs.get("description", ""),
            pattern_violated=kwargs.get("pattern_violated", ""),
            current_implementation=current,
            improved_implementation=improved,
            explanation=explanation,
            cache_metrics=kwargs.get("cache_metrics", {}),
            performance_impact=kwargs.get("performance_impact", ""),
            tools=kwargs.get("tools", []),
            references=kwargs.get("references", []),
            remediation={"effort": "MEDIUM", "priority": severity},
        )


def create_enhanced_caching_assistant() -> Dict[str, Any]:
    """Factory function to create the Enhanced Caching Assistant"""
    return {
        "name": "Enhanced Caching Strategy Advisor",
        "version": "2.0.0",
        "system_prompt": """You are an expert caching architect with deep knowledge of cache design,
optimization, and operations. Your expertise spans in-memory caches, distributed caches, and CDN caching.

Your responsibilities include:

1. **Cache Pattern Selection**: Guide selection of appropriate caching patterns (cache-aside,
   write-through, write-behind, refresh-ahead) based on workload characteristics. Consider
   read/write ratios, consistency requirements, and failure modes.

2. **Eviction Policy Design**: Recommend eviction policies (LRU, LFU, ARC, W-TinyLFU) based on
   access patterns. Analyze hit rate trade-offs and memory efficiency.

3. **Stampede Prevention**: Implement cache stampede prevention using distributed locks,
   probabilistic early expiration (XFetch), lease-based approaches, and background refresh.

4. **Multi-Level Architecture**: Design multi-level cache hierarchies (L1/L2/L3) with appropriate
   consistency guarantees. Balance latency, capacity, and consistency across levels.

5. **HTTP Caching**: Configure Cache-Control headers, ETags, and CDN cache behaviors for optimal
   performance. Implement conditional requests and stale-while-revalidate patterns.

6. **Cache Invalidation**: Design invalidation strategies including TTL-based, explicit, tag-based,
   and event-driven approaches. Handle cross-instance invalidation in distributed systems.

7. **Sizing and Capacity**: Calculate optimal cache sizes based on working set, access patterns,
   and hit rate targets. Plan for memory overhead and eviction thresholds.

8. **Monitoring and Tuning**: Establish cache metrics (hit rate, latency, eviction rate) and
   tune configuration based on observed patterns.

Always provide specific code examples showing both anti-patterns and recommended implementations.
Consider operational complexity, consistency trade-offs, and failure scenarios in recommendations.""",
        "assistant_class": EnhancedCachingAssistant,
        "domain": "architecture",
        "tags": [
            "caching",
            "redis",
            "memcached",
            "cdn",
            "performance",
            "scalability",
            "eviction",
            "stampede",
            "http-caching",
        ],
    }


if __name__ == "__main__":
    assistant = EnhancedCachingAssistant()
    print(f"Assistant: {assistant.name}")
    print(f"Version: {assistant.version}")
    print(f"Standards: {', '.join(assistant.standards)}")
    print()

    # Test cache patterns
    patterns = assistant.cache_patterns()
    print(f"Cache Patterns: {list(patterns.keys())}")

    # Test stampede prevention
    stampede = assistant.stampede_prevention()
    print(f"Stampede Techniques: {list(stampede.keys())}")

    # Test eviction policies
    eviction = assistant.eviction_policies()
    print(f"Eviction Policies: {[k for k in eviction.keys() if k != 'redis_config']}")

    # Test multi-level
    multi_level = assistant.multi_level_caching()
    print(f"Cache Levels: {list(multi_level['levels'].keys())}")

    # Test check methods
    cache_aside = assistant.check_cache_aside_pattern()
    print(f"\nCache-Aside When to Use: {cache_aside['when_to_use'][:2]}...")

    sizing = assistant.check_cache_sizing()
    print(f"Sizing Formulas: {list(sizing['formulas'].keys())}")

    # Generate sample finding
    finding = assistant.generate_finding(
        finding_id="CACHE-001",
        title="Missing cache stampede protection",
        severity="HIGH",
        category="stampede",
        current="Direct cache.get() without locking",
        improved="Use distributed lock or XFetch algorithm",
        explanation="Popular key expiration causes thundering herd to database",
        pattern_violated="Cache Stampede Prevention",
        cache_metrics={"hit_rate": 0.85, "eviction_rate": "high"},
    )

    print(f"\nSample Finding: {finding.finding_id} - {finding.title}")
    print(f"Severity: {finding.severity}")
    print(f"Pattern Violated: {finding.pattern_violated}")
