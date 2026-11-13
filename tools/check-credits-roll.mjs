// Observe the full native roll in an isolated, muted QA build.
import {readFile,writeFile,stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {connect,sleep,ensureInitialized} from './qa-session.mjs';
const id=process.argv[2];if(!/^[a-z0-9-]+$/.test(id||''))throw Error('Specify a new capture ID or dry-run.');
const folder='work/debug/rpg-portrait-name-preview-0.8.2';
const prefix='work/ui/credits-roll-'+id;
const layout=JSON.parse(await readFile('work/ui/credits-roll-layout.json','utf8'));
if(id==='dry-run') {console.log(JSON.stringify({rows:layout.length,nativeImage:[690,3500],sourceImage:[690,4000],nativeWait:60000,nativeAnimation:80000,mainSteamChanged:false}));process.exit(0);}
try{await stat(prefix+'.json');throw Error('Choose a new capture ID.');}catch(e){if(e.code!=='ENOENT')throw e;}
const hash=raw=>createHash('sha256').update(raw).digest('hex');
const proof={version:'0.8.2',binding:{scenario:hash(await readFile(folder+'/package.nw/data/scenario/settei/staff.ks')),runtime:hash(await readFile(folder+'/package.nw/english.js')),ui:hash(await readFile(folder+'/package.nw/english-ui.js')),art:hash(await readFile(folder+'/package.nw/data/fgimage/kiwame-en/common-staff.svg'))},rows:[],samples:[],captures:[],mainSteamChanged:false,userSavesWritten:false};
const client=await connect();const seen=new Set();
try{
 const executable=await client.js("require('path').dirname(process.execPath).split(String.fromCharCode(92)).join('/')");
 if(!executable.toLowerCase().endsWith('/'+folder))throw Error('Wrong isolated candidate.');
 await ensureInitialized(client);
 await client.js("(function(){var k=TYRANO.kag;k.ftag.startTag('s');k.stat.is_stop=false;k.stat.is_wait=false;k.stat.is_trans=false;k.stat.is_adding_text=false;k.stat.is_auto=false;k.stat.is_skip=false;k.stat.is_wait_auto=false;return true;}())");
 await client.js("window.creditTrace=[];['anim','wait','bgm','change_bg'].forEach(function(name){var tag=TYRANO.kag.ftag.master_tag[name];if(!tag)return;var old=tag.start;tag.start=function(pm){window.creditTrace.push({tag:name,pm:$.extend({},pm)});return old.apply(this,arguments)}});true");
 const start=Date.now();await client.js("window.kiwameQA.jump('settei/staff.ks','')");
 let firstTop=null,lastReport=0,poster=false,lastPoster=false;
 for(;Date.now()-start<90000;){
  const state=await client.js("(function(){var k=TYRANO.kag,t=k.ftag.array_tag[k.ftag.current_order_index]||{},n=$('img.staff').filter(':visible')[0],r=n&&n.getBoundingClientRect();return {scenario:k.stat.current_scenario,line:t.line+1,tag:t.name,strong:k.stat.is_strong_stop,wait:k.stat.is_wait,skip:k.stat.is_skip,image:n?{src:n.getAttribute('src'),loaded:n.complete&&n.naturalHeight>0,naturalWidth:n.naturalWidth,naturalHeight:n.naturalHeight,left:r.left,top:r.top,width:r.width,height:r.height}:null};}())");
  if(state.scenario==='inoti.ks')throw Error('Unexpected unrelated scene.');
  const elapsed=Date.now()-start;
  if(state.scenario==='settei/staff.ks'&&state.image?.loaded){
   const image=state.image;
   if(image.width!==690||image.height!==3500||image.naturalWidth!==690||image.naturalHeight!==4000||!image.src.endsWith('/kiwame-en/common-staff.svg')||state.skip)throw Error('Unexpected native credit geometry/mapping/speed.');
   if(firstTop===null)firstTop=image.top;
   proof.samples.push({elapsed,...image});
   for(const row of layout){
    const [x,y,right,bottom]=row.bounds;
    const viewport={left:image.left+x,right:image.left+right,top:image.top+y*.875,bottom:image.top+bottom*.875};
    if(!seen.has(row.row)&&viewport.top>=30&&viewport.bottom<=660&&viewport.left>=0&&viewport.right<=960){seen.add(row.row);proof.rows.push({...row,elapsed,viewport});}
   }
   if(!poster&&elapsed>=12000){const p=prefix+'-preview.png';await client.screenshot(p);proof.captures.push(p);poster=true;}
   if(!lastPoster&&seen.has(44)){const p=prefix+'-production.png';await client.screenshot(p);proof.captures.push(p);lastPoster=true;}
  }
  if(state.scenario==='title.ks'&&state.tag==='s'&&state.strong){proof.naturalReturn={elapsed,scenario:state.scenario,line:state.line};break;}
  if(elapsed-lastReport>25000){console.log(JSON.stringify({elapsed,visibleRows:seen.size}));lastReport=elapsed;}
  await client.screenshot();await sleep(200);
 }
 proof.trace=await client.js('window.creditTrace');
 if(!proof.naturalReturn||proof.naturalReturn.elapsed<59000||seen.size!==44||proof.samples.at(-1).top>=firstTop-1500)throw Error('Full native scroll/row visibility/title return failed.');
 if(!proof.trace.some(x=>x.tag==='anim'&&String(x.pm.time)==='80000'&&x.pm.top==='-=3000')||!proof.trace.some(x=>x.tag==='wait'&&String(x.pm.time)==='60000'))throw Error('Original scroll/timer commands changed.');
 proof.completed=true;
}catch(error){proof.error=error.message;throw error;}
finally{await writeFile(prefix+'.json',JSON.stringify(proof,null,2)+'\n',{flag:'wx'});client.close();console.log(JSON.stringify({completed:proof.completed,rows:proof.rows.length,naturalReturn:proof.naturalReturn,error:proof.error}));}
