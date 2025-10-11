# exporters/excel.py
import pandas as pd
import io
from xlsxwriter import Workbook
from typing import Dict, Any

class ExcelExporter:
    """Creates comprehensive Excel exports with multiple sheets"""
    
    def __init__(self):
        self.sheet_configs = {
            'Profile Overview': {'color': '#4CAF50'},
            'Skills': {'color': '#2196F3'},
            'Slayers': {'color': '#FF5722'},
            'Dungeons': {'color': '#9C27B0'},
            # ... more sheet configurations
        }
    
    def create_workbook(self, processed_data: Dict[str, Any]) -> bytes:
        """Generate complete Excel workbook with all data sheets"""
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Create formatted sheets for each data category
            self._create_profile_sheet(writer, processed_data)
            self._create_skills_sheet(writer, processed_data)
            self._create_inventories_sheet(writer, processed_data)
            # ... additional sheets
        
        return output.getvalue()
    
    def _create_skills_sheet(self, writer, data):
        """Create formatted skills sheet with charts"""
        if 'skills' in data:
            df = data['skills']
            df.to_excel(writer, sheet_name='Skills', index=False)
            
            # Add formatting and charts
            worksheet = writer.sheets['Skills']
            self._apply_skill_formatting(worksheet, df)
