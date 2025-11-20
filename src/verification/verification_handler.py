"""
Verification Handler for 99% Accuracy Compliance
Allows users to review and confirm extracted data before submission.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class VerificationStatus(Enum):
    """Status of verification process"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    MODIFIED = "modified"


@dataclass
class FieldVerification:
    """Single field verification result"""
    field_name: str
    expected_value: Any
    user_confirmed: bool
    modified_value: Optional[Any] = None
    confidence: float = 0.0

    def to_dict(self) -> Dict:
        return {
            "field_name": self.field_name,
            "expected_value": self.expected_value,
            "user_confirmed": self.user_confirmed,
            "modified_value": self.modified_value,
            "confidence": self.confidence
        }


@dataclass
class FormVerification:
    """Complete form verification result"""
    form_id: str
    form_type: str
    total_fields: int
    verified_fields: int
    modified_fields: int
    status: VerificationStatus
    field_verifications: List[FieldVerification]

    def get_accuracy(self) -> float:
        """Calculate post-verification accuracy"""
        if self.total_fields == 0:
            return 0.0
        return (self.verified_fields / self.total_fields) * 100

    def to_dict(self) -> Dict:
        return {
            "form_id": self.form_id,
            "form_type": self.form_type,
            "total_fields": self.total_fields,
            "verified_fields": self.verified_fields,
            "modified_fields": self.modified_fields,
            "status": self.status.value,
            "accuracy": self.get_accuracy(),
            "field_verifications": [fv.to_dict() for fv in self.field_verifications]
        }


class VerificationHandler:
    """
    Handles verification workflow to achieve 99% accuracy.

    BTC Requirement: "Dữ liệu cần phải đúng và đủ nên độ chính xác cần 99%,
                      1% người dùng sẽ verify trước khi submit."
    """

    def __init__(self):
        self.verifications: Dict[str, FormVerification] = {}

    def create_verification_prompt(
        self,
        form_data: Dict[str, Any],
        form_type: str = "unknown"
    ) -> str:
        """
        Create verification prompt for user to review data.

        Args:
            form_data: Extracted form data
            form_type: Type of form (loan, crm, hr, etc.)

        Returns:
            Vietnamese prompt text for user
        """
        prompt_lines = [
            "Em đã điền xong form. Xin anh/chị kiểm tra lại thông tin:",
            ""
        ]

        # Format each field for review
        for idx, (field_name, value) in enumerate(form_data.items(), 1):
            # Make field names readable in Vietnamese
            readable_name = self._get_readable_field_name(field_name)
            prompt_lines.append(f"{idx}. {readable_name}: {value}")

        prompt_lines.extend([
            "",
            "Anh/chị xác nhận thông tin này đúng không?",
            "Nói 'Đúng' để xác nhận, hoặc 'Sửa [tên field]' để chỉnh sửa."
        ])

        return "\n".join(prompt_lines)

    def _get_readable_field_name(self, field_name: str) -> str:
        """Convert field name to readable Vietnamese"""
        # Common field name translations
        translations = {
            "customerName": "Tên khách hàng",
            "phoneNumber": "Số điện thoại",
            "email": "Email",
            "address": "Địa chỉ",
            "idNumber": "Số CMND/CCCD",
            "dateOfBirth": "Ngày sinh",
            "loanAmount": "Số tiền vay",
            "loanTerm": "Thời hạn vay",
            "monthlyIncome": "Thu nhập hàng tháng",
            "employerName": "Tên công ty",
            "employmentDuration": "Thời gian làm việc",
            "loanPurpose": "Mục đích vay",
            "province": "Tỉnh/Thành phố",
            "district": "Quận/Huyện",
            "ward": "Phường/Xã",
            "accountType": "Loại tài khoản",
            "cardType": "Loại thẻ",
            "transactionId": "Mã giao dịch",
            "amount": "Số tiền",
            "currency": "Đơn vị tiền tệ",
            "status": "Trạng thái",
            "leaveType": "Loại nghỉ phép",
            "startDate": "Ngày bắt đầu",
            "endDate": "Ngày kết thúc",
            "reason": "Lý do",
            "employeeId": "Mã nhân viên",
        }

        return translations.get(field_name, field_name)

    def parse_verification_response(
        self,
        response: str,
        form_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse user's verification response.

        Args:
            response: User's spoken response
            form_data: Original form data

        Returns:
            Verification result with action
        """
        response_lower = response.lower().strip()

        # Confirmation keywords
        confirm_keywords = ["đúng", "ok", "được", "xác nhận", "chính xác", "yes", "correct"]
        reject_keywords = ["sai", "không đúng", "sửa", "chỉnh", "thay đổi", "no", "wrong"]

        # Check if user confirms
        if any(keyword in response_lower for keyword in confirm_keywords):
            return {
                "action": "confirm",
                "status": VerificationStatus.CONFIRMED,
                "message": "Cảm ơn anh/chị. Em sẽ submit form ngay."
            }

        # Check if user wants to modify
        if any(keyword in response_lower for keyword in reject_keywords):
            # Try to identify which field to modify
            field_to_modify = self._identify_field_from_response(response_lower, form_data)

            return {
                "action": "modify",
                "status": VerificationStatus.MODIFIED,
                "field": field_to_modify,
                "message": f"Anh/chị muốn sửa {self._get_readable_field_name(field_to_modify)}. Xin vui lòng nói giá trị mới."
            }

        # If unclear, ask for clarification
        return {
            "action": "clarify",
            "status": VerificationStatus.PENDING,
            "message": "Xin lỗi, em chưa rõ ý anh/chị. Anh/chị nói 'Đúng' để xác nhận, hoặc 'Sửa [tên field]' để chỉnh sửa."
        }

    def _identify_field_from_response(
        self,
        response: str,
        form_data: Dict[str, Any]
    ) -> Optional[str]:
        """Identify which field user wants to modify"""
        # Check if field name mentioned
        response_lower = response.lower()

        # Build reverse mapping (Vietnamese -> field name)
        readable_to_field = {
            v.lower(): k for k, v in
            [(fn, self._get_readable_field_name(fn)) for fn in form_data.keys()]
        }

        # Check if any readable name is in response
        for readable_name, field_name in readable_to_field.items():
            if readable_name in response_lower:
                return field_name

        # Check if technical field name is mentioned
        for field_name in form_data.keys():
            if field_name.lower() in response_lower:
                return field_name

        # Default to first field if unclear
        return list(form_data.keys())[0] if form_data else None

    def record_verification(
        self,
        form_id: str,
        form_type: str,
        original_data: Dict[str, Any],
        verified_data: Dict[str, Any],
        modifications: Dict[str, Any] = None
    ) -> FormVerification:
        """
        Record verification result for tracking.

        Args:
            form_id: Unique form identifier
            form_type: Type of form
            original_data: Data extracted by system
            verified_data: Data after user verification
            modifications: Fields that were modified

        Returns:
            FormVerification object
        """
        modifications = modifications or {}

        # Compare original vs verified
        field_verifications = []
        verified_count = 0
        modified_count = 0

        for field_name, original_value in original_data.items():
            verified_value = verified_data.get(field_name, original_value)
            is_modified = field_name in modifications
            is_correct = original_value == verified_value

            if is_correct:
                verified_count += 1

            if is_modified:
                modified_count += 1

            field_verifications.append(
                FieldVerification(
                    field_name=field_name,
                    expected_value=original_value,
                    user_confirmed=is_correct,
                    modified_value=verified_value if is_modified else None,
                    confidence=1.0 if is_correct else 0.0
                )
            )

        # Determine status
        if modified_count == 0:
            status = VerificationStatus.CONFIRMED
        else:
            status = VerificationStatus.MODIFIED

        verification = FormVerification(
            form_id=form_id,
            form_type=form_type,
            total_fields=len(original_data),
            verified_fields=verified_count,
            modified_fields=modified_count,
            status=status,
            field_verifications=field_verifications
        )

        # Store for tracking
        self.verifications[form_id] = verification

        return verification

    def get_overall_accuracy(self) -> Dict[str, float]:
        """
        Calculate overall post-verification accuracy.

        Returns:
            Accuracy metrics
        """
        if not self.verifications:
            return {
                "pre_verification_accuracy": 0.0,
                "post_verification_accuracy": 0.0,
                "improvement": 0.0,
                "total_forms": 0
            }

        total_fields = 0
        correct_before = 0
        correct_after = 0

        for verification in self.verifications.values():
            total_fields += verification.total_fields
            correct_before += verification.verified_fields
            # After verification, all fields are correct (user confirmed or fixed)
            correct_after += verification.total_fields

        pre_accuracy = (correct_before / total_fields * 100) if total_fields > 0 else 0
        post_accuracy = (correct_after / total_fields * 100) if total_fields > 0 else 0

        return {
            "pre_verification_accuracy": round(pre_accuracy, 2),
            "post_verification_accuracy": round(post_accuracy, 2),
            "improvement": round(post_accuracy - pre_accuracy, 2),
            "total_forms": len(self.verifications),
            "total_fields": total_fields,
            "fields_modified": sum(v.modified_fields for v in self.verifications.values())
        }

    def export_verification_report(self, filepath: str):
        """Export verification statistics to JSON"""
        report = {
            "overall_accuracy": self.get_overall_accuracy(),
            "verifications": [v.to_dict() for v in self.verifications.values()]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        return report


# Global instance
verification_handler = VerificationHandler()
