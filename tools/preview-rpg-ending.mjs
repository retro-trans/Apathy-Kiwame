// Copy the current GIF preview verbatim; record legacy SVGs in the QA renderer.
// Never edits the source asset or writes a game slot.
import {connect,ensureInitialized} from './qa-session.mjs';
import {mkdir,writeFile,copyFile,readFile} from 'node:fs/promises';
import {constants} from 'node:fs';
import path from 'node:path';
const output=process.argv[2];
if(!output)throw Error('Specify a new preview directory.');
await mkdir(output);
await mkdir(path.join(output,'frames'));
const c=await connect();
try{
 await ensureInitialized(c);
 const spec=JSON.parse(await readFile(new URL('../work/ui/rpg-game-over.json',import.meta.url),'utf8'));
 const clip=await c.js(`(function(){
  var target=window.kiwameEnglishUI.backgrounds['rpg/siboued.gif'];
  if(!/\.gif$/.test(target))return null;
  if(target!=='kiwame-en/rpg-game-over.gif')throw Error('Unexpected preview target');
  var fs=require('fs'),p=require('path'),file=p.join(p.dirname(process.execPath),'package.nw/data/bgimage',target);
  return {file:file,sha256:require('crypto').createHash('sha256').update(fs.readFileSync(file)).digest('hex'),frames:78,frameMs:50,width:640,height:460};
 }())`);
 if(clip){
  if(clip.sha256!==spec.rendered_animation_sha256)throw Error('Unexpected English GIF checksum');
  await copyFile(clip.file,path.join(output,'clip.gif'),constants.COPYFILE_EXCL);
  await writeFile(path.join(output,'capture.json'),JSON.stringify(clip,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify({...clip,file:'clip.gif'}));
 }else{
 const source=await c.js(`(function(){
  var fs=require('fs'),path=require('path'),crypto=require('crypto');
  var file=path.join(path.dirname(process.execPath),'package.nw','data','bgimage','kiwame-en','rpg-game-over.svg');
  var raw=fs.readFileSync(file,'utf8');
  var checksum=crypto.createHash('sha256').update(raw).digest('hex');
  if(checksum!=='cd8544d8d422f12941852957294004ff45ecddf7d557dc1a48d4ca01539d31c8')throw Error('Unexpected ending asset');
  var xml=(new DOMParser()).parseFromString(raw,'image/svg+xml');
  var host=document.createElement('div');host.id='kiwame-ending-preview';
  host.style.cssText='position:fixed;left:0;top:0;width:960px;height:690px;z-index:2147483647;pointer-events:none;background:black';
  var svg=document.importNode(xml.documentElement,true);host.appendChild(svg);document.body.appendChild(host);
  svg.pauseAnimations();svg.setCurrentTime(0);window.endingPreviewSVG=svg;
  return {sha256:checksum,frames:78,frameMs:50,width:960,height:690,label:svg.getAttribute('aria-label')};
 }())`);
 for(let i=0;i<source.frames;i++){
  await c.js(`window.endingPreviewSVG.setCurrentTime(${i*source.frameMs/1000});window.endingPreviewSVG.getCTM();true`);
  await c.screenshot(path.join(output,'frames',String(i).padStart(3,'0')+'.png'));
 }
 await writeFile(path.join(output,'capture.json'),JSON.stringify(source,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify(source));
 }
}finally{
 await c.js(`(function(){var h=document.getElementById('kiwame-ending-preview');if(h)h.remove();delete window.endingPreviewSVG;return true;}())`).catch(()=>{});
 c.close();
}
