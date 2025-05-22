from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, ObjectProperty
from kivy.utils import get_color_from_hex
from kivy.lang import Builder
from kivy.graphics import Color, Rectangle
from kivy.uix.behaviors import ButtonBehavior
import re

# Define KV string for markdown label
Builder.load_string('''
<MarkdownLabel>:
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
    markup: True
    size_hint_y: None
    height: self.texture_size[1] + dp(5)
    text_size: self.width, None
    halign: 'left'
    valign: 'top'
    padding: [dp(5), dp(2)]
    
<MarkdownLinkLabel>:
    markup: True
    size_hint_y: None
    height: self.texture_size[1] + dp(5)
    text_size: self.width, None
    halign: 'left'
    valign: 'top'
    padding: [dp(5), dp(2)]
    color: self.link_color
    canvas.before:
        Color:
            rgba: self.background_color
        Rectangle:
            pos: self.pos
            size: self.size
''')

class MarkdownLabel(Label):
    background_color = ListProperty([0, 0, 0, 0])

class MarkdownLinkLabel(ButtonBehavior, Label):
    url = StringProperty('')
    background_color = ListProperty([0, 0, 0, 0])
    link_color = ListProperty([0.3, 0.6, 1, 1])
    
    def on_press(self):
        print(f"Link clicked: {self.url}")

class MarkdownViewer(ScrollView):
    """Widget for displaying markdown text with styling."""
    markdown_text = StringProperty('')
    
    def __init__(self, **kwargs):
        super(MarkdownViewer, self).__init__(**kwargs)
        self.container = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter('height'))
        self.add_widget(self.container)
        
        self.bind(markdown_text=self.render_markdown)
    
    def render_markdown(self, instance, value):
        """Render markdown text with custom styling."""
        self.container.clear_widgets()
        
        if not value:
            return
            
        # Split the content by lines for processing
        lines = value.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Headers
            if line.startswith('# '):
                self._add_header(line[2:], 1)
            elif line.startswith('## '):
                self._add_header(line[3:], 2) 
            elif line.startswith('### '):
                self._add_header(line[4:], 3)
            elif line.startswith('#### '):
                self._add_header(line[5:], 4)
            elif line.startswith('##### '):
                self._add_header(line[6:], 5)
            elif line.startswith('###### '):
                self._add_header(line[7:], 6)
                
            # Horizontal rule
            elif line == '---' or line == '***' or line == '___':
                self._add_horizontal_rule()
                
            # Bullet list
            elif line.startswith('* ') or line.startswith('- '):
                items = []
                
                while i < len(lines) and (lines[i].strip().startswith('* ') or lines[i].strip().startswith('- ')):
                    item_text = lines[i].strip()[2:]
                    items.append(item_text)
                    i += 1
                    
                self._add_bullet_list(items)
                continue  # Skip the increment at the end
                
            # Numbered list
            elif self._is_numbered_list_item(line):
                items = []
                
                while i < len(lines) and self._is_numbered_list_item(lines[i].strip()):
                    num, item_text = self._parse_numbered_item(lines[i].strip())
                    items.append((num, item_text))
                    i += 1
                    
                self._add_numbered_list(items)
                continue  # Skip the increment at the end
                
            # Normal paragraph
            elif line:
                text = line
                i += 1
                
                # Collect paragraph lines
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#') and not lines[i].strip() in ['---', '***', '___']:
                    text += '\n' + lines[i]
                    i += 1
                    
                self._add_paragraph(text)
                continue  # Skip the increment at the end
                
            # Empty line
            elif not line and i < len(lines) - 1:
                spacer = BoxLayout(size_hint_y=None, height=dp(10))
                self.container.add_widget(spacer)
            
            i += 1
    
    def _add_header(self, text, level):
        """Add a header to the container."""
        font_sizes = {
            1: dp(24),
            2: dp(20),
            3: dp(18),
            4: dp(16), 
            5: dp(14),
            6: dp(12)
        }
        
        # Process basic formatting
        text = self._process_formatting(text)
        
        label = MarkdownLabel(
            text=text,
            font_size=font_sizes.get(level, dp(16)),
            bold=True,
            color=get_color_from_hex('FFFFFF'),
            background_color=[0.15, 0.15, 0.15, 0.3] if level <= 2 else [0, 0, 0, 0]
        )
        self.container.add_widget(label)
        
    def _add_paragraph(self, text):
        """Add a paragraph to the container."""
        # Process basic formatting
        text = self._process_formatting(text)
        
        label = MarkdownLabel(
            text=text,
            font_size=dp(14),
            color=get_color_from_hex('EEEEEE'),
            background_color=[0, 0, 0, 0]
        )
        self.container.add_widget(label)
        
    def _add_horizontal_rule(self):
        """Add a horizontal rule."""
        rule = BoxLayout(size_hint_y=None, height=dp(20))
        with rule.canvas:
            Color(0.4, 0.4, 0.4, 1)
            Rectangle(pos=(rule.x, rule.center_y - dp(1)), size=(rule.width, dp(1)))
        self.container.add_widget(rule)
            
    def _add_bullet_list(self, items):
        """Add a bullet list."""
        list_container = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        list_container.bind(minimum_height=list_container.setter('height'))
        
        for item in items:
            box = BoxLayout(size_hint_y=None, height=dp(30))
            box.bind(minimum_height=box.setter('height'))
            
            bullet_label = Label(
                text='• ',
                size_hint=(None, None),
                width=dp(30),
                height=dp(30),
                color=get_color_from_hex('CCCCCC')
            )
            
            item_text = self._process_formatting(item)
            content_label = MarkdownLabel(
                text=item_text,
                size_hint=(1, None),
                color=get_color_from_hex('EEEEEE'),
                background_color=[0, 0, 0, 0]
            )
            
            box.add_widget(bullet_label)
            box.add_widget(content_label)
            list_container.add_widget(box)
            
        self.container.add_widget(list_container)
            
    def _add_numbered_list(self, items):
        """Add a numbered list."""
        list_container = GridLayout(cols=1, size_hint_y=None, spacing=dp(5))
        list_container.bind(minimum_height=list_container.setter('height'))
        
        for num, item in items:
            box = BoxLayout(size_hint_y=None, height=dp(30))
            box.bind(minimum_height=box.setter('height'))
            
            number_label = Label(
                text=f"{num}. ",
                size_hint=(None, None),
                width=dp(30),
                height=dp(30),
                color=get_color_from_hex('CCCCCC')
            )
            
            item_text = self._process_formatting(item)
            content_label = MarkdownLabel(
                text=item_text,
                size_hint=(1, None),
                color=get_color_from_hex('EEEEEE'),
                background_color=[0, 0, 0, 0]
            )
            
            box.add_widget(number_label)
            box.add_widget(content_label)
            list_container.add_widget(box)
            
        self.container.add_widget(list_container)
            
    def _process_formatting(self, text):
        """Process markdown formatting."""
        # Bold
        text = re.sub(r'\*\*(.*?)\*\*', r'[b]\1[/b]', text)
        
        # Italic
        text = re.sub(r'\*(.*?)\*', r'[i]\1[/i]', text)
        
        # Links [text](url)
        text = re.sub(r'\[(.*?)\]\((.*?)\)', r'[color=4F98FF][ref=\2]\1[/ref][/color]', text)
        
        # Code inline
        text = re.sub(r'`(.*?)`', r'[color=66FF66][bgcolor=333333]\1[/bgcolor][/color]', text)
        
        return text
        
    def _is_numbered_list_item(self, line):
        """Check if the line is a numbered list item."""
        if not line:
            return False
            
        match = re.match(r'^\d+\.\s', line)
        return bool(match)
            
    def _parse_numbered_item(self, line):
        """Parse a numbered list item."""
        match = re.match(r'^(\d+)\.\s(.*)', line)
        if match:
            return int(match.group(1)), match.group(2)
        return 1, line
