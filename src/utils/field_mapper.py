"""
Field Mapper - Map Vietnamese field names to English form fields
"""

from typing import List, Optional, Dict
from difflib import get_close_matches


class FieldMapper:
    """Map Vietnamese field names to English form field names"""
    
    # Vietnamese to English field mappings
    FIELD_MAPPINGS = {
        # Personal Information
        "họ và tên": ["fullName", "customerName", "name", "fullname"],
        "họ tên": ["fullName", "customerName", "name"],
        "tên": ["firstName", "name", "customerName"],
        "họ": ["lastName", "surname"],
        "tên đệm": ["middleName"],
        
        # Contact Information
        "số điện thoại": ["phoneNumber", "phone", "mobile", "mobileNumber"],
        "điện thoại": ["phoneNumber", "phone", "mobile"],
        "sđt": ["phoneNumber", "phone"],
        "email": ["email", "emailAddress", "mail"],
        "địa chỉ": ["address", "location", "fullAddress"],
        "địa chỉ thường trú": ["permanentAddress", "address"],
        "địa chỉ tạm trú": ["temporaryAddress", "currentAddress"],
        
        # Identification
        "căn cước công dân": ["customerId", "idNumber", "nationalId", "cccd"],
        "cccd": ["customerId", "idNumber", "nationalId"],
        "cmnd": ["customerId", "idNumber", "nationalId"],
        "số cccd": ["customerId", "idNumber"],
        "số cmnd": ["customerId", "idNumber"],
        
        # Date Information
        "ngày sinh": ["dateOfBirth", "dob", "birthDate", "birthday"],
        "sinh nhật": ["dateOfBirth", "dob", "birthday"],
        "ngày cấp": ["issueDate", "issuedDate"],
        "ngày hết hạn": ["expiryDate", "expiredDate"],
        
        # Loan Information
        "số tiền": ["amount", "loanAmount", "money"],
        "số tiền vay": ["loanAmount", "amount"],
        "khoản vay": ["loanAmount", "amount"],
        "kỳ hạn": ["loanTerm", "term", "duration"],
        "thời hạn": ["loanTerm", "term", "duration"],
        "mục đích vay": ["loanPurpose", "purpose"],
        "lý do vay": ["loanPurpose", "purpose", "reason"],
        
        # Employment Information
        "nghề nghiệp": ["occupation", "job", "profession"],
        "công việc": ["occupation", "job"],
        "thu nhập": ["income", "salary", "monthlyIncome"],
        "lương": ["salary", "income", "monthlyIncome"],
        "công ty": ["company", "employer", "companyName"],
        "nơi làm việc": ["company", "employer", "workplace"],
        
        # Bank Information
        "số tài khoản": ["accountNumber", "bankAccount"],
        "tài khoản": ["accountNumber", "account"],
        "ngân hàng": ["bankName", "bank"],
        "chi nhánh": ["branch", "bankBranch"],
        
        # Other
        "ghi chú": ["note", "notes", "comment", "remarks"],
        "mô tả": ["description", "desc"],
        "trạng thái": ["status", "state"],
    }
    
    # Reverse mapping (English to Vietnamese)
    REVERSE_MAPPINGS = {}
    
    def __init__(self):
        """Initialize field mapper"""
        # Build reverse mappings
        if not FieldMapper.REVERSE_MAPPINGS:
            for viet_name, eng_names in FieldMapper.FIELD_MAPPINGS.items():
                for eng_name in eng_names:
                    if eng_name not in FieldMapper.REVERSE_MAPPINGS:
                        FieldMapper.REVERSE_MAPPINGS[eng_name.lower()] = []
                    FieldMapper.REVERSE_MAPPINGS[eng_name.lower()].append(viet_name)
    
    @staticmethod
    def find_english_fields(vietnamese_name: str) -> List[str]:
        """
        Find possible English field names for a Vietnamese field name
        
        Args:
            vietnamese_name: Vietnamese field name
            
        Returns:
            List of possible English field names
        """
        vietnamese_name = vietnamese_name.strip().lower()
        
        # Direct match
        if vietnamese_name in FieldMapper.FIELD_MAPPINGS:
            return FieldMapper.FIELD_MAPPINGS[vietnamese_name]
        
        # Fuzzy match
        close_matches = get_close_matches(
            vietnamese_name,
            FieldMapper.FIELD_MAPPINGS.keys(),
            n=1,
            cutoff=0.6
        )
        
        if close_matches:
            return FieldMapper.FIELD_MAPPINGS[close_matches[0]]
        
        return []
    
    @staticmethod
    def find_vietnamese_name(english_field: str) -> Optional[str]:
        """
        Find Vietnamese name for an English field name
        
        Args:
            english_field: English field name
            
        Returns:
            Vietnamese field name or None
        """
        english_field = english_field.strip().lower()
        
        if english_field in FieldMapper.REVERSE_MAPPINGS:
            return FieldMapper.REVERSE_MAPPINGS[english_field][0]
        
        return None
    
    @staticmethod
    def get_best_match(vietnamese_name: str, available_fields: List[str]) -> Optional[str]:
        """
        Get best matching English field from available fields
        
        Args:
            vietnamese_name: Vietnamese field name
            available_fields: List of available English field names
            
        Returns:
            Best matching field name or None
        """
        possible_fields = FieldMapper.find_english_fields(vietnamese_name)
        
        if not possible_fields:
            return None
        
        # Find first match in available fields
        available_lower = [f.lower() for f in available_fields]
        
        for possible in possible_fields:
            if possible.lower() in available_lower:
                # Return original case
                idx = available_lower.index(possible.lower())
                return available_fields[idx]
        
        return None
    
    @staticmethod
    def add_mapping(vietnamese_name: str, english_fields: List[str]):
        """
        Add custom field mapping
        
        Args:
            vietnamese_name: Vietnamese field name
            english_fields: List of English field names
        """
        vietnamese_name = vietnamese_name.strip().lower()
        FieldMapper.FIELD_MAPPINGS[vietnamese_name] = english_fields
        
        # Update reverse mappings
        for eng_field in english_fields:
            eng_lower = eng_field.lower()
            if eng_lower not in FieldMapper.REVERSE_MAPPINGS:
                FieldMapper.REVERSE_MAPPINGS[eng_lower] = []
            if vietnamese_name not in FieldMapper.REVERSE_MAPPINGS[eng_lower]:
                FieldMapper.REVERSE_MAPPINGS[eng_lower].append(vietnamese_name)


# Convenience functions
def map_vietnamese_to_english(vietnamese_name: str) -> List[str]:
    """Map Vietnamese field name to English field names"""
    return FieldMapper.find_english_fields(vietnamese_name)


def map_english_to_vietnamese(english_field: str) -> Optional[str]:
    """Map English field name to Vietnamese field name"""
    return FieldMapper.find_vietnamese_name(english_field)
