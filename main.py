import os
import configparser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from os.path import join, expanduser

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.core.clipboard import Clipboard
from kivy.animation import Animation
from kivy.utils import get_color_from_hex

# Import our custom markdown renderer
from markdown_renderer import MarkdownViewer

from logic import process      # ваша функция анализа


class MainWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.future = None
        self.api_key = None
        self.is_fullscreen_output = False
        self.pre_fullscreen_state = {}
        self._last_md_result = ""          # исходный markdown-текст

    # ---------- события ввода / интерфейса ----------

    def on_api_key_change(self, value):
        self.api_key = value.strip()
        App.get_running_app().save_api_key(self.api_key)
        self._update_analyze_button()

    def on_text_input(self, instance, value):
        self._update_analyze_button()

    def _update_analyze_button(self):
        ok = bool(self.ids.input_text.text.strip()) and bool(self.api_key)
        self.ids.analyze_btn.disabled = not ok

    # ---------- масштаб области вывода ----------

    def adjust_output_size(self, value):
        self.ids.output_container.size_hint_y = value
        if value < 0.9:                 # обычный режим
            remaining = 0.8 - (value - 0.6)
            self.ids.input_text.size_hint_y = max(0.1, min(0.6, remaining))
            self.ids.input_text.opacity = 1
            self.ids.input_text.disabled = False
        else:                           # почти fullscreen
            self.ids.input_text.size_hint_y = 0.1

        self.ids.output_size_label.text = f"{int(value * 100)}%"
        self.ids.fullscreen_btn.text = "Обычный режим" if value >= 0.95 else "На весь экран"

    def toggle_fullscreen_output(self):
        if not self.is_fullscreen_output:
            self.pre_fullscreen_state = {
                'input_size': self.ids.input_text.size_hint_y,
                'slider_value': self.ids.output_size_slider.value,
                'output_size': self.ids.output_container.size_hint_y
            }
            self.ids.input_text.opacity = 0
            self.ids.input_text.disabled = True
            self.ids.input_text.size_hint_y = 0.01

            Animation(size_hint_y=1, duration=0.3).start(self.ids.output_container)
            self.ids.output_size_slider.value = 1.0
            self.ids.fullscreen_btn.text = "Обычный режим"
            self.is_fullscreen_output = True
        else:
            self.ids.input_text.opacity = 1
            self.ids.input_text.disabled = False
            self.ids.input_text.size_hint_y = self.pre_fullscreen_state.get('input_size', 0.4)

            previous_size = self.pre_fullscreen_state.get('output_size', 0.6)
            Animation(size_hint_y=previous_size, duration=0.3).start(self.ids.output_container)
            self.ids.output_size_slider.value = previous_size
            self.ids.fullscreen_btn.text = "На весь экран"
            self.is_fullscreen_output = False

    # ---------- анализ текста ----------

    def on_analyze_press(self):
        if not self.ids.input_text.text.strip() or not self.api_key:
            return

        self.ids.analyze_btn.disabled = True
        self.ids.input_text.disabled = True
        self._set_output_md("Анализирую...")

        query = self.ids.input_text.text
        self.future = self.executor.submit(process, query, self.api_key)
        Clock.schedule_interval(self.check_future, 0.1)

    def check_future(self, dt):
        if self.future and self.future.done():
            try:
                result_md = self.future.result()      # markdown из back-end'а
            except Exception as e:
                result_md = f"Ошибка: {e}"

            self._set_output_md(result_md)
            self.ids.analyze_btn.disabled = False
            self.ids.input_text.disabled = False
            self.future = None
            return False
        return True

    # ---------- вывод результата ----------

    def _set_output_md(self, md_text: str):
        """Отображает markdown через MarkdownViewer."""
        self._last_md_result = md_text
        # Устанавливаем текст в MarkdownViewer вместо конвертации в BBCode
        self.ids.md_viewer.markdown_text = md_text

    # ---------- копирование ----------

    def copy_to_clipboard(self):
        """Копирует исходный markdown текст в буфер обмена."""
        if self._last_md_result and self._last_md_result != "Анализирую...":
            # Копируем исходный текст markdown без преобразований
            Clipboard.copy(self._last_md_result)
            
            orig = self.ids.copy_btn.text
            self.ids.copy_btn.text = "Скопировано!"
            Clock.schedule_once(lambda dt: setattr(self.ids.copy_btn, "text", orig), 2)

    def copy_as_html(self):
        if self._last_md_result and self._last_md_result != "Анализирую...":
            from md_converter import md_to_html
            
            # Конвертируем Markdown в HTML
            html_content = md_to_html(self._last_md_result)
            
            try:
                if os.name == 'nt':
                    try:
                        import win32clipboard
                        
                        # Формат для HTML в буфере обмена Windows
                        html_format = """Version:0.9
StartHTML:00000097
EndHTML:{0}
StartFragment:00000133
EndFragment:{1}
<html>
<body>
<!--StartFragment-->{2}<!--EndFragment-->
</body>
</html>"""
                        
                        fragment = html_content
                        html = html_format.format(
                            97 + len(fragment) + 78,  # EndHTML
                            97 + len(fragment) + 55,  # EndFragment
                            fragment
                        )
                        
                        win32clipboard.OpenClipboard()
                        win32clipboard.EmptyClipboard()
                        win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, html_content.encode('utf-8'))
                        
                        # Устанавливаем HTML формат
                        html_fmt = win32clipboard.RegisterClipboardFormat("HTML Format")
                        win32clipboard.SetClipboardData(html_fmt, html.encode('utf-8'))
                        win32clipboard.CloseClipboard()
                        
                        orig = self.ids.copy_html_btn.text
                        self.ids.copy_html_btn.text = "OK!"
                        Clock.schedule_once(lambda dt: setattr(self.ids.copy_html_btn, "text", orig), 2)
                        return
                    except ImportError:
                        pass
                
                # Если специфичный для платформы способ не сработал, используем обычный
                Clipboard.copy(html_content)
                
            except Exception as e:
                print(f"Ошибка при копировании HTML: {e}")
                # Если что-то пошло не так, используем обычное копирование текста
                Clipboard.copy(self._last_md_result)
            
            orig = self.ids.copy_html_btn.text
            self.ids.copy_html_btn.text = "OK!"
            Clock.schedule_once(lambda dt: setattr(self.ids.copy_html_btn, "text", orig), 2)



class AnalyzerApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.config_path = join(expanduser('~'), '.staffingapp')

    def build(self):
        kv_file = Path(__file__).with_name('ui.kv')
        Builder.load_file(str(kv_file))
        main = MainWindow()

        saved = self.load_api_key()
        if saved:
            main.api_key = saved
            main.ids.api_key.text = saved
        return main

    # ---------- хранение API-ключа ----------

    def _ensure_config(self):
        cfg = configparser.ConfigParser()
        cfg.read(self.config_path)
        if not cfg.has_section('settings'):
            cfg.add_section('settings')
        return cfg

    def load_api_key(self):
        cfg = self._ensure_config()
        return cfg.get('settings', 'api_key', fallback=None)

    def save_api_key(self, api_key):
        try:
            cfg = self._ensure_config()
            cfg.set('settings', 'api_key', api_key)
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                cfg.write(f)
        except Exception as e:
            print(f"Ошибка при сохранении API ключа: {e}")


if __name__ == '__main__':
    AnalyzerApp().run()
