"""Reusable token counting helpers for AI requests and analytics."""
import os
from functools import lru_cache

import tiktoken

DEFAULT_ENCODING_NAME = 'cl100k_base'


@lru_cache(maxsize=1)
def get_token_encoding():
    """Return the configured tiktoken encoding, initialized once per process."""
    encoding_name = os.environ.get('TOKEN_ENCODING_NAME', DEFAULT_ENCODING_NAME)
    return tiktoken.get_encoding(encoding_name)


def count_tokens(text):
    """Count tokens in arbitrary text using the configured OpenAI-compatible encoding."""
    return len(get_token_encoding().encode(str(text or ''), disallowed_special=()))
