// Native regression: ending -> title -> opening, plus a legacy RAM snapshot.
// Uses only the isolated QA copy and never writes a game save slot.
import {connect,ensureInitialized,sleep} from './qa-session.mjs';
import {readFile,writeFile} from 'node:fs/promises';
const [mode,output,legacyFile]=process.argv.slice(2);
if(!['baseline','fixed'].includes(mode)||!output)throw Error('Specify baseline|fixed and a new output JSON path; fixed also accepts a legacy snapshot path.');
const c=await connect();
async function state(){return c.js(`(function(){var k=TYRANO.kag,t=k.ftag.array_tag[k.ftag.current_order_index]||{},p=k.getMessageInnerLayer().find('p')[0];return {scenario:k.stat.current_scenario,line:t.line+1,tag:t.name,strong:k.stat.is_strong_stop,adding:k.stat.is_adding_text,vertical:k.stat.vertical,paragraphClass:p?p.className:null,writingMode:p?getComputedStyle(p).webkitWritingMode:null,float:p?getComputedStyle(p).cssFloat:null,choices:$('.kiwame_en_choice').filter(':visible').length,errors:window.layoutErrors||[]};}())`);}
async function until(test,advance=false){
 for(let start=Date.now();Date.now()-start<60000;){
  const s=await state();if(s.errors.length)throw Error(JSON.stringify(s));if(test(s))return s;
  if(advance&&!s.adding&&['l','p'].includes(s.tag))await c.js('window.kiwameQA.advance()');
  await c.screenshot();await sleep(30);
 }
 throw Error('Opening condition timed out: '+JSON.stringify(await state()));
}
function horizontal(s){return s.vertical==='false'&&s.writingMode==='horizontal-tb'&&!s.paragraphClass.includes('vertical_text')&&s.float==='none';}
try{
 await ensureInitialized(c);
 await c.js(`window.layoutErrors=[];$.error_message=function(m){window.layoutErrors.push(m)};window.addEventListener('error',function(e){if(e.message)window.layoutErrors.push(e.message)});TYRANO.kag.ftag.startTag('call',{storage:'rpg/rpg_settei.ks',target:'*初期化',auto_next:'stop'});true`);
 await until(s=>s.scenario==='title.ks'&&s.strong&&s.tag==='s');
 await c.js(`TYRANO.kag.layer.getFreeLayer().empty().hide();$('.fixlayer').remove();window.kiwameQA.jump('rpg/batoru.ks','死亡ED')`);
 await until(s=>s.scenario!=='title.ks');
 const afterEnding=await until(s=>s.scenario==='title.ks'&&s.strong&&s.tag==='s');
 if(afterEnding.vertical!=='true')throw Error('Native ending did not reproduce inherited vertical mode');
 await c.js(`TYRANO.kag.stat.ch_speed='0';window.kiwameQA.jump('op.ks','start')`);
 const firstPage=await until(s=>s.scenario==='op.ks'&&s.line===99&&s.tag==='l'&&!s.adding,true);
 if(mode==='baseline'&&!(firstPage.vertical==='false'&&firstPage.writingMode==='vertical-rl'))throw Error('Baseline did not reproduce the screenshot');
 if(mode==='fixed'&&!horizontal(firstPage))throw Error('First English page is not horizontal');
 await c.screenshot(output+'.png');
 await c.js(`(function(){var k=TYRANO.kag;k.menu.snapSave('QA opening layout',function(){window.layoutSnapshot=$.extend(true,{},k.menu.snap)},'false');return true;}())`);
 if(mode==='baseline')await writeFile(output+'.snapshot.json',JSON.stringify(await c.js('window.layoutSnapshot'))+'\n',{flag:'wx'});
 await until(s=>s.scenario==='op.ks'&&s.strong&&s.tag==='s'&&s.choices>0,true);
 await c.js(`$('.kiwame_en_choice').filter(':visible').last().trigger('click');true`);
 const afterChoice=await until(s=>['op.ks','maisou.ks'].includes(s.scenario)&&!s.adding&&['l','p'].includes(s.tag));
 if(!horizontal(afterChoice))throw Error('English after the first choice is not horizontal');
 const result={mode,afterEnding,firstPage,afterChoice,userSaveSlotsWritten:false,mainSteamChanged:false};
 if(mode==='fixed'&&legacyFile){
  const snapshot=JSON.parse(await readFile(legacyFile,'utf8'));
  await c.js(`TYRANO.kag.menu.loadGameData(${JSON.stringify(snapshot)},{bgm_over:'true'});true`);
  await sleep(700);
  result.legacy=await state();
  if(!horizontal(result.legacy)||result.legacy.errors.length)throw Error('Legacy paragraph was not repaired during load');
  await c.screenshot(output+'.legacy.png');
 }
 await writeFile(output,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify(result));
}finally{c.close();}
