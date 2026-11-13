// Reproduce the three reported passages using native RPG macros and pauses.
import {connect,ensureInitialized,sleep} from './qa-session.mjs';
import {writeFile} from 'node:fs/promises';
const [mode,id]=process.argv.slice(2);
if(!['baseline','fixed'].includes(mode)||!id||!/^[a-z0-9-]+$/.test(id))throw Error('Specify baseline|fixed and a new capture ID.');
const c=await connect();
async function read(){return c.js(`(function(){var k=TYRANO.kag,t=k.ftag.array_tag[k.ftag.current_order_index]||{},m=k.getStack('macro'),cached=m&&k.cache_scenario['./data/scenario/'+m.storage],caller=cached&&cached.array_s[m.index];var p=k.getMessageInnerLayer();return {scenario:k.stat.current_scenario,line:t.line+1,tag:t.name,callerScenario:m&&m.storage,callerLine:caller&&caller.line+1,adding:k.stat.is_adding_text,strong:k.stat.is_strong_stop,text:p.text(),html:p.html(),breaks:p.find('br').length,errors:window.flowErrors||[]};}())`);}
async function until(test,advance=false){
 for(let start=Date.now();Date.now()-start<55000;){
  const s=await read();if(s.errors.length)throw Error(JSON.stringify(s));if(test(s))return s;
  if(advance&&!s.adding&&['l','p'].includes(s.tag))await c.js('window.kiwameQA.advance()');
  await c.screenshot();await sleep(35);
 }
 throw Error('Flow condition timed out: '+JSON.stringify(await read()));
}
async function jump(file,label){
 await until(s=>!s.adding&&['s','p','l'].includes(s.tag));
 await c.js(`(function(){var k=TYRANO.kag;k.stat.stack.macro=[];k.stat.stack.if=[];k.stat.is_strong_stop=true;k.stat.ch_speed='0';window.kiwameQA.jump(${JSON.stringify(file)},${JSON.stringify(label)});return true;}())`);
 // Do not mistake a pause inherited from the previous scene for the new one.
 await until(s=>s.scenario===file||s.callerScenario===file);
}
async function snapshot(name){return c.js(`(function(){var k=TYRANO.kag;k.menu.snapSave('QA text flow',function(){window.${name}=$.extend(true,{},k.menu.snap)},'false');return true;}())`);}
try{
 await ensureInitialized(c);
 await c.js(`window.flowErrors=[];$.error_message=function(m){window.flowErrors.push(m)};window.addEventListener('error',function(e){if(e.message)window.flowErrors.push(e.message)});TYRANO.kag.ftag.startTag('call',{storage:'rpg/rpg_settei.ks',target:'*初期化',auto_next:'stop'});true`);
 await until(s=>s.scenario==='title.ks'&&s.tag==='s'&&s.strong);
 let parserCheck;
 if(mode==='fixed')parserCheck=await c.js(`(function(){
  var k=TYRANO.kag,v=window.kiwameEnglishUI,fs=require('fs'),p=require('path');
  var saved=k.stat.current_scenario,maps=v.flowMacroBreaks,count=0,orders=0,files=0;
  try{Object.keys(maps).forEach(function(name){
   k.stat.current_scenario=name;var raw=fs.readFileSync(p.join(p.dirname(process.execPath),'package.nw/data/scenario',name),'utf8');
   v.flowMacroBreaks={};var before=k.parser.parseScenario(raw);v.flowMacroBreaks=maps;var after=k.parser.parseScenario(raw);
   if(before.array_s.length!==after.array_s.length||JSON.stringify(before.map_label)!==JSON.stringify(after.map_label))throw Error('Parser structure changed');
   after.array_s.forEach(function(tag,i){var copy=$.extend(true,{},tag);if(Object.prototype.hasOwnProperty.call(copy.pm,'kiwame_flow_separator')){count++;delete copy.pm.kiwame_flow_separator}if(JSON.stringify(copy)!==JSON.stringify(before.array_s[i]))throw Error('Unexpected parsed command change')});
   orders+=after.array_s.length;files++;
  });}finally{v.flowMacroBreaks=maps;k.stat.current_scenario=saved}
  return {files:files,orders:orders,annotated:count,orderPositionsAndLabelsUnchanged:true};
 }())`);
 // Enter the original RPG setup at its layout transition: frame, margins,
 // font, title sequence and status HUD. Direct rpg00 entry inherits title UI.
 await c.js(`TYRANO.kag.ftag.startTag('chara_config',{pos_mode:'false'});true`);
 await c.js(`(function(){var k=TYRANO.kag;k.layer.getFreeLayer().empty().hide();$('.fixlayer').remove();k.stat.is_strong_stop=false;k.stat.ch_speed='0';k.loadScenario('rpg/rpg_op.ks',function(tags){var index=-1;for(var i=0;i<tags.length;i++){if(tags[i].name==='position'&&tags[i].line===64){index=i;break}}if(index<0)throw Error('Missing native RPG layout transition');k.ftag.buildTagIndex(tags,index-1,'yes')});return true;}())`);
 await until(s=>s.scenario==='rpg/rpg00.ks'&&s.tag==='p'&&!s.adding);
 await jump('rpg/stage.ks','玄関');
 await until(s=>s.scenario==='rpg/stage.ks'&&s.tag==='s'&&s.strong);
 await jump('rpg/stage.ks','玄関2');
 await until(s=>s.scenario==='rpg/stage.ks'&&s.tag==='s'&&s.strong);
 await jump('rpg/stage.ks','玄関イベント1');
 const commaPause=await until(s=>s.tag==='l'&&s.callerScenario==='rpg/stage.ks'&&s.callerLine===81&&!s.adding,true);
 if(!commaPause.text.endsWith('school days,'))throw Error('Wrong shoe-cubby pause');
 await snapshot('flowCommaSnapshot');
 await c.js('window.kiwameQA.advance()');
 const days=await until(s=>s.scenario==='rpg/stage.ks'&&s.line===82&&s.tag==='p'&&!s.adding);
 if(mode==='fixed'&&(!days.text.includes('school days, but')||days.breaks!==commaPause.breaks))throw Error('Comma continuation did not reflow');
 if(mode==='baseline'&&days.breaks<=commaPause.breaks)throw Error('Original comma break was not reproduced');
 await c.screenshot(`work/ui/rpg-flow-${id}-days.png`);
 await jump('rpg/rpg00.ks','シーン004');
 const cursePause=await until(s=>s.tag==='l'&&s.callerScenario==='rpg/rpg00.ks'&&s.callerLine===442&&!s.adding,true);
 await c.js('window.kiwameQA.advance()');
 const curseMiddle=await until(s=>s.tag==='l'&&s.callerScenario==='rpg/rpg00.ks'&&s.callerLine===443&&!s.adding);
 if(mode==='fixed'&&(!curseMiddle.text.includes('right now, you')||curseMiddle.breaks!==cursePause.breaks))throw Error('Curse comma continuation did not reflow');
 await c.js('window.kiwameQA.advance()');
 const curse=await until(s=>s.scenario==='rpg/rpg00.ks'&&s.line===444&&s.tag==='p'&&!s.adding);
 if(curse.breaks!==curseMiddle.breaks+1)throw Error('Sentence break after believe me was lost');
 await c.screenshot(`work/ui/rpg-flow-${id}-curse.png`);
 await c.js(`TYRANO.kag.stat.is_strong_stop=true;TYRANO.kag.ftag.startTag('chara_hide',{name:'hino_kao',layer:'message0',time:'0',wait:'false'});true`);
 await jump('rpg/batoru.ks','ショゴス_勝利');
 await until(s=>s.scenario==='rpg/batoru.ks'&&s.line===1341&&s.tag==='l'&&!s.adding,true);
 await c.js('window.kiwameQA.advance()');
 const eyelids=await until(s=>s.scenario==='rpg/batoru.ks'&&s.line===1343&&s.tag==='p'&&!s.adding);
 if(!eyelids.text.includes(mode==='fixed'?'But my eyelids':'Butmy eyelids'))throw Error('Missing-space expectation failed');
 await c.screenshot(`work/ui/rpg-flow-${id}-eyelids.png`);
 const result={mode,parserCheck,commaPause,days,cursePause,curseMiddle,curse,eyelids,mainSteamChanged:false,userSaveSlotsWritten:false};
 if(mode==='fixed'){
  // Old slot with its already rendered merged word. Keep the snapshot immutable.
  await c.js(`(function(){var k=TYRANO.kag,w=document.createTreeWalker(k.getMessageInnerLayer()[0],4,null,false),n;while((n=w.nextNode()))n.nodeValue=n.nodeValue.replace('But my eyelids','Butmy eyelids');return true;}())`);
  await snapshot('flowMergedSnapshot');
  await c.js(`TYRANO.kag.menu.loadGameData($.extend(true,{},window.flowMergedSnapshot),{bgm_over:'true'});true`);await sleep(500);
  result.legacyMerged=await read();if(!result.legacyMerged.text.includes('But my eyelids'))throw Error('Stored merged text was not repaired');
  // Old slot saved within lr, without our new macro metadata or caller cache.
  await c.js(`(function(){var s=window.flowCommaSnapshot;delete s.stat.mp.kiwame_flow_separator;s.stat.stack.macro.forEach(function(m){if(m.pm)delete m.pm.kiwame_flow_separator});delete TYRANO.kag.cache_scenario['./data/scenario/rpg/stage.ks'];TYRANO.kag.menu.loadGameData($.extend(true,{},s),{bgm_over:'true'});return true;}())`);
  await until(s=>s.tag==='l'&&!s.adding&&s.text.endsWith('school days,'));
  await c.js('window.kiwameQA.advance()');
  result.legacyPause=await until(s=>s.scenario==='rpg/stage.ks'&&s.line===82&&s.tag==='p'&&!s.adding);
  if(!result.legacyPause.text.includes('school days, but')||result.legacyPause.breaks!==commaPause.breaks)throw Error('Legacy lr pause did not reflow');
  await c.js(`(function(){var k=TYRANO.kag,w=document.createTreeWalker(k.getMessageInnerLayer()[0],4,null,false),n,done=false;while((n=w.nextNode())){var at=n.nodeValue.indexOf('school days, but');if(at<0)continue;var tail=n.splitText(at+'school days,'.length);tail.nodeValue=tail.nodeValue.slice(1);tail.parentNode.insertBefore(document.createElement('br'),tail);done=true;break}if(!done)throw Error('Could not build old hard-break fixture');return true;}())`);
  await snapshot('flowOldBreakSnapshot');
  await c.js(`TYRANO.kag.menu.loadGameData($.extend(true,{},window.flowOldBreakSnapshot),{bgm_over:'true'});true`);await sleep(500);
  result.legacyBreak=await read();
  if(!result.legacyBreak.text.includes('school days, but')||result.legacyBreak.breaks!==commaPause.breaks)throw Error('Stored hard break was not repaired');
 }
 await writeFile(`work/ui/rpg-flow-${id}-verification.json`,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify({mode,daysBreaks:days.breaks,curseBreaks:curse.breaks,eyelids:eyelids.text,legacyMerged:!!result.legacyMerged,legacyPause:!!result.legacyPause}));
}finally{c.close();}
