// Actual death ending -> translated animated background -> normal title return.
import {connect,ensureInitialized,sleep} from './qa-session.mjs';
import {writeFile} from 'node:fs/promises';
const id=process.argv[2];if(!id||!/^[a-z0-9-]+$/.test(id))throw Error('Specify a new capture ID.');
const c=await connect();
async function until(test){
 for(let start=Date.now();Date.now()-start<55000;){
  const s=await c.js(`(function(){var k=TYRANO.kag,t=k.ftag.array_tag[k.ftag.current_order_index]||{};return {scenario:k.stat.current_scenario,line:t.line+1,tag:t.name,strong:k.stat.is_strong_stop,adding:k.stat.is_adding_text,errors:window.cardErrors||[],card:$('.base_fore[style*="rpg-game-over.gif"]').length};}())`);
  if(s.errors.length)throw Error(JSON.stringify(s));if(test(s))return s;await c.screenshot();await sleep(40);
 }
 throw Error('Ending check timed out');
}
try{
 await ensureInitialized(c);
 await c.js(`window.cardErrors=[];window.cardTrace=[];$.error_message=function(m){window.cardErrors.push(m)};window.addEventListener('error',function(e){if(e.message)window.cardErrors.push(e.message)});(function(){var k=TYRANO.kag;['bg','wait'].forEach(function(name){var tag=k.ftag.master_tag[name],old=tag.start;tag.start=function(pm){window.cardTrace.push({tag:name,pm:$.extend({},pm),scenario:k.stat.current_scenario,at:Date.now()});return old.apply(this,arguments)}});k.ftag.startTag('call',{storage:'rpg/rpg_settei.ks',target:'*初期化',auto_next:'stop'});return true;}())`);
 await until(s=>s.scenario==='title.ks'&&s.strong&&s.tag==='s');
 await c.js(`TYRANO.kag.layer.getFreeLayer().empty().hide();$('.fixlayer').remove();window.kiwameQA.jump('rpg/batoru.ks','死亡ED')`);
 const ready=await until(s=>s.card===1&&s.tag==='wait'&&s.line===3345);
 const captures=[`work/ui/rpg-game-over-${id}-a.png`,`work/ui/rpg-game-over-${id}-b.png`];
 await c.screenshot(captures[0]);await sleep(650);await c.screenshot(captures[1]);
 const title=await until(s=>s.scenario==='title.ks'&&s.strong&&s.tag==='s');
 const trace=await c.js('window.cardTrace');
 if(!trace.some(x=>x.tag==='bg'&&x.pm.storage==='rpg/siboued.gif'))throw Error('Original background call missing');
 if(!trace.some(x=>x.tag==='wait'&&x.pm.time==='2000'))throw Error('Original card hold missing');
 await c.js(`window.cardProbe={ready:false};var cardImage=new Image();cardImage.onload=function(){window.cardProbe={ready:true,width:this.naturalWidth,height:this.naturalHeight}};cardImage.onerror=function(){window.cardProbe={error:'GIF decode failed'}};cardImage.src='./data/bgimage/kiwame-en/rpg-game-over.gif';true`);
 let decode;
 for(let i=0;i<100;i++){decode=await c.js('window.cardProbe');if(decode.error)throw Error(decode.error);if(decode.ready)break;await sleep(50);}
 if(!decode.ready||decode.width!==640||decode.height!==460)throw Error('Native GIF resolution/decode failed');
 const result={version:'0.8.2',ready,title,trace,decode,captures,mainSteamChanged:false,userSavesWritten:false};
 await writeFile(`work/ui/rpg-game-over-${id}-verification.json`,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify({ready,returnedToTitle:title.scenario,decode}));
}finally{c.close();}
