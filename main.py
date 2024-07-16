from kivy.app import App, EventDispatcher
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget

from colour import Color
from dataclasses import dataclass
import random
import math
import serial
import sys
from threading import Thread, Lock, Event
from time import sleep
from typing import List, Tuple
import can # python-can
import struct

import logging

# Get the logger for the 'can' module
can_logger = logging.getLogger('can')

# Set the logging level to WARNING to suppress TRACE and DEBUG messages
can_logger.setLevel(logging.WARNING)


init_done = Event()
ui_done = Event()

N_MODULES = 9
N_THERMISTORS_PER_MODULE = 24
N_THERMISTORS = N_MODULES * N_THERMISTORS_PER_MODULE

dead_therms = [
  [],
  [3],
  [],
  [],
  [],
  [],
  [],
  [],
  []
]

SERIAL_PORT_LINUX = "/dev/ttyACM0"
SERIAL_PORT_WINDOW = "COM0"
SERIAL_PORT_MAC = ""

SERIAL_BAUD_RATE = 115200

BYTE_ORDER= "big"

COLOR_GRADIENT = list(Color("green").range_to(Color("red"),100))

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
  BMS_BC_ID: int = int("1839F380", 16)
  GENERAL_BC_ID: int = int("1838F380", 16)


class Thermistor(EventDispatcher):
  temp = NumericProperty(0)
  ch = StringProperty("-")
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

    if self.ch == "-":
      self.ch = "|"
    else:
      self.ch = "-"
    print(f"Temperature for thermistor {self.n_module}:{self.n_therm} was updated to {self.temp} °C")

  def get_temp_colour(self, value, min, max):
    if max - min != 0:
      proportion = (value - min) / (max - min)
      index = math.floor(proportion * (len(COLOR_GRADIENT) - 1))
      # print(f'Colour index: {index}, min: {self.min_temp}, max: {self.max_temp}, current: {self.temp}')
      colour = COLOR_GRADIENT[index].get_rgb() + (1,)
      return colour

  def temp_callback(self, instance, value):
    self.max_temp = max(self.temp, self.max_temp)
    self.min_temp = min(self.temp, self.min_temp)

    if self.n_therm in dead_therms[self.n_module]:
      self.temp_label.text = "N/A"
      self.temp_label.color = Color("blue").get_rgb()
    else:
      self.temp_label.text = str(self.temp) + "°C " + self.ch
      self.temp_label.color = self.get_temp_colour(self.temp, 10, 60)


    
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
    
    
modules: List[Module] = []
last_read_module: int
            
def decode_can_data(can_id: bytes, data: bytes) -> None:
  if (can_id >> 4) == (IDs.GENERAL_BC_ID >> 4):
    _decode_gbc(data)
  elif (can_id >> 4) == (IDs.BMS_BC_ID >> 4):
    _decode_bmsbc(data)
  else:
    print(f"Unknown CAN ID: {can_id}")
  

def _decode_bmsbc(payload: bytes) -> None:
  # Extract values from payload
  n_m = int.from_bytes(payload[0:1], byteorder=BYTE_ORDER, signed=False)
  modules[n_m].min_temp = int.from_bytes(payload[1:2], byteorder=BYTE_ORDER, signed=True)
  modules[n_m].max_temp = int.from_bytes(payload[2:3], byteorder=BYTE_ORDER, signed=True)
  modules[n_m].avg_temp = int.from_bytes(payload[3:4], byteorder=BYTE_ORDER, signed=True)
  # Check value with checksum
  #checksum = int.from_bytes(payload[7:8], byteorder=BYTE_ORDER, signed=False)
  #if checksum != (n_m + modules[n_m].min_temp + modules[n_m].max_temp + modules[n_m].avg_temp + 0x41) % 256: # 0x41 is a magic number
  #  print(f"Checksum failed for module {n_m}")
  print(f"Module {n_m+1}\n\tMin: {modules[n_m].min_temp} °C\n\tAvg: {modules[n_m].avg_temp} °C\n\tMax: {modules[n_m].max_temp} °C")

def _decode_gbc(payload: bytes) -> None:
  rel_id = int.from_bytes(payload[0:2], byteorder=BYTE_ORDER, signed=False)
  print(rel_id)
  n_m = math.floor(rel_id / 80)
  print(n_m)
  n_t = rel_id % 80
  print(n_t)
  new_temp = int.from_bytes(payload[2:3], byteorder=BYTE_ORDER, signed=True)
  print(new_temp)
  
  with modules[n_m-1].lock:
    modules[n_m-1].thermistors[n_t].update_temp(float(new_temp))

class Start(Screen):
  pass

def init_thermistors():
  global modules
  for n_m in range(N_MODULES):
    therm_list = []
    for n_t in range(N_THERMISTORS_PER_MODULE):
      therm_list.append(Thermistor(n_m, n_t))
    modules.append(Module(n_m+1, therm_list))
  print("All thermistors initialised")
  reset_thermistors()
  
def reset_thermistors():
  global modules
  for m in modules:
    with m.lock:
      for t in m.thermistors:
        t.update_temp(0.0)
  print("All thermistors reset")

def add_border(widget, colour=(1, 0, 0, 1), thickness=1): #! Doesn't work
    with widget.canvas.before:
        Color(colour)
        Rectangle(pos=widget.pos, size=widget.size, width=thickness)
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
          modules[m].thermistors[t].bind(temp=modules[m].thermistors[t].temp_callback,
                                         ch=modules[m].thermistors[t].temp_callback)
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
        
  try:
    if sys.platform.startswith('linux'):
      #bus = can.interface.Bus(interface='slcan', channel=SERIAL_PORT_LINUX, bitrate=SERIAL_BAUD_RATE)
      bus = can.Bus(interface="socketcan", channel="can0")
    elif sys.platform.startswith('win32'):
      bus = can.interface.Bus(interface='slcan', channel=SERIAL_PORT_WINDOW, bitrate=SERIAL_BAUD_RATE)
    elif sys.platform.startswith('darwin'):
      print("Not implemented for MacOS")
      set_therm_error()
      return
    else:
      print(f"Unrecognised platform: {sys.platform}")
      set_therm_error()
      return
    
  except can.CanInitializationError as e:
    print(f"An error occurred when opening the can bus: {e}")
    set_therm_error()
    return
  except serial.SerialException as e:
    print(f"An error occurred when opening the serial port: {e}")
    set_therm_error()
    return
  except ValueError as e:
    print(f"Invalid parameters for can bus: {e}")
    set_therm_error()
    return
    
  while(not get_app_quit()):
    try:
      message = bus.recv(timeout=1.0)
      if message is not None:
        #print(message)
        decode_can_data(message.arbitration_id, message.data)
        
    except can.CanError as e:
          print(f"CAN error: {e}")
          set_therm_error()
          break
        
  bus.shutdown()
  print("CAN thread finished cleanly")
  
# For testing only, generates random CAN data, not currently in use
def generate_random_can_data(n_m: int) -> bytes:
    # Randomly choose between BMS_BC_ID and GENERAL_BC_ID
    can_id = random.choice([IDs.BMS_BC_ID, IDs.GENERAL_BC_ID])
    
    if can_id == IDs.BMS_BC_ID:
        min_temp = random.randint(-20, 80)
        max_temp = random.randint(min_temp, 80)
        avg_temp = random.randint(min_temp, max_temp)
        num_thermistors = random.randint(1, N_THERMISTORS_PER_MODULE)
        highest_therm_id = random.randint(0, N_THERMISTORS_PER_MODULE - 1)
        lowest_therm_id = random.randint(0, highest_therm_id)
        checksum = (n_m + min_temp + max_temp + avg_temp + num_thermistors + 
                    highest_therm_id + lowest_therm_id) % 256
        # Match module message byte pattern
        payload = struct.pack('>BbbbBBBB', n_m, min_temp, max_temp, avg_temp,
                              num_thermistors, highest_therm_id, lowest_therm_id, checksum)
    else:  # GENERAL_BC_ID
        therm_id = random.randint(0, N_THERMISTORS - 1)
        temp = random.randint(-20, 80)
        num_thermistors = random.randint(1, N_THERMISTORS)
        min_temp = random.randint(-20, temp)
        max_temp = random.randint(temp, 80)
        highest_therm_id = random.randint(0, N_THERMISTORS_PER_MODULE - 1)
        lowest_therm_id = random.randint(0, highest_therm_id)
        # Match general message byte pattern
        payload = struct.pack('>HbBbbBB', therm_id, temp, num_thermistors, min_temp,
                              max_temp, highest_therm_id, lowest_therm_id)
    
    return can_id.to_bytes(4, byteorder=BYTE_ORDER) + payload

if __name__ == '__main__':
  app = MyApp()
  
  serial_thread = Thread(target=serial_thread_target)
  serial_thread.start()
  
  app.run()
  
  set_app_quit(True)
  
  serial_thread.join()
