"""
Accuracy Tracking Module
Tracks form filling accuracy, command understanding, and field extraction success rates.
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from collections import defaultdict


@dataclass
class FieldValidation:
    """Single field validation result"""
    field_name: str
    expected_value: Optional[str]
    actual_value: Optional[str]
    is_correct: bool
    error_type: Optional[str] = None  # "missing", "incorrect", "format_error"
    confidence: float = 1.0


@dataclass
class FormAccuracyResult:
    """Complete form accuracy assessment"""
    session_id: str
    form_type: str
    total_fields: int
    correct_fields: int
    incorrect_fields: int
    missing_fields: int
    accuracy_rate: float
    field_validations: List[FieldValidation] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "form_type": self.form_type,
            "total_fields": self.total_fields,
            "correct_fields": self.correct_fields,
            "incorrect_fields": self.incorrect_fields,
            "missing_fields": self.missing_fields,
            "accuracy_rate": self.accuracy_rate,
            "timestamp": self.timestamp.isoformat(),
            "field_validations": [
                {
                    "field_name": fv.field_name,
                    "expected": fv.expected_value,
                    "actual": fv.actual_value,
                    "is_correct": fv.is_correct,
                    "error_type": fv.error_type,
                    "confidence": fv.confidence
                }
                for fv in self.field_validations
            ]
        }


@dataclass
class CommandAccuracyResult:
    """Command understanding accuracy"""
    session_id: str
    command_text: str
    understood_intent: str
    expected_intent: Optional[str]
    is_correct: bool
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)


class AccuracyTracker:
    """
    Tracks accuracy metrics for the voice agent system.

    Metrics tracked:
    - Form filling accuracy (field-level and form-level)
    - Command understanding accuracy
    - Field extraction accuracy
    - Overall system accuracy
    """

    def __init__(self):
        self.form_results: List[FormAccuracyResult] = []
        self.command_results: List[CommandAccuracyResult] = []
        self.stats = {
            "total_forms": 0,
            "successful_forms": 0,
            "total_fields": 0,
            "correct_fields": 0,
            "total_commands": 0,
            "understood_commands": 0,
        }

    def track_form_accuracy(
        self,
        session_id: str,
        form_type: str,
        expected_data: Dict[str, str],
        actual_data: Dict[str, str],
        confidence_scores: Optional[Dict[str, float]] = None
    ) -> FormAccuracyResult:
        """
        Track accuracy for a filled form.

        Args:
            session_id: Unique session identifier
            form_type: Type of form (loan, crm, hr, etc.)
            expected_data: Expected field values
            actual_data: Actual filled values
            confidence_scores: Optional confidence scores per field

        Returns:
            FormAccuracyResult with detailed accuracy metrics
        """
        confidence_scores = confidence_scores or {}

        all_fields = set(expected_data.keys()) | set(actual_data.keys())
        field_validations = []
        correct_count = 0
        incorrect_count = 0
        missing_count = 0

        for field_name in all_fields:
            expected = expected_data.get(field_name)
            actual = actual_data.get(field_name)
            confidence = confidence_scores.get(field_name, 1.0)

            # Determine correctness
            if expected is None:
                # Extra field filled (not in expected)
                is_correct = True
                error_type = None
            elif actual is None or actual == "":
                # Missing field
                is_correct = False
                error_type = "missing"
                missing_count += 1
            elif self._normalize_value(expected) == self._normalize_value(actual):
                # Correct field
                is_correct = True
                error_type = None
                correct_count += 1
            else:
                # Incorrect field
                is_correct = False
                error_type = "incorrect"
                incorrect_count += 1

            field_validations.append(FieldValidation(
                field_name=field_name,
                expected_value=expected,
                actual_value=actual,
                is_correct=is_correct,
                error_type=error_type,
                confidence=confidence
            ))

        total_fields = len(expected_data)
        accuracy_rate = correct_count / total_fields if total_fields > 0 else 0.0

        result = FormAccuracyResult(
            session_id=session_id,
            form_type=form_type,
            total_fields=total_fields,
            correct_fields=correct_count,
            incorrect_fields=incorrect_count,
            missing_fields=missing_count,
            accuracy_rate=accuracy_rate,
            field_validations=field_validations
        )

        # Update stats
        self.form_results.append(result)
        self.stats["total_forms"] += 1
        if accuracy_rate >= 0.99:  # 99% threshold
            self.stats["successful_forms"] += 1
        self.stats["total_fields"] += total_fields
        self.stats["correct_fields"] += correct_count

        return result

    def track_command_accuracy(
        self,
        session_id: str,
        command_text: str,
        understood_intent: str,
        expected_intent: Optional[str] = None,
        confidence: float = 1.0
    ) -> CommandAccuracyResult:
        """
        Track accuracy for command understanding.

        Args:
            session_id: Unique session identifier
            command_text: Original voice command text
            understood_intent: What the system understood
            expected_intent: Expected intent (for testing)
            confidence: Confidence score of understanding

        Returns:
            CommandAccuracyResult
        """
        is_correct = True
        if expected_intent:
            is_correct = understood_intent == expected_intent

        result = CommandAccuracyResult(
            session_id=session_id,
            command_text=command_text,
            understood_intent=understood_intent,
            expected_intent=expected_intent,
            is_correct=is_correct,
            confidence=confidence
        )

        # Update stats
        self.command_results.append(result)
        self.stats["total_commands"] += 1
        if is_correct:
            self.stats["understood_commands"] += 1

        return result

    def get_overall_accuracy(self) -> Dict[str, float]:
        """
        Get overall accuracy metrics.

        Returns:
            Dictionary with accuracy percentages
        """
        form_accuracy = (
            self.stats["correct_fields"] / self.stats["total_fields"]
            if self.stats["total_fields"] > 0
            else 0.0
        )

        form_completion_rate = (
            self.stats["successful_forms"] / self.stats["total_forms"]
            if self.stats["total_forms"] > 0
            else 0.0
        )

        command_accuracy = (
            self.stats["understood_commands"] / self.stats["total_commands"]
            if self.stats["total_commands"] > 0
            else 0.0
        )

        return {
            "field_accuracy": round(form_accuracy * 100, 2),  # %
            "form_completion_rate": round(form_completion_rate * 100, 2),  # %
            "command_understanding_rate": round(command_accuracy * 100, 2),  # %
            "overall_accuracy": round((form_accuracy + command_accuracy) / 2 * 100, 2),  # %
        }

    def get_accuracy_by_form_type(self) -> Dict[str, Dict[str, float]]:
        """Get accuracy breakdown by form type"""
        form_type_stats = defaultdict(lambda: {"total": 0, "correct": 0, "forms": 0, "successful": 0})

        for result in self.form_results:
            stats = form_type_stats[result.form_type]
            stats["total"] += result.total_fields
            stats["correct"] += result.correct_fields
            stats["forms"] += 1
            if result.accuracy_rate >= 0.99:
                stats["successful"] += 1

        return {
            form_type: {
                "field_accuracy": round(stats["correct"] / stats["total"] * 100, 2) if stats["total"] > 0 else 0.0,
                "completion_rate": round(stats["successful"] / stats["forms"] * 100, 2) if stats["forms"] > 0 else 0.0,
                "total_forms": stats["forms"]
            }
            for form_type, stats in form_type_stats.items()
        }

    def get_common_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common error fields"""
        error_counts = defaultdict(int)
        error_details = defaultdict(lambda: {"missing": 0, "incorrect": 0, "examples": []})

        for result in self.form_results:
            for fv in result.field_validations:
                if not fv.is_correct:
                    error_counts[fv.field_name] += 1
                    details = error_details[fv.field_name]
                    if fv.error_type == "missing":
                        details["missing"] += 1
                    elif fv.error_type == "incorrect":
                        details["incorrect"] += 1

                    # Store example
                    if len(details["examples"]) < 3:
                        details["examples"].append({
                            "expected": fv.expected_value,
                            "actual": fv.actual_value,
                            "form_type": result.form_type
                        })

        # Sort by frequency
        sorted_errors = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:limit]

        return [
            {
                "field_name": field_name,
                "error_count": count,
                "missing_count": error_details[field_name]["missing"],
                "incorrect_count": error_details[field_name]["incorrect"],
                "examples": error_details[field_name]["examples"]
            }
            for field_name, count in sorted_errors
        ]

    def get_time_series_accuracy(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get accuracy over time (hourly buckets)"""
        now = datetime.now()
        cutoff = now - timedelta(hours=hours)

        # Filter recent results
        recent_results = [r for r in self.form_results if r.timestamp >= cutoff]

        # Group by hour
        hourly_stats = defaultdict(lambda: {"total": 0, "correct": 0})

        for result in recent_results:
            hour_key = result.timestamp.replace(minute=0, second=0, microsecond=0)
            stats = hourly_stats[hour_key]
            stats["total"] += result.total_fields
            stats["correct"] += result.correct_fields

        # Convert to list
        time_series = []
        for hour_key in sorted(hourly_stats.keys()):
            stats = hourly_stats[hour_key]
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0.0
            time_series.append({
                "timestamp": hour_key.isoformat(),
                "accuracy": round(accuracy * 100, 2),
                "total_fields": stats["total"]
            })

        return time_series

    def export_results(self, filepath: str):
        """Export all results to JSON file"""
        data = {
            "stats": self.stats,
            "overall_accuracy": self.get_overall_accuracy(),
            "accuracy_by_form_type": self.get_accuracy_by_form_type(),
            "common_errors": self.get_common_errors(),
            "form_results": [r.to_dict() for r in self.form_results],
            "command_results": [
                {
                    "session_id": cr.session_id,
                    "command_text": cr.command_text,
                    "understood_intent": cr.understood_intent,
                    "expected_intent": cr.expected_intent,
                    "is_correct": cr.is_correct,
                    "confidence": cr.confidence,
                    "timestamp": cr.timestamp.isoformat()
                }
                for cr in self.command_results
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _normalize_value(self, value: Optional[str]) -> str:
        """Normalize value for comparison"""
        if value is None:
            return ""
        # Remove extra whitespace, lowercase
        return " ".join(value.strip().lower().split())

    def reset(self):
        """Reset all tracking data"""
        self.form_results.clear()
        self.command_results.clear()
        self.stats = {
            "total_forms": 0,
            "successful_forms": 0,
            "total_fields": 0,
            "correct_fields": 0,
            "total_commands": 0,
            "understood_commands": 0,
        }


# Global instance
accuracy_tracker = AccuracyTracker()
