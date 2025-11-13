from src.nlp.instruction_parser import extract_structured_instructions


def test_extract_clear_field_instruction():
    message = (
        "Xin hãy xoá số điện thoại\n"
        "INSTRUCTION: Clear field \"phoneNumber\" (user mentioned \"số điện thoại\")."
    )

    cleaned, instructions = extract_structured_instructions(message)

    assert cleaned == "Xin hãy xoá số điện thoại"
    assert instructions == [{"type": "clear_field", "field": "phoneNumber"}]


def test_extract_clear_form_instruction():
    message = "INSTRUCTION: Reset or clear the entire form."

    cleaned, instructions = extract_structured_instructions(message)

    assert cleaned == ""
    assert instructions == [{"type": "clear_form"}]


def test_extract_navigate_instruction():
    message = (
        "Đi tới thông tin liên hệ\n"
        "INSTRUCTION: Navigate to section \"contact\"."
    )

    cleaned, instructions = extract_structured_instructions(message)

    assert cleaned == "Đi tới thông tin liên hệ"
    assert instructions == [{"type": "navigate_section", "section": "contact"}]


def test_extract_focus_field_instruction():
    message = (
        "Tìm số điện thoại\n"
        "INSTRUCTION: Focus field \"phoneNumber\" (user mentioned \"số điện thoại\")."
    )

    cleaned, instructions = extract_structured_instructions(message)

    assert cleaned == "Tìm số điện thoại"
    assert instructions == [{"type": "focus_field", "field": "phoneNumber"}]


def test_extract_read_field_instruction():
    message = (
        "Đọc lại số điện thoại\n"
        "INSTRUCTION: Read field \"phoneNumber\" (user mentioned \"số điện thoại\")."
    )

    cleaned, instructions = extract_structured_instructions(message)

    assert cleaned == "Đọc lại số điện thoại"
    assert instructions == [{"type": "read_field", "field": "phoneNumber"}]


def test_extract_summarize_instruction():
    message = "INSTRUCTION: Summarize filled fields."

    cleaned, instructions = extract_structured_instructions(message)

    assert cleaned == ""
    assert instructions == [{"type": "summarize_fields"}]


def test_extract_structured_instructions_no_matches():
    message = "Không có hướng dẫn đặc biệt"

    cleaned, instructions = extract_structured_instructions(message)

    assert cleaned == message
    assert instructions == []
