# processors/inventory.py
import base64
import pandas as pd
from typing import Dict, List, Any
import io

# Try to import nbtlib, but handle the case where it's not available
NBTLIB_AVAILABLE = False
try:
    import nbtlib
    NBTLIB_AVAILABLE = True
except ImportError:
    nbtlib = None

class InventoryProcessor:
    """Processes inventory data including NBT parsing for items"""
    
    def __init__(self):
        self.inventory_types = [
            'inv_contents', 'ender_chest_contents', 'wardrobe_contents',
            'equipment_contents', 'talisman_bag', 'potion_bag'
        ]
    
    def process_inventory(self, profile_data: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Process all inventory types and return structured data"""
        inventories = {}
        
        for inv_type in self.inventory_types:
            if inv_type in profile_data and profile_data[inv_type].get('data'):
                inventories[inv_type] = self._decode_inventory_data(
                    profile_data[inv_type]
                )
        
        return inventories
    
    def _decode_inventory_data(self, inventory_data: Dict) -> pd.DataFrame:
        """Decode base64 NBT data and extract item information"""
        items = []
        
        if not NBTLIB_AVAILABLE:
            # Return empty DataFrame if nbtlib is not available
            return pd.DataFrame(items)
        
        if 'data' in inventory_data:
            try:
                # Decode base64 NBT data
                if nbtlib is not None:
                    nbt_data = nbtlib.load(io.BytesIO(base64.b64decode(inventory_data['data'])))
                    
                    # The actual items are in the 'i' tag
                    for item_tag in nbt_data.get('i', []):
                        # Safely handle nbtlib types
                        item_id = item_tag.get('id', "")
                        if hasattr(item_id, 'unpack'):
                            item_id = str(item_id.unpack())
                        else:
                            item_id = str(item_id)
                            
                        count = item_tag.get('Count', 0)
                        if hasattr(count, 'unpack'):
                            count = int(count.unpack())
                        else:
                            count = int(count)
                            
                        damage = item_tag.get('Damage', 0)
                        if hasattr(damage, 'unpack'):
                            damage = int(damage.unpack())
                        else:
                            damage = int(damage)

                        item_details = {
                            'id': item_id,
                            'Count': count,
                            'Damage': damage,
                        }
                        
                        # Extract custom display name if it exists
                        if 'tag' in item_tag and 'display' in item_tag['tag']:
                            display_name = item_tag['tag']['display'].get('Name', "")
                            if hasattr(display_name, 'unpack'):
                                display_name = str(display_name.unpack())
                            else:
                                display_name = str(display_name)
                            item_details['display_name'] = display_name
                        
                        items.append(item_details)

            except Exception as e:
                print(f"Error decoding inventory data: {e}")

        return pd.DataFrame(items)