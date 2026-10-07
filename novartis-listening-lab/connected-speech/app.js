'use strict';
(() => {
const units = window.NVS_CONTENT;
const $ = id => document.getElementById(id);
const storageKey = 'nvs-connected-speech-v1';
let saved = {};
try { saved = JSON.parse(localStorage.getItem(storageKey) || '{}') || {}; } catch (_) {}
const allowedRates = [.72,.82,.95,1.05];
let scope = ['all','core','analyst'].includes(saved.scope) ? saved.scope : 'all';
let rate = allowedRates.includes(saved.rate) ? saved.rate : .82;
let blind = saved.blind === true, revealed = !blind;
const all = units.flatMap(u => u.sentences.map(s => ({...s, unit:u})));
let pool = [], current, randomBag = [], plays = 0, playToken = 0, loadingTimeout;
let daily = saved.daily && Array.isArray(saved.daily.heard) ? saved.daily : {date:'', heard:[]};
const audio = $('native-audio');
audio.preload = 'none'; audio.preservesPitch = true;
let fallbackUtterance = null;
let timerRemaining = 1200, timerDeadline = 0;
function day() { const d = new Date(); return `${d.getFullYear()}-${d.getMonth()+1}-${d.getDate()}`; }
function persist() { try { localStorage.setItem(storageKey, JSON.stringify({scope,rate,blind,current:current.id,daily})); } catch (_) {} }
function updateDaily() {
 if (daily.date !== day()) daily = {date:day(),heard:[]};
 daily.heard = [...new Set(daily.heard.filter(id => all.some(s => s.id===id)))];
 $('daily-progress').textContent = `今天已听完 ${daily.heard.length} / 60 句`;
}
function setStatus(text) { $('status').textContent = text; }
function clearLoading() { clearTimeout(loadingTimeout); loadingTimeout = null; }
function stop(message = '已停止，可重新播放。') {
 playToken++; clearLoading(); audio.pause();
 if (audio.readyState) audio.currentTime = 0;
 if ('speechSynthesis' in window) window.speechSynthesis.cancel();
 fallbackUtterance = null;
 document.body.classList.remove('playing'); $('play').textContent = '▶ 播放本句';
 $('audio-progress').value = 0;
 setStatus(message);
}
function makePool() { pool = all.filter(s => scope==='all' || (scope==='core' ? s.unit.core : s.unit.analyst)); randomBag = []; }
function renderAnswer() {
 const show = !blind || revealed;
 $('answer').hidden = !show; $('hidden-answer').hidden = show; $('reveal').hidden = !blind;
 $('reveal').textContent = show ? '隐藏原文' : '显示原文';
 $('library').hidden = blind;
 if (blind) $('library').open = false;
 $('blind').setAttribute('aria-pressed',String(blind));
}
function render() {
 $('scope').value = scope;
 document.querySelectorAll('[data-rate]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.rate)===rate)));
 $('position').textContent = `第 ${pool.indexOf(current)+1} / ${pool.length} 句 · 例句 ${current.id.endsWith('1')?'A':'B'}`;
 $('category').textContent = current.unit.analyst ? 'Analyst Question' : current.unit.core ? '核心语块' : '拓展语块';
 $('phrase').textContent = current.unit.phrase; $('sentence').textContent = current.text;
 $('sound').textContent = current.unit.sound; $('cue').textContent = current.unit.cue;
 $('function').textContent = `商务功能：${current.unit.function}`;
 $('plays').textContent = `本句听完 ${plays} 次`;
 renderAnswer(); renderLibrary(); updateDaily(); persist();
}
function select(sentence) {
 stop('点击播放，先听两遍。'); current = sentence; plays = 0; revealed = !blind;
 $('audio-recovery').hidden = true; audio.removeAttribute('src'); audio.load(); render();
}
function failed(text) {
 clearLoading(); document.body.classList.remove('playing'); $('play').textContent = '↻ 重试播放';
 $('audio-recovery').hidden = false; setStatus(text);
}
function play() {
 if (fallbackUtterance) stop();
 if (!audio.paused) { audio.pause(); clearLoading(); document.body.classList.remove('playing'); $('play').textContent='▶ 继续播放'; setStatus('已暂停。'); return; }
 const token = ++playToken;
 const source = new URL(current.audio,location.href).href;
 if (audio.src !== source) { audio.src = current.audio; audio.load(); }
 if (audio.ended) audio.currentTime = 0;
 audio.playbackRate = rate; audio.defaultPlaybackRate = rate;
 $('audio-recovery').hidden = true; setStatus('音频加载中…'); $('play').textContent='加载中…';
 clearLoading(); loadingTimeout = setTimeout(()=>{if(token===playToken) {audio.pause(); failed('加载超时，请检查网络后重试。');}},12000);
 // Keep play() in this click handler: mobile browsers require a user gesture.
 const result = audio.play();
 if (result) result.catch(e => { if(token!==playToken || e.name==='AbortError') return; failed(e.name==='NotAllowedError'?'浏览器未允许播放，请再点一次播放。':'音频未能加载，请重试。'); });
}
audio.addEventListener('loadedmetadata',()=>{audio.playbackRate=rate;});
audio.addEventListener('playing',()=>{ clearLoading(); document.body.classList.add('playing'); $('play').textContent='Ⅱ 暂停'; setStatus(`正在播放 · ${Math.round(rate*100)}% 语速`); });
audio.addEventListener('pause',()=>{document.body.classList.remove('playing'); if(!audio.ended) $('play').textContent=audio.currentTime>0?'▶ 继续播放':'▶ 播放本句';});
audio.addEventListener('waiting',()=>{if(!audio.paused) setStatus('正在缓冲…');});
audio.addEventListener('timeupdate',()=>{$('audio-progress').value=audio.duration?audio.currentTime/audio.duration:0;});
function heard() { plays++; updateDaily(); if(!daily.heard.includes(current.id)) daily.heard.push(current.id); updateDaily(); persist(); $('plays').textContent=`本句听完 ${plays} 次`; }
audio.addEventListener('ended',()=>{clearLoading(); document.body.classList.remove('playing'); $('play').textContent='↻ 再听一次'; heard(); setStatus(plays<2?'已听完，再听一次，然后显示原文。':'已听完两遍，可以核对原文或跟读。');});
audio.addEventListener('error',()=>{if(audio.getAttribute('src')) failed('音频加载失败，请检查网络后重试。');});
$('play').addEventListener('click',play); $('stop').addEventListener('click',()=>stop());
$('previous').addEventListener('click',()=>select(pool[(pool.indexOf(current)-1+pool.length)%pool.length]));
$('next').addEventListener('click',()=>select(pool[(pool.indexOf(current)+1)%pool.length]));
$('scope').addEventListener('change',()=>{scope=$('scope').value; $('search').value=''; makePool(); select(pool[0]);});
$('blind').addEventListener('click',()=>{blind=!blind; revealed=!blind; renderAnswer(); persist();});
$('reveal').addEventListener('click',()=>{revealed=!revealed; renderAnswer();});
document.querySelectorAll('[data-rate]').forEach(b=>b.addEventListener('click',()=>{
 rate=Number(b.dataset.rate); audio.playbackRate=rate; audio.defaultPlaybackRate=rate; render();
 if(!audio.paused) setStatus(`正在播放 · ${Math.round(rate*100)}% 语速`);
}));
function shuffled(list) {const a=[...list]; for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];} return a;}
$('random').addEventListener('click',()=>{
 if(!randomBag.length) randomBag=shuffled(pool.filter(s=>s.id!==current.id));
 select(randomBag.pop() || pool[0]); play();
});
function renderLibrary() {
 const relevant = units.filter(u=>scope==='all'||(scope==='core'?u.core:u.analyst));
 const term = $('search').value.trim().toLowerCase();
 const filtered = relevant.filter(u=>[u.phrase,u.function,u.cue,...u.sentences.map(s=>s.text)].join(' ').toLowerCase().includes(term));
 $('library-count').textContent = `${filtered.length} 组`; $('groups').replaceChildren();
 if(!filtered.length){const p=document.createElement('p');p.className='group';p.textContent='没有匹配的语块，试试其他关键词。';$('groups').append(p);}
 for(const u of filtered){
  const article=document.createElement('article');article.className='group'+(u.id===current.unit.id?' active':'');
  const title=document.createElement('h3');title.lang='en';title.textContent=`${u.id}. ${u.phrase}`;article.append(title);
  const tag=document.createElement('span');tag.className='small';tag.textContent=u.function;article.append(tag);
  u.sentences.forEach((s,i)=>{
   const row=document.createElement('div');row.className='group-sentence';
   const p=document.createElement('p');p.lang='en';p.textContent=s.text;
   const button=document.createElement('button');button.textContent=`▶ ${i?'B':'A'}`;button.setAttribute('aria-label',`播放第 ${u.id} 组例句 ${i?'B':'A'}`);
   button.addEventListener('click',()=>{select(pool.find(x=>x.id===s.id));play();$('position').scrollIntoView({block:'center',behavior:'instant'});});
   row.append(p,button);article.append(row);
  });$('groups').append(article);
 }
}
$('search').addEventListener('input',renderLibrary);
$('tts-play').addEventListener('click',()=>{
 if(!('speechSynthesis' in window)){setStatus('此浏览器不支持备用语音。请重试上方音频。');return;}
 const voices=window.speechSynthesis.getVoices().filter(v=>/^en[-_]/i.test(v.lang));
 if(!voices.length){setStatus('未找到英文语音。请重试上方音频或在设备上添加英语语音。');return;}
 stop(); const token=++playToken;
 const utterance=new SpeechSynthesisUtterance(current.text);fallbackUtterance=utterance;utterance.voice=voices.find(v=>v.lang==='en-US')||voices[0];utterance.lang=utterance.voice.lang;utterance.rate=rate;
 utterance.onstart=()=>{if(token!==playToken)return;document.body.classList.add('playing');setStatus('正在播放备用英文语音。');};
 utterance.onend=()=>{if(token!==playToken)return;fallbackUtterance=null;document.body.classList.remove('playing');heard();setStatus('备用语音已播放完毕。');};
 utterance.onerror=()=>{if(token===playToken){fallbackUtterance=null;failed('备用语音未能播放，请重试预生成音频。');}};
 window.speechSynthesis.speak(utterance);
});
function renderTimer() {
 const seconds=timerDeadline?Math.max(0,Math.ceil((timerDeadline-Date.now())/1000)):timerRemaining;
 if(timerDeadline && seconds===0){timerDeadline=0;timerRemaining=0;$('timer-toggle').textContent='再练 20 分钟';setStatus('20 分钟训练完成。可以结束或继续练习。');}
 $('timer').textContent=`${String(Math.floor(seconds/60)).padStart(2,'0')}:${String(seconds%60).padStart(2,'0')}`;
}
$('timer-toggle').addEventListener('click',()=>{
 if(timerDeadline){timerRemaining=Math.max(0,Math.ceil((timerDeadline-Date.now())/1000));timerDeadline=0;$('timer-toggle').textContent='继续计时';}
 else {if(timerRemaining===0)timerRemaining=1200;timerDeadline=Date.now()+timerRemaining*1000;$('timer-toggle').textContent='暂停计时';}
 renderTimer();
});
setInterval(renderTimer,1000);
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop('已停止。返回后点击播放继续训练。');renderTimer();});
window.addEventListener('pagehide',()=>stop());
makePool();current=pool.find(s=>s.id===saved.current)||pool[0];render();
})();
