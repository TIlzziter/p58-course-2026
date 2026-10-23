const $=id=>document.getElementById(id);
const params=new URLSearchParams(location.hash.slice(1));
let current=Math.max(0,Math.min(slides.length-1,(Number(params.get('slide'))||1)-1));
let mode=params.get('mode')==='technical'?'technical':'simple';
let pace=params.get('pace')==='90'?'90':'105';
let lastFocus=null;
function route(){return slides.map((s,i)=>i).filter(i=>pace!=='90'||!data[i].optional)}
function fit(){const w=innerWidth,h=Math.max(120,innerHeight-110);$('stage').style.transform=`scale(${Math.min(w/1280,h/720)})`}
function syncHash(){history.replaceState(null,'',`#slide=${current+1}&mode=${mode}&pace=${pace}`)}
function render(){
 document.body.dataset.mode=mode;document.body.dataset.pace=pace;
 slides.forEach((s,i)=>{s.classList.toggle('active',i===current);s.setAttribute('aria-hidden',i!==current);s.inert=i!==current});
 $('modeSimple').setAttribute('aria-pressed',mode==='simple');$('modeTechnical').setAttribute('aria-pressed',mode==='technical');
 $('pace').value=pace;
 $('answers').disabled=mode==='technical'||!slides[current].querySelector('.simple .answer');
 $('counter').textContent=`${current+1} / ${slides.length}`;
 const visible=route(),idx=visible.indexOf(current);
 $('position').textContent=`Лекция ${data[current].lesson} · ${mode==='simple'?'Простой':'Технический'} режим · ${data[current].mins} мин${data[current].optional?' · дополнительный слайд':''}`;
 $('prev').disabled=current===visible[0];$('next').disabled=current===visible.at(-1);
 $('progress').style.width=`${((idx+1)/visible.length)*100}%`;
 $('lesson1').setAttribute('aria-pressed',data[current].lesson===1);$('lesson2').setAttribute('aria-pressed',data[current].lesson===2);
 document.title=`${current+1}. ${data[current].title} — Как работает сеть`;
 syncHash();fit();
}
function show(i){current=Math.max(0,Math.min(slides.length-1,i));render()}
function step(dir){const r=route();const at=r.indexOf(current);if(at<0){const candidates=r.filter(i=>dir>0?i>current:i<current);if(candidates.length)show(dir>0?candidates[0]:candidates.at(-1))}else show(r[Math.max(0,Math.min(r.length-1,at+dir))])}
function setMode(m){mode=m;render()}
function reveal(){if(mode!=='simple')return;const buttons=[...slides[current].querySelectorAll('.simple .answer')];const open=buttons.some(b=>b.getAttribute('aria-expanded')==='false');buttons.forEach(b=>b.setAttribute('aria-expanded',open))}
function closeModals(){document.querySelectorAll('.modal').forEach(m=>m.classList.remove('open'));lastFocus?.focus();lastFocus=null}
function openModal(id){lastFocus=document.activeElement;document.querySelectorAll('.modal').forEach(m=>m.classList.remove('open'));$(id).classList.add('open');$(id).querySelector('button').focus()}
function toc(){
 const box=$('tocItems');box.replaceChildren();
 data.forEach((s,i)=>{if(pace==='90'&&s.optional)return;const b=document.createElement('button');b.className='control tocitem'+(current===i?' selected':'');b.textContent=`${i+1}. ${s.title}${s.optional?' (+)':''}`;b.onclick=()=>{closeModals();show(i)};box.append(b)});
 openModal('tocModal')
}
$('modeSimple').onclick=()=>setMode('simple');$('modeTechnical').onclick=()=>setMode('technical');
$('prev').onclick=()=>step(-1);$('next').onclick=()=>step(1);$('answers').onclick=reveal;
$('lesson1').onclick=()=>show(0);$('lesson2').onclick=()=>show(data.findIndex(s=>s.lesson===2));
$('pace').onchange=e=>{pace=e.target.value;if(pace==='90'&&data[current].optional){const r=route();current=r.find(i=>i>current)??r.at(-1)}render()};
$('contents').onclick=toc;
$('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.documentElement.requestFullscreen()}catch{$('position').textContent='Полный экран недоступен в этом просмотрщике. Откройте HTML в браузере.'}};
$('help').onclick=()=>openModal('helpModal');
 document.querySelectorAll('.modal').forEach(m=>{m.addEventListener('click',e=>{if(e.target===m)closeModals()});m.querySelector('.close').onclick=closeModals});
 document.addEventListener('click',e=>{const b=e.target.closest('.answer');if(b)b.setAttribute('aria-expanded',b.getAttribute('aria-expanded')!=='true')});
 document.addEventListener('keydown',e=>{
  const modal=document.querySelector('.modal.open');
  if(e.key==='Escape'){closeModals();return}
  if(modal){if(e.key==='Tab'){const els=[...modal.querySelectorAll('button,a[href],select')];const first=els[0],last=els.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}return}
  if(e.ctrlKey||e.metaKey||e.altKey)return;
  if(e.target.matches('select,input,textarea'))return;
  if(e.key===' '&&e.target.matches('button,a'))return;
  if(['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)){e.preventDefault();step(1)}
  else if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();step(-1)}
  else if(e.key==='Home'){e.preventDefault();show(route()[0])}
  else if(e.key==='End'){e.preventDefault();show(route().at(-1))}
  else if(['t','T','е','Е'].includes(e.key))setMode(mode==='simple'?'technical':'simple');
  else if(['a','A','ф','Ф'].includes(e.key))reveal();
  else if(['g','G','п','П'].includes(e.key))toc();
  else if(['f','F','а','А'].includes(e.key))$('fullscreen').click();
 });
 addEventListener('hashchange',()=>{const p=new URLSearchParams(location.hash.slice(1));const i=Number(p.get('slide'))-1;if(Number.isFinite(i)&&i>=0&&i<slides.length)current=i;mode=p.get('mode')==='technical'?'technical':'simple';pace=p.get('pace')==='90'?'90':'105';if(pace==='90'&&data[current].optional)current=route().find(i=>i>current)??route().at(-1);render()});
 addEventListener('resize',fit);
 if(pace==='90'&&data[current].optional)current=route().find(i=>i>current)??route().at(-1);
 render();
