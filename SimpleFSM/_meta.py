from SimpleFSM.state import State
import networkx as nx

class MetaFSM(type):
  def __new__(cls, name, base, attrs):
    new_cls = super().__new__(cls, name, base, attrs)
    
    if name != 'FSM':
      new_cls.states = dict()
      new_cls.start_state_name = None
      
      # Find State Objects using state name
      for attr_name, value in attrs.items():
        if isinstance(value, State):
          if value.name in new_cls.states:
            raise AttributeError(f"State {value.name} already defined")
          
          if value._is_start:
            if new_cls.start_state_name is not None:
              raise AttributeError("Only one State object can be defined as the start")
            new_cls.start_state_name = value.name

          new_cls.states[value.name] = value

      if new_cls.start_state_name is None:
        raise AttributeError("There must be one State object defined as the start")

      # Find State Action using annotation
      for attr_name, value in attrs.items():
        if isinstance(value, staticmethod) and hasattr(action:=value.__func__, 'state_action'):
          state_name = getattr(action, 'state_action')
          if state_name not in new_cls.states: 
            raise AttributeError(f"No corresponding State named {state_name} found for action")
          elif new_cls.states[state_name].action is not None:
            raise AttributeError(f"Only one action can be defined for state {state_name}")
    
          new_cls.states[state_name].action = action

      # Find State Transitions using annotation
      num_states_with_transition = set()
      for attr_name, value in attrs.items():
        if isinstance(value, staticmethod) and hasattr(transition:=value.__func__, 'state_transition'):
          state_name = getattr(transition, 'state_transition')
          transition_dests = getattr(transition, 'transition_dests')
          if state_name not in new_cls.states: 
            raise AttributeError(f"No corresponding State named {state_name} found for transition")
          elif new_cls.states[state_name].transition is not None:
            raise AttributeError(f"Only one transition can be defined for state {state_name}")

          new_cls.states[state_name].transition = transition
          setattr(new_cls.states[state_name], 'transition_dests', transition_dests)
          num_states_with_transition.add(state_name)

      if len(missing_transitions := set(new_cls.states.keys()) - num_states_with_transition) > 0:
        raise AttributeError(f"The following states do not have transitions set: {missing_transitions}")

      FSM_graph = nx.DiGraph()
      for state_name, state_obj in new_cls.states.items():
        FSM_graph.add_node(state_name)
        for dest_state in state_obj.transition_dests:
          FSM_graph.add_edge(state_name, dest_state)

      setattr(new_cls, 'FSM_graph', FSM_graph)

    return new_cls
