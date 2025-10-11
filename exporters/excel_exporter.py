import pandas as pd
import io
from typing import Dict, Any
from datetime import datetime

class ExcelExporter:
    """Export processed SkyBlock data to Excel format with multiple sheets"""
    
    def __init__(self, processed_data: Dict[str, Any]):
        self.processed_data = processed_data
        self.workbook_buffer = io.BytesIO()
    
    def create_workbook(self) -> bytes:
        """Create a comprehensive Excel workbook with all data sheets"""
        with pd.ExcelWriter(self.workbook_buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            
            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            number_format = workbook.add_format({'num_format': '#,##0'})
            percent_format = workbook.add_format({'num_format': '0.00%'})
            date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})
            
            # Create sheets for each data category
            self._create_profile_overview_sheet(writer, header_format, date_format)
            self._create_skills_sheet(writer, header_format, number_format, percent_format)
            self._create_slayers_sheet(writer, header_format, number_format)
            self._create_dungeons_sheet(writer, header_format, number_format)
            self._create_inventory_sheet(writer, header_format, number_format)
            self._create_collections_sheet(writer, header_format, number_format)
            self._create_pets_sheet(writer, header_format, number_format)
            self._create_networth_sheet(writer, header_format, number_format)
            self._create_summary_sheet(writer, header_format, number_format)
        
        self.workbook_buffer.seek(0)
        return self.workbook_buffer.getvalue()
    
    def _create_profile_overview_sheet(self, writer, header_format, date_format):
        """Create profile overview sheet"""
        if 'profile_info' not in self.processed_data:
            return
        
        profile_data = self.processed_data['profile_info']['data']
        df = pd.DataFrame(profile_data)
        
        df.to_excel(writer, sheet_name='Profile Overview', index=False)
        worksheet = writer.sheets['Profile Overview']
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_len + 2, 50))
    
    def _create_skills_sheet(self, writer, header_format, number_format, percent_format):
        """Create skills data sheet with formatting"""
        if 'skills' not in self.processed_data:
            return
        
        skills_data = self.processed_data['skills']['data']
        df = pd.DataFrame(skills_data)
        
        df.to_excel(writer, sheet_name='Skills', index=False)
        worksheet = writer.sheets['Skills']
        
        # Apply header formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Apply number formatting to specific columns
        if 'xp' in df.columns:
            xp_col = df.columns.get_loc('xp')
            worksheet.set_column(xp_col, xp_col, 15, number_format)
        
        if 'xp_to_next' in df.columns:
            xp_next_col = df.columns.get_loc('xp_to_next')
            worksheet.set_column(xp_next_col, xp_next_col, 15, number_format)
        
        if 'progress_percent' in df.columns:
            progress_col = df.columns.get_loc('progress_percent')
            worksheet.set_column(progress_col, progress_col, 12, percent_format)
        
        # Add skill average at the bottom
        last_row = len(df) + 2
        skill_avg = self.processed_data['skills'].get('average', 0)
        worksheet.write(last_row, 0, 'Skill Average:', header_format)
        worksheet.write(last_row, 1, skill_avg, number_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_len + 2, 20))
    
    def _create_slayers_sheet(self, writer, header_format, number_format):
        """Create slayers data sheet"""
        if 'slayers' not in self.processed_data:
            return
        
        slayers_data = self.processed_data['slayers']['data']
        df = pd.DataFrame(slayers_data)
        
        df.to_excel(writer, sheet_name='Slayers', index=False)
        worksheet = writer.sheets['Slayers']
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Format XP column
        if 'xp' in df.columns:
            xp_col = df.columns.get_loc('xp')
            worksheet.set_column(xp_col, xp_col, 15, number_format)
        
        # Format kill columns
        kill_columns = [col for col in df.columns if 'kills' in col]
        for col in kill_columns:
            col_idx = df.columns.get_loc(col)
            worksheet.set_column(col_idx, col_idx, 12, number_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_len + 2, 18))
    
    def _create_dungeons_sheet(self, writer, header_format, number_format):
        """Create dungeons data sheet"""
        if 'dungeons' not in self.processed_data:
            return
        
        dungeons_data = self.processed_data['dungeons']['data']
        df = pd.DataFrame(dungeons_data)
        
        df.to_excel(writer, sheet_name='Dungeons', index=False)
        worksheet = writer.sheets['Dungeons']
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Format XP column
        if 'xp' in df.columns:
            xp_col = df.columns.get_loc('xp')
            worksheet.set_column(xp_col, xp_col, 15, number_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_len + 2, 18))
    
    def _create_inventory_sheet(self, writer, header_format, number_format):
        """Create inventory summary sheet"""
        if 'inventory' not in self.processed_data:
            return
        
        inventory_data = self.processed_data['inventory']['data']
        df = pd.DataFrame(inventory_data)
        
        df.to_excel(writer, sheet_name='Inventory Summary', index=False)
        worksheet = writer.sheets['Inventory Summary']
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Format item count column
        if 'estimated_items' in df.columns:
            items_col = df.columns.get_loc('estimated_items')
            worksheet.set_column(items_col, items_col, 15, number_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_len + 2, 25))
    
    def _create_collections_sheet(self, writer, header_format, number_format):
        """Create collections data sheet"""
        if 'collections' not in self.processed_data:
            return
        
        collections_data = self.processed_data['collections']['data']
        df = pd.DataFrame(collections_data)
        
        df.to_excel(writer, sheet_name='Collections', index=False)
        worksheet = writer.sheets['Collections']
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Format amount column
        if 'amount' in df.columns:
            amount_col = df.columns.get_loc('amount')
            worksheet.set_column(amount_col, amount_col, 15, number_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_len + 2, 20))
    
    def _create_pets_sheet(self, writer, header_format, number_format):
        """Create pets data sheet"""
        if 'pets' not in self.processed_data:
            return
        
        pets_data = self.processed_data['pets']['data']
        if not pets_data:
            # Create empty sheet with headers
            df = pd.DataFrame(columns=['type', 'tier', 'level', 'xp', 'active', 'held_item'])
        else:
            df = pd.DataFrame(pets_data)
        
        df.to_excel(writer, sheet_name='Pets', index=False)
        worksheet = writer.sheets['Pets']
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        if not df.empty:
            # Format XP column
            if 'xp' in df.columns:
                xp_col = df.columns.get_loc('xp')
                worksheet.set_column(xp_col, xp_col, 15, number_format)
            
            # Auto-adjust column widths
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).str.len().max(), len(col))
                worksheet.set_column(i, i, min(max_len + 2, 18))
    
    def _create_networth_sheet(self, writer, header_format, number_format):
        """Create networth data sheet"""
        if 'networth' not in self.processed_data:
            return
        
        networth_data = self.processed_data['networth']['data']
        df = pd.DataFrame(networth_data)
        
        df.to_excel(writer, sheet_name='Networth', index=False)
        worksheet = writer.sheets['Networth']
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Format coin columns
        coin_columns = ['purse', 'bank', 'total']
        for col in coin_columns:
            if col in df.columns:
                col_idx = df.columns.get_loc(col)
                worksheet.set_column(col_idx, col_idx, 15, number_format)
        
        # Add total networth at bottom
        last_row = len(df) + 2
        total_networth = self.processed_data['networth'].get('total', 0)
        worksheet.write(last_row, 0, 'Total Networth:', header_format)
        worksheet.write(last_row, 1, total_networth, number_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_len + 2, 18))
    
    def _create_summary_sheet(self, writer, header_format, number_format):
        """Create a summary sheet with key statistics"""
        summary_data = []
        
        # Profile info
        if 'profile_info' in self.processed_data:
            profile_summary = self.processed_data['profile_info']['summary']
            summary_data.append({
                'Category': 'Profile',
                'Metric': 'Profile Name',
                'Value': profile_summary.get('profile_name', 'Unknown')
            })
            summary_data.append({
                'Category': 'Profile',
                'Metric': 'Game Mode',
                'Value': profile_summary.get('game_mode', 'Normal')
            })
        
        # Skills summary
        if 'skills' in self.processed_data:
            skills_summary = self.processed_data['skills']['summary']
            summary_data.append({
                'Category': 'Skills',
                'Metric': 'Skill Average',
                'Value': f"{skills_summary.get('skill_average', 0):.2f}"
            })
            summary_data.append({
                'Category': 'Skills',
                'Metric': 'Maxed Skills',
                'Value': skills_summary.get('maxed_skills', 0)
            })
        
        # Slayers summary
        if 'slayers' in self.processed_data:
            slayers_summary = self.processed_data['slayers']['summary']
            summary_data.append({
                'Category': 'Slayers',
                'Metric': 'Total Slayer XP',
                'Value': slayers_summary.get('total_slayer_xp', 0)
            })
            summary_data.append({
                'Category': 'Slayers',
                'Metric': 'Total Boss Kills',
                'Value': slayers_summary.get('total_kills', 0)
            })
        
        # Networth summary
        if 'networth' in self.processed_data:
            networth_summary = self.processed_data['networth']['summary']
            summary_data.append({
                'Category': 'Networth',
                'Metric': 'Liquid Coins',
                'Value': networth_summary.get('liquid_coins', 0)
            })
        
        # Collections summary
        if 'collections' in self.processed_data:
            collections_summary = self.processed_data['collections']['summary']
            summary_data.append({
                'Category': 'Collections',
                'Metric': 'Total Collections',
                'Value': collections_summary.get('total_collections', 0)
            })
            summary_data.append({
                'Category': 'Collections',
                'Metric': 'Maxed Collections',
                'Value': collections_summary.get('maxed_collections', 0)
            })
        
        # Pets summary
        if 'pets' in self.processed_data:
            pets_summary = self.processed_data['pets']['summary']
            summary_data.append({
                'Category': 'Pets',
                'Metric': 'Total Pets',
                'Value': pets_summary.get('total_pets', 0)
            })
            summary_data.append({
                'Category': 'Pets',
                'Metric': 'Legendary Pets',
                'Value': pets_summary.get('legendary_pets', 0)
            })
        
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Summary', index=False)
        worksheet = writer.sheets['Summary']
        
        # Apply formatting
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Auto-adjust column widths
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).str.len().max(), len(col))
            worksheet.set_column(i, i, min(max_len + 2, 25))
        
        # Add export timestamp
        timestamp_row = len(df) + 3
        worksheet.write(timestamp_row, 0, 'Exported on:', header_format)
        worksheet.write(timestamp_row, 1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))