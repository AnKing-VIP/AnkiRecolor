from typing import Any


class InvalidConfigValueError(Exception):
    def __init__(self, key: str, expected: str, value: Any):
        self.key = key
        self.expected = expected
        self.value = value

    def __str__(self) -> str:
        return f"For config: {self.key}\nexpected value is: {self.expected}\nbut instead encountered: {self.value}"
