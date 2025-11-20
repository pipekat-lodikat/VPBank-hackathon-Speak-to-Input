"""
Vietnamese Date Parser
Parses various Vietnamese date formats to standard format
"""

import re
from datetime import datetime
from typing import Optional, Dict


class VietnameseDateParser:
    """Parse Vietnamese date formats to ISO format"""
    
    # Month names in Vietnamese
    MONTH_NAMES = {
        "một": 1, "hai": 2, "ba": 3, "bốn": 4, "năm": 5, "sáu": 6,
        "bảy": 7, "tám": 8, "chín": 9, "mười": 10, "mười một": 11, "mười hai": 12,
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6,
        "7": 7, "8": 8, "9": 9, "10": 10, "11": 11, "12": 12,
    }
    
    @staticmethod
    def parse(date_str: str) -> Optional[str]:
        """
        Parse Vietnamese date string to ISO format (YYYY-MM-DD)
        
        Supported formats:
        - "15/03/1990"
        - "15-03-1990"
        - "15.03.1990"
        - "15 tháng 3 năm 1990"
        - "ngày 15 tháng 3 năm 1990"
        - "15/3/90"
        - "15-3-90"
        
        Args:
            date_str: Vietnamese date string
            
        Returns:
            ISO format date string (YYYY-MM-DD) or None if parsing fails
        """
        if not date_str:
            return None
            
        date_str = date_str.strip().lower()
        
        # Try different patterns
        parsers = [
            VietnameseDateParser._parse_slash_format,
            VietnameseDateParser._parse_dash_format,
            VietnameseDateParser._parse_dot_format,
            VietnameseDateParser._parse_vietnamese_format,
            VietnameseDateParser._parse_short_year,
        ]
        
        for parser in parsers:
            result = parser(date_str)
            if result:
                return result
                
        return None
    
    @staticmethod
    def _parse_slash_format(date_str: str) -> Optional[str]:
        """Parse DD/MM/YYYY format"""
        pattern = r'(\d{1,2})/(\d{1,2})/(\d{4})'
        match = re.search(pattern, date_str)
        if match:
            day, month, year = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
        return None
    
    @staticmethod
    def _parse_dash_format(date_str: str) -> Optional[str]:
        """Parse DD-MM-YYYY format"""
        pattern = r'(\d{1,2})-(\d{1,2})-(\d{4})'
        match = re.search(pattern, date_str)
        if match:
            day, month, year = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
        return None
    
    @staticmethod
    def _parse_dot_format(date_str: str) -> Optional[str]:
        """Parse DD.MM.YYYY format"""
        pattern = r'(\d{1,2})\.(\d{1,2})\.(\d{4})'
        match = re.search(pattern, date_str)
        if match:
            day, month, year = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
        return None
    
    @staticmethod
    def _parse_vietnamese_format(date_str: str) -> Optional[str]:
        """Parse 'ngày DD tháng MM năm YYYY' format"""
        # Pattern: ngày 15 tháng 3 năm 1990
        pattern = r'(?:ngày\s+)?(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})'
        match = re.search(pattern, date_str)
        if match:
            day, month, year = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
        return None
    
    @staticmethod
    def _parse_short_year(date_str: str) -> Optional[str]:
        """Parse DD/MM/YY format (2-digit year)"""
        pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{2})(?!\d)'
        match = re.search(pattern, date_str)
        if match:
            day, month, year = match.groups()
            # Convert 2-digit year to 4-digit
            year_int = int(year)
            if year_int >= 0 and year_int <= 30:
                full_year = 2000 + year_int
            else:
                full_year = 1900 + year_int
            
            try:
                date_obj = datetime(full_year, int(month), int(day))
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                return None
        return None
    
    @staticmethod
    def parse_to_display(date_str: str, format: str = "DD/MM/YYYY") -> Optional[str]:
        """
        Parse and convert to display format
        
        Args:
            date_str: Vietnamese date string
            format: Output format (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD)
            
        Returns:
            Formatted date string
        """
        iso_date = VietnameseDateParser.parse(date_str)
        if not iso_date:
            return None
            
        date_obj = datetime.strptime(iso_date, '%Y-%m-%d')
        
        if format == "DD/MM/YYYY":
            return date_obj.strftime('%d/%m/%Y')
        elif format == "MM/DD/YYYY":
            return date_obj.strftime('%m/%d/%Y')
        elif format == "YYYY-MM-DD":
            return iso_date
        else:
            return iso_date


# Convenience function
def parse_vietnamese_date(date_str: str) -> Optional[str]:
    """
    Parse Vietnamese date string to ISO format
    
    Args:
        date_str: Vietnamese date string
        
    Returns:
        ISO format date string (YYYY-MM-DD)
    """
    return VietnameseDateParser.parse(date_str)
