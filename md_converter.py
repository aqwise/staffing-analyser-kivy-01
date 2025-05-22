import mistune

def md_to_html(markdown_text):
    """Convert Markdown to HTML."""
    html_output = mistune.html(markdown_text)
    return html_output

def md_to_formatted_text(markdown_text):
    """Convert Markdown to formatted plain text (for chat apps)."""
    # This simply preserves the markdown syntax for apps that support it
    return markdown_text
