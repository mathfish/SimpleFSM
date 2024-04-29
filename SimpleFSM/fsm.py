from datetime import datetime
from pathlib import Path
import pickle
import sys
from types import MappingProxyType
import warnings
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, Generator, Tuple
from SimpleFSM._meta import MetaFSM
from SimpleFSM.state import State 
  
class FSM(metaclass=MetaFSM):

  __default_contexts = {'curent_state'}

  def __init__(self, user_context_data:Dict=None, checkpoint_file_path:str=None, 
               start_from_checkpoint_file:str=None, 
               checkpoint_every:int=None, replace_checkpoint=True):
    
    if start_from_checkpoint_file is None:
      self.__context_data = dict()
      # save current_state name
      self.__context_data['current_state'] = self.start_state_name
      self._load_user_context_data(user_context_data)

      # set current state object
      self.current_state = self.start_state_name
      self._events_processed = 0
      self.checkpoint_file_path_base =\
        self._setup_checkpoint(checkpoint_file_path)
      self.checkpoint_every = checkpoint_every
      self._replace_checkpoint = replace_checkpoint
    else:
      self._start_from_checkpoint(start_from_checkpoint_file)

    self.event_generator = None

  def _load_user_context_data(self, user_context_data):
    for default_context in FSM.__default_contexts:
      if user_context_data.get(default_context) is not None:
        raise AttributeError(f"The key for {default_context} in context_fieldsis protected")

    self.__context_data.update(user_context_data)

  def _setup_checkpoint(self, checkpoint_file_path):
    def_path = "./data"
    chk_pt_name = chk_pt_name = self.__class__.__name__ + "_checkpoint.pkl"

    if checkpoint_file_path is not None:
      chk_pt_path = Path(checkpoint_file_path)
    else:
      chk_pt_path = Path(def_path)

    return chk_pt_path / chk_pt_name
    
  def _start_from_checkpoint(self, start_from_checkpoint_file):
    chk_pt = Path(start_from_checkpoint_file)

    if chk_pt.exists():
      with open(chk_pt, 'rb') as f:
        checkpoint_data = pickle.load(f)
        if self._loaded_checkpoint_isvalid(checkpoint_data):
          self.__context_data = checkpoint_data.pop("context_data")
          for k, v in checkpoint_data.items():
            setattr(self, k, v)
          self.current_state = self.__context_data['current_state']

        else:
          raise AttributeError("Loaded checkpoint data not valid for current state machine context")
    else:
      raise AttributeError(f"No checkpoint file exists at {start_from_checkpoint_file}")

  def _loaded_checkpoint_isvalid(self, checkpoint):
    return checkpoint['context_data']['current_state'] in self.states.keys()

  @property   
  def context_data(self)->Dict:
    return MappingProxyType(self.__context_data)

  @property 
  def current_state(self)->State:
    return self._current_state

  @current_state.setter
  def current_state(self, next_state:str)->None:
    self._current_state =\
      self.states[next_state]
    self.__context_data['current_state'] = next_state

  @property
  def event_generator(self)->Generator:
    return self._event_generator

  @event_generator.setter
  def event_generator(self, event_generator:Generator):
    self._event_generator = event_generator

  def start(self, event_generator:Generator):
    self.event_generator = event_generator

    try:
      for event in self.event_generator:
        self._process_event(event) 
        if self.checkpoint_every is not None\
          and self._events_processed % self.checkpoint_every == 0:
            self._create_checkpoint()
    except KeyboardInterrupt:
      print("Processing interrupted by user.")
    finally:
      self._create_checkpoint()
      try:
        print("save and exit")
        sys.exit()
      except SystemExit:
        # avoid exception message from IPython 
        pass 

  def _process_event(self, event_item):
    next_state_name = self.current_state.do_transition(event_item, self.__context_data)
    self.current_state = next_state_name
    self.current_state.do_action(event_item, self.__context_data)
    self._events_processed += 1
    

  def plot_graph(self, fig_size:Tuple=(12, 10)):
    fig, ax = plt.subplots(figsize=fig_size)
    nx.draw(self.FSM_graph, 
            with_labels=True, 
            node_size=1000, 
            node_color="skyblue", 
            font_size=12, 
            font_weight="bold",
            ax=ax)
    plt.show()


  def _create_checkpoint(self):
    if not self._replace_checkpoint:
     chk_pt_name = self.__class__.__name__ \
     + datetime.now().strftime("_%Y-%m-%d_%H:%M:%S_checkpoint.pkl")
     chk_pt_url = self.checkpoint_file_path_base.with_name(chk_pt_name)
    else:
     chk_pt_url = self.checkpoint_file_path_base
     checkpoint_data = self._build_checkpoint() 

    try: 
      with open(chk_pt_url, 'wb') as f:
        pickle.dump(checkpoint_data, f) 
    except Exception as e:
      warnings.warn(f"An error was encountered creating checkpoint: {e}")

  def _build_checkpoint(self):
    checkpoint_data = dict()
    checkpoint_data['context_data'] = self.__context_data
    checkpoint_data['_events_processed'] = self._events_processed
    checkpoint_data['checkpoint_file_path_base'] = self.checkpoint_file_path_base
    checkpoint_data['checkpoint_every'] = self.checkpoint_every
    checkpoint_data['_replace_checkpoint'] = self._replace_checkpoint

    return checkpoint_data
