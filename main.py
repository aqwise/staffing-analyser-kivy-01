from concurrent.futures import ThreadPoolExecutor
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from logic import process

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None
        self.api_key = None
    
    def on_api_key_change(self, value):
        self.api_key = value.strip()
        self._update_analyze_button()
    
    def on_text_input(self, instance, value):
        self._update_analyze_button()
    
    def _update_analyze_button(self):
        self.ids.analyze_btn.disabled = not (bool(self.ids.input_text.text.strip()) and bool(self.api_key))
    
    def on_analyze_press(self):
        if not self.ids.input_text.text.strip() or not self.api_key:
            return
        
        self.ids.analyze_btn.disabled = True
        self.ids.input_text.disabled = True
        self.ids.output_text.text = "Анализирую..."
        
        query = self.ids.input_text.text
        self.future = self.executor.submit(process, query, self.api_key)
        Clock.schedule_interval(self.check_future, 0.1)
    
    def check_future(self, dt):
        if self.future and self.future.done():
            try:
                result = self.future.result()
                self.ids.output_text.text = result
            except Exception as e:
                self.ids.output_text.text = f"Ошибка: {str(e)}"
            
            self.ids.analyze_btn.disabled = False
            self.ids.input_text.disabled = False
            self.future = None
            return False
        return True

class AnalyzerApp(App):
    def build(self):
        Builder.load_file('ui.kv')
        return MainWindow()

if __name__ == '__main__':
    AnalyzerApp().run()