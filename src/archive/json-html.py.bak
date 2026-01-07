import json
import string
import sys
import re
from html import escape
from collections import defaultdict

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

def ligature_inflection(word):
    if word[-1].lower() in {'a', 'e', 'i', 'o', 'u'}:
        return f"{word}ng"
    if word[-1].lower() == 'n':
        return f"{word}g"
    return None

def generate_ligature_inflection(word):
    new_inflection = ligature_inflection(word)
    if new_inflection is None:
      return f''''''
    return f'''
    <idx:iform value="{new_inflection}" />
    '''

def generate_inflections(word):
    inflections = []
    inflections.append(generate_ligature_inflection(word))
    if inflections:
        return f'''
        <idx:infl inflgrp="other">
        {' '.join(inflections)}
        </idx:infl>
        '''
    else:
        return f''''''

def create_verb_inflections(conjugated_forms):
    return f'''
    <idx:infl inflgrp="verb">
    <idx:iform name="progressive" value="{conjugated_forms[0]}" />
    {generate_ligature_inflection(conjugated_forms[0])}
    <idx:iform name="completed" value="{conjugated_forms[1]}" />
    {generate_ligature_inflection(conjugated_forms[1])}
    <idx:iform name="contemplated" value="{conjugated_forms[2]}" />
    {generate_ligature_inflection(conjugated_forms[2])}
    </idx:infl>
    '''

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
    entries_dict = {}

    for entry in data:

        word = escape(entry['word'])

        if word not in entries_dict:
            entries_dict[word] = {
                'word': word,
                'definitions': [],
                'inflections': [],
                'count': 0,

            }
            entries_dict[word]['inflections'].append(generate_inflections(word))

        entries_dict[word]['definitions'].append(escape(entry['definition']))
        entries_dict[word]['count'] += 1

        root, conjugations = extract_conjugations(escape(entry['definition']))
        if conjugations:
          entries_dict[word]['inflections'].append(create_verb_inflections(conjugations))

    for key, value in entries_dict.items():
        entries.append(
            f"""<idx:entry name="default" scriptable="yes" spell="yes">
              <h5><dt><idx:orth value="{key.replace(' ', '_')}">{key}
                {''.join(value['inflections'])}
              </idx:orth></dt></h5>
              <dd>{''.join("{}) {}<br>".format(n, i) for n, i in zip(string.ascii_uppercase, value['definitions']))}</dd>
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
    
    return stats

if __name__ == "__main__":
    # Handle command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python converter.py input.json output.html")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    result = json_to_kindle_html(input_file, output_file)
    