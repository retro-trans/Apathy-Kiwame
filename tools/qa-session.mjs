// Shared client for the isolated NW.js debugger (Node 22+).
import {writeFile} from 'node:fs/promises';

export const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
// A RAM snapshot does not contain global alias tables from the normal boot scripts.
export async function ensureInitialized(client) {
    for (const start=Date.now();Date.now()-start<45000;) {
        const state=await client.js("(function(){var k=TYRANO.kag,t=k.ftag.array_tag[k.ftag.current_order_index]||{};return {scenario:k.stat.current_scenario,line:t.line+1,tag:t.name,adding:k.stat.is_adding_text,strong:k.stat.is_strong_stop,aliases:typeof SE==='object'&&typeof BGM==='object'};}())");
        if(!state.scenario||!state.tag) {await client.screenshot();await sleep(100);continue;}
        if(state.scenario==='inoti.ks'&&state.line>=3352&&state.line<=3455)throw Error('Retained scene requires blind handling before startup checks');
        if(!['first.ks','title.ks'].includes(state.scenario)) {
            if(state.aliases&&!state.adding&&['l','p','s'].includes(state.tag))return;
            if(state.aliases&&!state.strong) {await client.screenshot();await sleep(100);continue;}
            // Startup calls briefly inherit a strong-stop flag while their next
            // scenario is loading. Observe that transition without restarting.
            if(/^(settei\/|make\.ks$|\.\.\/others\/plugin\/)/.test(state.scenario)&&!['l','p','s'].includes(state.tag)) {await client.screenshot();await sleep(100);continue;}
            throw Error('QA game needs completed normal boot: '+JSON.stringify(state));
        }
        await client.screenshot();
        if(state.scenario==='first.ks'&&state.line===11&&state.tag==='l'&&
                await client.js('!!window.kiwameEnglishUI.readableStartupPause')) {
            await client.js("window.kiwameQA.click('.layer_event_click')");
            continue;
        }
        if(state.scenario==='title.ks'&&state.strong&&state.aliases) {
            if(await client.js("$('img[src*=\"endings-normal\"]').filter(':visible').length===1"))return;
        }
        for(const selector of ['img[src*="accept-normal"]','img[src*="yes-normal"]']) {
            if(await client.js(`$(${JSON.stringify(selector)}).filter(':visible').length===1`)) {
                await client.js(`window.kiwameQA.click(${JSON.stringify(selector)})`);break;
            }
        }
        await sleep(100);
    }
    throw Error('Normal QA startup observation timed out; inspect the existing instance');
}
export async function connect({requireQA=true} = {}) {
    const port = Number(process.env.KIWAME_QA_PORT || 9229);
    let page;
    for (const start = Date.now(); Date.now() - start < 20000;) {
        try {
            const pages = await (await fetch(`http://127.0.0.1:${port}/json`, {signal: AbortSignal.timeout(1000)})).json();
            page = pages.find(p => p.url === 'app://./index.html' && p.webSocketDebuggerUrl);
            if (page) break;
        } catch (_) {}
        await sleep(200);
    }
    if (!page) throw new Error('Isolated game debugger did not become ready.');
    const address = new URL(page.webSocketDebuggerUrl);
    if (address.hostname !== '127.0.0.1' || Number(address.port) !== port) throw new Error('Nonlocal debugger.');
    const socket = new WebSocket(address);
    await new Promise((resolve, reject) => {
        socket.addEventListener('open', resolve, {once:true});
        socket.addEventListener('error', reject, {once:true});
    });
    let id = 0;
    function send(method, params = {}) {
        return new Promise((resolve, reject) => {
            const current = ++id;
            const timer = setTimeout(() => {socket.removeEventListener('message', receive); reject(new Error(method+' timed out'));}, 10000);
            function receive(event) {
                const reply = JSON.parse(event.data);
                if (reply.id !== current) return;
                clearTimeout(timer); socket.removeEventListener('message', receive);
                if (reply.error || reply.result?.wasThrown) reject(new Error(JSON.stringify(reply.error || reply.result.result)));
                else resolve(reply.result);
            }
            socket.addEventListener('message', receive);
            socket.send(JSON.stringify({id:current,method,params}));
        });
    }
    const js = async expression => (await send('Runtime.evaluate',{expression,returnByValue:true})).result.value;
    if (requireQA) {
        let ready = false;
        for (const start = Date.now(); Date.now() - start < 20000;) {
            ready = await js('typeof window.kiwameQA === "object"');
            if (ready) break;
            await sleep(100);
        }
        if (!ready) {socket.close(); throw new Error('QA runtime missing.');}
    }
    return {js,send,close:()=>socket.close(),
        screenshot: async file => {
            const shot = await send('Page.captureScreenshot',{format:'png'});
            if (file) await writeFile(file,Buffer.from(shot.data,'base64'),{flag:'wx'});
        }};
}
