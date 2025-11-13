"""
Pronoun Resolver - Resolve Vietnamese pronouns to actual values
"""

from typing import Dict, Optional, Any
from datetime import datetime


class PronounResolver:
    """Resolve Vietnamese pronouns based on conversation context"""
    
    def __init__(self):
        """Initialize pronoun resolver"""
        self.context: Dict[str, Any] = {
            "last_person": None,
            "last_person_gender": None,
            "last_field": None,
            "last_value": None,
            "last_object": None,
            "entities": {},  # Named entities
            "timestamp": None,
        }
    
    def update_person(self, name: str, gender: Optional[str] = None):
        """
        Update last mentioned person
        
        Args:
            name: Person's name
            gender: Gender (male/female/unknown)
        """
        self.context["last_person"] = name
        self.context["last_person_gender"] = gender or "unknown"
        self.context["timestamp"] = datetime.now()
        
        # Store in entities
        if name:
            self.context["entities"][name.lower()] = {
                "type": "person",
                "gender": gender,
                "timestamp": datetime.now()
            }
    
    def update_field(self, field_name: str, value: Any = None):
        """
        Update last mentioned field
        
        Args:
            field_name: Field name
            value: Field value
        """
        self.context["last_field"] = field_name
        self.context["last_value"] = value
        self.context["timestamp"] = datetime.now()
    
    def update_object(self, object_name: str):
        """
        Update last mentioned object
        
        Args:
            object_name: Object name
        """
        self.context["last_object"] = object_name
        self.context["timestamp"] = datetime.now()
    
    def resolve_pronoun(self, text: str) -> str:
        """
        Resolve pronouns in text to actual values
        
        Args:
            text: Text containing pronouns
            
        Returns:
            Text with pronouns resolved
        """
        text_lower = text.lower()
        resolved = text
        
        # Male pronouns: anh ấy, ông ấy, anh ta
        male_pronouns = ["anh ấy", "ông ấy", "anh ta", "ông ta"]
        for pronoun in male_pronouns:
            if pronoun in text_lower:
                if self.context["last_person"] and self.context["last_person_gender"] == "male":
                    # Case-insensitive replacement
                    import re
                    pattern = re.compile(re.escape(pronoun), re.IGNORECASE)
                    resolved = pattern.sub(self.context["last_person"], resolved)
        
        # Female pronouns: cô ấy, bà ấy, chị ấy
        female_pronouns = ["cô ấy", "bà ấy", "chị ấy", "cô ta", "bà ta", "chị ta"]
        for pronoun in female_pronouns:
            if pronoun in text_lower:
                if self.context["last_person"] and self.context["last_person_gender"] == "female":
                    # Case-insensitive replacement
                    import re
                    pattern = re.compile(re.escape(pronoun), re.IGNORECASE)
                    resolved = pattern.sub(self.context["last_person"], resolved)
        
        # Neutral pronouns: nó, đó, ấy
        if " nó " in text_lower or text_lower.startswith("nó "):
            if self.context["last_field"]:
                import re
                # Replace "nó" at start or with space before
                resolved = re.sub(r'\bnó\b', self.context['last_field'], resolved, flags=re.IGNORECASE)
        
        if " đó " in text_lower or text_lower.startswith("đó "):
            if self.context["last_object"]:
                import re
                # Replace "đó" at start or with space before
                resolved = re.sub(r'\bđó\b', self.context['last_object'], resolved, flags=re.IGNORECASE)
        
        return resolved
    
    def extract_and_update(self, text: str) -> str:
        """
        Extract entities from text and update context
        
        Args:
            text: Input text
            
        Returns:
            Text with pronouns resolved
        """
        text_lower = text.lower()
        
        # Detect person mentions
        person_patterns = [
            ("tên là", "name"),
            ("tôi là", "name"),
            ("mình là", "name"),
        ]
        
        for pattern, entity_type in person_patterns:
            if pattern in text_lower:
                # Extract name after pattern
                idx = text_lower.index(pattern)
                after_pattern = text[idx + len(pattern):].strip()
                # Get first few words as name
                name_parts = after_pattern.split()[:3]
                name = " ".join(name_parts)
                
                # Detect gender from name or context
                gender = self._detect_gender(name, text_lower)
                self.update_person(name, gender)
        
        # Detect field mentions
        field_patterns = ["điền", "nhập", "field", "trường"]
        for pattern in field_patterns:
            if pattern in text_lower:
                # Try to extract field name
                # This is simplified - real implementation would be more sophisticated
                pass
        
        # Resolve pronouns
        return self.resolve_pronoun(text)
    
    def _detect_gender(self, name: str, context: str) -> str:
        """
        Detect gender from name or context
        
        Args:
            name: Person's name
            context: Surrounding context
            
        Returns:
            Gender (male/female/unknown)
        """
        context_lower = context.lower()
        
        # Male indicators
        male_indicators = ["anh", "ông", "mr", "nam"]
        for indicator in male_indicators:
            if indicator in context_lower:
                return "male"
        
        # Female indicators
        female_indicators = ["chị", "cô", "bà", "ms", "mrs", "nữ"]
        for indicator in female_indicators:
            if indicator in context_lower:
                return "female"
        
        # Common Vietnamese male names
        male_names = ["văn", "đức", "minh", "hoàng", "tuấn", "hùng"]
        for male_name in male_names:
            if male_name in name.lower():
                return "male"
        
        # Common Vietnamese female names
        female_names = ["thị", "hương", "lan", "mai", "hoa", "linh"]
        for female_name in female_names:
            if female_name in name.lower():
                return "female"
        
        return "unknown"
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context"""
        return self.context.copy()
    
    def clear_context(self):
        """Clear context"""
        self.context = {
            "last_person": None,
            "last_person_gender": None,
            "last_field": None,
            "last_value": None,
            "last_object": None,
            "entities": {},
            "timestamp": None,
        }


# Global resolver instance
_resolver = PronounResolver()


def resolve_pronouns(text: str) -> str:
    """
    Resolve pronouns in text
    
    Args:
        text: Text containing pronouns
        
    Returns:
        Text with pronouns resolved
    """
    return _resolver.extract_and_update(text)


def update_person_context(name: str, gender: Optional[str] = None):
    """Update person context"""
    _resolver.update_person(name, gender)


def update_field_context(field_name: str, value: Any = None):
    """Update field context"""
    _resolver.update_field(field_name, value)


def get_resolver() -> PronounResolver:
    """Get global resolver instance"""
    return _resolver
