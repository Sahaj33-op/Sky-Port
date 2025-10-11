import requests
import time
from typing import Optional, Dict, Any
import streamlit as st

class MojangAPI:
    """Mojang API client for UUID and username resolution"""
    
    BASE_URL = "https://api.mojang.com"
    SESSION_URL = "https://sessionserver.mojang.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Sky-Port/1.0.0 (Minecraft UUID Resolver)'
        })
        self.last_request_time = 0
        self.request_interval = 1  # 1 second between requests to be respectful
    
    def _rate_limit(self):
        """Implement simple rate limiting"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.request_interval:
            time.sleep(self.request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def _make_request(self, url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
        """Make a rate-limited request to Mojang API"""
        self._rate_limit()
        
        try:
            response = self.session.get(url, timeout=timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 204:
                # No content - player not found
                return None
            elif response.status_code == 429:
                st.warning("Rate limited by Mojang API. Please wait.")
                time.sleep(5)
                return None
            else:
                st.error(f"Mojang API error: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Request to Mojang API failed: {str(e)}")
            return None
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_uuid(_self, username: str) -> Optional[Dict[str, Any]]:
        """Get UUID from username"""
        if not username or len(username) < 1 or len(username) > 16:
            return None
        
        url = f"{_self.BASE_URL}/users/profiles/minecraft/{username}"
        data = _self._make_request(url)
        
        if data and 'id' in data:
            # Add dashes to UUID for easier reading
            uuid = data['id']
            formatted_uuid = f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"
            data['formatted_id'] = formatted_uuid
        
        return data
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour  
    def get_username(_self, uuid: str) -> Optional[str]:
        """Get current username from UUID"""
        # Remove dashes from UUID if present
        clean_uuid = uuid.replace('-', '')
        
        if len(clean_uuid) != 32:
            return None
        
        url = f"{_self.SESSION_URL}/session/minecraft/profile/{clean_uuid}"
        data = _self._make_request(url)
        
        if data and 'name' in data:
            return data['name']
        
        return None
    
    @st.cache_data(ttl=86400)  # Cache for 24 hours
    def get_name_history(_self, uuid: str) -> Optional[List[Dict[str, Any]]]:
        """Get name history for a UUID"""
        # Remove dashes from UUID if present
        clean_uuid = uuid.replace('-', '')
        
        if len(clean_uuid) != 32:
            return None
        
        # Note: This endpoint was deprecated by Mojang
        # Keeping for potential future restoration or alternative implementation
        return [{"name": _self.get_username(clean_uuid), "changedToAt": None}]
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_profile(_self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get full profile data including skin information"""
        # Remove dashes from UUID if present
        clean_uuid = uuid.replace('-', '')
        
        if len(clean_uuid) != 32:
            return None
        
        url = f"{_self.SESSION_URL}/session/minecraft/profile/{clean_uuid}"
        return _self._make_request(url)
    
    def is_valid_uuid(self, uuid: str) -> bool:
        """Check if a string is a valid Minecraft UUID"""
        clean_uuid = uuid.replace('-', '')
        return len(clean_uuid) == 32 and clean_uuid.isalnum()
    
    def is_valid_username(self, username: str) -> bool:
        """Check if a string is a valid Minecraft username"""
        if not username:
            return False
        
        # Minecraft usernames: 3-16 characters, alphanumeric and underscore only
        if not (3 <= len(username) <= 16):
            return False
        
        allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
        return all(c in allowed_chars for c in username)
    
    def format_uuid(self, uuid: str) -> str:
        """Add dashes to a UUID string"""
        clean_uuid = uuid.replace('-', '')
        if len(clean_uuid) == 32:
            return f"{clean_uuid[:8]}-{clean_uuid[8:12]}-{clean_uuid[12:16]}-{clean_uuid[16:20]}-{clean_uuid[20:]}"
        return uuid
    
    def clean_uuid(self, uuid: str) -> str:
        """Remove dashes from a UUID string"""
        return uuid.replace('-', '')