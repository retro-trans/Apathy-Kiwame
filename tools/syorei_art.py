"""Prepare guarded Summoning Incident lettering; default CLI never writes files.

The installer calls artwork(asset_root, maps). Existing Kazama torii artwork must
already be mapped. Only --preview writes separate SVGs below work/debug.
"""
from __future__ import annotations

import argparse
from base64 import b64encode
from hashlib import sha256
import json
from pathlib import Path
from xml.sax.saxutils import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_ASSETS=ROOT/'work/debug/kiwame-base/package.nw/data'
SPEC=ROOT/'work/ui/syorei-lettering.json'
LAYOUT=ROOT/'work/ui/syorei-layout.json'


def _hash(raw): return sha256(raw).hexdigest()
def _image(raw, suffix='.jpg'):
    mime='image/png' if suffix.lower()=='.png' else 'image/jpeg'
    return 'data:'+mime+';base64,'+b64encode(raw).decode('ascii')
def _rect(box,fill,rx=0):
    x,y,w,h=box
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>'
def _matrix(values): return 'matrix('+ ' '.join(str(x)for x in values)+')'


class _Font:
    """Outline the project font so SVG image loading needs no external font."""
    def __init__(self,path):
        self.font=TTFont(str(path));self.glyphs=self.font.getGlyphSet()
        self.cmap=self.font.getBestCmap();self.metrics=self.font['hmtx'].metrics
        self.units=self.font['head'].unitsPerEm;self.paths={}
    def advance(self,char):
        if ord(char)not in self.cmap:raise ValueError('Unsupported English glyph: '+repr(char))
        return self.metrics[self.cmap[ord(char)]][0]
    def width(self,text,size):return sum(self.advance(c)for c in text)*size/self.units
    def glyph(self,char):
        if char not in self.paths:
            self.advance(char)
            pen=SVGPathPen(self.glyphs);self.glyphs[self.cmap[ord(char)]].draw(pen)
            self.paths[char]=pen.getCommands()
        return self.paths[char]
    def wrap(self,text,size,width):
        lines=[];line=''
        for word in text.split():
            if self.width(word,size)>width:raise ValueError('Word exceeds lettering box: '+word)
            candidate=(line+' '+word).strip()
            if line and self.width(candidate,size)>width:lines.append(line);line=word
            else:line=candidate
        if line:lines.append(line)
        return lines


class _SVG:
    def __init__(self,raw,suffix,font):
        self.font=font;self.used=set();self.parts=[];self.serial=0
        self.base=f'<image id="scene" width="960" height="690" xlink:href="{_image(raw,suffix)}"/>'
    def add(self,markup):self.parts.append(markup)
    def text(self,text,x,baseline,size,fill='#222222',anchor='start',opacity=1):
        width=self.font.width(text,size)
        if anchor=='middle':x-=width/2
        out=[f'<g fill="{fill}" opacity="{opacity}" aria-label="{escape(text)}">']
        for char in text:
            self.used.add(char)
            if char!=' ':
                scale=size/self.font.units
                # Inline actual font outlines keep each SVG independent of
                # external font loading and shared glyph-reference lookups.
                out.append(f'<path d="{self.font.glyph(char)}" transform="translate({x:.5f},{baseline}) scale({scale:.8f},{-scale:.8f})"/>')
            x+=self.font.advance(char)*size/self.font.units
        out.append('</g>');return ''.join(out)
    def sprite(self,box,target_box):
        self.serial+=1;identifier='sprite'+str(self.serial)
        x,y,w,h=box;tx,ty,tw,th=target_box
        return (f'<svg x="{tx}" y="{ty}" width="{tw}" height="{th}" viewBox="{x} {y} {w} {h}" overflow="hidden">'
                '<use xlink:href="#scene"/></svg>')
    def finish(self):
        return ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="960" height="690" viewBox="0 0 960 690">'
                '<defs>'+self.base+'</defs><use xlink:href="#scene"/>'+''.join(self.parts)+'</svg>\n').encode('utf-8')


def _source(item,originals):return originals[item['asset_path'][5:]]


def _notification(item,raw,font,spec,clean):
    svg=_SVG(raw,'.jpg',font)
    panel=item['native_panel_path']
    polygons='<polygon points="'+' '.join(f'{x},{y}'for x,y in item['patch_polygons'][0])+'"/><path d="'+panel+'"/>'
    svg.add('<defs><clipPath id="notification-patches">'+polygons+'</clipPath>'
            '<filter id="soft-notice" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="1.4"/></filter>'
            '<mask id="notification-feather" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><g fill="white" filter="url(#soft-notice)">'+polygons+'</g></mask>'
            '<clipPath id="notice-brand"><polygon points="'+' '.join(f'{x},{y}'for x,y in item['brand_preserve_polygon'])+'"/></clipPath></defs>')
    svg.add('<g clip-path="url(#notification-patches)" mask="url(#notification-feather)"><image width="960" height="690" preserveAspectRatio="none" xlink:href="'+_image(clean,'.png')+'"/></g>')
    svg.add('<use xlink:href="#scene" clip-path="url(#notice-brand)"/>')
    body=svg.text('No Service',12,16,10,'#a9a9a9')
    body+=svg.text('1m ago',348,225,10,'#626262','middle')
    body+=svg.text("You've been invited to a group.",78,262,17,'#202020')
    svg.add('<g transform="'+_matrix(spec['phone_matrix'])+'">'+body+'</g>')
    return svg.finish()


def _call(item,raw,font,spec):
    svg=_SVG(raw,'.jpg',font)
    body=_rect([24,73,352,76]if item['kind']=='in_call'else [24,65,352,155],'black')
    caller=next(x['english']for x in item['labels']if x['id']=='caller')
    if font.width(caller,34)>352:raise ValueError('Caller name exceeds phone box')
    body+=svg.text(caller,200,128,34,'#ececec','middle')
    if item['kind']=='outgoing':
        body+=svg.text('Calling...',200,185,15,'#a4a4a4','middle')
    elif item['kind']=='incoming':
        body+=_rect([55,562,100,45],'black')+_rect([265,570,95,45],'black')
        body+=svg.text('Decline',95,585,13,'#d7d7d7','middle')+svg.text('Answer',310,598,13,'#d7d7d7','middle')
        body+=_rect([230,430,158,54],'black')
        body+=svg.text('Reply with',309,449,13,'#d7d7d7','middle')+svg.text('message',309,468,13,'#d7d7d7','middle')
    # The in-call00:03 raster and all phone buttons stay unchanged.
    svg.add('<g transform="'+_matrix(spec['phone_matrix'])+'">'+body+'</g>')
    return svg.finish()


def _chat_upright(item,raw,font,spec):
    svg=_SVG(raw,'.jpg',font)
    index=str(spec['chats'].index(item)+1)
    avatars=spec['avatar_source_boxes'][index]
    svg.add('<defs><linearGradient id="chatbg" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#37364c"/><stop offset="1" stop-color="#323145"/></linearGradient>'
            '<clipPath id="chatbody"><rect x="440" y="29" width="392" height="580"/></clipPath>'
            '<clipPath id="chatheader"><rect x="483" y="0" width="300" height="29"/></clipPath></defs>')
    svg.add('<g clip-path="url(#chatheader)">'+_rect([483,0,300,29],'#303e50')+
            svg.text('Emergency Meeting (7)',633,21,20,'#dddddd','middle')+'</g>')
    parts=[_rect(spec['upright_chat_body'],'url(#chatbg)')]
    for node,avatar in zip(item['layout']['nodes'],avatars):
        mid=node['message_id'];message=spec['messages'][mid]['english'];emoji=node.get('emoji')
        if emoji:message=message.replace(' 😊','')
        size=node['font_size'];leading=node['line_height'];x,y=node['body_origin']
        lines=font.wrap(message,size,node['wrap_width'])
        bx,by,bw,bh=node['bubble_box']
        if y+size+(len(lines)-1)*leading+4>by+bh:raise ValueError('Chat copy overflows bubble: '+mid)
        own=mid.endswith('_player')
        parts.append(_rect(node['bubble_box'],'#8cdb26'if own else '#fafafa',17))
        # Preserve the original message-side direction, without adding a speaker.
        tail=(f'<path d="M{bx+bw-12},{by+3} l18,-6 -10,17 Z" fill="#8cdb26"/>'if own else
              f'<path d="M{bx+12},{by+3} l-18,-6 10,17 Z" fill="#fafafa"/>')
        parts.append(tail)
        for i,line in enumerate(lines):parts.append(svg.text(line,x,y+size+i*leading,size))
        sender=node.get('sender_label')
        if sender:
            sx,sy,sw,sh=sender['box'];parts.append(svg.text(sender['english'],sx,sy+sender['font_size'],sender['font_size'],'#d6d3dc'))
        if avatar:
            target_y=(sender['box'][1]-6)if sender else avatar[1]
            parts.append(svg.sprite(avatar,[443,target_y,37,37]))
        for label_key in ('timestamp','read_label'):
            label=node.get(label_key)
            if label:
                lx,ly,lw,lh=label['box']
                parts.append(svg.text(label['english'],lx,ly+label['font_size'],label['font_size'],'#dbd9df'))
        if emoji:
            # Exact source emoji pixels, rescaled to the planned20x20 UI size.
            ex,ey,er,eb=emoji['original_raster_box_xyxy']
            emoji_x=x+font.width(lines[-1],size)+4
            if emoji_x+20>bx+bw-7:raise ValueError('Emoji exceeds bubble')
            parts.append(svg.sprite([ex,ey,er-ex,eb-ey],[emoji_x,y+(len(lines)-1)*leading,20,20]))
    svg.add('<g clip-path="url(#chatbody)">'+''.join(parts)+'</g>')
    return svg.finish()


def _chat_tilted(item,raw,font,spec):
    svg=_SVG(raw,'.jpg',font)
    # Patches stay on the existing flat bubbles; original avatars and blurred
    # timestamp raster remain in their original native positions.
    nodes=[(x['bubble'],x['sender'],x['font'],x['line_height'])for x in spec['chat1_nodes']]
    parts=[]
    for mid,(box,label,size,leading)in zip(item['message_ids'],nodes):
        x,y,w,h=box;message=spec['messages'][mid]
        text_lines=font.wrap(message['english'],size,w-12)
        if 8+size+(len(text_lines)-1)*leading+4>h:raise ValueError('Tilted chat copy overflows: '+mid)
        parts.append(_rect(box,'#fafafa',13))
        parts.append(_rect(label,'#39384e'))
        parts.append(svg.text(message['sender'],label[0],label[1]+12,11,'#d5d1da'))
        for i,text in enumerate(text_lines):parts.append(svg.text(text,x+6,y+7+size+i*leading,size))
    svg.add('<g transform="'+_matrix(spec['chat1_rectified_inverse'])+'"><g transform="'+_matrix(spec['chat1_UI_plane'])+'">'+''.join(parts)+'</g></g>')
    return svg.finish()


def _title(item,raw,clean,font):
    svg=_SVG(raw,'.png',font)
    x,y,w,h=item['patch_box']
    # Clean texture is bounded by the original lettering region. Restore original
    # hand pixels and colored splatter above it, never the generated hand.
    hand=('M582 255 Q589 249 596 264 L626 307 L638 316 L632 231 Q636 215 646 223 L659 302 '
          'L667 304 L679 228 Q687 215 696 228 L686 309 L698 308 L718 257 Q726 249 732 257 '
          'L713 317 L716 349 Q722 373 710 393 L687 402 L643 399 L630 391 L622 375 '
          'L618 354 L623 335 L615 319 L597 291 Z')
    color_alpha='2 -1 -1 0 -0.12'if item['variant']=='red'else '-2 1 1 0 -0.12'
    svg.add(f'<defs><clipPath id="lettering"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>'
            f'<clipPath id="hand"><path d="{hand}"/></clipPath>'
            '<filter id="splatter" color-interpolation-filters="sRGB"><feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 '+color_alpha+'"/></filter></defs>')
    svg.add(f'<defs><linearGradient id="plate-x" x1="{x}" y1="0" x2="{x+w}" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="white" stop-opacity="0"/><stop offset=".035" stop-color="white"/><stop offset=".965" stop-color="white"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="plate-y" x1="0" y1="{y}" x2="0" y2="{y+h}" gradientUnits="userSpaceOnUse"><stop stop-color="white" stop-opacity="0"/><stop offset=".08" stop-color="white"/><stop offset=".92" stop-color="white"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>'
            f'<mask id="plate-mx" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#plate-x)"/></mask>'
            f'<mask id="plate-my" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#plate-y)"/></mask>'
            '<clipPath id="clean-texture-only"><rect x="540" y="260" width="85" height="155"/></clipPath>'
            '<linearGradient id="texture-fade" x1="540" y1="0" x2="560" y2="0" gradientUnits="userSpaceOnUse"><stop stop-color="white" stop-opacity="0"/><stop offset="1" stop-color="white"/></linearGradient>'
            '<mask id="texture-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="960" height="690"><rect x="540" y="260" width="85" height="155" fill="url(#texture-fade)"/></mask></defs>')
    svg.add('<g clip-path="url(#lettering)" mask="url(#plate-mx)"><g mask="url(#plate-my)"><image width="960" height="690" preserveAspectRatio="none" xlink:href="'+_image(clean,'.png')+'"/>'
            '<g clip-path="url(#clean-texture-only)" mask="url(#texture-mask)"><image x="200" width="960" height="690" preserveAspectRatio="none" xlink:href="'+_image(clean,'.png')+'"/></g></g></g>')
    svg.add('<g clip-path="url(#lettering)"><use xlink:href="#scene" filter="url(#splatter)"/></g>')
    svg.add('<use xlink:href="#scene" clip-path="url(#hand)"/>')
    for text,baseline in zip(item['lines'],item['baselines']):
        svg.add(svg.text(text,item['center_x'],baseline,item['font_size'],'#ffffff','middle'))
    return svg.finish()


def _board(item,raw,font,spec):
    svg=_SVG(raw,'.jpg',font);board=spec['board'];size=board['latin_annotation_style']['font_size']
    for column in board['cell_columns_right_to_left']:
        for roman,y in zip(column['labels'],column['centers_y']):
            if roman is None:continue
            svg.add(svg.text(roman,column['x'],y+43,size,'#243635','middle'))
    for label in board['responses']:svg.add(svg.text(label['english'],label['center'][0],label['center'][1],size,'#243635','middle'))
    coin=item.get('coin')
    if coin:
        cx,cy=coin['coin_center'];rx,ry=coin['clip_ellipse_radii']
        svg.add(f'<defs><clipPath id="coin"><ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}"/></clipPath></defs><use xlink:href="#scene" clip-path="url(#coin)"/>')
    return svg.finish()


def _caption_events(spec):
    events={}
    for seq in spec['board']['sequences']:
        base=seq['base_frame'];events[str(base['line'])]={'action':'clear','text':'','delay_ms':0,'trigger':'bg','cancel_pending':True,'native_transition_ms':base['transition_ms'],'sequence':seq['id']}
        for frame in seq['coin_frames']:
            events[str(frame['line'])]={'action':'clear','text':'',
                'delay_ms':0,'trigger':'bg','cancel_pending':True,
                'native_transition_ms':frame['transition_ms'],'sequence':seq['id']}
        # The next native command starts only after the final image transition
        # completes, including its asynchronous image loading time.
        show=seq['native_show_event'];clear=seq['native_clear_event']
        assert show['after_completed_source_line']==seq['coin_frames'][-1]['line']
        events[str(show['line'])]={'action':'show','text':seq['final_caption'],'delay_ms':0,
            'trigger':show['tag'],'cancel_pending':True,'sequence':seq['id'],
            'after_completed_source_line':show['after_completed_source_line']}
        if seq['id']=='cat':events[str(show['line'])]['retain_previous_until_clear']=True
        events[str(clear['line'])]={'action':'clear','text':'','delay_ms':0,'cancel_pending':True,
            'trigger':clear['tag'],'native_event':'layopt message0 visible=true','sequence':seq['id']}
    return events


def artwork(asset_root,maps) -> dict[Path,bytes]:
    """Prepare31 assets and source-keyed map additions; never overwrite files."""
    asset_root=Path(asset_root).resolve()
    spec=json.loads(SPEC.read_text(encoding='utf-8'))
    layout=json.loads(LAYOUT.read_text(encoding='utf-8'))
    scenario=asset_root/'scenario/syorei.ks'
    if _hash(scenario.read_bytes())!=spec['source_sha256']:
        # Installers render English scenarios before artwork. Accept only that
        # exact canonical render, never an arbitrary changed scenario.
        baseline=DEFAULT_ASSETS/'scenario/syorei.ks'
        if _hash(baseline.read_bytes())!=spec['source_sha256']:raise ValueError('Syorei source SHA mismatch')
        from scenario import render
        translation=json.loads((ROOT/'work/translation/en/syorei.en.json').read_text(encoding='utf-8-sig'))
        canonical=render(baseline.read_bytes(),translation)
        if scenario.read_bytes()!=canonical:raise ValueError('Syorei scenario is neither the exact original nor current canonical English render')
    if layout['source_sha256']!=spec['source_sha256']:raise ValueError('Layout source mismatch')
    command_lines=scenario.read_text(encoding='utf-8-sig').splitlines()
    for seq in spec['board']['sequences']:
        show=seq['native_show_event'];clear=seq['native_clear_event']
        show_command=command_lines[show['line']-1].strip()
        clear_command=command_lines[clear['line']-1].strip()
        if seq['id']=='cat':
            if show_command!='[bg storage=kuro.jpg time=1500]':raise ValueError('Cat completion trigger changed')
        elif show_command!='[wait time=2000]':raise ValueError('Board completion wait changed: '+seq['id'])
        if 'layopt 'not in clear_command or 'layer=message0'not in clear_command or 'visible=true'not in clear_command:raise ValueError('Board clear trigger changed: '+seq['id'])
    originals={}
    for item in spec['source_assets']:
        p=asset_root/item['path'];raw=p.read_bytes()
        if _hash(raw)!=item['sha256']:raise ValueError('Unexpected source image SHA256: '+item['path'])
        originals[item['path']]=raw
    font_path=ROOT/spec['font']['path']
    if _hash(font_path.read_bytes())!=spec['font']['sha256']:raise ValueError('Latin font SHA mismatch')
    clean={}
    for title in spec['titles']:
        raw=(ROOT/title['clean']).read_bytes()
        if _hash(raw)!=title['clean_sha256']:raise ValueError('Clean plate SHA mismatch')
        clean[title['variant']]=raw
    notification_clean=(ROOT/spec['notification']['clean']).read_bytes()
    if _hash(notification_clean)!=spec['notification']['clean_sha256']:raise ValueError('Notification clean plate SHA mismatch')
    # Preserve existing shared art and all unrelated route map entries.
    shared=spec['shared_board']['source']
    if shared not in maps.get('backgrounds',{}):raise ValueError('Install reviewed Kazama torii mapping before Syorei artwork')
    font=_Font(font_path);files={};additions={}
    def put(source,target,raw):
        if not source.startswith('bgimage/'):raise ValueError('Background source prefix mismatch')
        additions[source[8:]]=target
        files[asset_root/'bgimage'/target]=raw
    item=spec['notification'];put(item['asset_path'][5:],'kiwame-en/syorei-phone-notification.svg',_notification(item,_source(item,originals),font,spec,notification_clean))
    for i,item in enumerate(spec['calls'],1):
        put(item['asset_path'][5:],f'kiwame-en/syorei-phone-call-{i}.svg',_call(item,_source(item,originals),font,spec))
    for i,item in enumerate(spec['chats'],1):
        render=_chat_tilted if i==1 else _chat_upright
        put(item['asset_path'][5:],f'kiwame-en/syorei-phone-chat-{i}.svg',render(item,_source(item,originals),font,spec))
    for item in spec['titles']:
        put(item['asset_path'][5:],'kiwame-en/syorei-title-'+item['variant']+'.svg',_title(item,_source(item,originals),clean[item['variant']],font))
    for i,item in enumerate(spec['board']['frames']):
        if item['asset_path']=='data/bgimage/kazama/鳥居.jpg':continue
        put(item['asset_path'][5:],f'kiwame-en/syorei-board-{i:02}.svg',_board(item,_source(item,originals),font,spec))
    for source,target in additions.items():
        if source in maps['backgrounds']and maps['backgrounds'][source]!=target:raise ValueError('Conflicting existing Syorei mapping: '+source)
    if 'syorei.ks'in maps.get('choiceLayouts',{})and maps['choiceLayouts']['syorei.ks']!=layout['choices']:raise ValueError('Conflicting Syorei choice map')
    events=_caption_events(spec)
    if 'syorei.ks'in maps.get('scenarioBoardCaptions',{})and maps['scenarioBoardCaptions']['syorei.ks']!=events:raise ValueError('Conflicting Syorei board-caption map')
    maps['backgrounds'].update(additions)
    maps.setdefault('choiceLayouts',{})['syorei.ks']=layout['choices']
    maps.setdefault('scenarioBoardCaptions',{})['syorei.ks']=events
    maps.setdefault('scenarioBoardCaptionStyles',{})['syorei.ks']=spec['board']['caption_style']
    return files


def _within(path,parent):
    try:path.relative_to(parent);return True
    except ValueError:return False


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--assets',type=Path,default=DEFAULT_ASSETS)
    parser.add_argument('--preview',type=Path)
    args=parser.parse_args(argv)
    maps={'backgrounds':{'kazama/鳥居.jpg':'kiwame-en/kazama-board-37.svg'}}
    files=artwork(args.assets,maps)
    summary={'status':'dry run; no files written','assets':len(files),'guarded_source_images':32,
             'reused_shared_board':'kazama/鳥居.jpg','phone_images':11,'titles':2,'new_board_frames':18,
             'choice_lines':len(maps['choiceLayouts']['syorei.ks']),
             'caption_events':maps['scenarioBoardCaptions']['syorei.ks'],
             'output_hashes':{str(p.relative_to(args.assets.resolve())):_hash(raw)for p,raw in files.items()}}
    if args.preview:
        target=args.preview.resolve();debug=(ROOT/'work/debug').resolve();assets=args.assets.resolve()
        if (not _within(target,debug)or target==debug or _within(target,DEFAULT_ASSETS.parent)
            or _within(target,assets)or _within(assets,target)):raise ValueError('Preview must be separate from source assets, below work/debug')
        outputs={target/p.relative_to(assets):raw for p,raw in files.items()}
        for p,raw in outputs.items():
            if p.exists()and p.read_bytes()!=raw:raise ValueError('Preview file has different bytes; use a new preview directory: '+str(p))
        for p,raw in outputs.items():p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        (target/'maps.json').write_text(json.dumps(maps,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        summary['status']='private SVG preview only; game assets unchanged';summary['preview']=str(target)
        (target/'manifest.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    console={k:v for k,v in summary.items()if k not in ('caption_events','output_hashes')}
    console['caption_reveals']={k:v['text']for k,v in summary['caption_events'].items()if v['action']=='show'}
    print(json.dumps(console,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
