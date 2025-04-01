import json
import sys
from html import escape
from collections import defaultdict

def json_to_kindle_html(input_file, output_file):
    stats = {
        'total_read': 0,
        'entries_written': 0,
        'unique_words': defaultdict(int),
        'max_definitions': 0
    }
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    entries = []
    for entry in data:
        stats['total_read'] += 1
        word = escape(entry['word'])
        stats['unique_words'][word] += 1

        definition = escape(entry['definition'])
        entries.append(
            f"""<idx:entry name="default" scriptable="yes" spell="yes">
              <h5><dt><idx:orth>{word}</idx:orth></dt></h5>
              <dd>{definition}</dd>
            </idx:entry>
            <hr/>"""
        )
        stats['entries_written'] += 1
        
    stats['unique_word_count'] = len(stats['unique_words'])
    stats['max_definitions'] = max(stats['unique_words'].values(), default=0)

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
    
    return stats

if __name__ == "__main__":
    # Handle command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python converter.py input.json output.html")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    result = json_to_kindle_html(input_file, output_file)

    print(f"Total entries read: {result['total_read']}")
    print(f"Total entries written: {result['entries_written']}")
    print(f"Unique words: {result['unique_word_count']}")
    print(f"Max definitions for a single word: {result['max_definitions']}")
    