// Node 22+ client for the isolated copy's loopback debugger.
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

const port = Number(process.env.KIWAME_QA_PORT || 9229);
const [command, ...args] = process.argv.slice(2);
const commands = {
    state: 0, inspect: 1, metrics: 0, reload: 0, trace: 0, click: 1, advance: 0, jump: 2,
    preview: 1, clearPreview: 0, snapshot: 1, saved: 1, screenshot: 1,
};

async function main() {
    if (!Object.hasOwn(commands, command) || args.length !== commands[command]) {
        throw new Error('Usage: node tools/qa.mjs ' + Object.entries(commands)
            .map(([name, count]) => name + ' <arg>'.repeat(count)).join(' | '));
    }
    if (!Number.isInteger(port) || port < 1024 || port > 65535) throw new Error('Invalid QA port.');
    const response = await fetch(`http://127.0.0.1:${port}/json`, { signal: AbortSignal.timeout(3000) });
    if (!response.ok) throw new Error(`Debugger returned HTTP ${response.status}.`);
    const pages = await response.json();
    const page = pages.find(item => item.type === 'page' && item.url === 'app://./index.html');
    if (!page) throw new Error('Isolated Apathy Kiwame game window not found.');
    const address = new URL(page.webSocketDebuggerUrl);
    if (!['127.0.0.1', 'localhost'].includes(address.hostname) || Number(address.port) !== port) {
        throw new Error('Debugger advertised a nonlocal address.');
    }
    const socket = new WebSocket(address);
    let id = 0;
    try {
        await new Promise((resolveOpen, reject) => {
            socket.addEventListener('open', resolveOpen, { once: true });
            socket.addEventListener('error', reject, { once: true });
        });
        function send(method, params = {}) {
            return new Promise((resolveReply, reject) => {
                const current = ++id;
                const timeout = setTimeout(() => {
                    socket.removeEventListener('message', receive);
                    reject(new Error(`${method} timed out.`));
                }, 5000);
                function receive(event) {
                    const message = JSON.parse(event.data);
                    if (message.id !== current) return;
                    clearTimeout(timeout);
                    socket.removeEventListener('message', receive);
                    if (message.error) reject(new Error(message.error.message));
                    else resolveReply(message.result);
                }
                socket.addEventListener('message', receive);
                socket.send(JSON.stringify({ id: current, method, params }));
            });
        }
        async function evaluate(expression) {
            const reply = await send('Runtime.evaluate', { expression, returnByValue: true });
            if (reply.wasThrown || reply.exceptionDetails) throw new Error(reply.result.description);
            return reply.result.value;
        }
        if (!(await evaluate('typeof window.kiwameQA === "object"'))) {
            throw new Error('This instance does not have the QA runtime.');
        }
        if (command === 'screenshot') {
            const path = resolve(args[0]);
            const shot = await send('Page.captureScreenshot', { format: 'png' });
            await mkdir(dirname(path), { recursive: true });
            await writeFile(path, Buffer.from(shot.data, 'base64'), { flag: 'wx' });
            console.log(path);
        } else {
            const call = `window.kiwameQA.${command}(${args.map(JSON.stringify).join(',')})`;
            const result = await evaluate(`(function () { try { return {value: ${call}}; }
                catch (error) { return {error: String(error.message || error)}; } }())`);
            if (result.error) throw new Error(result.error);
            console.log(JSON.stringify(result.value, null, 2));
        }
    } finally {
        socket.close();
    }
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
