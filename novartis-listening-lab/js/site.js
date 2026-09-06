/* Novartis Listening Lab — lesson page interactivity */
(function(){
  var audio = document.querySelector('audio');
  if(!audio) return;
  var trk = audio.querySelector('track');
  var btn = document.querySelector('.subbtn');
  var subs = document.querySelector('.subs');
  var on = false, ready = false;

  function setMode(m){ try{ trk.track.mode = m; }catch(e){} }
  function render(){
    if(!on) return;
    var c = trk.track && trk.track.activeCues;
    if(c && c.length){ subs.innerHTML = '<span class="cur">'+esc(c[0].text)+'</span>'; }
    else { subs.innerHTML = '<span class="idle">…</span>'; }
  }
  function esc(s){ return String(s).replace(/[&<>]/g,function(ch){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[ch];}); }

  trk.addEventListener('load', function(){
    ready = true;
    if(!on) setMode('disabled');
    trk.track.addEventListener('cuechange', render);
  });
  if(trk.track){ ready = true; if(!on) setMode('disabled'); trk.track.addEventListener('cuechange', render); }

  btn.addEventListener('click', function(){
    on = !on;
    if(on){
      if(ready) setMode('showing');
      btn.classList.add('on'); btn.textContent = '🎬 隐藏英文字幕';
      subs.classList.add('on'); render();
    } else {
      if(ready) setMode('disabled');
      btn.classList.remove('on'); btn.textContent = '🎬 显示英文字幕';
      subs.classList.remove('on'); subs.textContent = '';
    }
  });

  // meeting map + score: persist to localStorage per lesson id
  var lessonId = document.body.dataset.lesson || '';
  function load(){
    try{
      var d = JSON.parse(localStorage.getItem('nll:'+lessonId) || '{}');
      document.querySelectorAll('[data-mm]').forEach(function(el){ if(el.dataset.mm in d) el.value = d[el.dataset.mm]; });
      ['first','assisted','fatigue'].forEach(function(k){ var el=document.querySelector('[data-score="'+k+'"]'); if(el && k in d) el.value=d[k]; });
    }catch(e){}
  }
  function save(){
    var d = {};
    document.querySelectorAll('[data-mm]').forEach(function(el){ d[el.dataset.mm]=el.value; });
    ['first','assisted','fatigue'].forEach(function(k){ var el=document.querySelector('[data-score="'+k+'"]'); if(el) d[k]=el.value; });
    try{ localStorage.setItem('nll:'+lessonId, JSON.stringify(d)); }catch(e){}
  }
  load();
  document.querySelectorAll('[data-mm],[data-score]').forEach(function(el){
    el.addEventListener('input', save);
  });
  var saveBtn = document.querySelector('.score-row button');
  if(saveBtn){
    saveBtn.addEventListener('click', function(){
      save();
      var note = document.querySelector('.score-row .saved');
      if(note){ note.textContent = '已保存 ✓'; setTimeout(function(){ note.textContent=''; }, 1500); }
    });
  }
})();
