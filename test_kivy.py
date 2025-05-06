from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.uix.button import Button

class TestApp(App):
    test_property = BooleanProperty(False)
    
    def build(self):
        return Button(text='Test Button')

if __name__ == '__main__':
    TestApp().run()