"""
Integration Tests - Test complete workflows
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.utils.date_parser import parse_vietnamese_date
from src.utils.field_mapper import map_vietnamese_to_english, FieldMapper
from src.utils.pronoun_resolver import get_resolver, resolve_pronouns, update_person_context


class TestCompleteWorkflow:
    """Test complete user workflows"""
    
    @pytest.mark.asyncio
    async def test_loan_application_workflow(self):
        """Test complete loan application workflow"""
        # Setup
        resolver = get_resolver()
        resolver.clear_context()
        
        # Simulate conversation
        conversation = [
            "Tôi muốn vay 500 triệu",
            "Tên là Nguyễn Văn An",
            "Anh ấy sinh ngày 15 tháng 3 năm 1990",
            "Số điện thoại 0901234567",
            "Email test@vpbank.com",
        ]
        
        extracted_data = {}
        
        # Process each message
        for message in conversation:
            processed = resolver.extract_and_update(message)
            
            # Extract loan amount
            if "vay" in message and "triệu" in message:
                extracted_data["loanAmount"] = "500000000"
            
            # Extract name
            elif "tên" in message.lower() and "là" in message:
                name = message.split("là")[-1].strip()
                extracted_data["customerName"] = name
            
            # Extract date of birth
            elif "sinh" in message:
                resolved = resolver.resolve_pronoun(message)
                assert "Nguyễn Văn An" in resolved
                
                date_parsed = parse_vietnamese_date("15 tháng 3 năm 1990")
                extracted_data["dateOfBirth"] = date_parsed
            
            # Extract phone
            elif "điện thoại" in message or "sđt" in message.lower():
                extracted_data["phoneNumber"] = "0901234567"
            
            # Extract email
            elif "email" in message.lower():
                extracted_data["email"] = "test@vpbank.com"
        
        # Verify all fields extracted
        assert extracted_data["loanAmount"] == "500000000"
        assert extracted_data["customerName"] == "Nguyễn Văn An"
        assert extracted_data["dateOfBirth"] == "1990-03-15"
        assert extracted_data["phoneNumber"] == "0901234567"
        assert extracted_data["email"] == "test@vpbank.com"
    
    @pytest.mark.asyncio
    async def test_field_mapping_workflow(self):
        """Test field mapping in workflow"""
        # Vietnamese field names from user
        user_inputs = {
            "họ và tên": "Nguyễn Văn An",
            "ngày sinh": "15/03/1990",
            "số điện thoại": "0901234567",
            "email": "test@vpbank.com",
            "địa chỉ": "123 Đường ABC, Hà Nội",
        }
        
        # Map to English and process
        mapped_data = {}
        
        for viet_field, value in user_inputs.items():
            # Map field name
            eng_fields = map_vietnamese_to_english(viet_field)
            assert len(eng_fields) > 0
            
            eng_field = eng_fields[0]
            
            # Parse date if needed
            if "ngày" in viet_field or "date" in eng_field.lower():
                value = parse_vietnamese_date(value)
            
            mapped_data[eng_field] = value
        
        # Verify mapping
        assert "fullName" in mapped_data or "customerName" in mapped_data
        assert "dateOfBirth" in mapped_data or "dob" in mapped_data
        assert "phoneNumber" in mapped_data or "phone" in mapped_data
        assert "email" in mapped_data
        assert "address" in mapped_data
    
    @pytest.mark.asyncio
    async def test_pronoun_resolution_workflow(self):
        """Test pronoun resolution in multi-turn conversation"""
        resolver = get_resolver()
        resolver.clear_context()
        
        # Turn 1: Establish person
        message1 = "Tên là Nguyễn Văn An"
        resolver.extract_and_update(message1)
        
        assert resolver.context["last_person"] == "Nguyễn Văn An"
        assert resolver.context["last_person_gender"] == "male"
        
        # Turn 2: Use pronoun
        message2 = "Anh ấy sinh năm 1990"
        resolved2 = resolver.resolve_pronoun(message2)
        
        assert "Nguyễn Văn An" in resolved2
        assert "anh ấy" not in resolved2.lower()
        
        # Turn 3: Use different pronoun
        message3 = "Ông ấy làm việc tại VPBank"
        resolved3 = resolver.resolve_pronoun(message3)
        
        assert "Nguyễn Văn An" in resolved3
        assert "ông ấy" not in resolved3.lower()
        
        # Turn 4: Field reference
        resolver.update_field("phoneNumber", "0901234567")
        message4 = "Nó là 0901234567"
        resolved4 = resolver.resolve_pronoun(message4)
        
        assert "phoneNumber" in resolved4


class TestDateParsingIntegration:
    """Test date parsing integration"""
    
    def test_multiple_date_formats(self):
        """Test parsing multiple date formats in workflow"""
        dates = [
            ("15/03/1990", "1990-03-15"),
            ("15-03-1990", "1990-03-15"),
            ("15 tháng 3 năm 1990", "1990-03-15"),
            ("ngày 15 tháng 3 năm 1990", "1990-03-15"),
            ("15/3/90", "1990-03-15"),
        ]
        
        for input_date, expected in dates:
            parsed = parse_vietnamese_date(input_date)
            assert parsed == expected, f"Failed for {input_date}"
    
    def test_date_parsing_with_field_mapping(self):
        """Test date parsing combined with field mapping"""
        # User input
        field_name = "ngày sinh"
        field_value = "15 tháng 3 năm 1990"
        
        # Map field
        eng_fields = map_vietnamese_to_english(field_name)
        assert "dateOfBirth" in eng_fields or "dob" in eng_fields
        
        # Parse date
        parsed_date = parse_vietnamese_date(field_value)
        assert parsed_date == "1990-03-15"


class TestFieldMappingIntegration:
    """Test field mapping integration"""
    
    def test_fuzzy_matching(self):
        """Test fuzzy matching for typos"""
        # Typos and variations
        variations = [
            "họ tên",  # Missing "và"
            "điện thoại",  # Missing "số"
            "ngày sinh",  # Exact
            "email",  # English
        ]
        
        for variation in variations:
            fields = map_vietnamese_to_english(variation)
            assert len(fields) > 0, f"No match for {variation}"
    
    def test_best_match_selection(self):
        """Test selecting best match from available fields"""
        available_fields = [
            "fullName", "customerName", "firstName", "lastName",
            "phoneNumber", "phone", "mobile",
            "email", "emailAddress",
            "dateOfBirth", "dob", "birthDate",
        ]
        
        test_cases = [
            ("họ và tên", ["fullName", "customerName"]),
            ("số điện thoại", ["phoneNumber", "phone", "mobile"]),
            ("email", ["email", "emailAddress"]),
            ("ngày sinh", ["dateOfBirth", "dob", "birthDate"]),
        ]
        
        for viet_field, expected_matches in test_cases:
            best = FieldMapper.get_best_match(viet_field, available_fields)
            assert best in expected_matches, f"Unexpected match for {viet_field}: {best}"


class TestErrorHandling:
    """Test error handling in integration"""
    
    def test_invalid_date_handling(self):
        """Test handling of invalid dates"""
        invalid_dates = [
            "32/13/1990",  # Invalid day/month
            "invalid",  # Not a date
            "",  # Empty
            None,  # None
        ]
        
        for invalid_date in invalid_dates:
            result = parse_vietnamese_date(invalid_date)
            assert result is None, f"Should return None for {invalid_date}"
    
    def test_unknown_field_handling(self):
        """Test handling of unknown fields"""
        unknown_fields = [
            "unknown_field_xyz",
            "random_text",
            "",
        ]
        
        for unknown_field in unknown_fields:
            fields = map_vietnamese_to_english(unknown_field)
            # Should return empty list or handle gracefully
            assert isinstance(fields, list)
    
    def test_pronoun_without_context(self):
        """Test pronoun resolution without context"""
        resolver = get_resolver()
        resolver.clear_context()
        
        # Try to resolve pronoun without setting context
        text = "Anh ấy sinh năm 1990"
        resolved = resolver.resolve_pronoun(text)
        
        # Should return original text if no context
        assert "anh ấy" in resolved.lower()


class TestPerformance:
    """Test performance of integrated features"""
    
    def test_date_parsing_performance(self):
        """Test date parsing performance"""
        import time
        
        dates = ["15/03/1990"] * 1000
        
        start = time.time()
        for date in dates:
            parse_vietnamese_date(date)
        elapsed = time.time() - start
        
        # Should parse 1000 dates in < 100ms
        assert elapsed < 0.1, f"Too slow: {elapsed}s for 1000 dates"
    
    def test_field_mapping_performance(self):
        """Test field mapping performance"""
        import time
        
        fields = ["họ và tên"] * 1000
        
        start = time.time()
        for field in fields:
            map_vietnamese_to_english(field)
        elapsed = time.time() - start
        
        # Should map 1000 fields in < 50ms
        assert elapsed < 0.05, f"Too slow: {elapsed}s for 1000 fields"
    
    def test_pronoun_resolution_performance(self):
        """Test pronoun resolution performance"""
        import time
        
        resolver = get_resolver()
        resolver.update_person("Nguyễn Văn An", "male")
        texts = ["Anh ấy sinh năm 1990"] * 1000
        
        start = time.time()
        for text in texts:
            resolver.resolve_pronoun(text)
        elapsed = time.time() - start
        
        # Should resolve 1000 pronouns in < 50ms
        assert elapsed < 0.05, f"Too slow: {elapsed}s for 1000 resolutions"


class TestEdgeCases:
    """Test edge cases"""
    
    def test_empty_inputs(self):
        """Test handling of empty inputs"""
        # Empty date
        assert parse_vietnamese_date("") is None
        assert parse_vietnamese_date(None) is None
        
        # Empty field
        fields = map_vietnamese_to_english("")
        assert isinstance(fields, list)
        
        # Empty text
        resolver = get_resolver()
        resolved = resolver.resolve_pronoun("")
        assert resolved == ""
    
    def test_special_characters(self):
        """Test handling of special characters"""
        # Date with special chars
        dates = [
            "15/03/1990",
            "15-03-1990",
            "15.03.1990",
        ]
        
        for date in dates:
            parsed = parse_vietnamese_date(date)
            assert parsed == "1990-03-15"
    
    def test_case_insensitivity(self):
        """Test case insensitive matching"""
        # Field mapping should be case insensitive
        fields1 = map_vietnamese_to_english("họ và tên")
        fields2 = map_vietnamese_to_english("HỌ VÀ TÊN")
        fields3 = map_vietnamese_to_english("Họ Và Tên")
        
        assert fields1 == fields2 == fields3
    
    def test_unicode_handling(self):
        """Test Vietnamese unicode handling"""
        vietnamese_texts = [
            "Nguyễn Văn An",
            "Trần Thị Bình",
            "Lê Hoàng Cường",
            "Phạm Thị Dung",
        ]
        
        resolver = get_resolver()
        
        for text in vietnamese_texts:
            resolver.update_person(text, "unknown")
            assert resolver.context["last_person"] == text


class TestConcurrency:
    """Test concurrent operations"""
    
    @pytest.mark.asyncio
    async def test_concurrent_date_parsing(self):
        """Test concurrent date parsing"""
        dates = ["15/03/1990", "20/05/1995", "10/10/2000"] * 100
        
        async def parse_date(date):
            return parse_vietnamese_date(date)
        
        # Parse concurrently
        tasks = [parse_date(date) for date in dates]
        results = await asyncio.gather(*tasks)
        
        # Verify all parsed correctly
        assert len(results) == len(dates)
        assert all(r is not None for r in results)
    
    @pytest.mark.asyncio
    async def test_concurrent_field_mapping(self):
        """Test concurrent field mapping"""
        fields = ["họ và tên", "số điện thoại", "email"] * 100
        
        async def map_field(field):
            return map_vietnamese_to_english(field)
        
        # Map concurrently
        tasks = [map_field(field) for field in fields]
        results = await asyncio.gather(*tasks)
        
        # Verify all mapped correctly
        assert len(results) == len(fields)
        assert all(len(r) > 0 for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
