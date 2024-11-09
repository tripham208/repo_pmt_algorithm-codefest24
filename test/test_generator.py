from game.match import SWITCH_WEAPON_ACTION, USE_WEAPON_ACTION
from lib.utils.generator import gen_action_data


def test_gen_action_data():
    result = gen_action_data(SWITCH_WEAPON_ACTION, child=True)
    assert result == {"action": "switch weapon", "characterType": "child"}

    result = gen_action_data(USE_WEAPON_ACTION, mountain_god=True, child=True, payload="test_payload")
    assert result == {"action": "use weapon", "payload": "test_payload", "characterType": "child"}

    result = gen_action_data(USE_WEAPON_ACTION, mountain_god=True, payload="test_payload")
    assert result == {"action": "use weapon", "payload": "test_payload"}

    result = gen_action_data("default action")
    assert result == {"action": "default action"}