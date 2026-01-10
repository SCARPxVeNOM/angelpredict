"""
API Cache implementation with LRU eviction and TTL support.

This module provides caching functionality to reduce redundant API calls
and improve system performance.
"""

import time
import hashlib
import json
from collections import OrderedDict
from typing import Optional, Dict, Any
from dataclasses import dataclass
import threading
import logging

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: dict
    timestamp: float
    ttl: int
    access_count: int
    last_accessed: float


class APICache:
    """
    LRU cache with TTL for API responses.
    
    Implements Least Recently Used (LRU) eviction policy with time-to-live (TTL)
    for cache entries. Thread-safe for concurrent access.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 60):
        """
        Initialize LRU cache with TTL.
        
        Args:
            max_size: Maximum cache entries
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
            
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        logger.info(f"APICache initialized: max_size={max_size}, ttl={ttl_seconds}s")
    
    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if a cache entry has expired."""
        age = time.time() - entry.timestamp
        return age >= self.ttl_seconds
    
    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if self._cache:
            key, entry = self._cache.popitem(last=False)
            self._evictions += 1
            logger.debug(f"Evicted LRU entry: {key}")
    
    def get(self, key: str) -> Optional[dict]:
        """
        Get cached value if exists and not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found or expired
        """
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                logger.debug(f"Cache miss: {key}")
                return None
            
            # Check if expired
            if self._is_expired(entry):
                del self._cache[key]
                self._misses += 1
                logger.debug(f"Cache expired: {key}")
                return None
            
            # Update access metadata
            entry.access_count += 1
            entry.last_accessed = time.time()
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            
            self._hits += 1
            logger.debug(f"Cache hit: {key} (age={time.time() - entry.timestamp:.1f}s)")
            return entry.value
    
    def set(self, key: str, value: dict) -> None:
        """
        Store value in cache.
        
        Args:
            key: Cache key
            value: Data to cache
        """
        with self._lock:
            # If key exists, remove it first (will be re-added at end)
            if key in self._cache:
                del self._cache[key]
            
            # Evict LRU if at capacity
            while len(self._cache) >= self.max_size:
                self._evict_lru()
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                ttl=self.ttl_seconds,
                access_count=0,
                last_accessed=time.time()
            )
            
            self._cache[key] = entry
            logger.debug(f"Cache set: {key} (size={len(self._cache)}/{self.max_size})")
    
    def invalidate(self, key: str) -> None:
        """
        Remove entry from cache.
        
        Args:
            key: Cache key to invalidate
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Cache invalidated: {key}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"Cache cleared: {count} entries removed")
    
    def get_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 2),
                'evictions': self._evictions,
                'ttl_seconds': self.ttl_seconds
            }
    
    @staticmethod
    def generate_key(endpoint: str, **params) -> str:
        """
        Generate cache key from endpoint and parameters.
        
        Args:
            endpoint: API endpoint name
            **params: Request parameters
            
        Returns:
            Cache key string
        """
        # Sort params for consistent key generation
        sorted_params = sorted(params.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
        
        return f"{endpoint}:{params_hash}"
