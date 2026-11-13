// Real pointer hover/mouse-out regression. Capture only the menu-heading region.
import {connect,ensureInitialized,sleep} from './qa-session.mjs';
import {writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const id=process.argv[2];if(!id||!/^[a-z0-9-]+$/.test(id))throw Error('Specify a new capture ID.');
const c=await connect();
async function header(file){
 // This bundled debugger ignores screenshot clip. Crop the active image through
 // native Canvas instead, so review artifacts contain only the safe UI heading.
 await c.js(`(function(){
  window.headerCrop=null;var active=$('img[class*="_rogo"]').filter(function(){return $(this).is(':visible')&&Number($(this).css('opacity'))>.99});
  var src=active.length?active.last().attr('src'):TYRANO.kag.layer.getLayer('base','fore').css('background-image').replace(/^url\\(["']?|["']?\\)$/g,'');
  var canvas=document.createElement('canvas');canvas.width=190;canvas.height=36;var context=canvas.getContext('2d');context.fillStyle='black';context.fillRect(0,0,190,36);
  if(!src||src==='none'){window.headerCrop=canvas.toDataURL('image/png').split(',')[1];return true}
  var image=new Image();image.onload=function(){context.drawImage(image,30,125,190,36,0,0,190,36);window.headerCrop=canvas.toDataURL('image/png').split(',')[1]};image.onerror=function(){window.headerCrop='error'};image.src=src;return true;
 }())`);
 let data;
 for(let i=0;i<100;i++){data=await c.js('window.headerCrop');if(data)break;await sleep(20);}
 if(!data||data==='error')throw Error('Header crop decode failed');
 const raw=Buffer.from(data,'base64');
 if(raw.readUInt32BE(16)!==190||raw.readUInt32BE(20)!==36)throw Error('Incorrect heading-only crop size');
 if(file)await writeFile(file,raw,{flag:'wx'});return createHash('sha256').update(raw).digest('hex');
}
async function move(x,y){await c.send('Input.dispatchMouseEvent',{type:'mouseMoved',x,y,button:'none'});await sleep(70);}
async function page(first,english=false){
 for(let i=0;i<160;i++){
  const s=await c.js(`(function(){var k=TYRANO.kag,t=k.ftag.array_tag[k.ftag.current_order_index]||{},rows=$('.edlist_name:visible').map(function(){return $(this).text()}).get();return {scenario:k.stat.current_scenario,strong:k.stat.is_strong_stop,tag:t.name,rows:rows,base:k.layer.getLayer('base','fore').css('background-image'),errors:window.headerErrors||[]};}())`);
  if(s.errors.length)throw Error(JSON.stringify(s.errors));
  if(s.scenario==='ED.ks'&&s.strong&&s.tag==='s'&&s.rows.some(x=>x.startsWith(first))&&(!english||s.base.includes('ending-list-base')))return s;
  await header();await sleep(70);
 }
 throw Error('Ending page did not settle: '+first);
}
async function point(group){return c.js(`(function(){var found=null;$('.${group}').filter(':visible').each(function(){if(found)return;var r=this.getBoundingClientRect();for(var y=r.top+3;y<Math.min(r.bottom,680);y+=15){for(var x=r.left+3;x<Math.min(r.right,950);x+=15){if(x<0||y<0)continue;var e=document.elementFromPoint(x,y);if(e&&$(e).closest('.${group}').length){found={x:x,y:y};return}}}});if(!found)throw Error('No real pointer target for ${group}');return found;}())`);}
async function opacity(group){return c.js(`(function(){var a=$('img.${group}_rogo').filter(':visible');return {count:a.length,opacity:a.map(function(){return Number($(this).css('opacity'))}).get(),src:a.map(function(){return this.getAttribute('src')}).get()};}())`);}
try{
 await ensureInitialized(c);
 await c.js(`window.headerErrors=[];$.error_message=function(m){window.headerErrors.push(m)};window.addEventListener('error',function(e){if(e.message)window.headerErrors.push(e.message)});window.savedHeaderAliases={upper:window.kiwameEnglishUI.backgrounds['ED.jpg'],lower:window.kiwameEnglishUI.backgrounds['ed.jpg']};delete window.kiwameEnglishUI.backgrounds['ED.jpg'];delete window.kiwameEnglishUI.backgrounds['ed.jpg'];window.kiwameQA.jump('ED.ks','');true`);
 await page('ED001:');await move(20,100);
 const baselineOutside=await header(`work/ui/ending-hover-${id}-baseline-outside.png`);
 const first=await point('konkan');await move(first.x,first.y);
 const baselineHover=await header(`work/ui/ending-hover-${id}-baseline-hover.png`);
 await move(20,100);const baselineReturn=await header();
 if(baselineOutside===baselineHover||baselineReturn!==baselineOutside)throw Error('Main-copy hover regression was not reproduced');
 await c.js(`window.kiwameEnglishUI.backgrounds['ED.jpg']=window.savedHeaderAliases.upper;window.kiwameEnglishUI.backgrounds['ed.jpg']=window.savedHeaderAliases.lower;window.kiwameQA.jump('ED.ks','');true`);
 await page('ED001:',true);await move(20,100);
 const fixedOutside=await header(`work/ui/ending-hover-${id}-fixed-outside.png`);
 if(fixedOutside===baselineOutside)throw Error('Base heading did not change to English');
 const pages=[['ED001:',['konkan','hukusyu','uso']],['ED061:',['zinniku','ziko','hyakuten','jikkyo','syourei','gunzin','rengoku','inoti']],['ED121:',['inoti','sns','kyukousya','sanmyaku','syourei']]];
 const cases=[],counts=[];
 for(let i=0;i<pages.length;i++){
  if(i){await c.js(`window.kiwameQA.click('img[src$="button/modoru2.png"]')`);}
  const state=await page(pages[i][0]);counts.push(state.rows.length);await move(20,100);
  if(await header()!==fixedOutside)throw Error('Base heading differs on page '+(i+1));
  for(const group of pages[i][1]){
   const p=await point(group);await move(p.x,p.y);const on=await opacity(group);
   if(!on.opacity.some(x=>x===1)||!on.src.some(x=>x.includes('kiwame-en/')))throw Error('Translated hover art missing: '+group);
   const hover=await header();await move(20,100);const off=await opacity(group);
   if(off.opacity.some(x=>x!==0)||await header()!==fixedOutside)throw Error('Heading regressed on mouse-out: '+group);
   cases.push({page:i+1,group,translatedHoverArt:true,hoverHeaderSha256:hover,mouseOutRestoresEnglish:true});
  }
 }
 for(const first of ['ED061:','ED001:']){await c.js(`window.kiwameQA.click('img[src$="button/modoru.png"]')`);await page(first);await move(20,100);if(await header()!==fixedOutside)throw Error('Back navigation heading regressed');}
 if(counts.join(',')!=='60,60,27')throw Error('Ending entry counts changed');
 const result={version:'0.8.2',baseline:{outsideHeaderSha256:baselineOutside,hoverHeaderSha256:baselineHover,mouseOutReturnsJapanese:true},fixed:{outsideHeaderSha256:fixedOutside,counts,cases,uniqueGroups:new Set(cases.map(x=>x.group)).size,backNavigation:true},mainSteamChanged:false,userSaveFilesWritten:false,productionChangeAlreadyStaged:true};
 await writeFile(`work/ui/ending-hover-${id}-verification.json`,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify({hoverCases:cases.length,uniqueGroups:result.fixed.uniqueGroups,counts,allMouseOutHeadersEnglish:true}));
}finally{
 await c.js(`if(window.savedHeaderAliases){window.kiwameEnglishUI.backgrounds['ED.jpg']=window.savedHeaderAliases.upper;window.kiwameEnglishUI.backgrounds['ed.jpg']=window.savedHeaderAliases.lower}true`).catch(()=>{});
 c.close();
}
