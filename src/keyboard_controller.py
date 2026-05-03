from __future__ import annotations

from typing import Dict, Optional, Set

from pynput.keyboard import Controller, Key, KeyCode


class KeyboardGameController:
    SPECIAL_KEYS = {
        "space": Key.space,
        "enter": Key.enter,
        "tab": Key.tab,
        "shift": Key.shift,
        "ctrl": Key.ctrl,
        "alt": Key.alt,
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "esc": Key.esc,
    }

    def __init__(self) -> None:
        self._keyboard = Controller()
        self._pressed: Set[str] = set()

    def update(self, key_name: Optional[str]) -> None:
        normalized = self._normalize_key(key_name)
        target_keys = {normalized} if normalized else set()

        for key in list(self._pressed - target_keys):
            self._keyboard.release(self._to_key_object(key))
            self._pressed.remove(key)

        for key in target_keys - self._pressed:
            self._keyboard.press(self._to_key_object(key))
            self._pressed.add(key)

    def release_all(self) -> None:
        for key in list(self._pressed):
            self._keyboard.release(self._to_key_object(key))
            self._pressed.remove(key)

    def _normalize_key(self, key_name: Optional[str]) -> Optional[str]:
        if key_name is None:
            return None
        normalized = key_name.strip().lower()
        return normalized or None

    def is_supported(self, key_name: Optional[str]) -> bool:
        normalized = self._normalize_key(key_name)
        if normalized is None:
            return False
        try:
            self._to_key_object(normalized)
        except ValueError:
            return False
        return True

    def _to_key_object(self, key_name: str):
        if key_name in self.SPECIAL_KEYS:
            return self.SPECIAL_KEYS[key_name]
        if len(key_name) == 1:
            return KeyCode.from_char(key_name)
        raise ValueError(
            f"Unsupported key '{key_name}'. Use a single character or one of: "
            f"{', '.join(sorted(self.SPECIAL_KEYS))}"
        )
