import requests
import time
from typing import Optional, Dict, Any, List
from utils.rate_limiter import RateLimiter

# Custom Exceptions for this module
class HypixelAPIError(Exception):
    """Base exception for Hypixel API client errors."""
    pass

class RateLimitError(HypixelAPIError):
    """Raised when the rate limit is exceeded."""
    pass

class InvalidAPIKeyError(HypixelAPIError):
    """Raised when the API key is invalid."""
    pass

class HypixelAPI:
    """Hypixel API client with error handling"""
    
    BASE_URL = "https://api.hypixel.net"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(max_requests=100, time_window=300)  # 100 req/5min
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Sky-Port/1.0.0 (Hypixel SkyBlock Profile Exporter)'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a rate-limited request to the Hypixel API"""
        if not self.rate_limiter.can_make_request():
            raise RateLimitError("Rate limit reached. Please wait before making another request.")
        
        if params is None:
            params = {}
        
        params['key'] = self.api_key
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                timeout=30
            )
            
            self.rate_limiter.record_request()
            
            if response.status_code == 403:
                raise InvalidAPIKeyError("Invalid API key or access denied.")
            elif response.status_code == 429:
                raise RateLimitError("Rate limited by Hypixel API. Please wait.")

            # Raise an exception for any other bad status codes (4xx or 5xx)
            response.raise_for_status()

            data = response.json()
            if data.get('success'):
                return data
            else:
                raise HypixelAPIError(f"API Error: {data.get('cause', 'Unknown error')}")
                
        except requests.exceptions.RequestException as e:
            raise HypixelAPIError(f"Request failed: {str(e)}") from e
    
    def test_api_key(self) -> bool:
        """Test if the API key is valid"""
        try:
            self._make_request('/key')
            return True
        except HypixelAPIError:
            return False
    
    def get_player(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get basic player information"""
        return self._make_request('/player', {'uuid': uuid})
    
    def get_skyblock_profiles(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get all SkyBlock profiles for a player"""
        return self._make_request('/v2/skyblock/profiles', {'uuid': uuid})
    
    # ... (rest of the class methods are fine)
    def get_skyblock_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific SkyBlock profile"""
        return self._make_request('/v2/skyblock/profile', {'profile': profile_id})
    
    def get_skyblock_museum(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get museum data for a profile"""
        return self._make_request('/v2/skyblock/museum', {'profile': profile_id})
    
    def get_skyblock_garden(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Get garden data for a profile"""
        return self._make_request('/v2/skyblock/garden', {'profile': profile_id})
    
    def get_bazaar(self) -> Optional[Dict[str, Any]]:
        """Get current bazaar data"""
        return self._make_request('/v2/skyblock/bazaar')
    
    def get_auctions(self, page: int = 0) -> Optional[Dict[str, Any]]:
        """Get auction house data"""
        return self._make_request('/v2/skyblock/auctions', {'page': page})
    
    def get_skyblock_items(self) -> Optional[Dict[str, Any]]:
        """Get SkyBlock items data"""
        return self._make_request('/v2/resources/skyblock/items')
    
    def get_skyblock_collections(self) -> Optional[Dict[str, Any]]:
        """Get SkyBlock collections data"""
        return self._make_request('/v2/resources/skyblock/collections')