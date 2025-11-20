"""
Test suite for utility modules
"""

import pytest
from src.utils.date_parser import VietnameseDateParser, parse_vietnamese_date
from src.utils.field_mapper import FieldMapper, map_vietnamese_to_english
from src.utils.pronoun_resolver import PronounResolver, resolve_pronouns


class TestVietnameseDateParser:
    """Test Vietnamese date parser"""
    
    def test_parse_slash_format(self):
        """Test DD/MM/YYYY format"""
        assert VietnameseDateParser.parse("15/03/1990") == "1990-03-15"
        assert VietnameseDateParser.parse("1/1/2000") == "2000-01-01"
        assert VietnameseDateParser.parse("31/12/1999") == "1999-12-31"
    
    def test_parse_dash_format(self):
        """Test DD-MM-YYYY format"""
        assert VietnameseDateParser.parse("15-03-1990") == "1990-03-15"
        assert VietnameseDateParser.parse("1-1-2000") == "2000-01-01"
    
    def test_parse_dot_format(self):
        """Test DD.MM.YYYY format"""
        assert VietnameseDateParser.parse("15.03.1990") == "1990-03-15"
        assert VietnameseDateParser.parse("1.1.2000") == "2000-01-01"
    
    def test_parse_vietnamese_format(self):
        """Test 'ngày DD tháng MM năm YYYY' format"""
        assert VietnameseDateParser.parse("ngày 15 tháng 3 năm 1990") == "1990-03-15"
        assert VietnameseDateParser.parse("15 tháng 3 năm 1990") == "1990-03-15"
        assert VietnameseDateParser.parse("ngày 1 tháng 1 năm 2000") == "2000-01-01"
    
    def test_parse_short_year(self):
        """Test DD/MM/YY format"""
        assert VietnameseDateParser.parse("15/03/90") == "1990-03-15"
        assert VietnameseDateParser.parse("15/03/25") == "2025-03-15"
        assert VietnameseDateParser.parse("15-03-90") == "1990-03-15"
    
    def test_parse_invalid_date(self):
        """Test invalid dates"""
        assert VietnameseDateParser.parse("32/13/1990") is None
        assert VietnameseDateParser.parse("invalid") is None
        assert VietnameseDateParser.parse("") is None
        assert VietnameseDateParser.parse(None) is None
    
    def test_parse_to_display(self):
        """Test conversion to display format"""
        assert VietnameseDateParser.parse_to_display("15/03/1990", "DD/MM/YYYY") == "15/03/1990"
        assert VietnameseDateParser.parse_to_display("15/03/1990", "MM/DD/YYYY") == "03/15/1990"
        assert VietnameseDateParser.parse_to_display("15/03/1990", "YYYY-MM-DD") == "1990-03-15"
    
    def test_convenience_function(self):
        """Test convenience function"""
        assert parse_vietnamese_date("15/03/1990") == "1990-03-15"


class TestFieldMapper:
    """Test field mapper"""
    
    def test_find_english_fields_exact_match(self):
        """Test exact Vietnamese to English mapping"""
        fields = FieldMapper.find_english_fields("họ và tên")
        assert "fullName" in fields
        assert "customerName" in fields
        
        fields = FieldMapper.find_english_fields("số điện thoại")
        assert "phoneNumber" in fields
        assert "phone" in fields
    
    def test_find_english_fields_fuzzy_match(self):
        """Test fuzzy matching"""
        fields = FieldMapper.find_english_fields("họ tên")
        assert len(fields) > 0
        
        fields = FieldMapper.find_english_fields("điện thoại")
        assert len(fields) > 0
    
    def test_find_vietnamese_name(self):
        """Test English to Vietnamese mapping"""
        mapper = FieldMapper()
        viet_name = FieldMapper.find_vietnamese_name("phoneNumber")
        assert viet_name is not None
        
        viet_name = FieldMapper.find_vietnamese_name("email")
        assert viet_name is not None
    
    def test_get_best_match(self):
        """Test best match selection"""
        available = ["fullName", "phoneNumber", "email", "address"]
        
        match = FieldMapper.get_best_match("họ và tên", available)
        assert match == "fullName"
        
        match = FieldMapper.get_best_match("số điện thoại", available)
        assert match == "phoneNumber"
        
        match = FieldMapper.get_best_match("email", available)
        assert match == "email"
    
    def test_get_best_match_no_match(self):
        """Test when no match found"""
        available = ["someField", "anotherField"]
        match = FieldMapper.get_best_match("họ và tên", available)
        assert match is None
    
    def test_add_custom_mapping(self):
        """Test adding custom mapping"""
        FieldMapper.add_mapping("tên riêng", ["customName", "specialName"])
        fields = FieldMapper.find_english_fields("tên riêng")
        assert "customName" in fields
        assert "specialName" in fields
    
    def test_convenience_function(self):
        """Test convenience function"""
        fields = map_vietnamese_to_english("họ và tên")
        assert len(fields) > 0


class TestPronounResolver:
    """Test pronoun resolver"""
    
    def test_update_person(self):
        """Test updating person context"""
        resolver = PronounResolver()
        resolver.update_person("Nguyễn Văn An", "male")
        
        context = resolver.get_context()
        assert context["last_person"] == "Nguyễn Văn An"
        assert context["last_person_gender"] == "male"
    
    def test_resolve_male_pronoun(self):
        """Test resolving male pronouns"""
        resolver = PronounResolver()
        resolver.update_person("Nguyễn Văn An", "male")
        
        resolved = resolver.resolve_pronoun("Anh ấy sinh năm 1990")
        assert "Nguyễn Văn An" in resolved
        
        resolved = resolver.resolve_pronoun("Ông ấy làm việc tại VPBank")
        assert "Nguyễn Văn An" in resolved
    
    def test_resolve_female_pronoun(self):
        """Test resolving female pronouns"""
        resolver = PronounResolver()
        resolver.update_person("Nguyễn Thị Lan", "female")
        
        resolved = resolver.resolve_pronoun("Cô ấy sinh năm 1990")
        assert "Nguyễn Thị Lan" in resolved
        
        resolved = resolver.resolve_pronoun("Chị ấy làm việc tại VPBank")
        assert "Nguyễn Thị Lan" in resolved
    
    def test_resolve_neutral_pronoun(self):
        """Test resolving neutral pronouns"""
        resolver = PronounResolver()
        resolver.update_field("phoneNumber", "0901234567")
        
        resolved = resolver.resolve_pronoun("Nó là 0901234567")
        assert "phoneNumber" in resolved
    
    def test_extract_and_update_person(self):
        """Test extracting person from text"""
        resolver = PronounResolver()
        text = "Tên là Nguyễn Văn An"
        resolver.extract_and_update(text)
        
        context = resolver.get_context()
        assert context["last_person"] is not None
    
    def test_detect_gender_from_name(self):
        """Test gender detection"""
        resolver = PronounResolver()
        
        # Male name
        gender = resolver._detect_gender("Nguyễn Văn An", "")
        assert gender == "male"
        
        # Female name
        gender = resolver._detect_gender("Nguyễn Thị Lan", "")
        assert gender == "female"
    
    def test_detect_gender_from_context(self):
        """Test gender detection from context"""
        resolver = PronounResolver()
        
        gender = resolver._detect_gender("An", "Anh An làm việc")
        assert gender == "male"
        
        gender = resolver._detect_gender("Lan", "Chị Lan làm việc")
        assert gender == "female"
    
    def test_clear_context(self):
        """Test clearing context"""
        resolver = PronounResolver()
        resolver.update_person("Test", "male")
        resolver.clear_context()
        
        context = resolver.get_context()
        assert context["last_person"] is None
        assert context["last_person_gender"] is None
    
    def test_convenience_function(self):
        """Test convenience function"""
        from src.utils.pronoun_resolver import update_person_context
        
        update_person_context("Nguyễn Văn An", "male")
        resolved = resolve_pronouns("Anh ấy sinh năm 1990")
        assert "Nguyễn Văn An" in resolved


class TestIntegration:
    """Test integration between utilities"""
    
    def test_date_parser_with_field_mapper(self):
        """Test using date parser with field mapper"""
        # Map Vietnamese field name
        fields = map_vietnamese_to_english("ngày sinh")
        assert "dateOfBirth" in fields or "dob" in fields
        
        # Parse Vietnamese date
        date = parse_vietnamese_date("15/03/1990")
        assert date == "1990-03-15"
    
    def test_pronoun_resolver_with_field_mapper(self):
        """Test pronoun resolver with field mapper"""
        resolver = PronounResolver()
        
        # Update context with Vietnamese field name
        viet_field = "số điện thoại"
        eng_fields = map_vietnamese_to_english(viet_field)
        resolver.update_field(eng_fields[0] if eng_fields else viet_field)
        
        # Resolve pronoun
        resolved = resolver.resolve_pronoun("Nó là 0901234567")
        assert eng_fields[0] in resolved if eng_fields else viet_field in resolved
    
    def test_complete_workflow(self):
        """Test complete workflow with all utilities"""
        resolver = PronounResolver()
        
        # Step 1: User says name
        text1 = "Tên là Nguyễn Văn An"
        resolver.extract_and_update(text1)
        
        # Step 2: User uses pronoun
        text2 = "Anh ấy sinh ngày 15 tháng 3 năm 1990"
        resolved = resolver.resolve_pronoun(text2)
        assert "Nguyễn Văn An" in resolved
        
        # Step 3: Parse date
        date = parse_vietnamese_date("15 tháng 3 năm 1990")
        assert date == "1990-03-15"
        
        # Step 4: Map field
        fields = map_vietnamese_to_english("ngày sinh")
        assert len(fields) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
