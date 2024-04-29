from SimpleFSM import FSM, State, state_action, state_transition
import pytest


@pytest.fixture
def TestFSM():
    class TestFSM(FSM):
        state_one = State("state_one", is_start=True)
        state_two = State("state_two")

        @staticmethod 
        @state_action("state_one")
        def state_one_proc(event_item, context_data):
            context_data['value'] = 1

        @staticmethod
        @state_transition("state_one", ["state_two"])
        def state_one_trans(event_item, context_data):
            return "state_two"

        @staticmethod 
        @state_action("state_two")
        def state_two_proc(event_item, context_data):
            context_data['value'] = 2

        @staticmethod
        @state_transition("state_two", ["state_one"])
        def state_two_trans(event_item, context_data):
            return "state_one"

    return TestFSM

def test_fsm_has_states_saved(TestFSM):
    assert set(TestFSM.states.keys()) == {'state_one', 'state_two'}
    assert TestFSM.states['state_one']._is_start 

def test_fsm_start(TestFSM, tmp_path):
    test_fsm = TestFSM(checkpoint_file_path=tmp_path, user_context_data={'value': None})
    test_fsm.start(['event'])

    assert test_fsm.current_state.name == 'state_two'
    assert test_fsm.user_context_data['value'] == 2

    test_fsm.start(['event'])

    assert test_fsm.current_state.name == 'state_one'
    assert test_fsm.user_context_data['value'] == 1

    assert (tmp_path / 'TestFSM_checkpoint.pkl').exists()

def test_unique_states():
    with pytest.raises(AttributeError) as attr_err:
        class TestFSM(FSM):
            state_one = State("state_one", is_start=True)
            state_two = State("state_one")

            @staticmethod 
            @state_action("state_one")
            def state_one_proc(event_item, context_data):
                context_data['value'] = 1

            @staticmethod
            @state_transition("state_one", ["state_two"])
            def state_one_trans(event_item, context_data):
                return "state_two"

            @staticmethod 
            @state_action("state_two")
            def state_two_proc(event_item, context_data):
                context_data['value'] = 2

            @staticmethod
            @state_transition("state_two", ["state_one"])
            def state_two_trans(event_item, context_data):
                return "state_one" 

def test_unique_states_actions():
    with pytest.raises(AttributeError) as attr_err:
        class TestFSM(FSM):
            state_one = State("state_one", is_start=True)
            state_two = State("state_two")

            @staticmethod 
            @state_action("state_one")
            def state_one_proc(event_item, context_data):
                context_data['value'] = 1

            @staticmethod
            @state_transition("state_one", ["state_two"])
            def state_one_trans(event_item, context_data):
                return "state_two"

            @staticmethod 
            @state_action("state_one")
            def state_two_proc(event_item, context_data):
                context_data['value'] = 2

            @staticmethod
            @state_transition("state_two", ["state_one"])
            def state_two_trans(event_item, context_data):
                return "state_one"

def test_unique_states_transitions():
    with pytest.raises(AttributeError) as attr_err:
        class TestFSM(FSM):
            state_one = State("state_one", is_start=True)
            state_two = State("state_two")

            @staticmethod 
            @state_action("state_one")
            def state_one_proc(event_item, context_data):
                context_data['value'] = 1

            @staticmethod
            @state_transition("state_one", ["state_two"])
            def state_one_trans(event_item, context_data):
                return "state_two"

            @staticmethod 
            @state_action("state_two")
            def state_two_proc(event_item, context_data):
                context_data['value'] = 2

            @staticmethod
            @state_transition("state_one", ["state_one"])
            def state_two_trans(event_item, context_data):
                return "state_one"  

def test_dest_states_exist():
    with pytest.raises(AttributeError) as attr_err:
        class TestFSM(FSM):
            state_one = State("state_one", is_start=True)
            state_two = State("state_two")

            @staticmethod 
            @state_action("state_one")
            def state_one_proc(event_item, context_data):
                context_data['value'] = 1

            @staticmethod
            @state_transition("state_one", ["state_two"])
            def state_one_trans(event_item, context_data):
                return "state_two"

            @staticmethod 
            @state_action("state_two")
            def state_two_proc(event_item, context_data):
                context_data['value'] = 2

            @staticmethod
            @state_transition("state_two", ["state_three"])
            def state_two_trans(event_item, context_data):
                return "state_one" 

def test_all_states_have_transition():
    with pytest.raises(AttributeError) as attr_err:
        class TestFSM(FSM):
            state_one = State("state_one", is_start=True)
            state_two = State("state_two")

            @staticmethod 
            @state_action("state_one")
            def state_one_proc(event_item, context_data):
                context_data['value'] = 1

            @staticmethod
            @state_transition("state_one", ["state_two"])
            def state_one_trans(event_item, context_data):
                return "state_two"

            @staticmethod 
            @state_action("state_two")
            def state_two_proc(event_item, context_data):
                context_data['value'] = 2