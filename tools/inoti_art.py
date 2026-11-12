"""Build Life title/prop lettering with clipped clean plates and vector Latin text."""
from base64 import b64encode
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parents[1]

def data_image(path):
    mime='image/jpeg' if path.suffix.lower() in ('.jpg','.jpeg') else 'image/png'
    return 'data:'+mime+';base64,'+b64encode(path.read_bytes()).decode('ascii')

def patched_image(original,item,prefix='patch'):
    width,height=item['width'],item['height'];clean=ROOT/item['clean']
    parts=[f'<image width="{width}" height="{height}" xlink:href="{data_image(original)}"/>']
    for index,(x,y,w,h) in enumerate(item['patches']):
        name=prefix+str(index);fx=min(7,w/8)/w;fy=min(7,h/8)/h
        parts.extend([
            f'<defs><linearGradient id="{name}x"><stop offset="0" stop-color="white" stop-opacity="0"/><stop offset="{fx}" stop-color="white"/><stop offset="{1-fx}" stop-color="white"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>',
            f'<linearGradient id="{name}y" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="white" stop-opacity="0"/><stop offset="{fy}" stop-color="white"/><stop offset="{1-fy}" stop-color="white"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>',
            f'<mask id="{name}mx" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{name}x)"/></mask>',
            f'<mask id="{name}my" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{name}y)"/></mask></defs>',
            f'<g mask="url(#{name}mx)"><image width="{width}" height="{height}" mask="url(#{name}my)" xlink:href="{data_image(clean)}"/></g>'
        ])
    return ''.join(parts)

def start(width,height):
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'

def life_word(x,baseline,size,color,identifier):
    text=f'<text x="{x}" y="{baseline}" text-anchor="middle" font-family="Segoe Print,Comic Sans MS,cursive" font-weight="600" font-size="{size}">Life</text>'
    return (f'<defs><linearGradient id="{identifier}fade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="white"/><stop offset="1" stop-color="black"/></linearGradient>'
        f'<mask id="{identifier}mask" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><rect x="0" y="{baseline+14}" width="960" height="{size}" fill="url(#{identifier}fade)"/></mask></defs>'
        f'<g fill="{color}">{text}</g><g mask="url(#{identifier}mask)" opacity=".58"><g transform="translate(0,{2*(baseline+8)}) scale(1,-1)" fill="{color if color=="#ffffff" else "#8e6855"}">{text}</g></g>')

def title(color):
    return (start(960,690)+'<rect width="960" height="690" fill="black"/>'+life_word(480,352,92,color,'title')+'</svg>\n').encode('utf-8')

def extras(asset_root):
    spec=json.loads((ROOT/'work/ui/inoti-lettering.json').read_text(encoding='utf-8'))
    files={}
    for suffix,color in [('white','#ffffff'),('red','#d90018')]:
        files[asset_root/'bgimage/kiwame-en'/f'inoti-title-{suffix}.svg']=title(color)
    item=spec['pendant_name']
    body=patched_image(asset_root/'bgimage'/item['source'],item,'name')
    body+='<g fill="black" stroke="white" stroke-width="4" stroke-linejoin="round" paint-order="stroke" text-anchor="middle" font-family="Segoe Print,Comic Sans MS,cursive" font-weight="600">'
    for y,size,text in [(337,56,item['text'][0]),(415,46,item['text'][1])]:
        body+=f'<text x="470" y="{y}" font-size="{size}">{escape(text)}</text>'
    files[asset_root/'bgimage/kiwame-en/inoti-pendant-name.svg']=(start(960,690)+body+'</g></svg>\n').encode('utf-8')
    item=spec['ending_hover'];body=patched_image(asset_root/'fgimage'/item['source'],item,'hover')
    body+=life_word(665,103,58,'#d90018','hover')
    body+='<text x="38" y="151" fill="white" font-family="Georgia,serif" font-size="21">Ending List</text>'
    files[asset_root/'fgimage/kiwame-en/inoti-ending-hover.svg']=(start(960,690)+body+'</svg>\n').encode('utf-8')
    item=spec['wrong_answer'];body=patched_image(asset_root/'fgimage'/item['source'],item,'board')
    body+='<g transform="translate(175,160) rotate(-10.3)" fill="white" stroke="white" stroke-width="1.4" text-anchor="middle" font-family="Segoe Print,Comic Sans MS,cursive" font-weight="600"><text x="0" y="-12" font-size="49">Wrong</text><text x="0" y="45" font-size="46">Answer</text></g>'
    files[asset_root/'fgimage/kiwame-en/inoti-wrong-answer.svg']=(start(470,600)+body+'</svg>\n').encode('utf-8')
    return files
