"""Utility functions to detect structured intents from user voice commands."""
from __future__ import annotations

from typing import Dict, List


CLEAR_FIELD_KEYWORDS = [
    "xóa",
    "xoá",
    "clear",
    "delete",
    "bỏ",
    "erase",
]

CLEAR_FORM_KEYWORDS = [
    "xóa form",
    "xoá form",
    "clear form",
    "reset form",
    "làm lại",
    "làm mới",
]

NAVIGATE_KEYWORDS = [
    "đi tới",
    "chuyển tới",
    "chuyển sang",
    "navigate",
    "go to",
    "đến mục",
]

FOCUS_FIELD_KEYWORDS = [
    "tìm",
    "search",
    "focus",
    "đi tới trường",
    "chọn trường",
    "điền vào",
    "select field",
]

READ_FIELD_KEYWORDS = [
    "đọc",
    "đọc lại",
    "xem",
    "kiểm tra",
    "show",
    "đọc số",
    "cho tôi biết",
]

REVIEW_FORM_KEYWORDS = [
    "đọc lại form",
    "tổng kết",
    "cho tôi xem lại",
    "review",
    "kiểm tra lại",
    "đọc lại thông tin",
    "xem lại thông tin",
]

FIELD_SYNONYMS: Dict[str, List[str]] = {
    "customerName": ["tên", "họ tên", "fullname", "name"],
    "customerId": ["căn cước", "cccd", "cmnd", "mã khách", "id"],
    "phoneNumber": ["số điện thoại", "điện thoại", "phone"],
    "email": ["email", "thư điện tử"],
    "dateOfBirth": ["ngày sinh", "birth", "dob"],
    "address": ["địa chỉ", "address"],
    "loanAmount": ["số tiền", "khoản vay", "loan amount"],
    "loanTerm": ["kỳ hạn", "thời hạn", "loan term"],
    "loanPurpose": ["mục đích", "purpose"],
    "monthlyIncome": ["thu nhập", "income"],
    "emailConfirmed": ["xác nhận email", "confirm email", "email confirmation"],
    "province": ["tỉnh", "thành phố", "province", "city"],
    "occupation": ["nghề nghiệp", "occupation", "job"],
    "salary": ["lương", "thu nhập", "salary"],
    "loanType": ["loại khoản vay", "loan type"],
}

SECTION_SYNONYMS: Dict[str, List[str]] = {
    "contact": ["liên hệ", "contact", "thông tin liên hệ"],
    "financial": ["tài chính", "financial"],
    "employment": ["công việc", "employment"],
}


def detect_intents(message: str) -> List[str]:
    """Return extra instructions for the browser agent based on user message.

    The browser agent understands appended instructions such as
    "INSTRUCTION: Clear field \"phoneNumber\".". We emit those when
    recognizing explicit voice commands like "xoá số điện thoại".
    """

    if not message:
        return []

    msg = message.lower()
    instructions: List[str] = []

    # Clear form intent
    if any(phrase in msg for phrase in CLEAR_FORM_KEYWORDS):
        instructions.append("INSTRUCTION: Reset or clear the entire form.")

    # Clear individual fields
    for field, synonyms in FIELD_SYNONYMS.items():
        if any(keyword in msg for keyword in CLEAR_FIELD_KEYWORDS):
            if any(syn in msg for syn in synonyms):
                instructions.append(
                    f'INSTRUCTION: Clear field "{field}" (user mentioned "{_first_match(msg, synonyms)}").'
                )
        # Focus instructions (search/find field)
        if any(keyword in msg for keyword in FOCUS_FIELD_KEYWORDS):
            if any(syn in msg for syn in synonyms):
                instructions.append(
                    f'INSTRUCTION: Focus field "{field}" (user mentioned "{_first_match(msg, synonyms)}").'
                )
        if any(keyword in msg for keyword in READ_FIELD_KEYWORDS):
            if any(syn in msg for syn in synonyms):
                instructions.append(
                    f'INSTRUCTION: Read field "{field}" (user mentioned "{_first_match(msg, synonyms)}").'
                )

    # Navigation intents
    if any(prefix in msg for prefix in NAVIGATE_KEYWORDS):
        section_match = _find_section(msg)
        if section_match:
            instructions.append(
                f'INSTRUCTION: Navigate to section "{section_match}".'
            )

    if any(keyword in msg for keyword in REVIEW_FORM_KEYWORDS):
        instructions.append("INSTRUCTION: Summarize filled fields.")

    return instructions


def _first_match(msg: str, synonyms: List[str]) -> str:
    for syn in synonyms:
        if syn in msg:
            return syn
    return synonyms[0] if synonyms else ""


def _find_section(msg: str) -> str | None:
    for section, synonyms in SECTION_SYNONYMS.items():
        if any(syn in msg for syn in synonyms):
            return section
    return None
