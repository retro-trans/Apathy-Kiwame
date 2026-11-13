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
TEXT_JOINS = {
    ('rpg/batoru.ks', '1343:1'): ('But', 'my eyelids were already...'),
}
JOIN_TRANSPARENT = {'l', 'フラッシュ'}
MACRO_LAYOUT = {
    ('rpg/stage.ks','352:1'): ("“Ph'nglui mglw'nafh Cthulhu", "R'lyeh wgah'nagl fhtagn.”"),
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
            ordinals = Counter()
            for a,b,tag in spans:
                value = line[a:b]
                name = re.match(r'\s*(\w+)',value[1:-1] if value.startswith('[') else value[1:])[1] if tag else 'text'
                ordinals[name] += 1
                result.append({'name':name, 'line':number, 'ordinal':ordinals[name] if name in ('r','lr','text') else None,
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
    if left['name'] in ('r','lr') or right['name'] in ('r','lr'):
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
    report = {'version':2, 'policy':'Reflow continuous English and RPG lr macros; preserve pauses, paragraphs, speakers, sentence ends, emphasis and layout commands.',
              'manual_review':{'speaker_boundaries':['sindo.ks:1802:1','fukuzawa.ks:3098:1','fukuzawa.ks:3111:1','fukuzawa.ks:3295:1','fukuzawa.ks:3359:1'],
                               'inline_quotation':'game.ks:4326:1 and jyuku.ks:1975:1 continue narration around embedded quotations; preserve genuine speaker-label breaks.',
                               'checks':'Reviewed capitalized continuations, dash/ellipsis joins, all distinct quoted speaker labels, name substitutions, abbreviations, and commands adjoining breaks.'},
              'english_fields':0, 'scenarios':{}, 'soft_breaks':{}, 'macro_breaks':{}, 'text_joins':{}, 'counts':{}}
    total = Counter()
    for scenario,data in translations(ROOT/'work/translation/en').items():
        raw = render((ROOT/'work/debug/kiwame-base/package.nw'/scenario).read_bytes(),data)
        items = tokens(raw)
        rows = []
        mapping = {}
        macro_mapping = {}
        joins = {}
        counts = Counter()
        name = scenario.removeprefix('data/scenario/')
        for index,item in enumerate(items):
            if item['name'] == 'text':
                join_key = f"{item['line']}:{item['ordinal']}"
                expected = TEXT_JOINS.get((name,join_key))
                if expected:
                    previous = index - 1
                    while previous >= 0 and items[previous]['name'] in JOIN_TRANSPARENT:
                        previous -= 1
                    left = items[previous] if previous >= 0 else None
                    if not left or left['name'] != 'text' or (left['text'].strip(),item['text'].strip()) != expected:
                        raise ValueError('Recheck text join: '+name+':'+join_key)
                    joins[join_key] = {'before':expected[0], 'after':expected[1], 'separator':' '}
            if item['name'] not in ('r','lr'):
                continue
            reason = classify(items,index,data['rows'])
            if item['name'] == 'lr' and not name.startswith('rpg/'):
                reason = 'outside-rpg-macro'
            if scenario == 'data/scenario/inoti.ks' and 3356 <= item['line'] <= 3438:
                # Adapted summary controls its three page boundaries in life-summary.js.
                reason = 'adapted-summary-boundary'
            key = f"{item['line']}:{item['ordinal']}"
            override = INLINE_QUOTATIONS.get((name,key))
            if override:
                left,right = neighbor(items,index,-1),neighbor(items,index,1)
                if (left['text'],right['text']) != override:
                    raise ValueError('Recheck the inline quotation override: '+name+':'+key)
                reason = 'soft-space'
            layout = MACRO_LAYOUT.get((name,key)) if item['name']=='lr' else None
            if layout:
                left,right = neighbor(items,index,-1),neighbor(items,index,1)
                if (left['text'],right['text']) != layout:
                    raise ValueError('Recheck RPG ritual layout: '+name+':'+key)
                reason = 'ritual-layout'
            counts[reason] += 1
            left,right = neighbor(items,index,-1),neighbor(items,index,1)
            row = {'key':key,'kind':item['name'],'action':reason,
                   'before':left['text'] if left else '', 'after':right['text'] if right else ''}
            if name == 'inoti.ks' and any(t and 3352 <= t['line'] <= 3455 for t in (item,left,right)):
                row['before'] = row['after'] = '[adapted summary; source text omitted]'
            rows.append(row)
            if reason == 'soft-space':
                row['separator'] = separator(row['before'],row['after'])
                (macro_mapping if item['name']=='lr' else mapping)[key] = row['separator']
        name = scenario.removeprefix('data/scenario/')
        report['scenarios'][name] = {'fields':len(data['rows']), 'counts':dict(counts), 'breaks':rows}
        if mapping:
            report['soft_breaks'][name] = mapping
        if macro_mapping:
            report['macro_breaks'][name] = macro_mapping
        if joins:
            report['text_joins'][name] = joins
        total.update(counts)
        report['english_fields'] += len(data['rows'])
    report['counts'] = dict(total)
    return report


def install_map(maps, report=None):
    report = report or audit()
    maps['flowBreaks'] = report['soft_breaks']
    maps['flowMacroBreaks'] = report['macro_breaks']
    maps['flowTextJoins'] = {scenario:{key:row['separator'] for key,row in joins.items()}
                             for scenario,joins in report['text_joins'].items()}
    maps['flowTextJoinPairs'] = {scenario:[[row['before'],row['after'],row['separator']] for row in joins.values()]
                                 for scenario,joins in report['text_joins'].items()}
    maps['flowMacroTails'] = {}
    for scenario,data in report['scenarios'].items():
        tails = {}
        for row in data['breaks']:
            if row['kind'] != 'lr':
                continue
            tails.setdefault(row['before'].strip(),set()).add(row.get('separator') if row['action']=='soft-space' else None)
        safe = [[tail,next(iter(values))] for tail,values in tails.items() if tail and len(values)==1 and None not in values]
        if safe:
            maps['flowMacroTails'][scenario] = sorted(safe,key=lambda pair:(-len(pair[0]),pair[0]))
    maps['flowPairs'] = {scenario:list({(row['before'].strip(), row['after'].strip(), row['separator'])
                                       for row in data['breaks'] if row['action']=='soft-space'})
                         for scenario,data in report['scenarios'].items() if scenario in report['soft_breaks'] or scenario in report['macro_breaks']}
    for scenario,pairs in maps['flowPairs'].items():
        maps['flowPairs'][scenario] = [list(pair) for pair in sorted(pairs)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    report = audit()
    print(report['english_fields'],'English fields;',len(report['scenarios']),'translated scenario files')
    print(report['counts'])
    print('RPG macro soft breaks:',sum(map(len,report['macro_breaks'].values())), '; text joins:',report['text_joins'])
    for scenario,data in report['scenarios'].items():
        soft = [row for row in data['breaks'] if row['action']=='soft-space']
        if soft:
            print(scenario,len(soft),'soft breaks; samples:',ascii(soft[:2]))
    if args.write:
        write_json(ROOT/'work/ui/english-flow-audit.json', report)


if __name__=='__main__':
    main()
