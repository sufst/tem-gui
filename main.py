import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.clock import Clock

NUM_OF_MODULES = 10
THERMISTORS_PER_MODULE = 13

Builder.load_file("view/test.kv")

def decode_data(data):
  #TO BE IMPLEMENTED LATER
  return data

class Start(Screen):

  def add_buttons(self):
    new_btn = Button(text="hello")
    self.ids.grid_id.add_widget(new_btn)


class MyApp(App):
  
  def build(self):
    # self.layout = MyRootWidget()
    
    # self.segments = GridLayout(rows=NUM_OF_MODULES)
    # self.segment1 = GridLayout(cols=2)

    # self.thermistor1 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor1.add_widget(Label(text="Temp."))
    # self.thermistor1.add_widget(Label(text="Thermistor ID"))

    # self.thermistor2 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor2.add_widget(Label(text="Temp."))
    # self.thermistor2.add_widget(Label(text="Thermistor ID"))

    # self.thermistor3 = GridLayout(rows=2, orientation="tb-lr")
    # self.thermistor3.add_widget(Label(text="Temp."))
    # self.thermistor3.add_widget(Label(text="Thermistor ID"))

    # self.segments.add_widget(self.segment1)
    # self.layout.add_widget(self.segments)
    # print("TEST")
    return Start()
    # return self.segments

  
  # def update(self, *args):
  #   self.name


if __name__ == '__main__':
  app = MyApp()
  app.run()
