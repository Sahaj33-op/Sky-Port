import pandas as pd
import io
import zipfile
from typing import Dict, Any, List
from datetime import datetime

class CSVExporter:
    """Export processed SkyBlock data to CSV format"""
    
    def __init__(self, processed_data: Dict[str, Any]):
        self.processed_data = processed_data
    
    def create_section_csv(self, section: str) -> str:
        """Create a CSV export for a specific data section"""
        if section not in self.processed_data:
            # Return error CSV
            error_df = pd.DataFrame([{
                'error': f'Section "{section}" not found',
                'available_sections': ', '.join(self.processed_data.keys())
            }])
            return error_df.to_csv(index=False)
        
        section_data = self.processed_data[section]
        
        if 'data' not in section_data or not section_data['data']:
            # Return empty CSV with appropriate headers
            return self._create_empty_csv_for_section(section)
        
        # Convert data to DataFrame
        df = pd.DataFrame(section_data['data'])
        
        # Add metadata header
        metadata_rows = [
            ['# Sky-Port Export'],
            [f'# Section: {section}'],
            [f'# Exported: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'],
            ['# Data starts below'],
            ['']
        ]
        
        # Create CSV with metadata
        output = io.StringIO()
        
        # Write metadata
        for row in metadata_rows:
            output.write(','.join(row) + '\n')
        
        # Write data
        df.to_csv(output, index=False)
        
        return output.getvalue()
    
    def create_all_sections_zip(self) -> bytes:
        """Create a ZIP file containing CSV exports for all sections"""
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Export each section to CSV
            for section_name in self.processed_data.keys():
                csv_data = self.create_section_csv(section_name)
                zip_file.writestr(f"{section_name}.csv", csv_data)
            
            # Add a summary CSV
            summary_csv = self._create_summary_csv()
            zip_file.writestr("summary.csv", summary_csv)
            
            # Add export info
            export_info = self._create_export_info_csv()
            zip_file.writestr("export_info.csv", export_info)
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
    
    def create_combined_csv(self) -> str:
        """Create a single CSV file with all data sections"""
        combined_data = []
        
        # Add metadata
        combined_data.extend([
            ['# Sky-Port Combined Export'],
            [f'# Exported: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'],
            ['# All profile data combined'],
            [''],
        ])
        
        # Process each section
        for section_name, section_data in self.processed_data.items():
            # Section header
            combined_data.append([f'## {section_name.upper()} ##'])
            combined_data.append([''])
            
            if 'data' in section_data and section_data['data']:
                df = pd.DataFrame(section_data['data'])
                
                # Convert DataFrame to list of lists
                header = df.columns.tolist()
                combined_data.append(header)
                
                for _, row in df.iterrows():
                    combined_data.append(row.tolist())
            else:
                combined_data.append(['No data available for this section'])
            
            combined_data.append([''])  # Empty row between sections
        
        # Convert to CSV string
        output = io.StringIO()
        for row in combined_data:
            # Convert all values to strings and handle None/NaN values
            str_row = [str(val) if val is not None else '' for val in row]
            output.write(','.join(str_row) + '\n')
        
        return output.getvalue()
    
    def create_skills_detailed_csv(self) -> str:
        """Create a detailed CSV export specifically for skills data"""
        if 'skills' not in self.processed_data:
            return "skill,error\nNo Skills Data,Skills data not found in profile"
        
        skills_data = self.processed_data['skills']['data']
        df = pd.DataFrame(skills_data)
        
        # Add calculated columns
        if 'level' in df.columns and 'xp' in df.columns:
            df['xp_formatted'] = df['xp'].apply(lambda x: f"{x:,}")
            df['level_category'] = df['level'].apply(self._categorize_skill_level)
        
        # Add skill average as a summary row
        skill_avg = self.processed_data['skills'].get('average', 0)
        
        output = io.StringIO()
        
        # Write header info
        output.write(f"# Skills Export - Skill Average: {skill_avg:.2f}\n")
        output.write(f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("\n")
        
        # Write data
        df.to_csv(output, index=False)
        
        # Add summary
        output.write("\n# Summary\n")
        output.write(f"Skill Average,{skill_avg:.2f}\n")
        output.write(f"Total Skills,{len(df)}\n")
        
        if 'level' in df.columns:
            maxed_skills = len(df[df['level'] >= 50])
            output.write(f"Maxed Skills (50+),{maxed_skills}\n")
            
            high_skills = len(df[df['level'] >= 40])
            output.write(f"High Level Skills (40+),{high_skills}\n")
        
        return output.getvalue()
    
    def create_collections_detailed_csv(self) -> str:
        """Create a detailed CSV export specifically for collections data"""
        if 'collections' not in self.processed_data:
            return "collection,error\nNo Collections Data,Collections data not found in profile"
        
        collections_data = self.processed_data['collections']['data']
        if not collections_data:
            return "collection,message\nNo Collections,No collection progress found"
        
        df = pd.DataFrame(collections_data)
        
        # Add formatted columns
        if 'amount' in df.columns:
            df['amount_formatted'] = df['amount'].apply(lambda x: f"{x:,}")
        
        if 'max_tier' in df.columns:
            df['tier_status'] = df['max_tier'].apply(self._categorize_collection_tier)
        
        # Sort by category and amount
        if 'category' in df.columns and 'amount' in df.columns:
            df = df.sort_values(['category', 'amount'], ascending=[True, False])
        
        output = io.StringIO()
        
        # Write header info
        collections_summary = self.processed_data['collections'].get('summary', {})
        total_collections = collections_summary.get('total_collections', 0)
        maxed_collections = collections_summary.get('maxed_collections', 0)
        
        output.write(f"# Collections Export - Total: {total_collections}, Maxed: {maxed_collections}\n")
        output.write(f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("\n")
        
        # Write data
        df.to_csv(output, index=False)
        
        # Add category summaries
        if 'category' in df.columns:
            output.write("\n# Category Summaries\n")
            category_summary = df.groupby('category').agg({
                'amount': 'sum',
                'max_tier': 'mean'
            }).round(2)
            
            category_summary.to_csv(output)
        
        return output.getvalue()
    
    def _create_empty_csv_for_section(self, section: str) -> str:
        """Create an empty CSV with appropriate headers for a section"""
        headers_map = {
            'skills': ['skill', 'level', 'xp', 'xp_to_next', 'progress_percent'],
            'slayers': ['slayer', 'xp', 'level', 'tier_1_kills', 'tier_2_kills', 'tier_3_kills', 'tier_4_kills', 'total_kills'],
            'dungeons': ['type', 'level', 'xp', 'highest_floor'],
            'inventory': ['inventory_type', 'estimated_items', 'last_updated'],
            'collections': ['collection', 'category', 'amount', 'max_tier'],
            'pets': ['type', 'tier', 'level', 'xp', 'active', 'held_item'],
            'networth': ['category', 'purse', 'bank', 'total'],
            'profile_info': ['profile_name', 'game_mode', 'last_save', 'fairy_souls', 'fairy_exchanges', 'deaths']
        }
        
        headers = headers_map.get(section, ['data', 'value'])
        df = pd.DataFrame(columns=headers)
        
        output = io.StringIO()
        output.write(f"# {section.title()} - No Data Available\n")
        output.write(f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        output.write("\n")
        df.to_csv(output, index=False)
        
        return output.getvalue()
    
    def _create_summary_csv(self) -> str:
        """Create a summary CSV with key statistics from all sections"""
        summary_data = []
        
        # Add header
        summary_data.extend([
            ['# Sky-Port Profile Summary'],
            [f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'],
            [''],
            ['Category', 'Metric', 'Value']
        ])
        
        # Extract summaries from each section
        for section_name, section_data in self.processed_data.items():
            if isinstance(section_data, dict) and 'summary' in section_data:
                summary = section_data['summary']
                
                for metric, value in summary.items():
                    summary_data.append([
                        section_name.title(),
                        metric.replace('_', ' ').title(),
                        str(value)
                    ])
        
        # Convert to CSV
        output = io.StringIO()
        for row in summary_data:
            output.write(','.join(row) + '\n')
        
        return output.getvalue()
    
    def _create_export_info_csv(self) -> str:
        """Create an export information CSV"""
        info_data = [
            ['# Sky-Port Export Information'],
            [''],
            ['Property', 'Value'],
            ['Export Tool', 'Sky-Port v1.0.0'],
            ['Export Format', 'CSV'],
            ['Export Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['Total Sections', str(len(self.processed_data))],
            ['Sections Included', ', '.join(self.processed_data.keys())]
        ]
        
        output = io.StringIO()
        for row in info_data:
            output.write(','.join(row) + '\n')
        
        return output.getvalue()
    
    def _categorize_skill_level(self, level: int) -> str:
        """Categorize skill level into ranges"""
        if level >= 50:
            return "Maxed (50+)"
        elif level >= 40:
            return "High (40-49)"
        elif level >= 30:
            return "Medium (30-39)"
        elif level >= 20:
            return "Low (20-29)"
        else:
            return "Beginner (0-19)"
    
    def _categorize_collection_tier(self, tier: int) -> str:
        """Categorize collection tier into ranges"""
        if tier >= 10:
            return "Maxed"
        elif tier >= 7:
            return "High"
        elif tier >= 4:
            return "Medium"
        elif tier >= 1:
            return "Low"
        else:
            return "None"