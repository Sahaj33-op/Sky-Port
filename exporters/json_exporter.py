import json
from typing import Dict, Any
from datetime import datetime

class JSONExporter:
    """Export processed SkyBlock data to JSON format"""
    
    def __init__(self, processed_data: Dict[str, Any]):
        self.processed_data = processed_data
    
    def create_export(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        """Create a comprehensive JSON export of all processed data"""
        export_data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'exporter': 'Sky-Port v1.0.0',
                'format_version': '1.0'
            },
            'profile_data': self.processed_data
        }
        
        # Add summary statistics
        export_data['summary'] = self._generate_summary()
        
        return json.dumps(export_data, indent=indent, ensure_ascii=ensure_ascii, default=str)
    
    def create_section_export(self, section: str, indent: int = 2) -> str:
        """Create a JSON export for a specific data section"""
        if section not in self.processed_data:
            return json.dumps({
                'error': f'Section "{section}" not found in processed data',
                'available_sections': list(self.processed_data.keys())
            }, indent=indent)
        
        section_data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'exporter': 'Sky-Port v1.0.0',
                'section': section,
                'format_version': '1.0'
            },
            'data': self.processed_data[section]
        }
        
        return json.dumps(section_data, indent=indent, ensure_ascii=False, default=str)
    
    def create_minimal_export(self) -> str:
        """Create a minimal JSON export with only essential data"""
        minimal_data = {}
        
        # Profile overview
        if 'profile_info' in self.processed_data:
            profile_summary = self.processed_data['profile_info']['summary']
            minimal_data['profile'] = {
                'name': profile_summary.get('profile_name', 'Unknown'),
                'game_mode': profile_summary.get('game_mode', 'normal'),
                'last_active': profile_summary.get('last_active')
            }
        
        # Skills summary
        if 'skills' in self.processed_data:
            skills_summary = self.processed_data['skills']['summary']
            minimal_data['skills'] = {
                'average': skills_summary.get('skill_average', 0),
                'maxed': skills_summary.get('maxed_skills', 0)
            }
        
        # Slayers summary
        if 'slayers' in self.processed_data:
            slayers_summary = self.processed_data['slayers']['summary']
            minimal_data['slayers'] = {
                'total_xp': slayers_summary.get('total_slayer_xp', 0),
                'total_kills': slayers_summary.get('total_kills', 0)
            }
        
        # Networth summary
        if 'networth' in self.processed_data:
            minimal_data['networth'] = self.processed_data['networth'].get('total', 0)
        
        # Collections summary
        if 'collections' in self.processed_data:
            collections_summary = self.processed_data['collections']['summary']
            minimal_data['collections'] = {
                'total': collections_summary.get('total_collections', 0),
                'maxed': collections_summary.get('maxed_collections', 0)
            }
        
        export_data = {
            'export_info': {
                'exported_at': datetime.now().isoformat(),
                'exporter': 'Sky-Port v1.0.0 (Minimal)',
                'format_version': '1.0'
            },
            'data': minimal_data
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False, default=str)
    
    def create_raw_export(self) -> str:
        """Create a raw JSON export without additional metadata"""
        return json.dumps(self.processed_data, indent=2, ensure_ascii=False, default=str)
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics for the export"""
        summary = {
            'data_categories': list(self.processed_data.keys()),
            'total_categories': len(self.processed_data)
        }
        
        # Add category-specific summaries
        for category, data in self.processed_data.items():
            if isinstance(data, dict) and 'summary' in data:
                summary[f'{category}_summary'] = data['summary']
            elif isinstance(data, dict) and 'data' in data:
                summary[f'{category}_items'] = len(data['data']) if isinstance(data['data'], list) else 1
        
        return summary
    
    def validate_export_data(self) -> Dict[str, Any]:
        """Validate the processed data and return validation results"""
        validation = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'statistics': {}
        }
        
        # Check for required data categories
        required_categories = ['profile_info', 'skills', 'slayers', 'dungeons']
        for category in required_categories:
            if category not in self.processed_data:
                validation['errors'].append(f'Missing required category: {category}')
                validation['is_valid'] = False
        
        # Check data structure
        for category, data in self.processed_data.items():
            if not isinstance(data, dict):
                validation['errors'].append(f'Invalid data structure for category: {category}')
                validation['is_valid'] = False
                continue
            
            if 'data' not in data:
                validation['warnings'].append(f'No data field found in category: {category}')
            
            if 'summary' not in data:
                validation['warnings'].append(f'No summary field found in category: {category}')
            
            # Count items in each category
            if 'data' in data and isinstance(data['data'], list):
                validation['statistics'][f'{category}_count'] = len(data['data'])
        
        return validation
    
    def create_structured_export(self) -> str:
        """Create a structured JSON export optimized for data analysis"""
        structured_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'exporter': 'Sky-Port v1.0.0',
                'format': 'structured_analysis',
                'version': '1.0'
            },
            'profile': {},
            'statistics': {},
            'raw_data': {}
        }
        
        # Extract profile information
        if 'profile_info' in self.processed_data:
            profile_data = self.processed_data['profile_info']
            if 'summary' in profile_data:
                structured_data['profile'] = profile_data['summary']
        
        # Extract summary statistics from all categories
        for category, data in self.processed_data.items():
            if isinstance(data, dict) and 'summary' in data:
                structured_data['statistics'][category] = data['summary']
        
        # Include raw data for detailed analysis
        structured_data['raw_data'] = self.processed_data
        
        # Add computed metrics
        structured_data['computed_metrics'] = self._compute_additional_metrics()
        
        return json.dumps(structured_data, indent=2, ensure_ascii=False, default=str)
    
    def _compute_additional_metrics(self) -> Dict[str, Any]:
        """Compute additional metrics for analysis"""
        metrics = {}
        
        # Skills metrics
        if 'skills' in self.processed_data:
            skills_data = self.processed_data['skills'].get('data', [])
            if skills_data:
                skill_levels = [skill.get('level', 0) for skill in skills_data if skill.get('skill', '').lower() not in ['social', 'carpentry']]
                if skill_levels:
                    metrics['skills_analysis'] = {
                        'average_level': sum(skill_levels) / len(skill_levels),
                        'highest_level': max(skill_levels),
                        'lowest_level': min(skill_levels),
                        'levels_above_30': len([l for l in skill_levels if l >= 30]),
                        'levels_above_40': len([l for l in skill_levels if l >= 40]),
                        'levels_above_50': len([l for l in skill_levels if l >= 50])
                    }
        
        # Slayers metrics
        if 'slayers' in self.processed_data:
            slayers_data = self.processed_data['slayers'].get('data', [])
            if slayers_data:
                slayer_levels = [slayer.get('level', 0) for slayer in slayers_data]
                metrics['slayers_analysis'] = {
                    'average_level': sum(slayer_levels) / len(slayer_levels) if slayer_levels else 0,
                    'highest_level': max(slayer_levels) if slayer_levels else 0,
                    'total_xp': sum([slayer.get('xp', 0) for slayer in slayers_data]),
                    'maxed_slayers': len([l for l in slayer_levels if l >= 9])
                }
        
        # Collections metrics
        if 'collections' in self.processed_data:
            collections_data = self.processed_data['collections'].get('data', [])
            if collections_data:
                collection_tiers = [coll.get('max_tier', 0) for coll in collections_data]
                metrics['collections_analysis'] = {
                    'average_tier': sum(collection_tiers) / len(collection_tiers) if collection_tiers else 0,
                    'highest_tier': max(collection_tiers) if collection_tiers else 0,
                    'total_items': sum([coll.get('amount', 0) for coll in collections_data]),
                    'maxed_collections': len([t for t in collection_tiers if t >= 10])
                }
        
        return metrics