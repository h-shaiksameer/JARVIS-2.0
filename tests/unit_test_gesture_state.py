from tools.gesture_state import GestureState, GestureStateMachine


def update(machine, now_ms, *, over=True, pinch=0.02, hands=1, poses=None):
    return machine.update(
        pointer_over_object=over,
        thumb=(0.5, 0.5),
        index=(0.5 + pinch, 0.5),
        hands=hands,
        now_ms=now_ms,
        hand_poses=poses,
    )


def test_pinch_requires_two_seconds_before_selection():
    machine = GestureStateMachine()
    assert update(machine, 0) == GestureState.PINCHING
    assert update(machine, 1900) == GestureState.PINCHING
    assert update(machine, 2000) == GestureState.GRABBING
    assert machine.selected is True


def test_pinch_does_not_select_object_outside_pointer():
    machine = GestureStateMachine()
    update(machine, 0, over=False)
    update(machine, 2500, over=False)
    assert machine.selected is False
    assert machine.state == GestureState.IDLE


def test_scaling_does_not_release_until_clear_separation():
    machine = GestureStateMachine()
    update(machine, 0)
    update(machine, 2000)
    assert update(machine, 2050, pinch=0.08) == GestureState.SCALING
    update(machine, 2100, pinch=0.18)
    update(machine, 2200, pinch=0.18)
    assert update(machine, 2300, pinch=0.18) == GestureState.RELEASING
    assert machine.selected is False


def test_two_hands_rotate_only_after_selection():
    machine = GestureStateMachine()
    update(machine, 0, hands=2, poses=("OPEN", "OPEN"))
    assert machine.state != GestureState.ROTATING
    update(machine, 0)
    update(machine, 2000)
    assert update(machine, 2050, hands=2) == GestureState.ROTATING


def test_two_hand_fists_and_open_hands_zoom_after_stable_pose():
    machine = GestureStateMachine()
    update(machine, 0, poses=("FIST", "FIST"))
    update(machine, 899, poses=("FIST", "FIST"))
    update(machine, 900, poses=("FIST", "FIST"))
    assert machine.zoom_action == "ZOOM_OUT"

    update(machine, 1000, poses=None)
    update(machine, 1100, poses=("OPEN", "OPEN"))
    update(machine, 2000, poses=("OPEN", "OPEN"))
    assert machine.zoom_action == "ZOOM_IN"


def test_tracking_loss_cancels_after_timeout():
    machine = GestureStateMachine()
    update(machine, 0)
    update(machine, 2000)
    for _ in range(machine.config.lost_frames + 1):
        machine.update(pointer_over_object=False, thumb=None, index=None, now_ms=3000)
    assert machine.state == GestureState.IDLE
    assert machine.selected is False
