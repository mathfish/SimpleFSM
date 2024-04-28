from typing import List, Callable

def state_action(state_name):
  def enriched_action(func: Callable):
    setattr(func, 'state_action', state_name)
    return func

  return enriched_action 

def state_transition(state_name:str, dests: List):
  def enriched_transition(func: Callable):
    setattr(func, 'state_transition', state_name)
    setattr(func, 'transition_dests', dests)
    return func
  
  return enriched_transition

class State:
  def __init__(self, name:str, is_start: bool=False):
    self.name = name.lower()
    self._is_start = is_start
    self.action = None
    self.transition = None
    self.context_data = None

  @property
  def action(self):
    return self._action 

  @action.setter
  def action(self, func: Callable)->None:
    self._action = func

  @property
  def transition(self):
    return self._transition

  @transition.setter
  def transition(self, func: Callable)->None:
    self._transition = func

  def do_action(self, event_item, context_data)->None:
    if self.action:
      _ = self.action(event_item, context_data)

  def do_transition(self, event_item, context_data)->None:
      return self.transition(event_item, context_data)