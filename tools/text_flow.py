"""Audit original hard breaks in reviewed English without changing scenario orders."""
import argparse
from collections import Counter
import json
import re

from scenario import JAPANESE, render, split_tags, translations, write_json
from steam_game import ROOT

TRANSPARENT = {'l'}
SENTENCE_END = re.compile(r'''[.!?:;\u2026\u2025\u22ef][\u201d\u2019"')\]]*$''')
def character_names():
    names = set()
    for path in (ROOT/'work/glossary').glob('*.json'):
        glossary = json.loads(path.read_text(encoding='utf-8'))
        people = glossary.get('characters', []) + [entry for entry in glossary.get('entries', [])
                                                   if isinstance(entry,dict) and entry.get('kind') in ('person','character')]
        names.update(item['en'] for item in people if isinstance(item,dict) and isinstance(item.get('en'),str))
    return names


CHARACTERS = character_names()
INLINE_QUOTATIONS = {
    ('game.ks','4326:1'):('I suppose she wanted to hear him say', '\u201cOf course.\u201d'),
    ('jyuku.ks','1975:1'):("What if they'd already been \u201cdisposed of,\u201d", 'and the two people standing there were completely different'),
}


def tokens(raw):
    """Relevant visible tokens; retain other commands as boundaries."""
    result = []
    script = False
    comment = False
    for number, line in enumerate(raw.decode('utf-8-sig').splitlines(), 1):
        line = line.strip()
        if line == '/*':
            comment = True
        elif line == '*/':
            comment = False
        elif not comment and line and not line.startswith(';'):
            if line.startswith(('[endscript]', '@endscript')):
                script = False
                result.append({'name':'endscript', 'line':number, 'text':''})
                continue
            if script:
                continue
            if line.startswith('*'):
                result.append({'name':'label', 'line':number, 'text':''})
                continue
            if line.startswith('#'):
                result.append({'name':'chara_ptext', 'line':number, 'text':''})
                continue
            if line.startswith('_'):
                line = line[1:]
            spans = [(0,len(line),True)] if line.startswith('@') else split_tags(line)
            ordinal = 0
            for a,b,tag in spans:
                value = line[a:b]
                name = re.match(r'\s*(\w+)',value[1:-1] if value.startswith('[') else value[1:])[1] if tag else 'text'
                if name == 'r':
                    ordinal += 1
                result.append({'name':name, 'line':number, 'ordinal':ordinal if name=='r' else None,
                               'text':value if not tag else '', 'raw':value if tag else ''})
                if name == 'iscript':
                    script = True
    return result


def neighbor(items, index, direction):
    index += direction
    while 0 <= index < len(items) and items[index]['name'] in TRANSPARENT:
        index += direction
    return items[index] if 0 <= index < len(items) else None


def classify(items, index, reviewed):
    left = neighbor(items,index,-1)
    right = neighbor(items,index,1)
    if not left or not right:
        return 'boundary'
    if left['name']=='r' or right['name']=='r':
        return 'paragraph'
    if left['name'] not in ('text','emb') or right['name'] not in ('text','emb'):
        return 'command-or-layout'
    if not all(t['name']=='emb' or f"{t['line']}:text" in reviewed for t in (left,right)):
        return 'outside-reviewed-text'
    a,b = left['text'].strip(),right['text'].strip()
    if JAPANESE.search(a+b):
        return 'outside-reviewed-text'
    if left['name']=='emb':
        return 'name-or-substitution'
    if not a or (right['name']=='text' and not b):
        return 'boundary'
    if a in CHARACTERS:
        return 'speaker-name'
    if a.endswith(('\u201d','"')) or (b and b[0] in '\u201c"'):
        return 'speaker-or-quotation'
    if SENTENCE_END.search(a):
        return 'sentence-end'
    if b and (re.match(r'^[\u25b6\u2022\u2190\u2191\u2192\u2193]|^\d+[.)] ',b) or b.startswith('- ')):
        return 'list-or-layout'
    if a.casefold().strip(' ,') == b.casefold().strip(' ,') or (a.isupper() and b.isupper()):
        return 'emphasis'
    return 'soft-space'


def separator(before, after):
    # Attach split hyphenated words, em dashes, and punctuation without an extra space.
    return '' if before.rstrip().endswith(('-', '\u2014')) or after.lstrip().startswith(('.', ',', '!', '?', ';', ':', ')', '\u201d', '\u2019')) else ' '


def audit():
    report = {'version':1, 'policy':'Reflow continuous English; preserve paragraphs, speakers, sentence ends, emphasis and layout commands.',
              'manual_review':{'speaker_boundaries':['sindo.ks:1802:1','fukuzawa.ks:3098:1','fukuzawa.ks:3111:1','fukuzawa.ks:3295:1','fukuzawa.ks:3359:1'],
                               'inline_quotation':'game.ks:4326:1 and jyuku.ks:1975:1 continue narration around embedded quotations; preserve genuine speaker-label breaks.',
                               'checks':'Reviewed capitalized continuations, dash/ellipsis joins, all distinct quoted speaker labels, name substitutions, abbreviations, and commands adjoining breaks.'},
              'english_fields':0, 'scenarios':{}, 'soft_breaks':{}, 'counts':{}}
    total = Counter()
    for scenario,data in translations(ROOT/'work/translation/en').items():
        raw = render((ROOT/'work/debug/kiwame-base/package.nw'/scenario).read_bytes(),data)
        items = tokens(raw)
        rows = []
        mapping = {}
        counts = Counter()
        for index,item in enumerate(items):
            if item['name'] != 'r':
                continue
            reason = classify(items,index,data['rows'])
            if scenario == 'data/scenario/inoti.ks' and 3356 <= item['line'] <= 3438:
                # Adapted summary controls its three page boundaries in life-summary.js.
                reason = 'adapted-summary-boundary'
            key = f"{item['line']}:{item['ordinal']}"
            name = scenario.removeprefix('data/scenario/')
            override = INLINE_QUOTATIONS.get((name,key))
            if override:
                left,right = neighbor(items,index,-1),neighbor(items,index,1)
                if (left['text'],right['text']) != override:
                    raise ValueError('Recheck the inline quotation override: '+name+':'+key)
                reason = 'soft-space'
            counts[reason] += 1
            left,right = neighbor(items,index,-1),neighbor(items,index,1)
            row = {'key':key,'action':reason,
                   'before':left['text'] if left else '', 'after':right['text'] if right else ''}
            rows.append(row)
            if reason == 'soft-space':
                row['separator'] = separator(row['before'],row['after'])
                mapping[key] = row['separator']
        name = scenario.removeprefix('data/scenario/')
        report['scenarios'][name] = {'fields':len(data['rows']), 'counts':dict(counts), 'breaks':rows}
        if mapping:
            report['soft_breaks'][name] = mapping
        total.update(counts)
        report['english_fields'] += len(data['rows'])
    report['counts'] = dict(total)
    return report


def install_map(maps, report=None):
    report = report or audit()
    maps['flowBreaks'] = report['soft_breaks']
    maps['flowPairs'] = {scenario:list({(row['before'].strip(), row['after'].strip(), row['separator'])
                                       for row in data['breaks'] if row['action']=='soft-space'})
                         for scenario,data in report['scenarios'].items() if scenario in report['soft_breaks']}
    for scenario,pairs in maps['flowPairs'].items():
        maps['flowPairs'][scenario] = [list(pair) for pair in sorted(pairs)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    report = audit()
    print(report['english_fields'],'English fields;',len(report['scenarios']),'translated scenario files')
    print(report['counts'])
    for scenario,data in report['scenarios'].items():
        soft = [row for row in data['breaks'] if row['action']=='soft-space']
        if soft:
            print(scenario,len(soft),'soft breaks; samples:',ascii(soft[:2]))
    if args.write:
        write_json(ROOT/'work/ui/english-flow-audit.json', report)


if __name__=='__main__':
    main()
