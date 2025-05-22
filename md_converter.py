import mistune
from html2text import HTML2Text
from io import StringIO

def md_to_html(markdown_text):
    """Convert Markdown to HTML."""
    html_output = mistune.html(markdown_text)
    return html_output

def md_to_rtf(markdown_text):
    """Convert Markdown to RTF format (simplified version)."""
    # First convert to HTML
    html = mistune.html(markdown_text)
    
    # Basic RTF header
    rtf = r'{\rtf1\ansi\ansicpg1251\deff0\deflang1049'
    rtf += r'{\fonttbl{\f0\fswiss\fprq2\fcharset0 Arial;}}'
    rtf += r'{\colortbl;\red0\green0\blue0;\red0\green0\blue255;}'
    
    # Convert HTML to RTF (simplified)
    h = HTML2Text()
    h.ignore_links = False
    h.body_width = 0  # No wrapping
    text = h.handle(html)
    
    # Simple conversion of basic formatting
    text = text.replace('**', r'{\b ').replace('**', r'}')
    text = text.replace('*', r'{\i ').replace('*', r'}')
    
    # Add the text to the RTF
    rtf += r'\viewkind4\uc1\pard\f0\fs24 '
    rtf += text.replace('\n', r'\par ')
    rtf += r'}'
    
    return rtf

def md_to_formatted_text(markdown_text):
    """Convert Markdown to formatted plain text (for chat apps)."""
    # This simply preserves the markdown syntax for apps that support it
    return markdown_text
