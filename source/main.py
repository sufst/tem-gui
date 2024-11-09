""" Main module for the TEM GUI application.

This module contains the main application class and the serial thread target function.
The serial thread target function reads data from the CAN bus and updates the GUI with the temperature values.

Example:
  To run the application, simply run the module:

    $ python main.py

"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

import random
import serial
import sys
from threading import Thread, Lock, Event
from time import sleep
from typing import List
import can # python-can
import logging

from components.Module import Module
from components.Thermistor import Thermistor
from utils.randomiser import generate_random_can_data
from utils.constants import *
from utils.can_decoder import decode_can_data
from utils.data_logger import DataLogger

# Get the logger for the 'can' module
can_logger = logging.getLogger('can')

# Set the logging level to WARNING to suppress TRACE and DEBUG messages
can_logger.setLevel(logging.WARNING)

# App execution mode flag
RANDOM_DATA_DEFINITION = True   # Set to True to generate random data; False to read data from the CAN bus
ENABLE_LOGGING = True           # Set to True to enable loggings

init_done = Event()
ui_done = Event()

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

modules: List[Module] = []
last_read_module: int

class Start(Screen):
  pass

def init_thermistors():
  global modules
  for module_id in range(N_MODULES):
    therm_list = []
    for therm_id in range(N_THERMISTORS_PER_MODULE):
      therm_list.append(Thermistor(module_id, therm_id))
    modules.append(Module(module_id+1, therm_list))
  print("All thermistors initialised")
  reset_thermistors()

def reset_thermistors():
  global modules
  for m in modules:
    with m.lock:
      for t in m.thermistors:
        t.update_temp(0.0)
  print("All thermistors reset")

def set_therm_error():
  for module_id in range(N_MODULES):
    with modules[module_id].lock:
      for t in modules[module_id].thermistors:
        t.update_temp(sys.float_info.min_exp)

class MyApp(App):
  def build(self):
    self.title = TITLE
    self.icon = ICON

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
      modules[m].bind(min_temp=modules[m].temp_callback, avg_temp=modules[m].temp_callback, max_temp=modules[m].temp_callback, number_of_thermistors=modules[m].temp_callback)
      module_layout.add_widget(m_label)

      for t in range(N_THERMISTORS_PER_MODULE):
        with modules[m].lock:
          thermistor_layout = GridLayout(rows=1, spacing=0, orientation="tb-lr", padding=0)
          temp_label = Label(text="", halign="center", valign="center")
          modules[m].thermistors[t].temp_label = temp_label
          modules[m].thermistors[t].bind(temp=modules[m].thermistors[t].temp_callback)
          thermistor_layout.add_widget(temp_label)
          module_layout.add_widget(thermistor_layout)
      self.root_layout.add_widget(module_layout)
    
    ui_done.set()
    # self.root.add_widget(self.layout)
    return self.root_layout

def serial_thread_target():
  init_thermistors()

  init_done.set()
  ui_done.wait()

  for module_id in range(N_MODULES):
    with modules[module_id].lock:
      print(f"Module {module_id}")
      print(f"Thermistors: {len(modules[module_id].thermistors)}")
      for t in modules[module_id].thermistors:
        print(f"\t{t}")
  if not RANDOM_DATA_DEFINITION:
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
    if RANDOM_DATA_DEFINITION:
      module_id = random.randint(0, N_MODULES - 1)
      random_can_data = generate_random_can_data(module_id, modules)
      can_id = int.from_bytes(random_can_data[:4], byteorder=BYTE_ORDER)
      payload = random_can_data[4:]

      decode_can_data(can_id, payload, modules)

      sleep(0.01)
    else:
      try:
        message = bus.recv(timeout=1.0)

        if message is not None:
          #print(message)
          decode_can_data(message.arbitration_id, message.data, modules)

      except can.CanError as e:
        print(f"CAN error: {e}")
        set_therm_error()
        break

      bus.shutdown()
  print("CAN thread finished cleanly")


if __name__ == '__main__':
  app = MyApp()
  data = DataLogger("csv")

  serial_thread = Thread(target=serial_thread_target)
  logger_thread = Thread(target=data.logging_thread, args=(modules, get_app_quit))

  serial_thread.start()
  if ENABLE_LOGGING:
    logger_thread.start()

  app.run()

  set_app_quit(True)

  serial_thread.join()
  if ENABLE_LOGGING:
    logger_thread.join()
