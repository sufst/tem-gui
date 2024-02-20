import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.clock import Clock

from dataclasses import dataclass
from typing import List, Tuple

N_MODULES = 10
N_THERMISTORS_PER_MODULE = 13

@dataclass
class IDs:
  BMS_BC_ID: int = 406451072 # int("1839F380", 16)
  GENERAL_BC_ID: int = 406385536 # int("1838F380", 16)


class Thermistor:
  def __init__(self, n_m, n_t):
    self.n_module = n_m
    self.n_therm = n_t
    self.temp = 0.0
    self.id_label = Label(text=f"ID: {self.n_therm}")
    self.temp_label = Label(text=f"{self.temp}°C")
    self.widget_grid = GridLayout(rows=2, orientation="tb-lr")
    self.widget_grid.add_widget(self.id_label)
    self.widget_grid.add_widget(self.temp_label)
    
  def update_temp(self, new_temp: float):
    self.temp = new_temp
    
modules: List[Tuple[GridLayout, List[Thermistor]]]

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
    for n_t in range(N_THERMISTORS_PER_MODULE):
      modules[n_m][0] = GridLayout(cols=N_THERMISTORS_PER_MODULE)
      modules[n_m][1][n_t] = Thermistor(n_m, n_t)

def add_labels(dest: GridLayout, m: Tuple[GridLayout, List[Thermistor]]):
  for t in m[1]:
    m[0].add_widget(t.id_label)
    m[0].add_widget(t.temp_label)

  dest.add_widget(m[0])

class MyApp(App):
    
  
  def build(self):
    self.modules_ui = GridLayout(rows=N_MODULES)
    
    init_thermistors()
    
    
    
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
  #   self.name


if __name__ == '__main__':
  app = MyApp()
  app.run()
