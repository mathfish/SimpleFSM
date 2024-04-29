from SimpleFSM.state import State
import networkx as nx
from typing import Dict, Set

class MetaFSM(type):
  def __new__(cls, name, base, attrs):
    new_cls = super().__new__(cls, name, base, attrs)
    
    # No need to process base class
    if name != 'FSM':
      new_cls.states = dict()
      new_cls.start_state_name = None
      
      # Find State Objects using state name and set in class level state dictionary
      cls.set_states(attrs, new_cls)

      if new_cls.start_state_name is None:
        raise AttributeError("There must be one State object defined as the start")

      # Find State Action using annotation
      cls.set_state_actions(attrs, new_cls)

      # Set State Transitions from annotations
      states_with_transition = cls.set_state_transitions(attrs, new_cls)

      # Verify all states have a transition   
      if len(missing_transitions := set(new_cls.states.keys()) - states_with_transition) > 0:
        raise AttributeError(f"The following states do not have transitions set: {missing_transitions}")

      # Create Network Graph        
      cls.create_state_graph(new_cls)

    return new_cls

  @staticmethod  
  def create_state_graph(new_cls)->None:
      '''Create graph image and set in new Class'''
      FSM_graph = nx.DiGraph()

      # Create node for all defined states
      for state_name, state_obj in new_cls.states.items():
        FSM_graph.add_node(state_name)
        # Create directed edge for all destinations states
        for dest_state in state_obj.transition_dests:
          FSM_graph.add_edge(state_name, dest_state)

      # set graph as attribute  
      setattr(new_cls, 'FSM_graph', FSM_graph)

  @staticmethod
  def set_states(attrs:Dict, new_cls)->None:
      '''Set up State objects for use'''

      for attr_name, value in attrs.items():
        # Check for State type
        if isinstance(value, State):
          # States must be uniquely defined (ie, by name)
          if value.name in new_cls.states:
            raise AttributeError(f"State {value.name} already defined")
          
          # Check if State is the starting point and that only one State is the start
          if value._is_start:
            if new_cls.start_state_name is not None:
              raise AttributeError("Only one State object can be defined as the start")
            new_cls.start_state_name = value.name

          # Set State object in class dictionary by name
          new_cls.states[value.name] = value

  @staticmethod
  def set_state_actions(attrs:Dict, new_cls)->None:
      '''Set action to be invokved by State'''

      for attr_name, value in attrs.items():
        # Check for static methods with 'state_action' attribute
        if isinstance(value, staticmethod) and hasattr(action:=value.__func__, 'state_action'):
          state_name = getattr(action, 'state_action')
          
          # state listed must be an existing one
          if state_name not in new_cls.states: 
            raise AttributeError(f"No corresponding State named {state_name} found for action")
          # all states can have only one action defined
          elif new_cls.states[state_name].action is not None:
            raise AttributeError(f"Only one action can be defined for state {state_name}")
    
          # set state action in State object  
          new_cls.states[state_name].action = action

  @staticmethod
  def set_state_transitions(attrs:Dict, new_cls)->Set:
      '''Sets transition function to State Object'''

      # keep track of all states with transition set  
      states_with_transition = set()

      for attr_name, value in attrs.items():
        # Check for static methods with 'state_transition' attribute
        if isinstance(value, staticmethod) and hasattr(transition:=value.__func__, 'state_transition'):
          state_name = getattr(transition, 'state_transition')
          transition_dests = getattr(transition, 'transition_dests')

          # state listed must be an existing one
          if state_name not in new_cls.states: 
            raise AttributeError(f"No corresponding State named {state_name} found for transition")
          # all states can only have one transition defined
          elif new_cls.states[state_name].transition is not None:
            raise AttributeError(f"Only one transition can be defined for state {state_name}")
          # defined destination states must be valid states
          elif len(non_defined_sates := set(transition_dests) - set(new_cls.states.keys())) > 0:
            raise AttributeError(f"The following {state_name} transition destination states are not defined states: {non_defined_sates}")

          # set transition method in State object  
          new_cls.states[state_name].transition = transition
          # add destinations to State object
          setattr(new_cls.states[state_name], 'transition_dests', transition_dests)
        
          states_with_transition.add(state_name)

      return states_with_transition
