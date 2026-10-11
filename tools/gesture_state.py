from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import hypot


class GestureState(str, Enum):
    IDLE = "IDLE"
    HOVERING = "HOVERING"
    PINCHING = "PINCHING"
    GRABBING = "GRABBING"
    DRAGGING = "DRAGGING"
    SCALING = "SCALING"
    ROTATING = "ROTATING"
    RELEASING = "RELEASING"


@dataclass
class GestureConfig:
    pinch_enter: float = 0.055
    pinch_exit: float = 0.17
    pinch_hold_ms: int = 2000
    release_frames: int = 3
    lost_frames: int = 12
    scale_delta: float = 0.018
    zoom_stable_ms: int = 900


@dataclass
class GestureStateMachine:
    config: GestureConfig = field(default_factory=GestureConfig)
    state: GestureState = GestureState.IDLE
    release_frames: int = 0
    lost_frames: int = 0
    selected: bool = False
    initial_pinch: float = 0.0
    pinch_started_ms: int | None = None
    zoom_pose: str | None = None
    zoom_started_ms: int | None = None
    zoom_action: str | None = None

    def update(
        self,
        *,
        pointer_over_object: bool,
        thumb: tuple[float, float] | None,
        index: tuple[float, float] | None,
        hands: int = 1,
        now_ms: int = 0,
        hand_poses: tuple[str, str] | None = None,
    ) -> GestureState:
        self.zoom_action = None
        if not self.selected and hand_poses and len(hand_poses) == 2 and hand_poses[0] == hand_poses[1] and hand_poses[0] in {"FIST", "OPEN"}:
            if self.zoom_pose != hand_poses[0]:
                self.zoom_pose = hand_poses[0]
                self.zoom_started_ms = now_ms
            elif self.zoom_started_ms is not None and now_ms - self.zoom_started_ms >= self.config.zoom_stable_ms:
                self.zoom_action = "ZOOM_OUT" if self.zoom_pose == "FIST" else "ZOOM_IN"
                self.zoom_started_ms = now_ms + 10**9
        else:
            self.zoom_pose = None
            self.zoom_started_ms = None

        if thumb is None or index is None:
            self.lost_frames += 1
            if self.lost_frames > self.config.lost_frames:
                self.selected = False
                self.pinch_started_ms = None
                self.state = GestureState.IDLE
            return self.state

        self.lost_frames = 0
        pinch = hypot(thumb[0] - index[0], thumb[1] - index[1])
        self.release_frames = self.release_frames + 1 if pinch > self.config.pinch_exit else 0

        if not self.selected and pointer_over_object and pinch < self.config.pinch_enter:
            if self.pinch_started_ms is None:
                self.pinch_started_ms = now_ms
                self.state = GestureState.PINCHING
            elif now_ms - self.pinch_started_ms >= self.config.pinch_hold_ms:
                self.selected = True
                self.initial_pinch = pinch
                self.state = GestureState.GRABBING
        elif not self.selected:
            self.pinch_started_ms = None
            self.state = GestureState.HOVERING if pointer_over_object else GestureState.IDLE
        elif self.release_frames >= self.config.release_frames:
            self.selected = False
            self.pinch_started_ms = None
            self.state = GestureState.RELEASING
        elif hands >= 2:
            self.state = GestureState.ROTATING
        elif abs(pinch - self.initial_pinch) >= self.config.scale_delta:
            self.state = GestureState.SCALING
        else:
            self.state = GestureState.DRAGGING
        return self.state
