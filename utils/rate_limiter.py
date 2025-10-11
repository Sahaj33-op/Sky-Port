import time
from typing import Dict, Optional

class RateLimiter:
    """Token bucket rate limiter for API requests"""
    
    def __init__(self, max_requests: int = 100, time_window: int = 300):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.request_times = []
        self.request_count = 0
        self.window_start = time.time()
    
    def can_make_request(self) -> bool:
        """Check if a request can be made within rate limits"""
        self._cleanup_old_requests()
        return len(self.request_times) < self.max_requests
    
    def record_request(self) -> None:
        """Record a new request timestamp"""
        current_time = time.time()
        self.request_times.append(current_time)
        self.request_count += 1
        self._cleanup_old_requests()
    
    def _cleanup_old_requests(self) -> None:
        """Remove request timestamps outside the time window"""
        current_time = time.time()
        cutoff_time = current_time - self.time_window
        
        # Remove old requests
        self.request_times = [t for t in self.request_times if t > cutoff_time]
        
        # Reset window if needed
        if current_time - self.window_start > self.time_window:
            self.window_start = current_time
            self.request_count = len(self.request_times)
    
    def get_time_until_reset(self) -> float:
        """Get seconds until rate limit resets"""
        if not self.request_times:
            return 0
        
        oldest_request = min(self.request_times)
        reset_time = oldest_request + self.time_window
        return max(0, reset_time - time.time())
    
    def get_remaining_requests(self) -> int:
        """Get number of remaining requests in current window"""
        self._cleanup_old_requests()
        return max(0, self.max_requests - len(self.request_times))
    
    def get_status(self) -> Dict[str, any]:
        """Get current rate limit status"""
        self._cleanup_old_requests()
        return {
            'requests_made': len(self.request_times),
            'requests_remaining': self.get_remaining_requests(),
            'time_until_reset': self.get_time_until_reset(),
            'can_make_request': self.can_make_request(),
            'window_start': self.window_start,
            'current_time': time.time()
        }
    
    def wait_if_needed(self) -> Optional[float]:
        """Wait if necessary to respect rate limits, return wait time"""
        if self.can_make_request():
            return None
        
        wait_time = self.get_time_until_reset()
        if wait_time > 0:
            time.sleep(wait_time)
            return wait_time
        
        return None

class GlobalRateLimiter:
    """Global rate limiter for managing multiple API endpoints"""
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
    
    def get_limiter(self, name: str, max_requests: int = 100, time_window: int = 300) -> RateLimiter:
        """Get or create a rate limiter for a specific endpoint"""
        if name not in self.limiters:
            self.limiters[name] = RateLimiter(max_requests, time_window)
        return self.limiters[name]
    
    def can_make_request(self, name: str) -> bool:
        """Check if a request can be made to a specific endpoint"""
        if name not in self.limiters:
            return True
        return self.limiters[name].can_make_request()
    
    def record_request(self, name: str) -> None:
        """Record a request to a specific endpoint"""
        if name in self.limiters:
            self.limiters[name].record_request()
    
    def get_all_status(self) -> Dict[str, Dict[str, any]]:
        """Get status for all rate limiters"""
        return {name: limiter.get_status() for name, limiter in self.limiters.items()}

# Global instance for use across the application
global_rate_limiter = GlobalRateLimiter()