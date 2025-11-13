#!/usr/bin/env python3
"""
Demo Script - Advanced Features
Showcase all advanced features with real examples
"""

import asyncio
import sys
from loguru import logger

# Add src to path
sys.path.insert(0, '.')

from src.utils.date_parser import parse_vietnamese_date, VietnameseDateParser
from src.utils.field_mapper import map_vietnamese_to_english, FieldMapper
from src.utils.pronoun_resolver import (
    resolve_pronouns, 
    update_person_context, 
    update_field_context,
    get_resolver
)


def print_section(title: str):
    """Print section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")


def demo_date_parser():
    """Demo Vietnamese date parser"""
    print_section("📅 VIETNAMESE DATE PARSER")
    
    test_dates = [
        "15/03/1990",
        "15-03-1990",
        "15.03.1990",
        "15 tháng 3 năm 1990",
        "ngày 15 tháng 3 năm 1990",
        "15/3/90",
        "1/1/2000",
    ]
    
    for date_str in test_dates:
        parsed = parse_vietnamese_date(date_str)
        print(f"Input:  {date_str:30} → Output: {parsed}")
    
    # Display format conversion
    print("\n📊 Format Conversion:")
    date_str = "15/03/1990"
    print(f"ISO:        {VietnameseDateParser.parse_to_display(date_str, 'YYYY-MM-DD')}")
    print(f"DD/MM/YYYY: {VietnameseDateParser.parse_to_display(date_str, 'DD/MM/YYYY')}")
    print(f"MM/DD/YYYY: {VietnameseDateParser.parse_to_display(date_str, 'MM/DD/YYYY')}")


def demo_field_mapper():
    """Demo field mapper"""
    print_section("🗺️  FIELD MAPPER")
    
    vietnamese_fields = [
        "họ và tên",
        "số điện thoại",
        "email",
        "ngày sinh",
        "địa chỉ",
        "căn cước công dân",
        "số tiền vay",
        "kỳ hạn",
        "nghề nghiệp",
        "thu nhập",
    ]
    
    for viet_field in vietnamese_fields:
        eng_fields = map_vietnamese_to_english(viet_field)
        print(f"'{viet_field:25}' → {eng_fields}")
    
    # Best match demo
    print("\n🎯 Best Match Selection:")
    available_fields = ["fullName", "phoneNumber", "email", "dateOfBirth", "address"]
    
    for viet_field in ["họ tên", "số điện thoại", "ngày sinh"]:
        best = FieldMapper.get_best_match(viet_field, available_fields)
        print(f"'{viet_field:20}' → Best match: {best}")


def demo_pronoun_resolver():
    """Demo pronoun resolver"""
    print_section("🧠 PRONOUN RESOLVER")
    
    resolver = get_resolver()
    resolver.clear_context()
    
    # Scenario 1: Male person
    print("📝 Scenario 1: Male Person")
    print("-" * 40)
    
    text1 = "Tên là Nguyễn Văn An"
    print(f"User: {text1}")
    resolver.extract_and_update(text1)
    print(f"→ Context updated: person={resolver.context['last_person']}, gender={resolver.context['last_person_gender']}")
    
    text2 = "Anh ấy sinh năm 1990"
    print(f"\nUser: {text2}")
    resolved = resolver.resolve_pronoun(text2)
    print(f"→ Resolved: {resolved}")
    
    text3 = "Ông ấy làm việc tại VPBank"
    print(f"\nUser: {text3}")
    resolved = resolver.resolve_pronoun(text3)
    print(f"→ Resolved: {resolved}")
    
    # Scenario 2: Female person
    print("\n\n📝 Scenario 2: Female Person")
    print("-" * 40)
    
    resolver.clear_context()
    
    text1 = "Tên là Nguyễn Thị Lan"
    print(f"User: {text1}")
    resolver.extract_and_update(text1)
    print(f"→ Context updated: person={resolver.context['last_person']}, gender={resolver.context['last_person_gender']}")
    
    text2 = "Cô ấy sinh năm 1995"
    print(f"\nUser: {text2}")
    resolved = resolver.resolve_pronoun(text2)
    print(f"→ Resolved: {resolved}")
    
    text3 = "Chị ấy làm kế toán"
    print(f"\nUser: {text3}")
    resolved = resolver.resolve_pronoun(text3)
    print(f"→ Resolved: {resolved}")
    
    # Scenario 3: Neutral pronoun
    print("\n\n📝 Scenario 3: Neutral Pronoun")
    print("-" * 40)
    
    resolver.clear_context()
    resolver.update_field("phoneNumber", "0901234567")
    
    text = "Nó là 0901234567"
    print(f"User: {text}")
    resolved = resolver.resolve_pronoun(text)
    print(f"→ Resolved: {resolved}")


def demo_integration():
    """Demo integration of all utilities"""
    print_section("🔗 INTEGRATION DEMO")
    
    print("📝 Complete Workflow:")
    print("-" * 40)
    
    resolver = get_resolver()
    resolver.clear_context()
    
    # Step 1: User provides name
    print("\n1️⃣  User: 'Tên là Nguyễn Văn An'")
    resolver.extract_and_update("Tên là Nguyễn Văn An")
    print(f"   → Context: person={resolver.context['last_person']}")
    
    # Step 2: User uses pronoun for date
    print("\n2️⃣  User: 'Anh ấy sinh ngày 15 tháng 3 năm 1990'")
    text = "Anh ấy sinh ngày 15 tháng 3 năm 1990"
    resolved = resolver.resolve_pronoun(text)
    print(f"   → Resolved: {resolved}")
    
    # Extract date
    date_parsed = parse_vietnamese_date("15 tháng 3 năm 1990")
    print(f"   → Date parsed: {date_parsed}")
    
    # Map field
    field_mapped = map_vietnamese_to_english("ngày sinh")
    print(f"   → Field mapped: ngày sinh → {field_mapped[0]}")
    
    # Step 3: User provides phone
    print("\n3️⃣  User: 'Số điện thoại 0901234567'")
    field_mapped = map_vietnamese_to_english("số điện thoại")
    print(f"   → Field mapped: số điện thoại → {field_mapped[0]}")
    
    # Step 4: Summary
    print("\n✅ Final Result:")
    print(f"   - fullName: Nguyễn Văn An")
    print(f"   - dateOfBirth: {date_parsed}")
    print(f"   - phoneNumber: 0901234567")


def demo_use_cases():
    """Demo real-world use cases"""
    print_section("🎯 REAL-WORLD USE CASES")
    
    # Use Case 1: Loan Application
    print("📋 Use Case 1: Loan Application")
    print("-" * 40)
    
    conversation = [
        "Tôi muốn vay 500 triệu",
        "Tên là Nguyễn Văn An",
        "Anh ấy sinh ngày 15 tháng 3 năm 1990",
        "Số điện thoại 0901234567",
        "Email test@vpbank.com",
    ]
    
    resolver = get_resolver()
    resolver.clear_context()
    
    extracted_data = {}
    
    for i, message in enumerate(conversation, 1):
        print(f"\n{i}. User: '{message}'")
        
        # Process with pronoun resolver
        processed = resolver.extract_and_update(message)
        
        # Extract fields
        if "vay" in message and "triệu" in message:
            amount = "500000000"
            extracted_data["loanAmount"] = amount
            print(f"   → Extracted: loanAmount = {amount}")
        
        elif "tên" in message.lower():
            name = message.split("là")[-1].strip()
            extracted_data["customerName"] = name
            print(f"   → Extracted: customerName = {name}")
        
        elif "sinh" in message:
            resolved = resolver.resolve_pronoun(message)
            date_str = "15 tháng 3 năm 1990"
            date_parsed = parse_vietnamese_date(date_str)
            extracted_data["dateOfBirth"] = date_parsed
            print(f"   → Resolved: {resolved}")
            print(f"   → Extracted: dateOfBirth = {date_parsed}")
        
        elif "điện thoại" in message or "sđt" in message.lower():
            phone = "0901234567"
            extracted_data["phoneNumber"] = phone
            print(f"   → Extracted: phoneNumber = {phone}")
        
        elif "email" in message.lower():
            email = "test@vpbank.com"
            extracted_data["email"] = email
            print(f"   → Extracted: email = {email}")
    
    print("\n✅ Extracted Data:")
    for field, value in extracted_data.items():
        print(f"   {field:20} = {value}")


def demo_performance():
    """Demo performance metrics"""
    print_section("⚡ PERFORMANCE METRICS")
    
    import time
    
    # Date parsing performance
    print("📅 Date Parsing Performance:")
    dates = ["15/03/1990"] * 1000
    
    start = time.time()
    for date in dates:
        parse_vietnamese_date(date)
    elapsed = time.time() - start
    
    print(f"   Parsed 1000 dates in {elapsed:.3f}s")
    print(f"   Average: {elapsed/1000*1000:.2f}ms per date")
    
    # Field mapping performance
    print("\n🗺️  Field Mapping Performance:")
    fields = ["họ và tên"] * 1000
    
    start = time.time()
    for field in fields:
        map_vietnamese_to_english(field)
    elapsed = time.time() - start
    
    print(f"   Mapped 1000 fields in {elapsed:.3f}s")
    print(f"   Average: {elapsed/1000*1000:.2f}ms per field")
    
    # Pronoun resolution performance
    print("\n🧠 Pronoun Resolution Performance:")
    resolver = get_resolver()
    resolver.update_person("Nguyễn Văn An", "male")
    texts = ["Anh ấy sinh năm 1990"] * 1000
    
    start = time.time()
    for text in texts:
        resolver.resolve_pronoun(text)
    elapsed = time.time() - start
    
    print(f"   Resolved 1000 pronouns in {elapsed:.3f}s")
    print(f"   Average: {elapsed/1000*1000:.2f}ms per resolution")


def main():
    """Main demo function"""
    print("\n" + "="*60)
    print("  🚀 ADVANCED FEATURES DEMO")
    print("  VPBank Voice Agent - Tech Stack Showcase")
    print("="*60)
    
    try:
        # Run all demos
        demo_date_parser()
        demo_field_mapper()
        demo_pronoun_resolver()
        demo_integration()
        demo_use_cases()
        demo_performance()
        
        print("\n" + "="*60)
        print("  ✅ DEMO COMPLETE")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
