"""
BTC Demo Test Suite
Test cases for VPBank Voice Agent demo presentation.

This suite contains realistic scenarios that BTC (Ban Tổ Chức) will test during the demo.
"""

import asyncio
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class FormType(Enum):
    """Form types supported"""
    LOAN = "loan"  # Vay vốn
    CRM = "crm"    # CRM
    HR = "hr"      # Nội bộ HR
    COMPLIANCE = "compliance"  # Tuân thủ
    OPERATIONS = "operations"  # Vận hành


class RegionalAccent(Enum):
    """Vietnamese regional accents"""
    NORTH = "north"      # Giọng Bắc
    CENTRAL = "central"  # Giọng Trung
    SOUTH = "south"      # Giọng Nam
    HUE = "hue"          # Giọng Huế


@dataclass
class TestCase:
    """Single test case for demo"""
    id: str
    name: str
    description: str
    form_type: FormType
    user_commands: List[str]  # Voice commands
    expected_fields: Dict[str, str]  # Expected form data
    accent: RegionalAccent = RegionalAccent.NORTH
    has_noise: bool = False
    has_correction: bool = False  # Test correction scenario
    priority: int = 1  # 1=must test, 2=should test, 3=nice to have


# ==================== PRIORITY 1: MUST-HAVE TEST CASES ====================

# Test Case 1: Basic Loan Application (Giọng Bắc)
TC01_BASIC_LOAN = TestCase(
    id="TC01",
    name="Đăng ký vay vốn cơ bản - Giọng Bắc",
    description="User điền form vay vốn với thông tin cơ bản, giọng Bắc chuẩn",
    form_type=FormType.LOAN,
    accent=RegionalAccent.NORTH,
    user_commands=[
        "Chào em, tôi muốn vay 500 triệu đồng",
        "Tên tôi là Nguyễn Văn An",
        "Số CMND là 036089012345",
        "Số điện thoại là 0963023600",
        "Email là an.nguyen@gmail.com",
        "Địa chỉ thường trú là số 15 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội",
        "Ngày sinh 15 tháng 3 năm 1990",
        "Mục đích vay để mua nhà",
        "Thu nhập hàng tháng là 30 triệu đồng",
        "Thời hạn vay là 10 năm",
        "Submit form giúp tôi"
    ],
    expected_fields={
        "customerName": "Nguyễn Văn An",
        "customerId": "036089012345",
        "phoneNumber": "0963023600",
        "email": "an.nguyen@gmail.com",
        "address": "Số 15 Trần Hưng Đạo, Hoàn Kiếm, Hà Nội",
        "dateOfBirth": "1990-03-15",
        "loanAmount": "500000000",
        "loanPurpose": "Mua nhà",
        "monthlyIncome": "30000000",
        "loanTerm": "10"
    },
    priority=1
)

# Test Case 2: CRM Update with Edit (Giọng Nam)
TC02_CRM_EDIT = TestCase(
    id="TC02",
    name="Cập nhật CRM với chỉnh sửa - Giọng Nam",
    description="User cập nhật thông tin khách hàng, có chỉnh sửa mid-conversation, giọng Nam",
    form_type=FormType.CRM,
    accent=RegionalAccent.SOUTH,
    has_correction=True,
    user_commands=[
        "Chào bạn, tôi cần cập nhật thông tin khách hàng",
        "Tên khách hàng là Trần Thị Bình",
        "Số điện thoại là 0909123456",
        "À không, sửa lại số điện thoại là 0909654321",  # Correction!
        "Email là binh.tran@vpbank.com.vn",
        "Phân loại khách hàng VIP",
        "Ghi chú là khách hàng quan tâm sản phẩm đầu tư",
        "Lưu thông tin này giúp tôi"
    ],
    expected_fields={
        "customerName": "Trần Thị Bình",
        "phoneNumber": "0909654321",  # Corrected value
        "email": "binh.tran@vpbank.com.vn",
        "customerSegment": "VIP",
        "notes": "Khách hàng quan tâm sản phẩm đầu tư"
    },
    priority=1
)

# Test Case 3: HR Leave Request with Navigation (Giọng Trung)
TC03_HR_NAVIGATION = TestCase(
    id="TC03",
    name="Đơn xin nghỉ phép với điều hướng - Giọng Trung",
    description="User điền đơn nghỉ phép, sử dụng lệnh điều hướng, giọng Trung",
    form_type=FormType.HR,
    accent=RegionalAccent.CENTRAL,
    user_commands=[
        "Tôi muốn gửi đơn xin nghỉ phép",
        "Nhảy đến mục thông tin nhân viên",  # Navigation
        "Tên tôi là Lê Văn Cường",
        "Mã nhân viên là VPB12345",
        "Bộ phận là Công nghệ thông tin",
        "Quay lại mục loại nghỉ",  # Navigation back
        "Loại nghỉ là nghỉ phép năm",
        "Từ ngày 20 tháng 12 năm 2025",
        "Đến ngày 25 tháng 12 năm 2025",
        "Lý do nghỉ để du lịch",
        "Gửi đơn"
    ],
    expected_fields={
        "employeeName": "Lê Văn Cường",
        "employeeId": "VPB12345",
        "department": "Công nghệ thông tin",
        "leaveType": "Nghỉ phép năm",
        "fromDate": "2025-12-20",
        "toDate": "2025-12-25",
        "reason": "Du lịch"
    },
    priority=1
)

# Test Case 4: Search and Delete Field (Giọng Huế)
TC04_SEARCH_DELETE = TestCase(
    id="TC04",
    name="Tìm kiếm và xóa trường - Giọng Huế",
    description="User tìm kiếm form, điền thông tin, sau đó xóa một trường, giọng Huế",
    form_type=FormType.COMPLIANCE,
    accent=RegionalAccent.HUE,
    user_commands=[
        "Tìm form báo cáo tuân thủ",  # Search
        "Loại báo cáo là vi phạm nội quy",
        "Mã sự vụ là INC-2025-001",
        "Mô tả sự việc là nhân viên vi phạm quy định bảo mật",
        "Xóa mô tả sự việc đi",  # Delete field
        "Nhập lại mô tả là phát hiện truy cập trái phép hệ thống",
        "Mức độ nghiêm trọng là cao",
        "Hành động đề xuất là đình chỉ công tác",
        "Submit"
    ],
    expected_fields={
        "reportType": "Vi phạm nội quy",
        "incidentId": "INC-2025-001",
        "description": "Phát hiện truy cập trái phép hệ thống",  # Re-entered
        "severity": "Cao",
        "proposedAction": "Đình chỉ công tác"
    },
    priority=1
)

# ==================== PRIORITY 2: SHOULD-HAVE TEST CASES ====================

# Test Case 5: Mixed Vietnamese-English (Giọng Bắc)
TC05_MIXED_LANGUAGE = TestCase(
    id="TC05",
    name="Song ngữ Việt-Anh mixed - Giọng Bắc",
    description="User nói trộn lẫn tiếng Việt và tiếng Anh",
    form_type=FormType.OPERATIONS,
    accent=RegionalAccent.NORTH,
    user_commands=[
        "Mở form transaction verification",  # Mixed
        "Transaction ID là TXN20250108-001",
        "Customer name là Phạm Thị Dung",
        "Amount là 50 triệu VND",
        "Payment method là credit card",  # English
        "Status là pending approval",  # English
        "Save form"
    ],
    expected_fields={
        "transactionId": "TXN20250108-001",
        "customerName": "Phạm Thị Dung",
        "amount": "50000000",
        "paymentMethod": "Credit card",
        "status": "Pending approval"
    },
    priority=2
)

# Test Case 6: Noisy Environment (Giọng Nam + Noise)
TC06_NOISY_ENVIRONMENT = TestCase(
    id="TC06",
    name="Môi trường ồn - Giọng Nam",
    description="User nói trong môi trường có tiếng ồn (văn phòng đông người)",
    form_type=FormType.LOAN,
    accent=RegionalAccent.SOUTH,
    has_noise=True,
    user_commands=[
        "Chào bạn, tôi muốn vay 300 triệu",  # Background noise
        "Tên là Võ Minh Tuấn",
        "CMND là 079088123456",
        "SĐT là 0938111222",
        "Email là tuan.vo@example.com"
    ],
    expected_fields={
        "customerName": "Võ Minh Tuấn",
        "customerId": "079088123456",
        "phoneNumber": "0938111222",
        "email": "tuan.vo@example.com",
        "loanAmount": "300000000"
    },
    priority=2
)

# Test Case 7: Complex Multi-Step with Pronouns (Giọng Bắc)
TC07_CONTEXT_PRONOUNS = TestCase(
    id="TC07",
    name="Đa bước với đại từ - Giọng Bắc",
    description="User sử dụng đại từ và ngữ cảnh phiên",
    form_type=FormType.CRM,
    accent=RegionalAccent.NORTH,
    user_commands=[
        "Tôi muốn thêm khách hàng mới tên Nguyễn Văn B",
        "Tuổi của anh ấy là 35",  # Pronoun: "anh ấy"
        "Số điện thoại của người đó là 0912345678",  # Pronoun: "người đó"
        "Email của ông ấy là b.nguyen@company.vn",  # Pronoun: "ông ấy"
        "Lưu thông tin này"  # Pronoun: "này"
    ],
    expected_fields={
        "customerName": "Nguyễn Văn B",
        "age": "35",
        "phoneNumber": "0912345678",
        "email": "b.nguyen@company.vn"
    },
    priority=2
)

# Test Case 8: Auto Spell Correction (Giọng Nam)
TC08_SPELL_CORRECTION = TestCase(
    id="TC08",
    name="Tự động sửa lỗi chính tả - Giọng Nam",
    description="Hệ thống tự động sửa lỗi phát âm/chính tả",
    form_type=FormType.HR,
    accent=RegionalAccent.SOUTH,
    user_commands=[
        "Gửi đơn nghỉ pép",  # Typo: "pép" → "phép"
        "Tên là Trần Văn Đ",  # Incomplete name
        "À không, Trần Văn Đức",  # Correction
        "Nghỉ từ ngày 15 tam",  # Typo: "tam" → "tháng 3"
        "Đến ngày 20 tam",
        "Submit"
    ],
    expected_fields={
        "employeeName": "Trần Văn Đức",
        "leaveType": "Nghỉ phép",  # Auto-corrected
        "fromDate": "2025-03-15",  # Auto-corrected
        "toDate": "2025-03-20"
    },
    priority=2
)

# ==================== PRIORITY 3: NICE-TO-HAVE TEST CASES ====================

# Test Case 9: All Accents Mixed Conversation
TC09_ALL_ACCENTS = TestCase(
    id="TC09",
    name="Hội thoại đa giọng vùng miền",
    description="Thử nghiệm tất cả giọng Bắc, Trung, Nam, Huế trong cùng session",
    form_type=FormType.LOAN,
    accent=RegionalAccent.NORTH,  # Starting accent
    user_commands=[
        "Chào em ơi, tớ muốn vay tiền",  # Bắc
        "Tên tui là Hoàng Văn E",  # Nam
        "CMND 123456789012",
        "SĐT 0987654321",
        "Submit đê"  # Huế
    ],
    expected_fields={
        "customerName": "Hoàng Văn E",
        "customerId": "123456789012",
        "phoneNumber": "0987654321"
    },
    priority=3
)

# Test Case 10: Very Long Form with Many Fields
TC10_LONG_FORM = TestCase(
    id="TC10",
    name="Form dài với nhiều trường",
    description="Test khả năng điền form phức tạp với 15+ trường",
    form_type=FormType.LOAN,
    accent=RegionalAccent.NORTH,
    user_commands=[
        "Mở form vay vốn",
        "Tên: Đinh Thị F",
        "CMND: 098765432101",
        "SĐT: 0901234567",
        "Email: f.dinh@test.vn",
        "Địa chỉ: 123 Láng Hạ, Đống Đa, Hà Nội",
        "Ngày sinh: 01/01/1985",
        "Giới tính: Nữ",
        "Nghề nghiệp: Giáo viên",
        "Nơi làm việc: Trường THPT ABC",
        "Thu nhập: 25 triệu",
        "Số tiền vay: 800 triệu",
        "Mục đích: Mua nhà",
        "Thời hạn: 15 năm",
        "Tài sản đảm bảo: Sổ đỏ nhà riêng",
        "Người liên hệ khẩn cấp: Đinh Văn G, 0909999888",
        "Submit"
    ],
    expected_fields={
        "customerName": "Đinh Thị F",
        "customerId": "098765432101",
        "phoneNumber": "0901234567",
        "email": "f.dinh@test.vn",
        "address": "123 Láng Hạ, Đống Đa, Hà Nội",
        "dateOfBirth": "1985-01-01",
        "gender": "Nữ",
        "occupation": "Giáo viên",
        "workplace": "Trường THPT ABC",
        "monthlyIncome": "25000000",
        "loanAmount": "800000000",
        "loanPurpose": "Mua nhà",
        "loanTerm": "15",
        "collateral": "Sổ đỏ nhà riêng",
        "emergencyContact": "Đinh Văn G, 0909999888"
    },
    priority=3
)


# ==================== TEST SUITE ====================

class BTCDemoTestSuite:
    """Complete test suite for BTC demo"""

    def __init__(self):
        self.test_cases = {
            # Priority 1
            "TC01": TC01_BASIC_LOAN,
            "TC02": TC02_CRM_EDIT,
            "TC03": TC03_HR_NAVIGATION,
            "TC04": TC04_SEARCH_DELETE,

            # Priority 2
            "TC05": TC05_MIXED_LANGUAGE,
            "TC06": TC06_NOISY_ENVIRONMENT,
            "TC07": TC07_CONTEXT_PRONOUNS,
            "TC08": TC08_SPELL_CORRECTION,

            # Priority 3
            "TC09": TC09_ALL_ACCENTS,
            "TC10": TC10_LONG_FORM,
        }

    def get_priority_1_tests(self) -> List[TestCase]:
        """Get must-have test cases for demo"""
        return [tc for tc in self.test_cases.values() if tc.priority == 1]

    def get_priority_2_tests(self) -> List[TestCase]:
        """Get should-have test cases"""
        return [tc for tc in self.test_cases.values() if tc.priority == 2]

    def get_tests_by_accent(self, accent: RegionalAccent) -> List[TestCase]:
        """Get tests by regional accent"""
        return [tc for tc in self.test_cases.values() if tc.accent == accent]

    def get_tests_by_form_type(self, form_type: FormType) -> List[TestCase]:
        """Get tests by form type"""
        return [tc for tc in self.test_cases.values() if tc.form_type == form_type]

    def print_summary(self):
        """Print test suite summary"""
        print("=" * 80)
        print("BTC DEMO TEST SUITE SUMMARY")
        print("=" * 80)

        p1 = self.get_priority_1_tests()
        p2 = self.get_priority_2_tests()
        p3 = [tc for tc in self.test_cases.values() if tc.priority == 3]

        print(f"\n📋 Total Test Cases: {len(self.test_cases)}")
        print(f"   - Priority 1 (Must-have): {len(p1)}")
        print(f"   - Priority 2 (Should-have): {len(p2)}")
        print(f"   - Priority 3 (Nice-to-have): {len(p3)}")

        print("\n🎯 Priority 1 Test Cases (MUST DEMO):")
        for tc in p1:
            print(f"   [{tc.id}] {tc.name}")
            print(f"       ↳ {tc.description}")

        print("\n⚡ Priority 2 Test Cases (SHOULD DEMO IF TIME):")
        for tc in p2:
            print(f"   [{tc.id}] {tc.name}")

        print("\n✨ Priority 3 Test Cases (NICE TO HAVE):")
        for tc in p3:
            print(f"   [{tc.id}] {tc.name}")

        print("\n🗣️ Coverage by Regional Accent:")
        for accent in RegionalAccent:
            tests = self.get_tests_by_accent(accent)
            print(f"   - {accent.value.capitalize()}: {len(tests)} tests")

        print("\n📝 Coverage by Form Type:")
        for form_type in FormType:
            tests = self.get_tests_by_form_type(form_type)
            print(f"   - {form_type.value.upper()}: {len(tests)} tests")

        print("\n" + "=" * 80)


# ==================== MAIN ====================

if __name__ == "__main__":
    suite = BTCDemoTestSuite()
    suite.print_summary()

    print("\n\n📖 DETAILED TEST CASES:\n")
    for tc_id, tc in suite.test_cases.items():
        print(f"{'=' * 80}")
        print(f"Test Case: {tc.id} - {tc.name}")
        print(f"{'=' * 80}")
        print(f"Description: {tc.description}")
        print(f"Form Type: {tc.form_type.value}")
        print(f"Accent: {tc.accent.value}")
        print(f"Priority: {tc.priority}")
        print(f"Has Noise: {tc.has_noise}")
        print(f"Has Correction: {tc.has_correction}")
        print(f"\nUser Commands:")
        for i, cmd in enumerate(tc.user_commands, 1):
            print(f"  {i}. \"{cmd}\"")
        print(f"\nExpected Form Data:")
        for field, value in tc.expected_fields.items():
            print(f"  - {field}: {value}")
        print()
