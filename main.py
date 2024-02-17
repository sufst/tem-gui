import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.clock import Clock

from typing import List

NUM_OF_MODULES = 10
THERMISTORS_PER_MODULE = 13

def decode_data(data: List[bytes]) -> None:
  # This probably won't run. I am writing it directly in GH :(
  # Endianess

  # 4 byte ID
  id = data[0:4] #? Inclusive?

  match(id):
    case 0x1839F380:
      _decode_bmsbc(data[4:]) #? Does this work? Who knows
    case 0x1838F380:
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
    self.modules = GridLayout(rows=NUM_OF_MODULES)
    # MODULE 1
    self.module1 = GridLayout(cols=THERMISTORS_PER_MODULE)


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
    self.module2 = GridLayout(cols=THERMISTORS_PER_MODULE)
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
