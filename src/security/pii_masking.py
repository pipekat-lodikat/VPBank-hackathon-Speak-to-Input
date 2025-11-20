"""
PII Data Masking for Logs
Masks sensitive personal information in logs to comply with privacy regulations
"""
import re
from typing import Optional


class PIIMasker:
    """Masks personally identifiable information (PII) in text"""

    # Regex patterns for Vietnamese PII
    PATTERNS = {
        # Phone numbers: 10 digits starting with 0 or +84
        "phone": [
            r'\b0\d{9}\b',  # 0xxxxxxxxx
            r'\b84\d{9}\b',  # 84xxxxxxxxx
            r'\+84\d{9}\b',  # +84xxxxxxxxx
        ],
        # Vietnamese ID (CCCD): 12 digits
        "cccd": [
            r'\b\d{12}\b',  # 12 consecutive digits
        ],
        # Email addresses
        "email": [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        ],
        # Credit card (basic pattern)
        "credit_card": [
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        ],
        # Date of birth patterns (DD/MM/YYYY)
        "dob": [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
        ],
        # Vietnamese names (heuristic: 2-4 capitalized words with Vietnamese chars)
        "name": [
            r'\b[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+(?:\s[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+){1,3}\b',
        ],
        # Addresses (heuristic: contains "số" + number or "phường/quận/huyện/tỉnh")
        "address": [
            r'(?:số\s*\d+[^\n,]{0,50}(?:phường|quận|huyện|tỉnh|thành phố)[^\n,]{0,50})',
        ],
    }

    MASK_MODES = {
        "partial": "partial",  # Show first/last chars: 096***600
        "full": "full",  # Complete masking: ***
        "hash": "hash",  # Hash with prefix: phone_abc123
    }

    def __init__(self, mode: str = "partial"):
        """
        Initialize PII masker

        Args:
            mode: Masking mode - "partial", "full", or "hash"
        """
        self.mode = mode

    def mask_phone(self, text: str) -> str:
        """Mask phone numbers"""
        for pattern in self.PATTERNS["phone"]:
            if self.mode == "partial":
                # Show first 3 and last 3: 096***600
                text = re.sub(pattern, lambda m: f"{m.group()[:3]}***{m.group()[-3:]}", text)
            elif self.mode == "full":
                text = re.sub(pattern, "***", text)
            else:  # hash
                text = re.sub(pattern, lambda m: f"phone_{hash(m.group()) % 1000000}", text)
        return text

    def mask_cccd(self, text: str) -> str:
        """Mask Vietnamese ID numbers"""
        for pattern in self.PATTERNS["cccd"]:
            if self.mode == "partial":
                # Show first 3 and last 3: 123***123
                text = re.sub(pattern, lambda m: f"{m.group()[:3]}***{m.group()[-3:]}", text)
            elif self.mode == "full":
                text = re.sub(pattern, "***", text)
            else:  # hash
                text = re.sub(pattern, lambda m: f"cccd_{hash(m.group()) % 1000000}", text)
        return text

    def mask_email(self, text: str) -> str:
        """Mask email addresses"""
        for pattern in self.PATTERNS["email"]:
            if self.mode == "partial":
                # Show first char and domain: a***@gmail.com
                def mask_fn(m):
                    email = m.group()
                    parts = email.split('@')
                    if len(parts) == 2:
                        return f"{parts[0][0]}***@{parts[1]}"
                    return "***"
                text = re.sub(pattern, mask_fn, text)
            elif self.mode == "full":
                text = re.sub(pattern, "***@***.***", text)
            else:  # hash
                text = re.sub(pattern, lambda m: f"email_{hash(m.group()) % 1000000}", text)
        return text

    def mask_credit_card(self, text: str) -> str:
        """Mask credit card numbers"""
        for pattern in self.PATTERNS["credit_card"]:
            if self.mode == "partial":
                # Show last 4: **** **** **** 1234
                text = re.sub(pattern, lambda m: f"**** **** **** {m.group()[-4:]}", text)
            elif self.mode == "full":
                text = re.sub(pattern, "**** **** **** ****", text)
            else:  # hash
                text = re.sub(pattern, lambda m: f"card_{hash(m.group()) % 1000000}", text)
        return text

    def mask_dob(self, text: str) -> str:
        """Mask date of birth"""
        for pattern in self.PATTERNS["dob"]:
            if self.mode == "partial":
                # Show year only: **/**/1990
                text = re.sub(pattern, lambda m: f"**/**/{m.group()[-4:]}", text)
            elif self.mode == "full":
                text = re.sub(pattern, "**/**/****", text)
            else:  # hash
                text = re.sub(pattern, lambda m: f"dob_{hash(m.group()) % 1000000}", text)
        return text

    def mask_name(self, text: str) -> str:
        """
        Mask Vietnamese names (conservative approach)
        Only mask if explicitly detected as name field
        """
        # We'll be conservative here - only mask when context is clear
        # Example: "Tên: Nguyễn Văn An" -> "Tên: N*** V*** A***"
        name_contexts = [
            r'(?:tên|họ tên|khách hàng|name)[:：\s]+([A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+(?:\s[A-ZÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ][a-zàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+){1,3})',
        ]

        for pattern in name_contexts:
            if self.mode == "partial":
                # Mask middle parts: Nguyễn V*** An
                def mask_fn(m):
                    name = m.group(1)
                    parts = name.split()
                    if len(parts) <= 1:
                        return m.group(0).replace(name, name[0] + "***")
                    masked = f"{parts[0]} "
                    for part in parts[1:-1]:
                        masked += part[0] + "*** "
                    masked += parts[-1]
                    return m.group(0).replace(name, masked)
                text = re.sub(pattern, mask_fn, text, flags=re.IGNORECASE)
            elif self.mode == "full":
                text = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), "***"), text, flags=re.IGNORECASE)
            else:  # hash
                text = re.sub(pattern, lambda m: m.group(0).replace(m.group(1), f"name_{hash(m.group(1)) % 1000000}"), text, flags=re.IGNORECASE)
        return text

    def mask_address(self, text: str) -> str:
        """Mask addresses"""
        for pattern in self.PATTERNS["address"]:
            if self.mode == "partial":
                text = re.sub(pattern, lambda m: f"số *** {m.group()[-20:]}", text, flags=re.IGNORECASE)
            elif self.mode == "full":
                text = re.sub(pattern, "***", text, flags=re.IGNORECASE)
            else:  # hash
                text = re.sub(pattern, lambda m: f"addr_{hash(m.group()) % 1000000}", text, flags=re.IGNORECASE)
        return text

    def mask_all(self, text: str, skip_types: Optional[list[str]] = None) -> str:
        """
        Mask all PII types in text

        Args:
            text: Input text
            skip_types: List of PII types to skip masking (e.g., ["name", "dob"])

        Returns:
            Text with PII masked
        """
        skip_types = skip_types or []

        if "phone" not in skip_types:
            text = self.mask_phone(text)
        if "cccd" not in skip_types:
            text = self.mask_cccd(text)
        if "email" not in skip_types:
            text = self.mask_email(text)
        if "credit_card" not in skip_types:
            text = self.mask_credit_card(text)
        if "dob" not in skip_types:
            text = self.mask_dob(text)
        if "name" not in skip_types:
            text = self.mask_name(text)
        if "address" not in skip_types:
            text = self.mask_address(text)

        return text


# Global instance for convenience
pii_masker = PIIMasker(mode="partial")


def mask_pii(text: str, mode: str = "partial", skip_types: Optional[list[str]] = None) -> str:
    """
    Convenience function to mask PII in text

    Args:
        text: Input text
        mode: Masking mode - "partial", "full", or "hash"
        skip_types: List of PII types to skip

    Returns:
        Text with PII masked
    """
    masker = PIIMasker(mode=mode)
    return masker.mask_all(text, skip_types=skip_types)
