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

from threading import Thread, Lock, Event
from time import sleep

from dataclasses import dataclass
from typing import List, Tuple

import random

init_done = Event()

N_MODULES = 10
N_THERMISTORS_PER_MODULE = 13

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
    self.temp = new_temp
    self.min_temp = min(self.min_temp, new_temp)
    self.max_temp = max(self.max_temp, new_temp)
    print(f"Temperature for thermistor {self.n_module}:{self.n_therm} was updated to {self.temp}")
    
  def temp_callback(self, instance, value):
    self.temp_label.text = str(self.temp)
    
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

class MyApp(App):
    
  def build(self):
    self.modules_ui = GridLayout(rows=N_MODULES)

    init_done.wait()

    for m in range(N_MODULES):
      grid = GridLayout(cols=N_THERMISTORS_PER_MODULE)
      for t in range(N_THERMISTORS_PER_MODULE):
        with modules[m][0]:
          t_grid = GridLayout(rows=2, orientation="tb-lr")
          temp_label = Label(text="")
          modules[m][1][t].temp_label = temp_label
          modules[m][1][t].bind(temp=modules[m][1][t].temp_callback)
          t_grid.add_widget(Label(text=f"{modules[m][1][t].n_therm}"))
          t_grid.add_widget(temp_label)
          grid.add_widget(t_grid)
      self.modules_ui.add_widget(grid)
    
    # # MODULE 1
    # self.module1 = GridLayout(cols=N_THERMISTORS_PER_MODULE)


    # self.thermistor1 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor1.add_widget(Label(text="Temp."))
    # self.thermistor1.add_widget(Label(text="Thermistor ID"))

    # self.thermistor2 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor2.add_widget(Label(text="Temp."))
    # self.thermistor2.add_widget(Label(text="Thermistor ID"))

    # self.thermistor3 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor3.add_widget(Label(text="Temp."))
    # self.thermistor3.add_widget(Label(text="Thermistor ID"))

    # self.module1.add_widget(Label(text="Module 1"))
    # self.module1.add_widget(self.thermistor1)
    # self.module1.add_widget(self.thermistor2)
    # self.module1.add_widget(self.thermistor3)
    
    # self.modules.add_widget(self.module1)
    
    # # MODULE 2
    # self.module2 = GridLayout(cols=N_THERMISTORS_PER_MODULE)
    # self.module2.add_widget(Label(text="Module 2"))

    # self.thermistor4 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor4.add_widget(Label(text="Temp."))
    # self.thermistor4.add_widget(Label(text="Thermistor ID"))

    # self.thermistor5 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor5.add_widget(Label(text="Temp."))
    # self.thermistor5.add_widget(Label(text="Thermistor ID"))

    # self.thermistor6 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor6.add_widget(Label(text="Temp."))
    # self.thermistor6.add_widget(Label(text="Thermistor ID"))

    
    # self.module2.add_widget(self.thermistor4)
    # self.module2.add_widget(self.thermistor5)
    # self.module2.add_widget(self.thermistor6)
    
    # self.modules.add_widget(self.module2)
    return self.modules_ui

  
  # def update(self, *args):
  #   for n_m, m in enumerate(self.modules_ui.children):
  #     with modules[n_m]:
  #       for n_t, t in enumerate(m):
  #         print(t)


if __name__ == '__main__':
  app = MyApp()
  
  ui_thread = Thread(target=app.run)
  ui_thread.start()
  
  init_thermistors()
  
  for n_m in range(N_MODULES):
    with modules[n_m][0]:
      print(f"Module {n_m}")
      for t in modules[n_m][1]:
        print(f"\t{t}")
  
  # Serial loop
  while(True):
    sleep(5)
    for n_m in range(N_MODULES):
      with modules[n_m][0]:
        for t in modules[n_m][1]:
          t.update_temp(random.random() * random.randint(0,255))
  
  
  ui_thread.join()
