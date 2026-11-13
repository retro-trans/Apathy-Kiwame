// Render English UI lettering through the measured effect in the bundled browser.
// Python measures motion only; all new animation pixels are drawn by native Canvas.
import {connect,ensureInitialized,sleep} from './qa-session.mjs';
import {mkdir,writeFile} from 'node:fs/promises';
import path from 'node:path';
const [model,output]=process.argv.slice(2);
if(!model||!output)throw Error('Specify effect-data JSON and a new output directory.');
await mkdir(output);await mkdir(path.join(output,'frames'));
const c=await connect();
try{
 await ensureInitialized(c);
 await c.js(`(function(){
  var fs=require('fs'),p=require('path');
  window.rpgEffect=JSON.parse(fs.readFileSync(${JSON.stringify(path.resolve(model))},'utf8'));
  var raw=fs.readFileSync(p.join(p.dirname(process.execPath),'package.nw/data/bgimage/kiwame-en/rpg-game-over-still.svg'));
  window.effectReady=false;window.effectError=null;
  var image=new Image();
  image.onerror=function(){window.effectError='English outline image failed to decode'};
  image.onload=function(){
   var base=document.createElement('canvas');base.width=640;base.height=460;
   var b=base.getContext('2d');b.drawImage(image,0,0,640,460);
   var mask=b.getImageData(0,0,640,460).data;
   var canvas=document.createElement('canvas');canvas.width=640;canvas.height=460;
   canvas.id='kiwame-effect-preview';canvas.style.cssText='position:fixed;left:0;top:0;width:960px;height:690px;z-index:2147483647';document.body.appendChild(canvas);
   var ctx=canvas.getContext('2d');
   window.renderEffectFrame=function(frame){
    var m=window.rpgEffect,bin=atob(m.frames[frame]),bytes=new Uint8Array(bin.length);
    for(var j=0;j<bin.length;j++)bytes[j]=bin.charCodeAt(j);
    var field=new Int16Array(bytes.buffer),out=ctx.createImageData(640,460),pixels=out.data;
    for(var i=3;i<pixels.length;i+=4)pixels[i]=255;
    function sample(x,y){
     if(x<0||x>=639||y<0||y>=459)return 0;
     var ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy,k=(iy*640+ix)*4;
     return mask[k]*(1-fx)*(1-fy)+mask[k+4]*fx*(1-fy)+mask[k+2560]*(1-fx)*fy+mask[k+2564]*fx*fy;
    }
    for(var y=m.y0;y<m.y0+(m.gridHeight-1)*m.step;y++){
     var qy=(y-m.y0)/m.step,iy=Math.floor(qy),fy=qy-iy;
     for(var x=0;x<640;x++){
      var qx=x/m.step,ix=Math.floor(qx),fx=qx-ix;
      var a=(iy*m.gridWidth+ix)*9,b=a+9,d=a+m.gridWidth*9,e=d+9;
      var wa=(1-fx)*(1-fy),wb=fx*(1-fy),wd=(1-fx)*fy,we=fx*fy;
      for(var channel=0;channel<3;channel++){
       var c=channel*3;
       var dx=(field[a+c]*wa+field[b+c]*wb+field[d+c]*wd+field[e+c]*we)/m.flowScale;
       var dy=(field[a+c+1]*wa+field[b+c+1]*wb+field[d+c+1]*wd+field[e+c+1]*we)/m.flowScale;
       var gain=(field[a+c+2]*wa+field[b+c+2]*wb+field[d+c+2]*wd+field[e+c+2]*we)/m.gainScale;
       pixels[(y*640+x)*4+channel]=sample(x+dx,y+dy)*gain;
      }
     }
    }
    ctx.putImageData(out,0,0);return canvas.toDataURL('image/png').split(',')[1];
   };
   window.effectReady=true;
  };
  image.src='data:image/svg+xml;base64,'+raw.toString('base64');return true;
 }())`);
 for(let i=0;i<100;i++){
  const s=await c.js('({ready:window.effectReady,error:window.effectError})');
  if(s.error)throw Error(s.error);if(s.ready)break;if(i===99)throw Error('Native mask render timed out');await sleep(50);
 }
 for(let i=0;i<78;i++){
  const png=await c.js(`window.renderEffectFrame(${i})`);
  await writeFile(path.join(output,'frames',String(i).padStart(3,'0')+'.png'),Buffer.from(png,'base64'),{flag:'wx'});
 }
 const summary=await c.js('({width:rpgEffect.width,height:rpgEffect.height,frames:rpgEffect.frames.length,frameMs:rpgEffect.frameMs,analysis:rpgEffect.analysis})');
 await writeFile(path.join(output,'render.json'),JSON.stringify(summary,null,2)+'\n',{flag:'wx'});
 console.log(JSON.stringify(summary));
}finally{
 await c.js(`(function(){var h=document.getElementById('kiwame-effect-preview');if(h)h.remove();delete window.renderEffectFrame;delete window.rpgEffect;return true;}())`).catch(()=>{});c.close();
}
