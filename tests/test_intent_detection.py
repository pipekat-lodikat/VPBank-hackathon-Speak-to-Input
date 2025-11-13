"""Tests for NLP intent detection utilities."""
from src.nlp.intent_detection import detect_intents


def test_detect_clear_phone_field():
    message = "Xoá số điện thoại của khách hàng"
    intents = detect_intents(message)
    assert any("phoneNumber" in instr for instr in intents)


def test_detect_clear_form():
    message = "Cho tôi reset form này"
    intents = detect_intents(message)
    assert any("Reset or clear the entire form" in instr for instr in intents)


def test_detect_navigation():
    message = "Đi tới phần thông tin liên hệ"
    intents = detect_intents(message)
    assert any("Navigate to section \"contact\"" in instr for instr in intents)


def test_detect_focus_field():
    message = "Tìm số điện thoại khách hàng"
    intents = detect_intents(message)
    assert any("Focus field \"phoneNumber\"" in instr for instr in intents)


def test_detect_read_field():
    message = "Đọc lại số điện thoại của khách"
    intents = detect_intents(message)
    assert any("Read field \"phoneNumber\"" in instr for instr in intents)


def test_detect_summarize_fields():
    message = "Cho tôi xem lại thông tin form"
    intents = detect_intents(message)
    assert any("Summarize filled fields" in instr for instr in intents)


def test_detect_intents_none():
    message = "Xin chào, tôi muốn tạo hồ sơ mới"
    intents = detect_intents(message)
    assert intents == []
