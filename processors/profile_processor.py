import pandas as pd
import json
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
import math

class ProfileProcessor:
    """Main processor for Hypixel SkyBlock profile data"""
    
    # XP requirements for skills (levels 0-60)
    SKILL_XP = [
        0, 50, 175, 375, 675, 1175, 1925, 2925, 4425, 6425, 9925, 14925, 22425, 32425, 47425, 67425, 97425,
        147425, 222425, 322425, 522425, 822425, 1222425, 1722425, 2322425, 3022425, 3822425, 4722425, 5722425,
        6822425, 8022425, 9322425, 10722425, 12222425, 13822425, 15522425, 17322425, 19222425, 21222425,
        23322425, 25522425, 27822425, 30222425, 32722425, 35322425, 38072425, 40972425, 44072425, 47472425,
        51172425, 55172425, 59472425, 64072425, 68972425, 74172425, 79672425, 85472425, 91572425, 97972425,
        104672425, 111672425
    ]
    
    # Slayer boss types
    SLAYERS = {
        'zombie': 'Revenant Horror',
        'spider': 'Tarantula Broodfather', 
        'wolf': 'Sven Packmaster',
        'enderman': 'Voidgloom Seraph',
        'blaze': 'Inferno Demonlord'
    }
    
    # Collection categories
    COLLECTION_CATEGORIES = {
        'FARMING': ['WHEAT', 'CARROT', 'POTATO', 'PUMPKIN', 'SUGAR_CANE', 'MELON', 'SEEDS', 'MUSHROOM_COLLECTION', 'COCOA', 'CACTUS', 'NETHER_STALK'],
        'MINING': ['COBBLESTONE', 'COAL', 'IRON_INGOT', 'GOLD_INGOT', 'DIAMOND', 'LAPIS_LAZULI', 'EMERALD', 'REDSTONE', 'QUARTZ', 'OBSIDIAN', 'GLOWSTONE_DUST', 'GRAVEL', 'ICE', 'NETHERRACK', 'SAND', 'END_STONE'],
        'COMBAT': ['ROTTEN_FLESH', 'BONE', 'STRING', 'SPIDER_EYE', 'GUNPOWDER', 'ENDER_PEARL', 'GHAST_TEAR', 'SLIME_BALL', 'BLAZE_ROD', 'MAGMA_CREAM'],
        'FORAGING': ['LOG', 'LOG:1', 'LOG:2', 'LOG_2:1'],
        'FISHING': ['RAW_FISH', 'RAW_FISH:1', 'RAW_FISH:2', 'RAW_FISH:3', 'PRISMARINE_SHARD', 'PRISMARINE_CRYSTALS', 'CLAY_BALL', 'WATER_LILY', 'INK_SACK', 'SPONGE']
    }
    
    def __init__(self, player_data: Dict[str, Any], profile_data: Dict[str, Any]):
        self.player_data = player_data
        self.profile_data = profile_data
        self.processed_data = {}
    
    def process_all_data(self) -> Dict[str, Any]:
        """Process all profile data and return structured results"""
        self.processed_data = {
            'profile_info': self._process_profile_info(),
            'skills': self._process_skills(),
            'slayers': self._process_slayers(),
            'dungeons': self._process_dungeons(),
            'inventory': self._process_inventory(),
            'collections': self._process_collections(),
            'pets': self._process_pets(),
            'networth': self._process_networth(),
            'misc': self._process_misc_stats()
        }
        
        return self.processed_data
    
    def _process_profile_info(self) -> Dict[str, Any]:
        """Process basic profile information"""
        last_save = self.player_data.get('last_save', 0)
        
        return {
            'data': [{
                'profile_name': self.profile_data.get('cute_name', 'Unknown'),
                'game_mode': self.profile_data.get('game_mode', 'normal'),
                'last_save': datetime.fromtimestamp(last_save / 1000).strftime('%Y-%m-%d %H:%M:%S') if last_save else 'Unknown',
                'fairy_souls': self.player_data.get('fairy_souls_collected', 0),
                'fairy_exchanges': self.player_data.get('fairy_exchanges', 0),
                'deaths': self.player_data.get('stats', {}).get('deaths', 0)
            }],
            'summary': {
                'profile_name': self.profile_data.get('cute_name', 'Unknown'),
                'game_mode': self.profile_data.get('game_mode', 'normal'),
                'last_active': datetime.fromtimestamp(last_save / 1000) if last_save else None
            }
        }
    
    def _process_skills(self) -> Dict[str, Any]:
        """Process skills data including levels and XP"""
        skills_data = []
        skill_xp = self.player_data.get('experience_skill', {})
        
        skills = ['farming', 'mining', 'combat', 'foraging', 'fishing', 'enchanting', 'alchemy', 'carpentry', 'runecrafting', 'taming', 'social']
        
        total_level = 0
        counted_skills = 0
        
        for skill in skills:
            xp = skill_xp.get(f'SKILL_{skill.upper()}', 0)
            level = self._calculate_skill_level(xp)
            
            skills_data.append({
                'skill': skill.title(),
                'level': level,
                'xp': xp,
                'xp_to_next': self._xp_to_next_level(xp, level),
                'progress_percent': self._skill_progress_percent(xp, level)
            })
            
            # Don't count social and carpentry in skill average
            if skill not in ['social', 'carpentry']:
                total_level += level
                counted_skills += 1
        
        skill_average = total_level / counted_skills if counted_skills > 0 else 0
        
        return {
            'data': skills_data,
            'average': skill_average,
            'summary': {
                'skill_average': skill_average,
                'total_skills': len(skills),
                'maxed_skills': len([s for s in skills_data if s['level'] >= 50])
            }
        }
    
    def _process_slayers(self) -> Dict[str, Any]:
        """Process slayer boss data"""
        slayers_data = []
        slayer_bosses = self.player_data.get('slayer_bosses', {})
        
        for slayer_type, display_name in self.SLAYERS.items():
            slayer_data = slayer_bosses.get(slayer_type, {})
            xp = slayer_data.get('xp', 0)
            
            boss_kills = {}
            for tier in range(1, 5):  # Tiers 1-4
                boss_kills[f'tier_{tier}'] = slayer_data.get('boss_kills_tier_{}'.format(tier), 0)
            
            slayers_data.append({
                'slayer': display_name,
                'xp': xp,
                'level': self._calculate_slayer_level(xp),
                'tier_1_kills': boss_kills.get('tier_1', 0),
                'tier_2_kills': boss_kills.get('tier_2', 0),
                'tier_3_kills': boss_kills.get('tier_3', 0),
                'tier_4_kills': boss_kills.get('tier_4', 0),
                'total_kills': sum(boss_kills.values())
            })
        
        total_slayer_xp = sum([s['xp'] for s in slayers_data])
        
        return {
            'data': slayers_data,
            'summary': {
                'total_slayer_xp': total_slayer_xp,
                'total_kills': sum([s['total_kills'] for s in slayers_data]),
                'maxed_slayers': len([s for s in slayers_data if s['level'] >= 9])
            }
        }
    
    def _process_dungeons(self) -> Dict[str, Any]:
        """Process dungeon data including catacombs and classes"""
        dungeons = self.player_data.get('dungeons', {})
        dungeon_data = []
        
        # Catacombs data
        catacombs = dungeons.get('dungeon_types', {}).get('catacombs', {})
        cata_xp = catacombs.get('experience', 0)
        cata_level = self._calculate_dungeon_level(cata_xp)
        
        dungeon_data.append({
            'type': 'Catacombs',
            'level': cata_level,
            'xp': cata_xp,
            'highest_floor': catacombs.get('highest_tier_completed', 0)
        })
        
        # Class data
        classes = ['healer', 'mage', 'berserk', 'archer', 'tank']
        class_data = []
        
        player_classes = dungeons.get('player_classes', {})
        for class_name in classes:
            class_info = player_classes.get(class_name, {})
            class_xp = class_info.get('experience', 0)
            class_level = self._calculate_dungeon_level(class_xp)
            
            class_data.append({
                'class': class_name.title(),
                'level': class_level,
                'xp': class_xp
            })
        
        return {
            'data': dungeon_data + class_data,
            'summary': {
                'catacombs_level': cata_level,
                'highest_floor': catacombs.get('highest_tier_completed', 0),
                'total_runs': sum([catacombs.get('tier_completions', {}).get(str(i), 0) for i in range(8)])
            }
        }
    
    def _process_inventory(self) -> Dict[str, Any]:
        """Process inventory data (simplified without NBT parsing for now)"""
        inventory_types = {
            'inv_contents': 'Main Inventory',
            'ender_chest_contents': 'Ender Chest',
            'wardrobe_contents': 'Wardrobe',
            'equipment_contents': 'Equipment'
        }
        
        inventory_data = []
        
        for inv_type, display_name in inventory_types.items():
            if inv_type in self.player_data:
                inv_data = self.player_data[inv_type]
                item_count = len(inv_data.get('data', '')) // 2 if 'data' in inv_data else 0
                
                inventory_data.append({
                    'inventory_type': display_name,
                    'estimated_items': item_count,
                    'last_updated': 'Available' if inv_type in self.player_data else 'Not Available'
                })
        
        return {
            'data': inventory_data,
            'summary': {
                'total_inventories': len([i for i in inventory_data if i['last_updated'] == 'Available']),
                'estimated_total_items': sum([i['estimated_items'] for i in inventory_data])
            }
        }
    
    def _process_collections(self) -> Dict[str, Any]:
        """Process collection data"""
        collections_data = []
        unlocked_tiers = self.player_data.get('unlocked_coll_tiers', [])
        collection_xp = self.player_data.get('collection', {})
        
        # Process each collection category
        for category, items in self.COLLECTION_CATEGORIES.items():
            for item in items:
                amount = collection_xp.get(item, 0)
                max_tier = max([int(tier.split('_')[-1]) for tier in unlocked_tiers if tier.startswith(f'{item}_')], default=0)
                
                if amount > 0 or max_tier > 0:  # Only include collections with progress
                    collections_data.append({
                        'collection': item.replace('_', ' ').title(),
                        'category': category.title(),
                        'amount': amount,
                        'max_tier': max_tier
                    })
        
        return {
            'data': collections_data,
            'summary': {
                'total_collections': len(collections_data),
                'maxed_collections': len([c for c in collections_data if c['max_tier'] >= 10]),
                'total_items_collected': sum([c['amount'] for c in collections_data])
            }
        }
    
    def _process_pets(self) -> Dict[str, Any]:
        """Process pets data"""
        pets_data = self.player_data.get('pets', [])
        processed_pets = []
        
        for pet in pets_data:
            processed_pets.append({
                'type': pet.get('type', 'Unknown'),
                'tier': pet.get('tier', 'COMMON'),
                'level': pet.get('level', 1),
                'xp': pet.get('exp', 0),
                'active': pet.get('active', False),
                'held_item': pet.get('heldItem', None)
            })
        
        return {
            'data': processed_pets,
            'summary': {
                'total_pets': len(processed_pets),
                'legendary_pets': len([p for p in processed_pets if p['tier'] == 'LEGENDARY']),
                'active_pet': next((p['type'] for p in processed_pets if p['active']), 'None')
            }
        }
    
    def _process_networth(self) -> Dict[str, Any]:
        """Process networth data (placeholder - would integrate with SkyHelper)"""
        # This would integrate with the SkyHelper Networth library
        # For now, providing basic coin data
        
        purse = self.player_data.get('coin_purse', 0)
        bank = self.profile_data.get('banking', {}).get('balance', 0)
        
        return {
            'data': [{
                'category': 'Coins',
                'purse': purse,
                'bank': bank,
                'total': purse + bank
            }],
            'total': purse + bank,
            'summary': {
                'liquid_coins': purse + bank,
                'estimated_total': purse + bank  # Placeholder for full networth calculation
            }
        }
    
    def _process_misc_stats(self) -> Dict[str, Any]:
        """Process miscellaneous statistics"""
        stats = self.player_data.get('stats', {})
        objectives = self.player_data.get('objectives', {})
        
        return {
            'data': [{
                'deaths': stats.get('deaths', 0),
                'kills': stats.get('kills', 0),
                'items_fished': stats.get('items_fished', 0),
                'pet_milestone_ores_mined': stats.get('pet_milestone_ores_mined', 0),
                'auctions_bids': stats.get('auctions_bids', 0),
                'auctions_won': stats.get('auctions_won', 0)
            }],
            'summary': {
                'total_objectives': len(objectives),
                'completed_objectives': len([o for o in objectives.values() if o.get('status') == 'COMPLETE'])
            }
        }
    
    def _calculate_skill_level(self, xp: float) -> int:
        """Calculate skill level from XP"""
        for level, required_xp in enumerate(self.SKILL_XP):
            if xp < required_xp:
                return level - 1
        return len(self.SKILL_XP) - 1
    
    def _xp_to_next_level(self, current_xp: float, current_level: int) -> float:
        """Calculate XP needed for next level"""
        if current_level >= len(self.SKILL_XP) - 1:
            return 0
        return self.SKILL_XP[current_level + 1] - current_xp
    
    def _skill_progress_percent(self, current_xp: float, current_level: int) -> float:
        """Calculate progress percentage to next level"""
        if current_level >= len(self.SKILL_XP) - 1:
            return 100.0
        
        current_level_xp = self.SKILL_XP[current_level]
        next_level_xp = self.SKILL_XP[current_level + 1]
        progress_xp = current_xp - current_level_xp
        level_xp_diff = next_level_xp - current_level_xp
        
        return (progress_xp / level_xp_diff) * 100 if level_xp_diff > 0 else 0
    
    def _calculate_slayer_level(self, xp: float) -> int:
        """Calculate slayer level from XP"""
        slayer_xp_requirements = [0, 5, 15, 200, 1000, 5000, 20000, 100000, 400000, 1000000]
        
        for level, required_xp in enumerate(slayer_xp_requirements):
            if xp < required_xp:
                return level - 1
        return len(slayer_xp_requirements) - 1
    
    def _calculate_dungeon_level(self, xp: float) -> int:
        """Calculate dungeon level from XP"""
        # Simplified dungeon XP calculation
        if xp < 50: return 0
        return min(50, int(math.log(xp / 50) / math.log(2)) + 1)