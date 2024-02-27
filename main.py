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
from colour import Color
import serial
import sys
import random
import math


init_done = Event()
ui_done = Event()

N_MODULES = 10
N_THERMISTORS_PER_MODULE = 24
N_THERMISTORS = N_MODULES * N_THERMISTORS_PER_MODULE

SERIAL_PORT_LINUX = "/dev/ttyACM0"
SERIAL_PORT_WINDOW = "COM1"
SERIAL_PORT_MAC = ""

SERIAL_BAUD_RATE = 115200

BYTE_ORDER= "big"

# COLOR_GRADIENT = list(Color("blue").range_to(Color("white"),50)) + list(Color("white").range_to(Color("red"),50))
COLOR_GRADIENT = list(Color("white").range_to(Color("red"),100))

app_quit = False
app_quit_lock = Lock()

example_bms_payload: bytes = b'\x00\x14\x2b\x1f\x18\x17\x00\xce'
example_gen_payload: bytes = b'\x00\x17\x2b\x18\x14\x2b\x17\x00'

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
    self.max_temp = max(self.temp, self.max_temp)
    self.min_temp = min(self.temp, self.min_temp)

    self.temp_label.text = str(self.temp) + "°C"
    if self.max_temp - self.min_temp != 0:
      proportion = (self.temp - self.min_temp) / (self.max_temp - self.min_temp)
      index = math.floor(proportion * (len(COLOR_GRADIENT) - 1))

      # print(f'Colour index: {index}, min: {self.min_temp}, max: {self.max_temp}, current: {self.temp}')
      colour = COLOR_GRADIENT[index].get_rgb() + (1,)
      self.temp_label.color = colour


    
class Module(EventDispatcher):
  max_temp = NumericProperty(0)
  avg_temp = NumericProperty(0)
  min_temp = NumericProperty(0)
  
  def __init__(self, n_m, therms):
    self.n_module = n_m
    self.lock = Lock()
    self.thermistors: List[Thermistor] = therms
    self.label = None
    
  def temp_callback(self, instance, value):
    self.label.text = f"[b]Module {self.n_module}[/b]\nMin: {self.min_temp}\nAvg: {self.avg_temp}\nMax:{self.max_temp}"
    
    
#modules: List[Tuple[Lock, List[Thermistor]]] = []
modules: List[Module] = []

last_read_module: int

def decode_data(data: bytes) -> None:
  # This probably won't run. I am writing it directly in GH :(
  # Endianess

  # 4 byte ID
  id = data[0:4]

  match(int.from_bytes(id, byteorder=BYTE_ORDER, signed=False)):
    case IDs.BMS_BC_ID:
      _decode_bmsbc(data[4:]) #? Does this work? Who knows
    case IDs.GENERAL_BC_ID:
      _decode_gbc(data[4:]) #?
    case _:
      pass # Not a TEM message
  

def _decode_bmsbc(payload: bytes) -> None:
  n_m = int.from_bytes(payload[0:1], byteorder=BYTE_ORDER, signed=False)
  modules[n_m].min_temp = int.from_bytes(payload[1:2], byteorder=BYTE_ORDER, signed=True)
  modules[n_m].max_temp = int.from_bytes(payload[2:3], byteorder=BYTE_ORDER, signed=True)
  modules[n_m].avg_temp = int.from_bytes(payload[3:4], byteorder=BYTE_ORDER, signed=True)
  print(f"Module {n_m}\n\tMin: {modules[n_m].min_temp} °C\n\tAvg: {modules[n_m].avg_temp} °C\n\tMax: {modules[n_m].max_temp} °C")

def _decode_gbc(payload: bytes) -> None:
  rel_id = int.from_bytes(payload[0:2], byteorder=BYTE_ORDER, signed=False)
  print(rel_id)
  n_m = math.floor(rel_id / N_THERMISTORS_PER_MODULE)
  print(n_m)
  n_t = rel_id % N_THERMISTORS_PER_MODULE
  print(n_t)
  new_temp = int.from_bytes(payload[2:3], byteorder=BYTE_ORDER, signed=True)
  print(new_temp)
  
  with modules[n_m].lock:
    modules[n_m].thermistors[n_t].update_temp(float(new_temp))

class Start(Screen):
  pass

def init_thermistors():
  global modules
  for n_m in range(N_MODULES):
    therm_list = []
    for n_t in range(N_THERMISTORS_PER_MODULE):
      therm_list.append(Thermistor(n_m, n_t))
    modules.append(Module(n_m, therm_list))
  print("All thermistors initialised")
  reset_thermistors()
  
def reset_thermistors():
  global modules
  for m in modules:
    with m.lock:
      for t in m.thermistors:
        t.update_temp(0.0)
  print("All thermistors reset")

def add_border(widget, color=(1, 0, 0, 1), thickness=1): #! Doesn't work
    with widget.canvas.before:
        Color(color)  # Set border color
        Rectangle(
            pos=widget.pos,  # Adjust position for inner border
            size=widget.size
        )
    return widget

class MyApp(App):
    
  def build(self):
    self.title = "TEM GUI"
    self.icon = r"stag.svg"
    
    self.root_layout = GridLayout(rows=N_MODULES+1)
    self.root_layout.bind(minimum_height=self.root_layout.setter('height'))

    init_done.wait()
    
    header = BoxLayout(orientation="horizontal", spacing=0, padding=0)
    for i in range (-1, N_THERMISTORS_PER_MODULE):
      if(i == -1):
        header.add_widget(Label(text=""))
      else: 
        header.add_widget(Label(text=f"Therm.\n{i}", bold=True, halign="center", valign="center"))
      
    self.root_layout.add_widget(header)

    for m in range(N_MODULES):
      module_layout = BoxLayout(orientation='horizontal')
      
      #m_label = Label(text=f"Module {m}", bold=True, halign="center", valign="center")
      m_label = Label(text="", halign="center", valign="center", markup=True)
      modules[m].label = m_label
      modules[m].bind(min_temp=modules[m].temp_callback, avg_temp=modules[m].temp_callback, max_temp=modules[m].temp_callback)
        
      module_layout.add_widget(m_label)
      for t in range(N_THERMISTORS_PER_MODULE):
        with modules[m].lock:
          thermistor_layout = GridLayout(rows=1, spacing=0, orientation="tb-lr", padding=0)
          temp_label = Label(text="", halign="center", valign="center")
          modules[m].thermistors[t].temp_label = temp_label
          modules[m].thermistors[t].bind(temp=modules[m].thermistors[t].temp_callback)
          #thermistor_layout.add_widget(Label(text=f"{modules[m].thermistors[t].n_therm}"))
          thermistor_layout.add_widget(temp_label)
          module_layout.add_widget(thermistor_layout)
      self.root_layout.add_widget(module_layout)
    
    ui_done.set()
    # self.root.add_widget(self.layout)
    return self.root_layout
  
def set_therm_error():
  for n_m in range(N_MODULES):
    with modules[n_m].lock:
      for t in modules[n_m].thermistors:
        t.update_temp(sys.float_info.min_exp)
  
def serial_thread_target():
  init_thermistors()
  
  init_done.set()
  ui_done.wait()
  
  for n_m in range(N_MODULES):
    with modules[n_m].lock:
      print(f"Module {n_m}")
      for t in modules[n_m].thermistors:
        print(f"\t{t}")
        
  ############################################################################### Serial Decode
  # Serial loop
  # sp: serial.Serial
  
  # plat = sys.platform
  
  # try:
  #   if plat.startswith('linux'):
  #     sp = serial.Serial(SERIAL_PORT_LINUX, SERIAL_BAUD_RATE)
  #   elif plat.startswith('win32'):
  #     sp = serial.Serial(SERIAL_PORT_WINDOW, SERIAL_BAUD_RATE)
  #   elif plat.startswith('darwin'):
  #     sp = serial.Serial(SERIAL_PORT_MAC, SERIAL_BAUD_RATE)
  #   else:
  #     print(f"Unrecognised platform: {plat}")
  #     set_therm_error()
  #     return
  # except serial.SerialException as e:
  #   print(f"An error occurred when opening the serial port: {e}")
  #   set_therm_error()
  #   return
  # except ValueError as e:
  #   print(f"Invalid parameters for serial connection: {e}")
  #   set_therm_error()
  #   return
  
  # if(not sp.is_open()):
  #   sp.open()
  
  # print("Serial port opened successfully")
  
  # while(sp.is_open() and not get_app_quit()):
  #   decode_data(sp.readline())
    
  # sp.close()
  ###############################################################################
  
  ############################################################################### Example Messages      
  # _decode_gbc(example_gen_payload)
  # _decode_bmsbc(example_bms_payload)
  # return
  ###############################################################################

  ############################################################################### Random Values
  while(not get_app_quit()):
    for n_m in range(N_MODULES):
      modules[n_m].min_temp = round(random.random() * random.randint(0,255), 2)
      modules[n_m].avg_temp = round(random.random() * random.randint(0,255), 2)
      modules[n_m].max_temp = round(random.random() * random.randint(0,255), 2)
      with modules[n_m].lock:
        for t in modules[n_m].thermistors:
          t.update_temp(round(random.random() * random.randint(0,255), 2))
    sleep(1)
  ###############################################################################
          
  print("Serial thread finished cleanly")

if __name__ == '__main__':
  app = MyApp()
  
  serial_thread = Thread(target=serial_thread_target)
  serial_thread.start()
  
  app.run()
  
  set_app_quit(True)
  
  serial_thread.join()
