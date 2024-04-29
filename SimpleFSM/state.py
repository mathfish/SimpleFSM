from typing import List, Callable

def state_action(state_name):
  '''Decorator to designate a state action that is to be attached to State object

    Parameters:
    state_name (str) - Name of the State object this action applies to

    The wrapped method must have the signature: 
      <any_method_name>(event_item, context_data)->None

    Wrapped Methods Parameters:
    event_item - Event item the FSM is processing and passed to State
    context_data (Dict) - Dictionary to store state for processing by the State object action. 
      Users can read and write as needed.
  '''
  def enriched_action(func: Callable):
    # set state_action attribute for identification
    setattr(func, 'state_action', state_name)
    return func

  return enriched_action 

def state_transition(state_name:str, dests: List):
  '''Decorator to designate a state transition that is to be attached to a State object
  
    Parameters:
    state_name (str) - Name of the State object this action applies to
    dests (List) - A list of state names that this transition logic
      routes to. These must be defined states

    The wrapped method must have the signature: 
      <any_method_name>(event_item, context_data)->str

    Wrapped Methods Parameters:
    event_item - Event item the FSM is processing and passed to State
    context_data (Dict) - Dictionary to store state for processing by the State object action. 
      Users can read and write as needed.

    Returns - Name of the State object this transition is routing to
  '''

  def enriched_transition(func: Callable):
    # set state_transition attribute for identification
    setattr(func, 'state_transition', state_name)
    setattr(func, 'transition_dests', dests)
    return func
  
  return enriched_transition

class State:
  '''Class to represent a State node'''
  def __init__(self, name:str, is_start: bool=False):
    ''' Initialize object with the name of the State and if it is the start

    The State object has other attributes set externally, such as the action and transition. 
    Users should only set two arguments shown here in the signature. 

    Parameters: 
    name (str) - Name of the State. This same name must be used for all 
      associated state actions and transitions
    is_start (bool) - Boolean to indicate if this State is the start node. 
      Only one State node can be the start
    '''

    self.name = name.lower()
    self._is_start = is_start
    self.action = None
    self.transition = None

  @property
  def action(self):
    '''Get state action'''
    return self._action 

  @action.setter
  def action(self, func: Callable)->None:
    '''Set the State Action - Called by Framework
    
    Users should not set the action directly but use the annotation state_action
    '''
    self._action = func

  @property
  def transition(self):
    '''Get state transition'''
    return self._transition

  @transition.setter
  def transition(self, func: Callable)->None:
    '''Set the State Transition - Called by Framework
    
    Users should not set the transition directly but use the annotation state_transition
    '''
    self._transition = func

  def do_action(self, event_item, context_data)->None:
    '''Performs the action for the State

    Called by FSM framework. 

    Parameters:
    event_item - Event item the FSM is processing and passed to State
    context_data (Dict) - Dictionary to store state for processing by the State object action. 
      Users can read and write to this as needed. 
    '''

    if self.action:
      _ = self.action(event_item, context_data)

  def do_transition(self, event_item, context_data)->None:
      '''Performs the transition for the State

    Called by FSM framework. 

    Parameters:
    event_item - Event item the FSM is processing and passed to State
    context_data (Dict) - Dictionary to store state for processing by the State object transition. 
      Users can read and write to this as needed. 
    '''
      return self.transition(event_item, context_data)