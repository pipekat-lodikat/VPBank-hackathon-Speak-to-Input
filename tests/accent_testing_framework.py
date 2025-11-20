#!/usr/bin/env python3
"""
Regional Accent Testing Framework for BTC Compliance

Tests Vietnamese regional accents: Bắc, Trung, Nam, Huế

BTC Requirement: "Nhân viên của VPB khắp các miền nên cần hỗ trợ đủ (Bắc, Trung, Nam, Huế...)"
"""

import sys
import os
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class VietnameseAccent(Enum):
    """Vietnamese regional accents"""
    BAC = "bac"  # Northern (Hanoi)
    TRUNG = "trung"  # Central (Huế, Đà Nẵng)
    NAM = "nam"  # Southern (Saigon)
    HUE = "hue"  # Huế specific


@dataclass
class AccentTestCase:
    """Test case for specific accent"""
    test_id: str
    accent: VietnameseAccent
    command: str
    expected_action: str
    expected_data: Dict
    description: str

    def to_dict(self) -> Dict:
        return {
            "test_id": self.test_id,
            "accent": self.accent.value,
            "command": self.command,
            "expected_action": self.expected_action,
            "expected_data": self.expected_data,
            "description": self.description
        }


@dataclass
class AccentTestResult:
    """Result of accent test"""
    test_case: AccentTestCase
    actual_action: str
    actual_data: Dict
    stt_transcript: str
    stt_confidence: float
    is_correct: bool
    execution_time_ms: float
    tester_name: str
    notes: str = ""

    def get_accuracy(self) -> float:
        """Calculate field-level accuracy"""
        if not self.test_case.expected_data:
            return 100.0 if self.is_correct else 0.0

        expected = self.test_case.expected_data
        actual = self.actual_data

        correct_fields = sum(
            1 for key in expected
            if key in actual and str(actual[key]).lower() == str(expected[key]).lower()
        )

        return (correct_fields / len(expected)) * 100 if expected else 0.0

    def to_dict(self) -> Dict:
        return {
            "test_case": self.test_case.to_dict(),
            "actual_action": self.actual_action,
            "actual_data": self.actual_data,
            "stt_transcript": self.stt_transcript,
            "stt_confidence": self.stt_confidence,
            "is_correct": self.is_correct,
            "accuracy": self.get_accuracy(),
            "execution_time_ms": self.execution_time_ms,
            "tester_name": self.tester_name,
            "notes": self.notes
        }


class AccentTestingFramework:
    """Framework for testing Vietnamese regional accents"""

    def __init__(self):
        self.test_cases: List[AccentTestCase] = []
        self.results: List[AccentTestResult] = []
        self._load_test_cases()

    def _load_test_cases(self):
        """Load test cases for each accent"""

        # TC01: Giọng Bắc - Loan Application
        self.test_cases.append(AccentTestCase(
            test_id="TC01_BAC",
            accent=VietnameseAccent.BAC,
            command="Xin chào, tôi muốn vay 500 triệu đồng",
            expected_action="fill_field",
            expected_data={"loanAmount": "500000000"},
            description="Giọng Bắc - Đăng ký vay cơ bản"
        ))

        self.test_cases.append(AccentTestCase(
            test_id="TC01_BAC_2",
            accent=VietnameseAccent.BAC,
            command="Tên tôi là Nguyễn Văn An",
            expected_action="fill_field",
            expected_data={"customerName": "Nguyễn Văn An"},
            description="Giọng Bắc - Nhập tên"
        ))

        self.test_cases.append(AccentTestCase(
            test_id="TC01_BAC_3",
            accent=VietnameseAccent.BAC,
            command="Số điện thoại là không chín tám bảy sáu năm bốn ba hai một",
            expected_action="fill_field",
            expected_data={"phoneNumber": "0987654321"},
            description="Giọng Bắc - Số điện thoại"
        ))

        # TC02: Giọng Nam - CRM Update
        self.test_cases.append(AccentTestCase(
            test_id="TC02_NAM",
            accent=VietnameseAccent.NAM,
            command="Cho tui cập nhật thông tin khách hàng",
            expected_action="navigate",
            expected_data={"action": "update_customer"},
            description="Giọng Nam - Cập nhật CRM"
        ))

        self.test_cases.append(AccentTestCase(
            test_id="TC02_NAM_2",
            accent=VietnameseAccent.NAM,
            command="Tên là Trần Văn Bình, địa chỉ ở Sài Gòn",
            expected_action="fill_field",
            expected_data={
                "customerName": "Trần Văn Bình",
                "address": "Sài Gòn"
            },
            description="Giọng Nam - Nhập thông tin"
        ))

        self.test_cases.append(AccentTestCase(
            test_id="TC02_NAM_3",
            accent=VietnameseAccent.NAM,
            command="Sửa email thành tranbinhvpb@gmail.com",
            expected_action="edit_field",
            expected_data={"email": "tranbinhvpb@gmail.com"},
            description="Giọng Nam - Sửa email"
        ))

        # TC03: Giọng Trung - HR Leave Request
        self.test_cases.append(AccentTestCase(
            test_id="TC03_TRUNG",
            accent=VietnameseAccent.TRUNG,
            command="Tui muốn xin nghỉ phép từ ngày mười một tháng mười một",
            expected_action="fill_field",
            expected_data={"startDate": "2025-11-11"},
            description="Giọng Trung - Xin nghỉ phép"
        ))

        self.test_cases.append(AccentTestCase(
            test_id="TC03_TRUNG_2",
            accent=VietnameseAccent.TRUNG,
            command="Loại nghỉ là nghỉ phép năm",
            expected_action="fill_field",
            expected_data={"leaveType": "Nghỉ phép năm"},
            description="Giọng Trung - Loại nghỉ phép"
        ))

        # TC04: Giọng Huế - Search and Delete
        self.test_cases.append(AccentTestCase(
            test_id="TC04_HUE",
            accent=VietnameseAccent.HUE,
            command="Tui tìm thông tin khách hàng tên là Lê Thị Dung",
            expected_action="search",
            expected_data={"searchQuery": "Lê Thị Dung"},
            description="Giọng Huế - Tìm kiếm"
        ))

        self.test_cases.append(AccentTestCase(
            test_id="TC04_HUE_2",
            accent=VietnameseAccent.HUE,
            command="Xóa trường địa chỉ đê",
            expected_action="delete_field",
            expected_data={"field": "address"},
            description="Giọng Huế - Xóa field"
        ))

        # Mixed accents in same conversation
        self.test_cases.append(AccentTestCase(
            test_id="TC09_MIXED",
            accent=VietnameseAccent.BAC,
            command="Tên là Phạm Văn Cường, tuổi là ba mươi lăm",
            expected_action="fill_field",
            expected_data={
                "customerName": "Phạm Văn Cường",
                "age": "35"
            },
            description="Mixed - Multiple fields"
        ))

    def get_test_cases_by_accent(self, accent: VietnameseAccent) -> List[AccentTestCase]:
        """Get all test cases for specific accent"""
        return [tc for tc in self.test_cases if tc.accent == accent]

    def record_test_result(self, result: AccentTestResult):
        """Record a test result"""
        self.results.append(result)

    def get_accuracy_by_accent(self) -> Dict[str, Dict]:
        """Calculate accuracy statistics by accent"""
        stats = {}

        for accent in VietnameseAccent:
            accent_results = [r for r in self.results if r.test_case.accent == accent]

            if not accent_results:
                continue

            total_tests = len(accent_results)
            correct_tests = sum(1 for r in accent_results if r.is_correct)
            avg_accuracy = sum(r.get_accuracy() for r in accent_results) / total_tests
            avg_confidence = sum(r.stt_confidence for r in accent_results) / total_tests
            avg_time = sum(r.execution_time_ms for r in accent_results) / total_tests

            stats[accent.value] = {
                "total_tests": total_tests,
                "correct_tests": correct_tests,
                "test_accuracy": (correct_tests / total_tests * 100),
                "field_accuracy": avg_accuracy,
                "avg_stt_confidence": avg_confidence,
                "avg_execution_time_ms": avg_time,
                "status": self._get_status(avg_accuracy)
            }

        return stats

    def _get_status(self, accuracy: float) -> str:
        """Get status based on accuracy"""
        if accuracy >= 95:
            return "✅ Excellent"
        elif accuracy >= 90:
            return "✅ Good"
        elif accuracy >= 85:
            return "⚠️ Fair"
        else:
            return "❌ Needs Improvement"

    def print_test_plan(self):
        """Print testing plan for BTC demo"""
        print("=" * 80)
        print("🎯 ACCENT TESTING PLAN FOR BTC DEMO")
        print("=" * 80)
        print()

        print("📋 Test Requirements:")
        print("- Test all 4 Vietnamese accents: Bắc, Trung, Nam, Huế")
        print("- Minimum 2-3 test cases per accent")
        print("- Measure: STT confidence, field accuracy, execution time")
        print("- Document: Tester name, notes, actual vs expected")
        print()

        for accent in VietnameseAccent:
            test_cases = self.get_test_cases_by_accent(accent)
            if test_cases:
                print(f"\n📍 {accent.value.upper()} ({len(test_cases)} test cases):")
                print("-" * 80)
                for tc in test_cases:
                    print(f"\n  {tc.test_id}: {tc.description}")
                    print(f"  Command: \"{tc.command}\"")
                    print(f"  Expected: {tc.expected_action}")
                    if tc.expected_data:
                        print(f"  Data: {tc.expected_data}")

        print()
        print("=" * 80)
        print("📝 TESTER INSTRUCTIONS")
        print("=" * 80)
        print()
        print("Chuẩn bị:")
        print("1. Tìm 4 người test (mỗi accent 1 người)")
        print("2. Mỗi người test 2-3 câu lệnh")
        print("3. Record: voice input, STT output, actual result")
        print()
        print("Trong quá trình test:")
        print("1. Đọc command tự nhiên (không robot)")
        print("2. Nói với tốc độ bình thường")
        print("3. Ghi chú nếu có vấn đề")
        print()
        print("Sau test:")
        print("1. Record kết quả vào framework")
        print("2. Export report: accent_test_results.json")
        print("3. Review accuracy by accent")
        print()

    def export_results(self, filepath: str):
        """Export test results to JSON"""
        report = {
            "test_date": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "accuracy_by_accent": self.get_accuracy_by_accent(),
            "detailed_results": [r.to_dict() for r in self.results]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report

    def print_results_summary(self):
        """Print summary of test results"""
        if not self.results:
            print("⚠️  No test results recorded yet.")
            return

        print("=" * 80)
        print("📊 ACCENT TESTING RESULTS SUMMARY")
        print("=" * 80)
        print()

        stats = self.get_accuracy_by_accent()

        print(f"{'Accent':<15} {'Tests':<8} {'Pass':<8} {'Field Acc':<12} {'Status':<20}")
        print("-" * 80)

        for accent, data in stats.items():
            print(
                f"{accent.upper():<15} "
                f"{data['total_tests']:<8} "
                f"{data['correct_tests']:<8} "
                f"{data['field_accuracy']:.1f}%{'':<7} "
                f"{data['status']:<20}"
            )

        print()
        print("Expected Accuracy by BTC Requirement:")
        print("  ✅ Bắc:   95-98% (Excellent)")
        print("  ✅ Nam:   90-95% (Good)")
        print("  ⚠️  Trung: 85-90% (Fair)")
        print("  ⚠️  Huế:   80-88% (Fair)")
        print()


# Global instance
accent_testing_framework = AccentTestingFramework()


def demo_usage():
    """Demonstrate how to use the framework"""
    print()
    print("=" * 80)
    print("📖 ACCENT TESTING FRAMEWORK - USAGE DEMO")
    print("=" * 80)
    print()

    # Print test plan
    accent_testing_framework.print_test_plan()

    print()
    print("=" * 80)
    print("💡 EXAMPLE: Recording a Test Result")
    print("=" * 80)
    print()

    # Example: Record a result
    test_case = accent_testing_framework.test_cases[0]  # TC01_BAC

    example_result = AccentTestResult(
        test_case=test_case,
        actual_action="fill_field",
        actual_data={"loanAmount": "500000000"},
        stt_transcript="Xin chào tôi muốn vay 500 triệu đồng",
        stt_confidence=0.96,
        is_correct=True,
        execution_time_ms=3842.5,
        tester_name="Nguyễn Văn An (Hà Nội)",
        notes="Clear pronunciation, good accuracy"
    )

    accent_testing_framework.record_test_result(example_result)

    print("✅ Recorded example result:")
    print(f"   Test: {test_case.test_id}")
    print(f"   Accent: {test_case.accent.value}")
    print(f"   Correct: {example_result.is_correct}")
    print(f"   Accuracy: {example_result.get_accuracy():.1f}%")
    print(f"   STT Confidence: {example_result.stt_confidence:.1%}")
    print()

    # Print summary
    accent_testing_framework.print_results_summary()


if __name__ == "__main__":
    demo_usage()

    print()
    print("=" * 80)
    print("📄 TO USE THIS FRAMEWORK:")
    print("=" * 80)
    print()
    print("1. Import the framework:")
    print("   from tests.accent_testing_framework import accent_testing_framework")
    print()
    print("2. Get test cases for accent:")
    print("   bac_tests = accent_testing_framework.get_test_cases_by_accent(VietnameseAccent.BAC)")
    print()
    print("3. Run test with native speaker")
    print()
    print("4. Record result:")
    print("   accent_testing_framework.record_test_result(result)")
    print()
    print("5. Export report:")
    print("   accent_testing_framework.export_results('accent_test_results.json')")
    print()
    print("6. View summary:")
    print("   accent_testing_framework.print_results_summary()")
    print()
