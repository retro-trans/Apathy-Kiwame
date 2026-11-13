// Exercise real DOM input in an isolated --debug build, never the Steam copy.
// KIWAME_QA_PORT=... node tools/check-choice-input.mjs baseline|fixed output.json
import {connect,ensureInitialized,sleep} from './qa-session.mjs';
import {writeFile} from 'node:fs/promises';

const [mode,output]=process.argv.slice(2);
if(!['baseline','fixed'].includes(mode)||!output)throw Error('Specify baseline|fixed and a new output JSON path.');
const c=await connect();
const read=()=>c.js(`(function(){var k=TYRANO.kag,t=k.ftag.array_tag[k.ftag.current_order_index]||{},m=k.stat.stack.macro;return {scenario:k.stat.current_scenario,line:t.line+1,tag:t.name,macroStorage:m.length?m[m.length-1].storage:null,strong:k.stat.is_strong_stop,adding:k.stat.is_adding_text,errors:window.choiceInputErrors.slice(),storyChoices:$('[data-event-tag="glink"]').filter(':visible').length,choices:$('.event-setting-element[data-event-tag="changecolorlink"]').filter(':visible').map(function(){return {text:$(this).text(),target:JSON.parse($(this).attr('data-event-pm')).target,readyIn:this.kiwameChoiceReadyAt-performance.now()};}).get()};}())`);
async function until(predicate,action){
 for(let start=Date.now();Date.now()-start<35000;){
  const s=await read();if(predicate(s))return s;
  if(action)await action(s);
  await sleep(40);
 }
 throw Error('QA condition timed out: '+JSON.stringify(await read()));
}
const ready=s=>s.scenario==='rpg/stage.ks'&&s.tag==='s'&&s.strong&&s.choices.length===2&&s.choices.every(x=>x.text.length>2);
async function cooldown(){return until(s=>s.choices.length&&s.choices.every(x=>x.readyIn<=0));}
async function probeCooldown(selector){
 await c.js(`(function(){var e=$(${JSON.stringify(selector)}).filter(':visible').first()[0];if(!e)throw Error('Missing probe choice');var deadline=e.kiwameChoiceReadyAt;if(deadline-performance.now()<300)throw Error('Missed fresh cooldown');var trace=window.choiceCooldownProbe={done:false,samples:[]};function send(type){var ev=new MouseEvent(type,{bubbles:true,cancelable:true,button:0});e.dispatchEvent(ev);trace.samples.push({type:type,elapsed:performance.now()-(deadline-500),blocked:ev.defaultPrevented})}send('click');send('touchstart');[150,300,450,490].forEach(function(ms){setTimeout(function(){send('click')},Math.max(0,deadline-500+ms-performance.now()))});setTimeout(function(){send('mousedown')},Math.max(0,deadline-20-performance.now()));setTimeout(function(){send('click');trace.done=true},Math.max(0,deadline+30-performance.now()));return true;}())`);
 for(let start=Date.now();Date.now()-start<3000;){
  const p=await c.js('window.choiceCooldownProbe');
  if(p.done){if(p.samples.some(s=>!s.blocked))throw Error('Cooldown accepted early input: '+JSON.stringify(p));if(!p.samples.some(s=>s.type==='click'&&s.elapsed>=500))throw Error('Held press was not checked across the deadline');return p;}
  await sleep(25);
 }
 throw Error('Cooldown probe timed out');
}
async function showChoices(){
 // Reset only this isolated QA scene, including any interrupted lr macro.
 await until(s=>!s.adding&&['s','p','l'].includes(s.tag));
 await c.js(`(function(){var k=TYRANO.kag;window.choiceInputErrors=[];k.stat.stack.macro=[];k.stat.stack.if=[];k.stat.is_strong_stop=true;k.stat.f.RPG荒井ルートイベント進行度=5;k.stat.f.RPG荒井ルート=true;k.stat.f.RPG荒井ルート_残りターン数=40;k.stat.f.RPG荒井ルート_ターン数カウント開始=true;k.stat.ch_speed='0';window.kiwameQA.jump('rpg/stage.ks','顕微鏡2');return true;}())`);
 await until(s=>s.choices.length===0);
 await until(s=>s.choices.some(x=>x.text.length>0),async s=>{
  if(!s.adding&&['l','p'].includes(s.tag)){
   if(s.scenario==='rpg/stage.ks'&&s.line===3279&&s.tag==='p')await c.js("TYRANO.kag.stat.ch_speed='25';true");
   await c.js('window.kiwameQA.advance()');
  }
 });
}
async function input(target,type='click'){
 return c.js(`(function(){var e=$('.event-setting-element[data-event-tag="changecolorlink"]').filter(':visible').filter(function(){return JSON.parse($(this).attr('data-event-pm')).target===${JSON.stringify(target)}})[0];if(!e)throw Error('Missing choice');var ev=new MouseEvent(${JSON.stringify(type)},{bubbles:true,cancelable:true});e.dispatchEvent(ev);return ev.defaultPrevented;}())`);
}
try{
 await ensureInitialized(c);
 await c.js(`window.choiceInputErrors=[];$.error_message=function(m){window.choiceInputErrors.push(m)};true`);
 await c.js(`window.addEventListener('error',function(e){if(e.message)window.choiceInputErrors.push('JavaScript: '+e.message)});true`);
 if(!await c.js('!!TYRANO.kag.stat.charas.boku_kao')){
  const before=await read();
  await c.js(`TYRANO.kag.ftag.startTag('call',{storage:'rpg/rpg_settei.ks',target:'*初期化',auto_next:'stop'});true`);
  await until(s=>s.scenario===before.scenario&&s.tag==='s'&&s.strong);
 }
 await showChoices();
 const during=await read();
 if(during.tag==='s'||during.scenario!=='settei/macro.ks')throw Error('Did not catch the choice drawing window');
 const earlyClickBlocked=await input('*覗く');
 const earlyTouchBlocked=mode==='fixed'?await input('*覗く','touchstart'):null;
 if(mode==='fixed')for(let i=0;i<8;i++)await input('*覗く');
 const drawn=await until(ready);
 if(mode==='baseline'&&!drawn.errors.some(e=>e.includes('覗く')))throw Error('Baseline did not reproduce the reported alert');
 if(mode==='fixed'&&(drawn.errors.length||!earlyClickBlocked||!earlyTouchBlocked))throw Error('Early input guard failed');
 const delayProbe=mode==='fixed'?await probeCooldown('[data-event-tag="changecolorlink"]'):null;
 // A real click after the [s] stop must still follow the original destination.
 const readyBurst=await c.js(`(function(){var blocked=[];for(var i=0;i<8;i++){var e=$('.event-setting-element[data-event-tag="changecolorlink"]').filter(':visible').first()[0];if(!e){blocked.push(null);continue}e.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true,button:0}));var ev=new MouseEvent('click',{bubbles:true,cancelable:true});e.dispatchEvent(ev);blocked.push(ev.defaultPrevented)}return blocked;}())`);
 const accepted=await until(s=>s.scenario==='rpg/stage.ks'&&s.line===3288&&s.tag==='p'&&!s.adding);
 const result={mode,during,earlyClickBlocked,earlyTouchBlocked,drawn,delayProbe,readyBurst,accepted};
 if(mode==='fixed'){
  if(accepted.errors.length)throw Error('Ready choice failed');
  await showChoices();await until(ready);
  // Use the engine's normal save/load machinery entirely in memory; no slot write.
  await c.js(`(function(){var k=TYRANO.kag;k.menu.snapSave('QA choice input',function(){window.choiceInputSnapshot=$.extend(true,{},k.menu.snap)},'false');return true;}())`);
  await c.js(`TYRANO.kag.menu.loadGameData($.extend(true,{},window.choiceInputSnapshot),{bgm_over:'true'});true`);
  await until(ready);
  // Confirm the rebuilt listener is protected while loading/drawing too.
  await c.js(`window.choiceInputStrong=TYRANO.kag.stat.is_strong_stop;TYRANO.kag.stat.is_strong_stop=false;true`);
  result.restoredEarlyBlocked=await input('*覗く');
  await c.js(`TYRANO.kag.stat.is_strong_stop=window.choiceInputStrong;true`);
  result.restoredCooldownBlocked=await input('*覗く');
  await cooldown();
  await input('*覗く','touchstart');
  result.restoredAccepted=await until(s=>s.scenario==='rpg/stage.ks'&&s.line===3288&&s.tag==='p'&&!s.adding);
  if(!result.restoredEarlyBlocked||!result.restoredCooldownBlocked||result.restoredAccepted.errors.length)throw Error('Restored choice guard failed');
  await showChoices();await until(ready);await cooldown();
  await input('*理科室_戻る');
  result.decline=await until(s=>s.scenario==='rpg/stage.ks'&&s.tag==='s'&&s.strong&&s.line!==3283);
  if(result.decline.errors.length)throw Error('Decline choice failed');
  await writeFile(output+'.microscope.json',JSON.stringify(result,null,2)+'\n',{flag:'wx'});
  console.log('Microscope early input, click burst, restored save and decline: passed');
  result.timed=[];
  const timedCases=[
   {line:788,target:'*ショゴスの針を避けた'},
   {line:864,target:'*ショゴス選択肢1_2'},
   {line:873,target:'*ショゴス選択肢1_1'},
   {line:881,target:'*ショゴス選択肢2_3'},
   {line:889,target:'*ショゴス選択肢3_2'}
  ];
  for(const test of timedCases){
   // The full battle setup shows the RPG message layer before these blocks.
   // Reproduce that visibility when entering a menu directly from the room view.
   await c.js(`(function(){var k=TYRANO.kag;k.stat.stack.macro=[];k.stat.stack.if=[];k.stat.is_strong_stop=false;k.stat.ch_speed='0';k.stat.f.現在HP=3;k.layer.getLayer('message0','fore').css({display:'block',visibility:'visible'});k.getMessageOuterLayer().css('opacity',1);window.choiceInputErrors=[];k.loadScenario('rpg/batoru.ks',function(tags){var index=-1;for(var i=0;i<tags.length;i++){if(tags[i].line===${test.line-1}&&tags[i].name==='選択肢'){index=i;break}}if(index<0)throw Error('Missing timed menu');k.ftag.buildTagIndex(tags,index-1,'yes')});return true;}())`);
   const waiting=await until(s=>s.scenario==='rpg/batoru.ks'&&s.tag==='wait'&&s.strong);
   const earlyBlocked=await input(test.target);
   if(!earlyBlocked)throw Error('Timed choice ignored cooldown');
   await cooldown();
   const blocked=await input(test.target);
   const followed=await until(s=>(s.scenario==='rpg/batoru.ks'||s.macroStorage==='rpg/batoru.ks')&&['l','p'].includes(s.tag)&&!s.adding);
   const timerCleared=await c.js('!TYRANO.kag.stat.is_wait');
   if(blocked||!timerCleared||followed.errors.length)throw Error('Timed choice was blocked or failed: '+test.line);
   result.timed.push({choiceLine:test.line,target:test.target,waitLine:waiting.line,earlyBlocked,acceptedScenario:followed.scenario,acceptedLine:followed.line,macroStorage:followed.macroStorage,timerCleared,errors:followed.errors});
   console.log('Timed menu '+test.line+': passed');
  }
  // Native regular story menu, not a synthetic button fixture.
  await until(s=>!s.adding&&['s','l','p'].includes(s.tag));
  await c.js(`(function(){var k=TYRANO.kag;k.stat.stack.macro=[];k.stat.stack.if=[];k.stat.is_strong_stop=true;k.stat.ch_speed='0';window.kiwameQA.jump('op.ks','start');return true;}())`);
  await until(s=>s.scenario==='op.ks'&&s.tag==='s'&&s.strong&&s.storyChoices>0,async s=>{if(!s.adding&&['l','p'].includes(s.tag)&&await c.js("$('.layer_event_click').filter(':visible').length===1"))await c.js('window.kiwameQA.advance()')});
  result.storyDelayProbe=await probeCooldown('[data-event-tag="glink"]');
  await c.js(`(function(){var e=$('[data-event-tag="glink"]').filter(':visible').first()[0];e.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,cancelable:true,button:0}));e.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true}));return true;}())`);
  result.storyAccepted=await until(s=>s.scenario==='op.ks'&&!s.adding&&['l','p'].includes(s.tag));
  if(result.storyAccepted.errors.length)throw Error('Regular story choice failed');
 }
 await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify({mode,earlyClickBlocked,earlyTouchBlocked,alerts:drawn.errors,readyChoiceLine:accepted.line,restoredEarlyBlocked:result.restoredEarlyBlocked,declineLine:result.decline?.line,timedMenus:result.timed?.length}));
}finally{c.close();}
