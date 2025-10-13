import requests
import time
from typing import Optional, Dict, Any, List

# Custom Exceptions for this module
class MojangAPIError(Exception):
    """Base exception for Mojang API client errors."""
    pass

class MojangRateLimitError(MojangAPIError):
    """Raised when the Mojang API rate limit is exceeded."""
    pass

class PlayerNotFoundError(MojangAPIError):
    """Raised when a player cannot be found."""
    pass

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
        self.request_interval = 1  # 1 second between requests
    
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
                raise MojangRateLimitError("Rate limited by Mojang API. Please wait.")
            
            response.raise_for_status() # Raise exceptions for other errors
            
        except requests.exceptions.RequestException as e:
            raise MojangAPIError(f"Request to Mojang API failed: {str(e)}") from e

    def get_uuid(self, username: str) -> Optional[Dict[str, Any]]:
        """Get UUID from username"""
        if not username or len(username) < 3 or len(username) > 16:
            raise ValueError("Invalid username provided.")
        
        url = f"{self.BASE_URL}/users/profiles/minecraft/{username}"
        data = self._make_request(url)
        
        if data and 'id' in data:
            uuid = data['id']
            formatted_uuid = f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"
            data['formatted_id'] = formatted_uuid
            return data
        
        raise PlayerNotFoundError(f"Player with username '{username}' not found.")
    
    # ... (rest of the class methods are fine)
    def get_username(self, uuid: str) -> Optional[str]:
        """Get current username from UUID"""
        clean_uuid = uuid.replace('-', '')
        if len(clean_uuid) != 32:
            return None
        
        url = f"{self.SESSION_URL}/session/minecraft/profile/{clean_uuid}"
        data = self._make_request(url)
        
        if data and 'name' in data:
            return data['name']
        return None

    def get_name_history(self, uuid: str) -> Optional[List[Dict[str, Any]]]:
        """Get name history for a UUID"""
        clean_uuid = uuid.replace('-', '')
        if len(clean_uuid) != 32:
            return None
        return [{"name": self.get_username(clean_uuid), "changedToAt": None}]

    def get_profile(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get full profile data including skin information"""
        clean_uuid = uuid.replace('-', '')
        if len(clean_uuid) != 32:
            return None
        url = f"{self.SESSION_URL}/session/minecraft/profile/{clean_uuid}"
        return self._make_request(url)