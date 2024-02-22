import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.app import EventDispatcher
from kivy.properties import NumericProperty
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from threading import Thread, Lock, Event
from time import sleep
from kivy.graphics import Color, Rectangle
from dataclasses import dataclass
from typing import List, Tuple
from kivy.uix.widget import Widget
import random

init_done = Event()

N_MODULES = 10
N_THERMISTORS_PER_MODULE = 24

app_quit = False
app_quit_lock = Lock()

def get_app_quit():
  with app_quit_lock:
    return app_quit

def set_app_quit(b):
  global app_quit
  with app_quit_lock:
    app_quit = b

@dataclass
class IDs:
  BMS_BC_ID: int = 406451072 # int("1839F380", 16)
  GENERAL_BC_ID: int = 406385536 # int("1838F380", 16)


class Thermistor(EventDispatcher):
  temp = NumericProperty(0)
  
  def __init__(self, n_m, n_t):
    self.n_module = n_m
    self.n_therm = n_t
    self.max_temp = 0.0
    self.min_temp = 0.0
    self.temp_label = None
    
  def __repr__(self) -> str:
    return f"{self.n_module}:{self.n_therm} = {self.temp} °C\t(min: {self.min_temp}, max: {self.max_temp})"
    
  def update_temp(self, new_temp: float):
    new_temp_rounded = round(new_temp, 2)
    self.temp = new_temp_rounded
    self.min_temp = min(self.min_temp, new_temp_rounded)
    self.max_temp = max(self.max_temp, new_temp_rounded)
    print(f"Temperature for thermistor {self.n_module}:{self.n_therm} was updated to {self.temp}")
    
  def temp_callback(self, instance, value):
    self.temp_label.text = str(self.temp) + "°C"
    
modules: List[Tuple[Lock, List[Thermistor]]] = []

last_read_module: int

def decode_data(data: bytes) -> None:
  # This probably won't run. I am writing it directly in GH :(
  # Endianess

  # 4 byte ID
  id = data[0:4]

  match(int.from_bytes(id, byteorder="big", signed=False)):
    case IDs.BMS_BC_ID:
      _decode_bmsbc(data[4:]) #? Does this work? Who knows
    case IDs.GENERAL_BC_ID:
      _decode_gbc(data[4:]) #?
    case _:
      pass
  

def _decode_bmsbc(payload: bytes) -> None:
  pass

def _decode_gbc(payload: bytes) -> None:
  pass

class Start(Screen):
  pass

def init_thermistors():
  global modules
  for n_m in range(N_MODULES):
    therm_list = []
    for n_t in range(N_THERMISTORS_PER_MODULE):
      therm_list.append(Thermistor(n_m, n_t))
    modules.append((Lock(), therm_list))
  print("All thermistors initialised")
  reset_thermistors()
  init_done.set()
  
def reset_thermistors():
  global modules
  for m in modules:
    with m[0]:
      for t in m[1]:
        t.update_temp(0.0)
  print("All thermistors reset")

def add_border(widget, color=(1, 0, 0, 1), thickness=2): #! Doesn't work
    with widget.canvas.before:
        Color(*color)  # Set border color
        Rectangle(
            pos=(widget.x + thickness, widget.y + thickness),  # Adjust position for inner border
            size=(widget.width - 2 * thickness, widget.height - 2 * thickness)
        )
    return widget

class MyApp(App):
    
  def build(self):
    self.root_layout = GridLayout(rows=N_MODULES)
    self.root_layout.bind(minimum_height=self.root_layout.setter('height'))

    init_done.wait()

    for m in range(N_MODULES):
      module_layout = BoxLayout(orientation='horizontal')
      module_layout = add_border(module_layout)
      module_layout.add_widget(Label(text=f"Module {m}", bold=True))
      for t in range(N_THERMISTORS_PER_MODULE):
        with modules[m][0]:
          thermistor_layout = GridLayout(rows=2, spacing=5, orientation="tb-lr")
          temp_label = Label(text="")
          modules[m][1][t].temp_label = temp_label
          modules[m][1][t].bind(temp=modules[m][1][t].temp_callback)
          thermistor_layout.add_widget(Label(text=f"{modules[m][1][t].n_therm}"))
          thermistor_layout.add_widget(temp_label)
          module_layout.add_widget(thermistor_layout)
      self.root_layout.add_widget(module_layout)
    
    # self.root.add_widget(self.layout)
    return self.root_layout
  
def serial_thread_target():
  init_thermistors()
  
  for n_m in range(N_MODULES):
    with modules[n_m][0]:
      print(f"Module {n_m}")
      for t in modules[n_m][1]:
        print(f"\t{t}")
  
  # Serial loop
  while(not get_app_quit()):
    sleep(1)
    for n_m in range(N_MODULES):
      with modules[n_m][0]:
        for t in modules[n_m][1]:
          t.update_temp(random.random() * random.randint(0,255))
          
  print("Serial thread finished cleanly")

if __name__ == '__main__':
  app = MyApp()
  
  serial_thread = Thread(target=serial_thread_target)
  serial_thread.start()
  
  app.run()
  
  set_app_quit(True)
  
  serial_thread.join()
