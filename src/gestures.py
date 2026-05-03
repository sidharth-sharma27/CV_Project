from __future__ import annotations

from typing import Any, Dict, List, Optional


FINGER_TIPS = {
    "thumb": 4,
    "index": 8,
    "middle": 12,
    "ring": 16,
    "pinky": 20,
}

FINGER_PIPS = {
    "thumb": 2,
    "index": 6,
    "middle": 10,
    "ring": 14,
    "pinky": 18,
 }

FINGER_ORDER = ["thumb", "index", "middle", "ring", "pinky"]
FingerState = Dict[str, bool]


def _normalized_points(hand_landmarks) -> List:
    return hand_landmarks.landmark


def extract_finger_state(hand_landmarks, handedness: str) -> FingerState:
    landmarks = _normalized_points(hand_landmarks)
    fingers_up: FingerState = {}

    thumb_tip = landmarks[FINGER_TIPS["thumb"]]
    thumb_joint = landmarks[FINGER_PIPS["thumb"]]
    if handedness == "Right":
        fingers_up["thumb"] = thumb_tip.x < thumb_joint.x
    else:
        fingers_up["thumb"] = thumb_tip.x > thumb_joint.x

    for finger in ("index", "middle", "ring", "pinky"):
        tip = landmarks[FINGER_TIPS[finger]]
        pip = landmarks[FINGER_PIPS[finger]]
        fingers_up[finger] = tip.y < pip.y

    return fingers_up


def describe_finger_state(state: Optional[FingerState]) -> str:
    if state is None:
        return "no hand detected"
    return ", ".join(
        f"{finger[0].upper()}:{'up' if state[finger] else 'down'}" for finger in FINGER_ORDER
    )


def matches_pattern(state: FingerState, pattern: Dict[str, Any]) -> bool:
    for finger in FINGER_ORDER:
        if bool(pattern.get(finger, False)) != bool(state.get(finger, False)):
            return False
    return True


def find_matching_gesture(
    state: Optional[FingerState],
    gestures: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if state is None:
        return None
    for gesture in gestures:
        pattern = gesture.get("pattern", {})
        if matches_pattern(state, pattern):
            return gesture
    return None
