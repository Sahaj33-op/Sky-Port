import requests
import json
from typing import Dict, Any, Optional
import logging

class EliteFarmingWeight:
    """Integration with Elite Bot farming weight system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.farming_weights = {
            'WHEAT': 1.0,
            'CARROT': 1.0,
            'POTATO': 1.0,
            'PUMPKIN': 1.0,
            'MELON': 2.0,
            'MUSHROOM': 1.0,
            'COCOA': 1.0,
            'CACTUS': 2.0,
            'SUGAR_CANE': 2.0,
            'NETHER_WART': 2.5,
        }
    
    def calculate_farming_weight(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate farming weight and related metrics"""
        try:
            farming_data = {
                'total_weight': 0,
                'crop_weights': {},
                'contest_medals': {},
                'farming_level': 0,
                'garden_level': 0,
                'unique_golds': 0,
                'breakdown': {}
            }
            
            # Get farming level
            experience = profile_data.get('experience', {})
            farming_xp = experience.get('SKILL_FARMING', 0)
            farming_data['farming_level'] = self._calculate_level_from_xp(farming_xp)
            
            # Get garden level
            garden_data = profile_data.get('garden', {})
            farming_data['garden_level'] = garden_data.get('garden_experience', 0) // 10000
            
            # Calculate crop weights
            collections = profile_data.get('collection', {})
            
            for crop, weight_per_item in self.farming_weights.items():
                crop_count = collections.get(crop, 0)
                crop_weight = crop_count * weight_per_item / 100000  # Scaling factor
                farming_data['crop_weights'][crop] = {
                    'count': crop_count,
                    'weight': crop_weight
                }
                farming_data['total_weight'] += crop_weight
            
            # Calculate contest medals
            farming_data['contest_medals'] = self._calculate_contest_medals(profile_data)
            
            # Add bonus weight for contests
            medal_bonus = (
                farming_data['contest_medals'].get('gold', 0) * 0.002 +
                farming_data['contest_medals'].get('silver', 0) * 0.001 +
                farming_data['contest_medals'].get('bronze', 0) * 0.0005
            )
            
            farming_data['total_weight'] += medal_bonus
            
            return farming_data
            
        except Exception as e:
            self.logger.error(f"Error calculating farming weight: {e}")
            return {'total_weight': 0, 'error': str(e)}
    
    def _calculate_level_from_xp(self, xp: float) -> int:
        """Calculate skill level from XP"""
        # Simplified XP table - would need complete implementation
        xp_table = [0, 50, 175, 375, 675, 1175, 1925, 2925, 4425, 6425, 9925, 14925, 22425, 32425, 47425, 67425, 97425, 147425, 222425, 322425, 522425, 822425, 1222425, 1722425, 2322425, 3022425, 3822425, 4722425, 5722425, 6822425, 8022425, 9322425, 10722425, 12222425, 13822425, 15522425, 17322425, 19222425, 21222425, 23322425, 25522425, 27822425, 30222425, 32722425, 35322425, 38072425, 40972425, 44072425, 47472425, 51172425, 55172425, 59472425, 64072425, 68972425, 74172425, 79672425, 85472425, 91572425, 97972425, 104672425, 111672425]
        
        for level, required_xp in enumerate(xp_table):
            if xp < required_xp:
                return level - 1
        return len(xp_table) - 1
    
    def _calculate_contest_medals(self, profile_data: Dict) -> Dict[str, int]:
        """Calculate farming contest medals"""
        try:
            jacob_data = profile_data.get('jacob2', {})
            medals_inventory = jacob_data.get('medals_inv', {})
            
            medals = {
                'gold': 0,
                'silver': 0,
                'bronze': 0,
                'total': 0
            }
            
            # Parse medal inventory
            for item_data in medals_inventory.values():
                if isinstance(item_data, dict):
                    item_type = item_data.get('type', '')
                    if 'gold' in item_type.lower():
                        medals['gold'] += 1
                    elif 'silver' in item_type.lower():
                        medals['silver'] += 1
                    elif 'bronze' in item_type.lower():
                        medals['bronze'] += 1
            
            medals['total'] = medals['gold'] + medals['silver'] + medals['bronze']
            return medals
            
        except Exception as e:
            self.logger.warning(f"Could not calculate contest medals: {e}")
            return {'gold': 0, 'silver': 0, 'bronze': 0, 'total': 0}