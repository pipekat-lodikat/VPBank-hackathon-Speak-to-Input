"""Parse structured INSTRUCTION lines embedded in conversation context."""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

INSTRUCTION_PATTERN = re.compile(r"^INSTRUCTION:\s*(.+)$", re.MULTILINE)
FIELD_PATTERN = re.compile(r'Clear field "(?P<field>[^"\\]+)"', re.IGNORECASE)
FOCUS_PATTERN = re.compile(r'Focus field "(?P<field>[^"\\]+)"', re.IGNORECASE)
READ_PATTERN = re.compile(r'Read field "(?P<field>[^"\\]+)"', re.IGNORECASE)
SECTION_PATTERN = re.compile(r'Navigate to section "(?P<section>[^"\\]+)"', re.IGNORECASE)
CLEAR_FORM_PATTERN = re.compile(r"Reset or clear the entire form", re.IGNORECASE)
SUMMARY_PATTERN = re.compile(r"Summarize filled fields", re.IGNORECASE)

Instruction = Dict[str, str]


def extract_structured_instructions(message: str) -> Tuple[str, List[Instruction]]:
    """Return (clean_message, structured_instructions) pair.

    We strip INSTRUCTION lines from the message so they are not sent to the LLM,
    while returning parsed metadata for deterministic automation steps.
    """

    if not message:
        return message, []

    instructions: List[Instruction] = []
    for instruction_line in INSTRUCTION_PATTERN.findall(message):
        parsed = _parse_instruction(instruction_line.strip())
        if parsed:
            instructions.append(parsed)

    # Remove instruction lines from the message that will be sent to the LLM
    cleaned_message = INSTRUCTION_PATTERN.sub("", message)
    cleaned_message = "\n".join(line for line in cleaned_message.splitlines() if line.strip())

    return cleaned_message.strip(), instructions


def _parse_instruction(instruction_line: str) -> Instruction | None:
    if not instruction_line:
        return None

    if CLEAR_FORM_PATTERN.search(instruction_line):
        return {"type": "clear_form"}

    if SUMMARY_PATTERN.search(instruction_line):
        return {"type": "summarize_fields"}

    field_match = FIELD_PATTERN.search(instruction_line)
    if field_match:
        return {
            "type": "clear_field",
            "field": field_match.group("field")
        }

    focus_match = FOCUS_PATTERN.search(instruction_line)
    if focus_match:
        return {
            "type": "focus_field",
            "field": focus_match.group("field")
        }

    read_match = READ_PATTERN.search(instruction_line)
    if read_match:
        return {
            "type": "read_field",
            "field": read_match.group("field")
        }

    section_match = SECTION_PATTERN.search(instruction_line)
    if section_match:
        return {
            "type": "navigate_section",
            "section": section_match.group("section")
        }

    return None
