#!/usr/bin/env python
"""
Simple LangSmith Custom Code Evaluator
Copy this function into LangSmith UI: Project → Evaluators → New Evaluator → Custom Code

Based on: https://docs.langchain.com/langsmith/online-evaluations#configure-a-custom-code-evaluator
"""


def perform_eval(run):
    """
    Evaluate workflow run for browser-agent-service

    Args:
        run: Run object containing inputs, outputs, timing info

    Returns:
        Dictionary with feedback scores: {"feedback_key": score, ...}
        Score range: 0.0 (bad) to 1.0 (good)
    """

    # Extract output from run - handle LangGraph message format
    output = ""
    if run.get("outputs"):
        outputs = run["outputs"]

        # Check for messages array (LangGraph format)
        if (
            "messages" in outputs
            and isinstance(outputs["messages"], list)
            and outputs["messages"]
        ):
            # Get the last AI message with actual content
            for msg in reversed(outputs["messages"]):
                if isinstance(msg, dict) and msg.get("type") == "ai":
                    content = msg.get("content", "")
                    # Skip empty content or tool-only responses
                    if content and (
                        isinstance(content, str)
                        or (
                            isinstance(content, list)
                            and any(
                                isinstance(c, dict) and c.get("type") == "text"
                                for c in content
                            )
                        )
                    ):
                        if isinstance(content, list):
                            # Extract text from content blocks
                            output = " ".join(
                                c.get("text", "")
                                for c in content
                                if isinstance(c, dict) and c.get("type") == "text"
                            )
                        else:
                            output = content
                        break

            # If no AI message with text, check tool messages for success indicators
            if not output:
                for msg in reversed(outputs["messages"]):
                    if isinstance(msg, dict) and msg.get("type") == "tool":
                        tool_content = msg.get("content", "")
                        if tool_content and (
                            "✅" in tool_content or "Đã" in tool_content
                        ):
                            output = tool_content
                            break

        # Fallback to other common keys
        if not output:
            output = outputs.get("result") or outputs.get("output") or ""

    output_str = str(output).lower()

    # 1. CORRECTNESS: Is the response valid and complete?
    correctness = 0.7  # default: reasonable

    if not output or len(output_str.strip()) < 10:
        correctness = 0.0  # empty or too short
    elif any(word in output_str for word in ["error", "failed", "exception"]):
        correctness = 0.3  # has errors
    elif any(
        word in output_str
        for word in ["thành công", "hoàn thành", "success", "xử lý", "✅", "đã điền"]
    ):
        correctness = 1.0  # successful

    # 2. QUALITY: Is the response well-formatted?
    quality = 0.0
    length = len(output_str.strip())

    # Good length (50-500 chars)
    if 50 <= length <= 500:
        quality += 0.5
    elif length > 10:
        quality += 0.2

    # Uses Vietnamese
    if any(char in output_str for char in ["ă", "â", "ê", "ô", "ơ", "ư", "đ"]):
        quality += 0.3

    # Professional tone
    if any(
        word in output_str for word in ["xin", "cảm ơn", "vui lòng", "dạ", "anh/chị"]
    ):
        quality += 0.2

    quality = min(quality, 1.0)

    # 3. PERFORMANCE: Is the response fast?
    performance = 0.5  # default

    if run.get("end_time") and run.get("start_time"):
        # Calculate duration
        start = run["start_time"]
        end = run["end_time"]

        # Parse datetime strings
        from datetime import datetime

        if isinstance(start, str):
            start = datetime.fromisoformat(start.replace("Z", "+00:00"))
        if isinstance(end, str):
            end = datetime.fromisoformat(end.replace("Z", "+00:00"))

        duration = (end - start).total_seconds()

        if duration < 5:
            performance = 1.0  # Fast
        elif duration < 10:
            performance = 0.8  # Good
        elif duration < 20:
            performance = 0.6  # Acceptable
        else:
            performance = 0.4  # Slow

    # Return all feedback scores
    return {"correctness": correctness, "quality": quality, "performance": performance}
