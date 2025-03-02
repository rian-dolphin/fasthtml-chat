"""Message history utilities for FastHTMLChat."""

import json
from typing import Dict, List, Optional


class ChatHistory:
    """Utility class for managing chat message history."""

    @staticmethod
    def parse_messages(messages: Optional[List[str]]) -> List[Dict[str, str]]:
        """
        Parse message strings from form data into a list of message dicts.

        Args:
            messages: List of JSON strings from form data

        Returns:
            List of message dicts with 'role' and 'content'
        """
        if not messages:
            return []

        result = []

        for msg_str in messages:
            try:
                msg = json.loads(msg_str)
                # Skip placeholder messages
                if msg.get("role") == "placeholder":
                    continue
                # Ensure we have the expected format
                if "role" in msg and "content" in msg:
                    result.append(msg)
            except (json.JSONDecodeError, AttributeError):
                # Skip invalid messages
                continue

        return result

    @staticmethod
    def limit_history(
        messages: List[Dict[str, str]],
        max_messages: Optional[int] = None,
        max_tokens: Optional[int] = None,
        approx_chars_per_token: int = 4,
    ) -> List[Dict[str, str]]:
        """
        Limit chat history to stay within constraints.

        Args:
            messages: List of message dicts
            max_messages: Maximum number of messages to keep
            max_tokens: Maximum approximate token count to keep
            approx_chars_per_token: Approximation of characters per token

        Returns:
            Truncated list of messages
        """
        if not messages:
            return []

        if max_messages and len(messages) > max_messages:
            messages = messages[-max_messages:]

        if max_tokens:
            # Very rough approximation of token count
            total_chars = sum(len(msg["content"]) for msg in messages)
            approx_tokens = total_chars / approx_chars_per_token

            if approx_tokens > max_tokens:
                # Remove oldest messages until under limit
                while messages and approx_tokens > max_tokens:
                    removed = messages.pop(0)
                    approx_tokens -= len(removed["content"]) / approx_chars_per_token

        return messages
