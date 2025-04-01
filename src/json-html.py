import json
import sys
import re
from html import escape
from collections import defaultdict

# def extract_conjugations(definition):
#     """Extract conjugated forms from parentheses pattern"""
#     match = re.match(r'^(\w+)\s+\(([^)]+)\)\s+v\., inf\.', definition)
#     return [word.strip() for word in match.group(1).split(',')] if match else []

# Enhanced regex pattern
CONJUGATION_PATTERN = re.compile(
    r'\(+((?:\([^)]+\)|[^),])+?(?:,\s*(?:\([^)]+\)|[^),])+?){2})\)'  # Handles nested conjugations
    r'(\s*\d+\.)?\s*v\.,?\s*inf\.',  # Handles numbered prefixes
    re.IGNORECASE
)

def extract_conjugations(definition):
    """Safely extract verb aspects while preserving root"""
    match = CONJUGATION_PATTERN.search(definition)
    if match:
        return match.group(1).strip(), [c.strip() for c in match.group(1).split(',')]
    return None, []

def create_redirect_entry(conjugated_form, root_word):
    """Generate Kindle-compatible cross-reference entry"""
    return f'''
    <idx:entry name="default" scriptable="yes" spell="yes">
      <h5><dt><idx:orth>{escape(conjugated_form)}</idx:orth></dt></h5>
      <dd>See: <a href="entry://{escape(root_word)}">{escape(root_word)}</a></dd>
    </idx:entry>
    <hr/>'''

def json_to_kindle_html(input_file, output_file):
    stats = {
        'total_read': 0,
        'entries_written': 0,
        'unique_words': defaultdict(int),
        'max_definitions': 0,
        'verbs_found': 0,
        'tenses_added': 0
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

        root, conjugations = extract_conjugations(definition)
        if conjugations:
          stats['verbs_found'] += 1
          effective_root = root or entry['word'].lower()
          for form in conjugations:
              stats['tenses_added'] += 1
              stats['unique_words'][form] += 1
              entries.append(create_redirect_entry(form, effective_root))

        # Add conjugation redirects
        # if "v., inf." in definition:
        #     stats['verbs_found'] += 1
        #     for conjugated in extract_conjugations(definition):
        #         entries.append(create_redirect_entry(conjugated, entry['word']))
        #         stats['entries_written'] += 1
        #         stats['tenses_added'] += 1
        
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
    print(f"Total verbs found: {result['verbs_found']} this should result in {3*result['verbs_found']} tenses added")
    print(f"Tenses added: {result['tenses_added']}")
    