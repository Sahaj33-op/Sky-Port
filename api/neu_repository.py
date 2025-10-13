import requests
import json
from typing import Dict, Any, Optional, List
import logging
import time

class NEURepository:
    """Integration with NotEnoughUpdates item repository"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://raw.githubusercontent.com/NotEnoughUpdates/NotEnoughUpdates-REPO/master"
        self.items_cache = {}
        self.last_update = 0
        self.cache_duration = 3600  # 1 hour
    
    def _fetch_item_data(self, item_id: str) -> Optional[Dict]:
        """Fetch item data from NEU repository"""
        try:
            url = f"{self.base_url}/items/{item_id}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            self.logger.warning(f"Could not fetch item data for {item_id}: {e}")
        
        return None
    
    def get_item_data(self, item_id: str) -> Dict[str, Any]:
        """Get comprehensive item data"""
        # Check cache
        if item_id in self.items_cache:
            return self.items_cache[item_id]
        
        # Fetch from repository
        item_data = self._fetch_item_data(item_id)
        
        if item_data:
            # Process and enhance item data
            enhanced_data = {
                'id': item_id,
                'display_name': item_data.get('displayname', item_id),
                'tier': item_data.get('tier', 'COMMON'),
                'category': item_data.get('category', 'MISC'),
                'npc_sell_price': item_data.get('npc_sell_price', 0),
                'lore': item_data.get('lore', []),
                'recipe': item_data.get('recipe', {}),
                'museum_data': item_data.get('museum', {}),
                'dungeon_item': 'DUNGEON' in item_data.get('lore', []),
                'soulbound': 'SOULBOUND' in item_data.get('lore', [])
            }
            
            self.items_cache[item_id] = enhanced_data
            return enhanced_data
        
        # Return basic data if not found
        return {
            'id': item_id,
            'display_name': item_id,
            'tier': 'COMMON',
            'category': 'MISC'
        }
    
    def enhance_item_data(self, inventory_data: Dict) -> Dict[str, Any]:
        """Enhance inventory items with NEU repository data"""
        enhanced_inventory = {
            'items': [],
            'total_value': 0,
            'rare_items': [],
            'dungeon_items': [],
            'museum_donations': []
        }
        
        try:
            # This would need proper NBT parsing
            # For now, return structure
            return enhanced_inventory
            
        except Exception as e:
            self.logger.error(f"Error enhancing item data: {e}")
            return enhanced_inventory
    
    def get_recipe_tree(self, item_id: str) -> Dict[str, Any]:
        """Get complete recipe tree for an item"""
        item_data = self.get_item_data(item_id)
        recipe = item_data.get('recipe', {})
        
        recipe_tree = {
            'item': item_id,
            'crafting_requirements': {},
            'total_cost': 0
        }
        
        # Build recipe tree recursively
        if recipe:
            for ingredient, amount in recipe.items():
                if isinstance(amount, (int, float)):
                    recipe_tree['crafting_requirements'][ingredient] = amount
        
        return recipe_tree