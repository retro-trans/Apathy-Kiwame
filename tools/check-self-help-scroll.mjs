// Decode and seek the preview in the game's isolated, muted NW.js renderer.
// No scenario jumps, slot writes or main-Steam mutations.
import {connect,ensureInitialized,sleep} from './qa-session.mjs';
import {writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const [movie,report,poster] = process.argv.slice(2);
if (!movie || !report || !poster) throw Error('Specify movie, new report and new poster paths.');
const client = await connect();
try {
  await ensureInitialized(client);
  await client.js(`(function(){var v=document.createElement('video');v.id='scroll-preview-qa';v.muted=true;v.preload='auto';v.style.cssText='position:fixed;left:0;top:0;width:960px;height:690px;background:black;z-index:999999';document.body.appendChild(v);v.src=${JSON.stringify(pathToFileURL(resolve(movie)).href)};v.load();return true;}())`);
  const read = () => client.js("(function(){var v=document.getElementById('scroll-preview-qa');return {ready:v.readyState,width:v.videoWidth,height:v.videoHeight,time:v.currentTime,duration:v.duration,seeking:v.seeking,error:v.error?v.error.code:null,muted:v.muted};}())");
  async function until(test) {
    for(let start=Date.now();Date.now()-start<15000;) {
      const state=await read();if(state.error)throw Error(JSON.stringify(state));
      if(test(state))return state;
      await client.screenshot();await sleep(60);
    }
    throw Error('Preview decode/seek timed out: '+JSON.stringify(await read()));
  }
  const initial = await until(s=>s.ready>=2);
  if(initial.width!==960||initial.height!==690||Math.abs(initial.duration-125.963)>.05)throw Error('Unexpected native movie geometry/timing.');
  const seeks=[];
  for(const time of [5,20,44,68,84,100,106,115,125]) {
    await client.js(`document.getElementById('scroll-preview-qa').currentTime=${time};true`);
    seeks.push(await until(s=>!s.seeking&&s.ready>=2&&Math.abs(s.time-time)<.1));
    if(time===44) {
      const data=await client.js("(function(){var c=document.createElement('canvas');c.width=960;c.height=690;c.getContext('2d').drawImage(document.getElementById('scroll-preview-qa'),0,0);return c.toDataURL('image/png').split(',')[1];}())");
      await writeFile(poster,Buffer.from(data,'base64'),{flag:'wx'});
    }
  }
  await client.js("var v=document.getElementById('scroll-preview-qa');v.currentTime=44;v.play();true");
  await until(s=>!s.seeking&&s.time>=44.8);
  const played=await read();
  await client.js("document.getElementById('scroll-preview-qa').pause();true");
  const result={version:'0.8.2-preview',initial,seeks,played,mainSteamChanged:false,userSavesWritten:false};
  await writeFile(report,JSON.stringify(result,null,2)+'\n',{flag:'wx'});
  console.log(JSON.stringify({decoded:true,seeks:seeks.length,playbackAdvanced:played.time>44.8,muted:played.muted}));
}finally{
  await client.js("var v=document.getElementById('scroll-preview-qa');if(v){v.pause();v.parentNode.removeChild(v)};true").catch(()=>{});
  client.close();
}
