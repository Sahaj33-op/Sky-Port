# processors/collections.py
import pandas as pd
from typing import Dict, Any

class CollectionsProcessor:
    """Processes collection data and minion crafting information"""
    
    def __init__(self):
        self.collection_categories = [
            'FARMING', 'MINING', 'COMBAT', 'FORAGING', 'FISHING'
        ]
    
    def process_collections(self, profile_data: Dict[str, Any]) -> pd.DataFrame:
        """Convert collections data to structured format"""
        collections_data = []
        
        if 'unlocked_coll_tiers' in profile_data:
            for collection in profile_data['unlocked_coll_tiers']:
                collection_info = self._get_collection_details(
                    collection, profile_data
                )
                collections_data.append(collection_info)
        
        return pd.DataFrame(collections_data)
