import requests
import time
from typing import Optional, Dict, Any, List
import streamlit as st
from utils.rate_limiter import RateLimiter

class HypixelAPI:
    """Hypixel API client with rate limiting and error handling"""
    
    BASE_URL = "https://api.hypixel.net"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(max_requests=100, time_window=300)  # 100 req/5min
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Sky-Port/1.0.0 (Hypixel SkyBlock Profile Exporter)'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make a rate-limited request to the Hypixel API"""
        if not self.rate_limiter.can_make_request():
            st.warning("Rate limit reached. Please wait before making another request.")
            return None
        
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
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    return data
                else:
                    st.error(f"API Error: {data.get('cause', 'Unknown error')}")
                    return None
            elif response.status_code == 403:
                st.error("Invalid API key or access denied")
                return None
            elif response.status_code == 429:
                st.warning("Rate limited by Hypixel API. Please wait.")
                return None
            else:
                st.error(f"HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Request failed: {str(e)}")
            return None
    
    def test_api_key(self) -> bool:
        """Test if the API key is valid"""
        response = self._make_request('/key')
        return response is not None
    
    def get_player(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get basic player information"""
        return self._make_request('/player', {'uuid': uuid})
    
    def get_skyblock_profiles(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get all SkyBlock profiles for a player"""
        return self._make_request('/v2/skyblock/profiles', {'uuid': uuid})
    
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
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_cached_bazaar(_self) -> Optional[Dict[str, Any]]:
        """Get cached bazaar data (updates every hour)"""
        return _self.get_bazaar()
    
    @st.cache_data(ttl=86400)  # Cache for 24 hours
    def get_cached_items(_self) -> Optional[Dict[str, Any]]:
        """Get cached items data (updates daily)"""
        return _self.get_skyblock_items()
    
    @st.cache_data(ttl=86400)  # Cache for 24 hours
    def get_cached_collections(_self) -> Optional[Dict[str, Any]]:
        """Get cached collections data (updates daily)"""
        return _self.get_skyblock_collections()
    
    def get_rate_limit_info(self) -> Dict[str, Any]:
        """Get current rate limit status"""
        return {
            'requests_made': self.rate_limiter.request_count,
            'requests_remaining': self.rate_limiter.max_requests - self.rate_limiter.request_count,
            'reset_time': self.rate_limiter.window_start + self.rate_limiter.time_window,
            'can_make_request': self.rate_limiter.can_make_request()
        }