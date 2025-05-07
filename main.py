import os
from concurrent.futures import ThreadPoolExecutor
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivy.animation import Animation
from logic import process

class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None
        self.api_key = None
        self.is_fullscreen_output = False
        self.pre_fullscreen_state = {}
    
    def on_api_key_change(self, value):
        self.api_key = value.strip()
        self._update_analyze_button()
    
    def on_text_input(self, instance, value):
        self._update_analyze_button()
    
    def _update_analyze_button(self):
        self.ids.analyze_btn.disabled = not (bool(self.ids.input_text.text.strip()) and bool(self.api_key))
    
    def adjust_output_size(self, value):
        # Update the output container size
        self.ids.output_container.size_hint_y = value
        
        # Adjust the input area size to maintain proper balance
        if value < 0.9:  # Normal mode
            remaining_space = 0.8 - (value - 0.6)  # 0.8 is the total available space after fixed elements
            self.ids.input_text.size_hint_y = max(0.1, min(0.6, remaining_space))
            self.ids.input_text.opacity = 1
            self.ids.input_text.disabled = False
        else:  # Near full screen mode
            # Make input area minimal
            self.ids.input_text.size_hint_y = 0.1
        
        # Update the percentage label
        self.ids.output_size_label.text = f"{int(value * 100)}%"
        
        # Update fullscreen button text
        if value >= 0.95:  # Very close to fullscreen
            self.ids.fullscreen_btn.text = "Обычный режим"
        else:
            self.ids.fullscreen_btn.text = "На весь экран"
    
    def toggle_fullscreen_output(self):
        if not self.is_fullscreen_output:
            # Save current state
            self.pre_fullscreen_state = {
                'input_size': self.ids.input_text.size_hint_y,
                'slider_value': self.ids.output_size_slider.value,
                'output_size': self.ids.output_container.size_hint_y
            }
            
            # Hide/minimize other elements
            self.ids.input_text.opacity = 0
            self.ids.input_text.disabled = True
            self.ids.input_text.size_hint_y = 0.01
            
            # Maximize output area with animation
            anim = Animation(size_hint_y=1, duration=0.3)
            anim.start(self.ids.output_container)
            
            # Update slider value
            self.ids.output_size_slider.value = 1.0
            
            # Update button text
            self.ids.fullscreen_btn.text = "Обычный режим"
            
            self.is_fullscreen_output = True
        else:
            # Restore pre-fullscreen state
            self.ids.input_text.opacity = 1
            self.ids.input_text.disabled = False
            self.ids.input_text.size_hint_y = self.pre_fullscreen_state.get('input_size', 0.4)
            
            # Restore output container size with animation
            previous_size = self.pre_fullscreen_state.get('output_size', 0.6)
            anim = Animation(size_hint_y=previous_size, duration=0.3)
            anim.start(self.ids.output_container)
            
            # Update slider value
            self.ids.output_size_slider.value = previous_size
            
            # Update button text
            self.ids.fullscreen_btn.text = "На весь экран"
            
            self.is_fullscreen_output = False
    
    def on_analyze_press(self):
        if not self.ids.input_text.text.strip() or not self.api_key:
            return
        
        self.ids.analyze_btn.disabled = True
        self.ids.input_text.disabled = True
        self.ids.output_text.text = "Анализирую..."
        
        query = self.ids.input_text.text
        self.future = self.executor.submit(process, query, self.api_key)
        Clock.schedule_interval(self.check_future, 0.1)
    
    def copy_to_clipboard(self):
        output_text = self.ids.output_text.text
        if output_text and output_text != "Анализирую...":
            Clipboard.copy(output_text)
            # Optional: provide visual feedback that text was copied
            original_text = self.ids.copy_btn.text
            self.ids.copy_btn.text = "Скопировано!"
            
            # Reset button text after 2 seconds
            def reset_button_text(dt):
                self.ids.copy_btn.text = original_text
            
            Clock.schedule_once(reset_button_text, 2)
    
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
        kv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui.kv')
        Builder.load_file(kv_file)
        return MainWindow()

if __name__ == '__main__':
    AnalyzerApp().run()