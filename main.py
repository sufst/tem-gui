import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.clock import Clock

from dataclasses import dataclass
from typing import List

N_MODULES = 10
N_THERMISTORS_PER_MODULE = 13

@dataclass
class IDs:
  BMS_BC_ID: int = 406451072 # int("1839F380", 16)
  GENERAL_BC_ID: int = 406385536 # int("1838F380", 16)

class Module:
  def __init__(self) -> None:
    self.thermistors:float = [0.0] * N_THERMISTORS_PER_MODULE
    
modules: List[Module] = [Module()] * N_MODULES

last_read_module: int

def decode_data(data: List[bytes]) -> None:
  # This probably won't run. I am writing it directly in GH :(
  # Endianess

  # 4 byte ID
  id = data[0:4] #? Inclusive?

  match(int.from_bytes(id, byteorder="big", signed=False)):
    case IDs.BMS_BC_ID:
      _decode_bmsbc(data[4:]) #? Does this work? Who knows
    case IDs.GENERAL_BC_ID:
      _decode_gbc(data[4:]) #?
    case _:
      pass
  
  #TO BE IMPLEMENTED LATER

def _decode_bmsbc(payload: List[bytes]) -> None:
  pass

def _decode_gbc(payload: List[bytes]) -> None:
  pass

class Start(Screen):
  pass


class MyApp(App):
  
  def build(self):
    self.modules = GridLayout(rows=N_MODULES)
    # MODULE 1
    self.module1 = GridLayout(cols=N_THERMISTORS_PER_MODULE)


    self.thermistor1 = GridLayout(rows=2, orientation="tb-lr")
    self.thermistor1.add_widget(Label(text="Temp."))
    self.thermistor1.add_widget(Label(text="Thermistor ID"))

    self.thermistor2 = GridLayout(rows=2, orientation="tb-lr")
    self.thermistor2.add_widget(Label(text="Temp."))
    self.thermistor2.add_widget(Label(text="Thermistor ID"))

    self.thermistor3 = GridLayout(rows=2, orientation="tb-lr")
    self.thermistor3.add_widget(Label(text="Temp."))
    self.thermistor3.add_widget(Label(text="Thermistor ID"))

    self.module1.add_widget(Label(text="Module 1"))
    self.module1.add_widget(self.thermistor1)
    self.module1.add_widget(self.thermistor2)
    self.module1.add_widget(self.thermistor3)
    
    self.modules.add_widget(self.module1)
    
    # MODULE 2
    self.module2 = GridLayout(cols=N_THERMISTORS_PER_MODULE)
    self.module2.add_widget(Label(text="Module 2"))

    self.thermistor4 = GridLayout(rows=2, orientation="tb-lr")
    self.thermistor4.add_widget(Label(text="Temp."))
    self.thermistor4.add_widget(Label(text="Thermistor ID"))

    self.thermistor5 = GridLayout(rows=2, orientation="tb-lr")
    self.thermistor5.add_widget(Label(text="Temp."))
    self.thermistor5.add_widget(Label(text="Thermistor ID"))

    self.thermistor6 = GridLayout(rows=2, orientation="tb-lr")
    self.thermistor6.add_widget(Label(text="Temp."))
    self.thermistor6.add_widget(Label(text="Thermistor ID"))

    
    self.module2.add_widget(self.thermistor4)
    self.module2.add_widget(self.thermistor5)
    self.module2.add_widget(self.thermistor6)
    
    self.modules.add_widget(self.module2)
    return self.modules

  
  # def update(self, *args):
  #   self.name


if __name__ == '__main__':
  app = MyApp()
  app.run()
