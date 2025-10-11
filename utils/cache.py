import time
import json
import hashlib
from typing import Any, Optional, Dict, Callable
import streamlit as st
from datetime import datetime, timedelta

class CacheManager:
    """Advanced caching system for API responses and processed data"""
    
    def __init__(self):
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a unique cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else None
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if a cache entry has expired"""
        if 'expires_at' not in cache_entry:
            return False
        return time.time() > cache_entry['expires_at']
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if not self._is_expired(entry):
                self.cache_stats['hits'] += 1
                entry['last_accessed'] = time.time()
                return entry['data']
            else:
                # Remove expired entry
                del self.memory_cache[key]
                self.cache_stats['evictions'] += 1
        
        self.cache_stats['misses'] += 1
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set a value in cache with TTL (time to live) in seconds"""
        expires_at = time.time() + ttl if ttl > 0 else None
        
        self.memory_cache[key] = {
            'data': value,
            'created_at': time.time(),
            'last_accessed': time.time(),
            'expires_at': expires_at,
            'ttl': ttl
        }
    
    def delete(self, key: str) -> bool:
        """Delete a specific cache entry"""
        if key in self.memory_cache:
            del self.memory_cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        self.memory_cache.clear()
        self.cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def cleanup_expired(self) -> int:
        """Remove all expired entries and return count removed"""
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self.memory_cache.items():
            if self._is_expired(entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            self.cache_stats['evictions'] += 1
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'entries': len(self.memory_cache),
            'hits': self.cache_stats['hits'],
            'misses': self.cache_stats['misses'],
            'evictions': self.cache_stats['evictions'],
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed information about cached entries"""
        current_time = time.time()
        entries_info = []
        
        for key, entry in self.memory_cache.items():
            info = {
                'key': key[:16] + '...' if len(key) > 16 else key,
                'created_ago': round(current_time - entry['created_at'], 2),
                'last_accessed_ago': round(current_time - entry['last_accessed'], 2),
                'expires_in': round(entry['expires_at'] - current_time, 2) if entry['expires_at'] else 'Never',
                'ttl': entry['ttl'],
                'is_expired': self._is_expired(entry)
            }
            entries_info.append(info)
        
        return {
            'stats': self.get_stats(),
            'entries': entries_info
        }
    
    def cached_function(self, ttl: int = 3600, key_prefix: str = ''):
        """Decorator for caching function results"""
        def decorator(func: Callable):
            def wrapper(*args, **kwargs):
                # Generate cache key
                func_key = f"{key_prefix}{func.__name__}"
                cache_key = self._generate_cache_key(func_key, *args, **kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator

# Global cache manager instance
global_cache = CacheManager()

# Streamlit-specific caching utilities
class StreamlitCache:
    """Streamlit-specific caching utilities"""
    
    @staticmethod
    def cache_profile_data(ttl: int = 1800):  # 30 minutes
        """Decorator for caching profile data"""
        return st.cache_data(ttl=ttl, show_spinner=False)
    
    @staticmethod
    def cache_api_response(ttl: int = 3600):  # 1 hour
        """Decorator for caching API responses"""
        return st.cache_data(ttl=ttl, show_spinner=False)
    
    @staticmethod
    def cache_static_data(ttl: int = 86400):  # 24 hours
        """Decorator for caching static data like items, collections"""
        return st.cache_data(ttl=ttl, show_spinner=False)
    
    @staticmethod
    def cache_resource(ttl: int = 3600):
        """Decorator for caching expensive resources"""
        return st.cache_resource(ttl=ttl, show_spinner=False)

# Convenience functions
def get_cached_data(key: str) -> Optional[Any]:
    """Get data from global cache"""
    return global_cache.get(key)

def set_cached_data(key: str, value: Any, ttl: int = 3600) -> None:
    """Set data in global cache"""
    global_cache.set(key, value, ttl)

def clear_cache() -> None:
    """Clear global cache"""
    global_cache.clear()

def get_cache_stats() -> Dict[str, Any]:
    """Get global cache statistics"""
    return global_cache.get_stats()