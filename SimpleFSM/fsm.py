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
  '''Base for finite state machine'''

  __default_contexts = {'curent_state'}

  def __init__(self, user_context_data:Dict=dict(), checkpoint_file_path:str=None, 
               start_from_checkpoint_file:str=None, checkpoint_every:int=None, 
               replace_checkpoint=True):
    '''Initialize base finite state machine object

    Parameters: 
    user_context_data (Dict) - Dictionary to hold state that shared between 
        and used in actions and transitions
    checkpoint_file_path (str) - The file path where to save the pickle checkpoint 
        of the FSM. If not specified will save in ./data directory, creating one if necessary
    start_from_checkpoint_file (str) - The file path where to load FSM from a checkpoint. 
        If this file exists, all other arguments are ignored and the FSM uses the checkpoint data
    checkpoint_every (int) - The number of actions to save out the FSM state. If None, the FSM state
        is only saved at shutdown
    replace_checkpoint (bool) - If True, then a standard name is used for the checkpoint file and 
        always overrides the previous checkpoint file. If False, a timestamp is used to maintain 
        previous checkpoint files. 
    
    '''
    
    # if no checkpoint file found, then new FSM 
    if start_from_checkpoint_file is None:
      self.user_context_data = user_context_data

      # create context data to hold FSM system data
      self.__context_data = dict()
      # save current_state name
      self.__context_data['current_state'] = self.start_state_name
      # set current state object
      self._set_current_state(self.start_state_name)

      self._events_processed = 0

      self.checkpoint_file_path_base =\
        self._setup_checkpoint(checkpoint_file_path)
      self.checkpoint_every = checkpoint_every
      self._replace_checkpoint = replace_checkpoint
    else:
      # users provides checkpoint file, then ony update state data with it
      self._start_from_checkpoint(start_from_checkpoint_file)

    self.event_generator = None

  def _setup_checkpoint(self, checkpoint_file_path):
    '''Set up checkpoint location 
    
    Uses the user-defined checkpoint location or the default
    location ./data. If this directory, doesn't exist it is 
    created. 
    '''
    def_path = "./data"
    chk_pt_name = self.__class__.__name__ + "_checkpoint.pkl"

    if checkpoint_file_path is not None:
      chk_pt_path = Path(checkpoint_file_path)
    else:
      chk_pt_path = Path(def_path)
      if not chk_pt_path.exists():
        chk_pt_path.mkdir(parents=True)

    return chk_pt_path / chk_pt_name
    
  def _start_from_checkpoint(self, start_from_checkpoint_file):
    '''Restore FSM state from checkpoint'''

    chk_pt = Path(start_from_checkpoint_file)

    if chk_pt.exists():
      with open(chk_pt, 'rb') as f:
        checkpoint_data = pickle.load(f)
        if self._loaded_checkpoint_isvalid(checkpoint_data):
          self.__context_data = checkpoint_data.pop("context_data")
          # if user_content_data exists load it else an empty dict()
          self.user_context_data = checkpoint_data.pop('user_context_data')\
              if 'user_context_data' in checkpoint_data else dict()
          
          # all other items, as add top leve key-value pairs
          for k, v in checkpoint_data.items():
            setattr(self, k, v)

          # Set the current state of FSM to that in checkpoint
          self._set_current_state(self.__context_data['current_state'])

        else:
          raise AttributeError("Loaded checkpoint data not valid for current state machine context")
    else:
      raise AttributeError(f"No checkpoint file exists at {start_from_checkpoint_file}")

  def _loaded_checkpoint_isvalid(self, checkpoint):
    '''Verify the current State node from before is still valid'''
    return checkpoint['context_data']['current_state'] in self.states.keys()

  @property   
  def context_data(self)->Dict:
    '''Shows system context data - read only view'''
    return MappingProxyType(self.__context_data)

  @property 
  def current_state(self)->State:
    '''Returns the current State Object'''
    return self._current_state

  def _set_current_state(self, next_state:str)->None:
    '''Sets the Current State Object - Should only be done by FSM framework'''
    self._current_state =\
      self.states[next_state]
    self.__context_data['current_state'] = next_state

  @property
  def event_generator(self)->Generator:
    '''Return user supplied generator of events'''
    return self._event_generator

  @event_generator.setter
  def event_generator(self, event_generator:Generator):
    '''Set event genrator for FSM to process'''
    self._event_generator = event_generator

  def start(self, event_generator:Generator):
    '''Starts the FSM processing incoming events from supplied generator'''

    self.event_generator = event_generator

    try:
      for event in self.event_generator:
        self._process_event(event)

        # save checkpoint if every nth checkpoint saving defined 
        if self.checkpoint_every is not None\
          and self._events_processed % self.checkpoint_every == 0:
            self._create_checkpoint()
    except KeyboardInterrupt:
      print("Processing interrupted by user.")
    finally:
      # save system state into checkpoint
      self._create_checkpoint()
      try:
        print("save and exit")
        sys.exit()
      except SystemExit:
        # avoid exception message from IPython 
        pass 

  def _process_event(self, event_item):
    '''Processes events through FSM logic
    
    1. Event item received and transition logic applied based on current state
    2. Transition logic applied first and routes to appropriate next State
    3. State action applied
    4. Next event received ... 
    '''

    next_state_name = self.current_state.do_transition(event_item, self.user_context_data)
    self._set_current_state(next_state_name)
    self.current_state.do_action(event_item, self.user_context_data)
    # keep track of how many events are processed
    self._events_processed += 1

  def plot_graph(self, fig_size:Tuple=(12, 10)):
    '''Plot graph of FSM network
    
    Nodes are States and edges are directed transitions between States

    Parameters:
    fig_size (Tuple(int, int)) - Sets the size of the figure
    '''

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
    '''Create checkpoint file'''

    # If not replacing checkpoints, name has datestamp applied
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
    '''Builds dictionary for pickling'''
    checkpoint_data = dict()
    checkpoint_data['context_data'] = self.__context_data
    checkpoint_data['user_context_data'] = self.user_context_data
    checkpoint_data['_events_processed'] = self._events_processed
    checkpoint_data['checkpoint_file_path_base'] = self.checkpoint_file_path_base
    checkpoint_data['checkpoint_every'] = self.checkpoint_every
    checkpoint_data['_replace_checkpoint'] = self._replace_checkpoint

    return checkpoint_data
