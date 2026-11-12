"""Render reviewed common lettering without installing assets or changing scripts.

Default execution validates and reports in memory. --preview writes an isolated
common-art-draft directory. artwork(asset_root, maps) returns installable bytes.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'work/ui/common-lettering.json'
PROOFS: list[dict] = []


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def font(size):
    return ImageFont.truetype(str(ROOT / 'tools/fonts/genei-latin/GenEiLateGoP_v2.ttf'), size)


def box_mask(size, box, feather=0):
    x, y, w, h = map(int, box)
    m = Image.new('L', size)
    ImageDraw.Draw(m).rectangle((x, y, x+w-1, y+h-1), fill=255)
    if feather:
        # Fade inward only: never allow generated content outside the patch.
        blurred = m.filter(ImageFilter.GaussianBlur(feather))
        m = ImageChops.multiply(m, blurred)
    return m


def changed_mask(a, b):
    aa = np.asarray(a.convert('RGBA')).astype(np.int16)
    bb = np.asarray(b.convert('RGBA')).astype(np.int16)
    return Image.fromarray((np.any(aa != bb, axis=2)*255).astype('uint8'))


def paste_patch(out, plate, box, allowed, feather=2, protect=None):
    mask = box_mask(out.size, box, feather)
    if protect is not None:
        mask = ImageChops.subtract(mask, protect)
    out.paste(plate, (0, 0), mask)
    allowed.paste(255, mask=box_mask(out.size, box))


def text(out, allowed, value, x, baseline, size, *, color='white', anchor='ls', stroke=0):
    layer = Image.new('RGBA', out.size)
    ImageDraw.Draw(layer).text((x, baseline), value, font=font(size), fill=color,
                               anchor=anchor, stroke_width=stroke, stroke_fill='black')
    mask = layer.getchannel('A')
    out.alpha_composite(layer)
    allowed.paste(255, mask=mask.point(lambda v: 255 if v else 0))


def fit_size(lines, width, preferred):
    for size in range(preferred, 7, -1):
        if max(font(size).getlength(s) for s in lines) <= width:
            return size
    raise ValueError('Whole-word English copy does not fit its approved region.')


def atlas_plate(item, spec):
    atlas = Image.open(ROOT/spec['atlas']).convert('RGBA').resize(tuple(spec['atlas_reference_size']), Image.Resampling.LANCZOS)
    x, y, w, h = item['plate_tile']['tile_box']
    tile = atlas.crop((x, y, x+w, y+h)).resize((960, 200), Image.Resampling.LANCZOS)
    plate = Image.new('RGBA', (960, 690))
    plate.paste(tile)
    return plate


def preserve_colored_symbols(original, stem):
    a = np.asarray(original.convert('RGB')).astype(float)
    keep = np.zeros(a.shape[:2], dtype=bool)
    if stem == 'hyakuten':
        return Image.open(ROOT/'work/ui/art/common-hyakuten-seal-protect.png').convert('L')
    if stem == 'syourei':
        keep = (a[:,:,0] > 1.5*a[:,:,1]) & (a[:,:,0] > 1.5*a[:,:,2]) & (a[:,:,0] > 40)
    if stem == 'jikkyo':
        # Keep controller illustrations exactly; pink title-edge antialiasing
        # must not be mistaken for red artwork and restored above cleanup.
        keep[69:99,600:625] = True
        keep[59:106,744:777] = True
    if stem == 'syourei':
        # Original handprint lies to the right of the title glyphs.
        keep[:,753:] = True
    return Image.fromarray((keep*255).astype('uint8'))


def adjusted_gray(source, reference, roi):
    """Match already-reviewed source-scene lettering to the darker ED copy."""
    src = source.convert('L'); ref = reference.convert('L')
    x,y,w,h=roi
    a=np.asarray(src.crop((x,y,x+w,y+h)),dtype=float).ravel()
    b=np.asarray(ref.crop((x,y,x+w,y+h)),dtype=float).ravel()
    slope,offset=np.polyfit(a,b,1)
    slope=float(np.clip(slope,.05,1.2));offset=float(np.clip(offset,-35,35))
    arr=np.clip(np.asarray(src,dtype=float)*slope+offset,0,255).astype('uint8')
    return Image.fromarray(arr).convert('RGBA')


def embedded(out, original, allowed, stem, spec):
    if stem == 'jikkyo':
        src=Image.open(ROOT/'work/ui/art/common-reuse-majiru.png').convert('RGBA')
        src=adjusted_gray(src,original,[250,220,450,280])
        paste_patch(out,src,[288,192,359,227],allowed,3)
    elif stem == 'rengoku':
        src=Image.open(ROOT/spec['dating_plate']).convert('RGBA').resize(out.size,Image.Resampling.LANCZOS)
        for rect in [[463,350,446,64],[657,448,144,41],[697,506,168,41],[802,563,112,43]]:
            paste_patch(out,src,rect,allowed,3)
        text(out,allowed,'Heart Sensation',689,392,28,color='#303030',anchor='ms',stroke=1)
        for word,x,y in [('Start',741,481),('Continue',782,540),('Quit',858,596)]:
            text(out,allowed,word,x,y,25,color='#3c3c3c',anchor='ms')
    elif stem == 'sns':
        src=Image.open(ROOT/'work/ui/art/common-reuse-sns.png').convert('RGBA')
        src=adjusted_gray(src,original,[380,170,440,380]).filter(ImageFilter.GaussianBlur(2))
        for block in spec['sns_blocks']:
            a,b,c,d,tx,ty=block['transform'];x,y,w,h=block['rect']
            corners=[(a*xx+c*yy+tx,b*xx+d*yy+ty) for xx,yy in [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]]
            m=Image.new('L',out.size);ImageDraw.Draw(m).polygon(corners,fill=255)
            edge=m.filter(ImageFilter.MaxFilter(7))
            blend=ImageChops.multiply(m.filter(ImageFilter.GaussianBlur(1)),edge)
            # The baked route badge occludes part of the top phone message.
            # Do not reveal that hidden text or paint over the badge frame.
            excluded=box_mask(out.size,[550,25,260,137])
            blend=ImageChops.subtract(blend,excluded)
            edge=ImageChops.subtract(edge,excluded)
            out.paste(src,(0,0),blend)
            allowed.paste(255,mask=edge)
    elif stem == 'syourei':
        # Same physical grid; annotate, don't invent an English alphabet grid.
        layer=Image.new('RGBA',out.size);d=ImageDraw.Draw(layer)
        for col in spec['board_columns']:
            for label,y in zip(col['labels'],col['centers_y']):
                if label is not None:
                    d.text((col['x'],y+43),label,font=font(17),anchor='ms',fill='#101711',stroke_width=1,stroke_fill='#45453d')
        for label,x in [('YES',265),('NO',697)]:
            d.text((x,193),label,font=font(17),anchor='ms',fill='#101711',stroke_width=1,stroke_fill='#45453d')
        # Coin remains above all lettering at its original position.
        coin=Image.new('L',out.size);ImageDraw.Draw(coin).ellipse((471,101,580,209),fill=255)
        alpha=ImageChops.subtract(layer.getchannel('A'),coin);layer.putalpha(alpha)
        out.alpha_composite(layer);allowed.paste(255,mask=alpha.point(lambda v:255 if v else 0))


def ending(original,item,spec):
    out=original.copy();allowed=Image.new('L',out.size)
    stem=Path(item['source']).stem
    plate=atlas_plate(item,spec);protect=preserve_colored_symbols(original,stem)
    if stem in ('hyakuten','zinniku'):
        atlas=Image.open(ROOT/spec['emblems_plate']).convert('RGBA').resize((960,480),Image.Resampling.LANCZOS)
        x=0 if stem=='hyakuten' else 480
        tile=atlas.crop((x,0,x+480,400)).resize((240,200),Image.Resampling.LANCZOS)
        plate.paste(tile,(570,0))
    for rect in item['cleanup_rects']:
        use_plate=plate
        if stem=='jikkyo' and rect[0]>500:
            use_plate=Image.open(ROOT/spec['jikkyo_plate']).convert('RGBA').resize(out.size,Image.Resampling.LANCZOS)
        paste_patch(out,use_plate,rect,allowed,2,protect)
    embedded(out,original,allowed,stem,spec)
    text(out,allowed,'Ending List',38,151,21)
    title=item['title']
    if stem=='title1':
        text(out,allowed,'Kiwame',582,141,21,stroke=1)
    elif stem=='gunzin':
        text(out,allowed,"A Soldier's",684,58,17,anchor='ms')
        text(out,allowed,'Last',684,144,10,color='black',anchor='ms')
        text(out,allowed,'Letter',684,159,10,color='black',anchor='ms')
    else:
        x,y,w,h=title['proposed_lettering_box'];lines=title['proposed_lines']
        size=fit_size(lines,w,title['font_size']);step=size+4
        top=y+max(0,(h-len(lines)*step)/2)
        for i,line in enumerate(lines):
            color='black' if stem=='zinniku' else 'white'
            text(out,allowed,line,x+w/2,top+size+i*step,size,color=color,anchor='ms',stroke=0 if stem=='zinniku' else 1)
    return out,allowed


def newspaper(original,item):
    # A generated blank-paper plate supplies the photographic cleanup.  The
    # stored boundary blend is anchored separately and clipped to its mask;
    # English is deterministic lettering on a transparent layer.
    plate=Image.open(ROOT/item['blended_plate']).convert('RGBA')
    patch_mask=Image.open(ROOT/item['patch_mask']).convert('L')
    out=original.copy();out.paste(plate,(0,0),patch_mask)
    rot=original.rotate(-51,expand=True)
    layer=Image.new('RGBA',rot.size);d=ImageDraw.Draw(layer)
    for block in item['blocks']:
        value=block.get('english',block.get('english_proposal'))
        x,y,w,h=block['rectified_edit_box'];size=block['font_size']
        for i,line in enumerate(block.get('lines',[value])):
            baseline=block.get('baseline',y+size+i*block.get('line_height',size+4))
            d.text((x,baseline),line,font=font(size),fill='#3b352e',anchor='ls')
    layer=layer.filter(ImageFilter.GaussianBlur(.55))
    layer.putalpha(ImageChops.multiply(layer.getchannel('A'),rot.getchannel('A')))
    back=layer.rotate(51,expand=True,resample=Image.Resampling.BICUBIC)
    left=(back.width-original.width)//2;top=(back.height-original.height)//2
    back=back.crop((left,top,left+original.width,top+original.height))
    out.alpha_composite(back)
    allowed=ImageChops.lighter(patch_mask,back.getchannel('A')).point(lambda v:255 if v else 0)
    return out,allowed


def raster(original,item,spec):
    kind=item['kind'];out=original.copy();allowed=Image.new('L',out.size)
    if kind=='newspaper':return newspaper(original,item)
    if kind=='ending':return ending(original,item,spec)
    if kind in ('main','trial'):
        if kind=='trial':
            box=[210,45,106,32];out.paste((0,0,0,255),tuple([box[0],box[1],box[0]+box[2],box[1]+box[3]]));allowed.paste(255,mask=box_mask(out.size,box))
            text(out,allowed,'- Demo -',263,70,21,anchor='ms')
        b=item['badge'];text(out,allowed,b['english'],b['x'],b['baseline'],b['font_size'],stroke=1)
    elif kind=='site':
        patch=[0,0,60,24];out.paste((0,0,0,0),(0,0,60,24));allowed.paste(255,mask=box_mask(out.size,patch))
        keep=Image.new('L',out.size);d=ImageDraw.Draw(keep);d.ellipse((12,15,48,43),fill=255);d.rectangle((0,24,59,44),fill=255)
        out.paste(original,(0,0),keep)
        color='white' if Path(item['source']).stem=='bana2' else 'black'
        text(out,allowed,'Official Site',30,11,9,color=color,anchor='ms')
    elif kind=='disclaimer':
        box=[55,127,787,350];out.paste((0,0,0,255),(55,127,842,477));allowed.paste(255,mask=box_mask(out.size,box))
        for b in item['blocks']:
            x,y,w,h=b['box']
            if b['id'] in ('heading','continue'):text(out,allowed,b['english'],x+w/2,b['baseline'],b['font_size'],anchor='ms')
            else:
                for i,line in enumerate(b['suggested_lines']):text(out,allowed,line,x,y+b['font_size']+i*b['line_height'],b['font_size'])
    elif kind=='staff':
        for row in item['rows']:
            if row['kind']!='role':continue
            x,y,w,h=row['proposed_edit_box'];out.paste((0,0,0,0),(x,y,x+w,y+h));allowed.paste(255,mask=box_mask(out.size,[x,y,w,h]))
            text(out,allowed,row['english'],235,row['source_ink_bounds_xyxy'][1]+15,16,color='#ff0000')
    elif kind!='publisher':raise ValueError('Unknown common-art kind: '+kind)
    return out,allowed


def artwork(asset_root,maps):
    """Validate exact originals; return 29 asset payloads, without filesystem writes."""
    spec=json.loads(SPEC.read_text(encoding='utf-8'));files={};PROOFS.clear()
    if digest(ROOT/spec['font'])!=spec['font_sha256']:raise ValueError('Common lettering font SHA mismatch.')
    for plate in spec['clean_plates']:
        if digest(ROOT/plate['path'])!=plate['sha256']:raise ValueError('Clean plate SHA mismatch: '+plate['path'])
    for reused in spec['reused_source_renders']:
        if digest(ROOT/reused['path'])!=reused['sha256']:raise ValueError('Reused source-render SHA mismatch.')
    for item in spec['items']:
        source=asset_root/item['source']
        if digest(source)!=item['source_sha256']:raise ValueError('Original SHA mismatch: '+item['source'])
        original=Image.open(source).convert('RGBA')
        if list(original.size)!=item['dimensions']:raise ValueError('Original dimensions changed.')
        folder=Path(item['source']).parts[0];target=asset_root/folder/'kiwame-en'/item['target']
        group=maps.setdefault(item['map_group'],{});mapped='kiwame-en/'+item['target'];existing=group.get(item['map_key'])
        if existing not in (None,mapped):raise ValueError('Conflicting common image map: '+item['map_key'])
        group[item['map_key']]=mapped
        if item['kind']=='life_reuse':
            from inoti_art import extras
            payload=extras(asset_root)[target]
            files[target]=payload
            PROOFS.append({'id':item['id'],'source':item['source'],'source_sha256':item['source_sha256'],'output_sha256':sha256(payload).hexdigest(),'existing_life_map':'reused unchanged','review':'Existing reviewed Life hover reused; no conflicting map.'})
            continue
        out,allowed=raster(original,item,spec);change=changed_mask(original,out)
        outside=ImageChops.subtract(change,allowed)
        if outside.getbbox():raise ValueError('Pixels changed outside explicit common lettering: '+item['id'])
        if item['kind'] in ('main','trial'):
            if out.crop((73,644,373,670)).tobytes()!=original.crop((73,644,373,670)).tobytes():raise ValueError('Copyright pixels changed.')
        if item['kind']=='staff':
            for row in item['rows']:
                if row['kind']=='name' and out.crop(tuple(row['source_ink_bounds_xyxy'])).tobytes()!=original.crop(tuple(row['source_ink_bounds_xyxy'])).tobytes():raise ValueError('Credited name pixels changed.')
        buf=BytesIO();out.save(buf,format='PNG');payload=buf.getvalue();files[target]=payload
        PROOFS.append({'id':item['id'],'source':item['source'],'source_sha256':item['source_sha256'],'dimensions':list(out.size),'output_sha256':sha256(payload).hexdigest(),'changed_bbox':change.getbbox(),'outside_allowed_pixels':0,'copyright_preserved':True if item['kind'] in ('main','trial') else None,'all37credited_name_rects_preserved':True if item['kind']=='staff' else None})
    if len(files)!=29:raise ValueError('Expected 29 common assets.')
    return files


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--preview',type=Path);args=parser.parse_args()
    base=ROOT/'work/debug/kiwame-base/package.nw/data';maps={'backgrounds':{},'images':{},'buttons':{}};files=artwork(base,maps)
    report={'status':'Common artwork candidate; native approval pending','source_spec_sha256':digest(SPEC),'asset_count':len(files),'maps':maps,'proofs':PROOFS,'review':{'accuracy':'Copy rechecked against reviewed common-art plan; no clipped/blurred prose invented, names and copyrights protected.','editorial':'Full approved copy retained; font sizes/whole-word lines adjusted only geometrically.','proofreading':'29 source SHA/dimensions, mapping collisions, decoded RGBA pixels outside explicit masks, 37 credited-name rectangles, and copyright rectangles checked.','native_fit':'Not evaluated; no native/CDP launch. Artwork changes no commands. Root will replace only the disclaimer1500ms hold with a native click pause matching the footer; other startup timings remain unchanged.'},'change_log':[{'date':'2026-11-11','change':'Rendered common English candidate in memory with29mappedassets; original scripts/durations untouched.'}]}
    print('29 common assets validated in memory; no installation performed.')
    if args.preview:
        dest=args.preview.resolve();dest.relative_to((ROOT/'work/debug').resolve())
        if not dest.name.startswith('common-art-draft'):raise ValueError('Preview must use common-art-draft prefix.')
        dest.mkdir(parents=True,exist_ok=False)
        for path,raw in files.items():(dest/path.name).write_bytes(raw)
        (dest/'proof-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Wrote isolated preview to',dest)


if __name__=='__main__':main()
