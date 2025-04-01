import json
from html import escape

def json_to_kindle_html(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = []
    for entry in data:
        word = escape(entry['word'])
        definition = escape(entry['definition'])
        entries.append(
            f"""<idx:entry name="default" scriptable="yes" spell="yes">
              <h5><dt><idx:orth>{word}</idx:orth></dt></h5>
              <dd>{definition}</dd>
            </idx:entry>
            <hr/>"""
        )
    
    html_template = f"""<html xmlns:idx="https://kindlegen.s3.amazonaws.com/AmazonKindlePublishingGuidelines.pdf">
      <head><meta charset="utf-8"></head>
      <body>
        <mbp:frameset>
          {"".join(entries)}
        </mbp:frameset>
      </body>
    </html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)

# Usage
json_to_kindle_html('data/tagalog_dict.json', 'res/dictionary.html')