# Author: M. El Aabaribaoune (@um6p)

import os
import markdown
from weasyprint import HTML, CSS

def convert_to_pdf(input_file, output_file, is_txt=False):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    if is_txt:
        html_content = f"<html><body><pre>{content}</pre></body></html>"
    else:
        html_body = markdown.markdown(content, extensions=['tables', 'fenced_code', 'codehilite'])
        html_content = f"<html><body>{html_body}</body></html>"

    css = CSS(string='''
        @page { size: A4; margin: 2cm; }
        body { font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; }
        h1, h2, h3, h4 { color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; white-space: pre-wrap; font-size: 12px; font-family: Consolas, monospace; border: 1px solid #e9ecef; }
        code { background: #f8f9fa; padding: 2px 5px; border-radius: 3px; font-family: Consolas, monospace; font-size: 13px; color: #d63384; }
        pre code { color: inherit; background: transparent; padding: 0; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; font-size: 14px; }
        th, td { border: 1px solid #dee2e6; padding: 10px; text-align: left; }
        th { background-color: #f8f9fa; font-weight: bold; }
        blockquote { border-left: 4px solid #adb5bd; margin: 0 0 1rem; padding: 0.5rem 1rem; color: #6c757d; background: #f8f9fa; }
        a { color: #0d6efd; text-decoration: none; }
        li { margin-bottom: 5px; }
    ''')

    HTML(string=html_content).write_pdf(output_file, stylesheets=[css])
    print(f"Generated {output_file}")

os.chdir("docs")

convert_to_pdf("COMPILATION_AND_STATUS_SUMMARY.txt", "COMPILATION_AND_STATUS_SUMMARY.pdf", is_txt=True)
convert_to_pdf("EXPERIMENT_SETUP.md", "EXPERIMENT_SETUP.pdf")
convert_to_pdf("TROUBLESHOOTING_LOG.md", "TROUBLESHOOTING_LOG.pdf")
