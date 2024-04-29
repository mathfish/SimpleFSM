from SimpleFSM.state import state_action, state_transition


def test_state_action_decorator():
    @state_action("my_state")
    def test_action(event_item, context_data):
        context_data["test_key"] = "test_value"

    assert hasattr(test_action, 'state_action')
    assert getattr(test_action, 'state_action') == "my_state"

def test_state_transition_decorator():
    @state_transition("my_state", ["dest_state_1", "dest_state_2"])
    def test_transition(event_item, context_data):
        return 'dest_state_1'
    
    assert hasattr(test_transition, 'state_transition')
    assert hasattr(test_transition, 'transition_dests')
    assert getattr(test_transition, 'state_transition') == 'my_state'
    assert getattr(test_transition, 'transition_dests') == ['dest_state_1', 'dest_state_2']

