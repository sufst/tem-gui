import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label

thermistorsPerModule = 3


Builder.load_file("view/test.kv")

def decode_data(data):
  #TO BE IMPLEMENTED LATER
  return data

class Start(Screen):
  thermistorsPerModule = 3

  def add_buttons(self):
    new_btn = Button(text="hello")
    self.ids.grid_id.add_widget(new)
class MyApp(App):
  
  def build(self):
    return Start()
  
if __name__ == '__main__':
  thermistorsPerModule = 3
  MyApp().run()
