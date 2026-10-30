'use strict';
/* Isolated prototype: no network, storage, tracking, service worker, or dependency. */
const $ = (id) => document.getElementById(id);
const CHAPTERS = window.ASV_DIGITAL_COMPARISON?.chapters || {};
const DEMO_HOTSPOTS = window.ASV_DEMO_HOTSPOTS?.hotspots || [];
const PAGES = [17,18,21];
const SIZE = {w:1057,h:1693};
const DATA = {
  mode:'original',layout:'auto',paper:'graphite',theme:'light',showMarkers:true,compare:false,selected:null
};
const MODES = {
  original:{title:'Original 1901 facsimile',desc:'Original historical colors and page texture, unmodified.',badge:'Archival appearance'},
  invert:{title:'Direct inversion',desc:'The exact original pixels with one display-only color inversion. No processing or extra assets.',badge:'CSS filter only'},
  processed:{title:'Clean dark · transparent ink',desc:'Precomputed ink transparency laid over a chosen background. Original stays untouched.',badge:'One reusable alpha layer'},
  enhanced:{title:'Enhanced historical print',desc:'A separately prepared image with gentle local background leveling and edge clarity.',badge:'Precomputed clarity layer'},
  digital:{title:'Digital comparison reader',desc:'Selectable, reflowable text imported from OpenBible.info for demonstration, not our scan-certified edition.',badge:'Structured text'}
};
const COLOR = {graphite:'#172629',navy:'#132238',forest:'#112b25',plum:'#282139'};
const RECT = {
  left:{17:[.018,.244,.427,.955],18:[.018,.031,.427,.955],21:[.018,.031,.427,.955]},
  right:{17:[.551,.244,.984,.955],18:[.551,.031,.984,.955],21:[.551,.031,.984,.955]}
};
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
const effectiveLayout=()=>DATA.layout==='auto'?(matchMedia('(max-width: 800px)').matches?'columns':'pages'):DATA.layout;
function asset(page,mode){return `assets/page-${page}-${mode==='original'||mode==='invert'?'original':mode==='processed'?'ink':'enhanced'}.webp`}
function skin(surface,mode,page){
  surface.dataset.style=mode;
  const img=surface.querySelector('img.raster');
  if(img){const desired=asset(page,mode);if(img.getAttribute('src')!==desired)img.setAttribute('src',desired);
    img.classList.toggle('inverted',mode==='invert');img.classList.toggle('ink-mask',mode==='processed');img.classList.toggle('enhanced',mode==='enhanced');}
}
function makeHotspot(host,page,crop){
  if(!DATA.showMarkers) return;
  const [cx0,cy0,cx1,cy1] = crop;
  DEMO_HOTSPOTS.filter(h=>h.page===page).forEach(h=>{
    const [x0,y0,x1,y1]=h.rect;
    const ax0=Math.max(x0,cx0),ay0=Math.max(y0,cy0),ax1=Math.min(x1,cx1),ay1=Math.min(y1,cy1);
    if(ax1<=ax0||ay1<=ay0)return;
    const b=document.createElement('button');b.type='button';b.className='hotspot';b.dataset.verse=h.verse;
    b.setAttribute('aria-label',`Select Genesis ${h.verse}; sample hotspot, not yet audited`);
    b.title=`Genesis ${h.verse} · sample coordinate, visual-review pending`;
    b.style.left=`${100*(ax0-cx0)/(cx1-cx0)}%`;
    b.style.top=`${100*(ay0-cy0)/(cy1-cy0)}%`;
    b.style.width=`${100*(ax1-ax0)/(cx1-cx0)}%`;
    b.style.height=`${100*(ay1-ay0)/(cy1-cy0)}%`;
    b.addEventListener('click',()=>selectVerse(h.verse,true));
    host.appendChild(b);
  });
}
function imageSurface(page,crop,mode,side){
  const div=document.createElement('div');const isFull=!side;
  div.className=isFull?'historical-page':'column-image';
  div.dataset.page=String(page);div.dataset.style=mode;
  if(!isFull){
    const [x0,y0,x1,y1]=crop,dx=x1-x0,dy=y1-y0;
    div.style.aspectRatio=`${SIZE.w*dx}/${SIZE.h*dy}`;
    const img=new Image();img.className='raster';img.alt=`1901 printed ASV page ${page}, ${side} Scripture text column`;
    img.style.width=`${100/dx}%`;img.style.left=`${-100*x0/dx}%`;img.style.top=`${-100*y0/dy}%`;
    img.loading=page===17?'eager':'lazy';img.decoding='async';div.appendChild(img);
  } else {
    const img=new Image();img.className='raster';img.alt=`Complete unmodified-layout image of ASV 1901 PDF page ${page}`;
    img.loading=page===17?'eager':'lazy';img.decoding='async';div.appendChild(img);
  }
  skin(div,mode,page);
  makeHotspot(div,page,crop);
  return div;
}
function pageHead(page){const t=document.createElement('h3');t.textContent=`1901 printing · Source PDF page ${page}`;return t}
function pageSet(page,mode){
  const container=document.createElement('div');container.className='pageunit';container.id=`printed-page-${page}`;
  container.appendChild(pageHead(page));
  if(effectiveLayout()==='pages'){
    if(DATA.compare&&DATA.mode!=='original'){
      const comp=document.createElement('div');comp.className='comparison-layout';
      comp.appendChild(labeledSurface('Original 1901',imageSurface(page,[0,0,1,1],'original')));
      comp.appendChild(labeledSurface(MODES[mode].title,imageSurface(page,[0,0,1,1],mode)));
      container.appendChild(comp);
    }else container.appendChild(imageSurface(page,[0,0,1,1],mode));
  }else{
    for(const side of ['left','right']){
      const sect=document.createElement('div');sect.className='column-group';
      const cap=document.createElement('div');cap.className='column-label';cap.textContent=side==='left'?'First printed Scripture column':'Second printed Scripture column';sect.appendChild(cap);
      if(DATA.compare&&DATA.mode!=='original'){
        const comp=document.createElement('div');comp.className='comparison-layout';
        comp.appendChild(labeledSurface('Original',imageSurface(page,RECT[side][page],'original',side)));
        comp.appendChild(labeledSurface(MODES[mode].title,imageSurface(page,RECT[side][page],mode,side)));
        sect.appendChild(comp);
      }else sect.appendChild(imageSurface(page,RECT[side][page],mode,side));
      container.appendChild(sect);
    }
  }
  return container;
}
function labeledSurface(label,surface){const box=document.createElement('div');const cap=document.createElement('div');cap.className='comparison-label';cap.textContent=label;box.append(cap,surface);return box;}
function renderHistorical(){
  const wrap=$('facsimile');wrap.innerHTML='';wrap.classList.toggle('view-columns',effectiveLayout()==='columns');
  const frag=document.createDocumentFragment();PAGES.forEach(p=>frag.appendChild(pageSet(p,DATA.mode)));wrap.appendChild(frag);
  syncSelectedHighlights();
}
function renderDigital(){
  const host=$('digitalReader');if(host.childElementCount)return;
  const frag=document.createDocumentFragment();
  for(const [chapter,verses] of Object.entries(CHAPTERS)){
    const sec=document.createElement('section');sec.className='digital-chapter';sec.id=`chapter-${chapter}`;
    const title=document.createElement('h3');title.textContent=`Genesis ${chapter}`;sec.appendChild(title);
    const body=document.createElement('p');
    for(const [verse,txt] of Object.entries(verses)){
      const span=document.createElement('span');span.className='digital-verse';span.tabIndex=0;span.role='button';
      span.dataset.verse=`${chapter}:${verse}`;
      span.setAttribute('aria-label',`Select Genesis ${chapter}:${verse}`);
      const sup=document.createElement('sup');sup.textContent=verse;span.append(sup,document.createTextNode(txt+' '));
      span.addEventListener('click',()=>selectVerse(`${chapter}:${verse}`,true));
      span.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();selectVerse(`${chapter}:${verse}`,true)}});
      body.appendChild(span);
    }
    sec.appendChild(body);frag.appendChild(sec);
  }
  host.appendChild(frag);
}
function showView(){
  const digital=DATA.mode==='digital';
  $('facsimile').classList.toggle('is-hidden',digital);
  $('digitalReader').classList.toggle('is-hidden',!digital);
  $('layout').disabled=digital;$('markers').disabled=digital;$('sideBySide').disabled=digital;
  $('paperOptions').classList.toggle('is-hidden',DATA.mode!=='processed');
  $('activeTitle').textContent=MODES[DATA.mode].title;$('modeDescription').textContent=MODES[DATA.mode].desc;
  $('layoutBadge').textContent=digital?'Reflowable text':effectiveLayout()==='pages'?'Full printed pages':'Continuous columns';
  $('imageCount').textContent=digital?'80 comparison verses':'Images loaded near viewport';
  document.documentElement.style.setProperty('--paper',COLOR[DATA.paper]);
  [...document.querySelectorAll('.mode-card')].forEach(btn=>{
    const selected=btn.dataset.mode===DATA.mode;btn.classList.toggle('chosen',selected);btn.setAttribute('aria-checked',String(selected));
  });
  if(digital){renderDigital();syncSelectedHighlights();}
  else renderHistorical();
}
function syncSelectedHighlights(){
  document.querySelectorAll('[data-verse].hotspot,[data-verse].digital-verse').forEach(x=>{
    const yes=DATA.selected===x.dataset.verse;x.classList.toggle('selected',yes);
    if(x.classList.contains('hotspot'))x.setAttribute('aria-pressed',String(yes));
  });
  $('clearSelection').disabled=!DATA.selected;
}
function chapterOf(k){return Number(k.split(':')[0]);}
function pageFor(v){const [c,n]=v.split(':').map(Number);return c===1?(n>=27?18:17):c===2?(n>=23?21:18):21;}
function populateVerses(){const ch=$('chapter').value,box=$('verse'),previous=box.value;box.innerHTML='';
  for(const v of Object.keys(CHAPTERS[ch]||{})){const o=document.createElement('option');o.value=v;o.textContent=v;box.appendChild(o)}
  if(CHAPTERS[ch]?.[previous])box.value=previous;
}
function renderWords(){
  const [ch,v]=(DATA.selected||'1:1').split(':');const txt=CHAPTERS[ch]?.[v]||'(Text unavailable)';
  $('verseWords').replaceChildren();
  const parts=txt.split(/(\s+)/);parts.forEach(s=>{
    if(!s.trim()){$('verseWords').appendChild(document.createTextNode(s));return;}
    const word=document.createElement('button');word.type='button';word.className='word';word.textContent=s;
    word.addEventListener('click',()=>{
      const was=word.classList.contains('chosen');$('verseWords').querySelectorAll('.word').forEach(b=>b.classList.remove('chosen'));
      if(was){$('studyDetail').textContent='Word selection cleared.';return;}
      word.classList.add('chosen');const cleaned=s.replace(/[^\p{L}\p{N}'’-]/gu,'');
      $('studyDetail').textContent=`Selected “${cleaned}” in Genesis ${DATA.selected}. This demonstrates word-level interaction in the expanded verse; Hebrew/Greek alignments are not yet verified.`;
    });
    $('verseWords').appendChild(word);
  });
  $('studyDetail').textContent='Select any word for a word-study interaction sample. Original-language alignment remains unverified.';
}
function selectVerse(ref,toggle=false,scroll=false){
  if(toggle&&DATA.selected===ref){clearSelection();return;}
  const [ch,verse]=ref.split(':');if(!CHAPTERS[ch]?.[verse])return;
  DATA.selected=ref;$('selectedRef').textContent=`Genesis ${ref}`;
  $('chapter').value=ch;populateVerses();$('verse').value=verse;
  renderWords();$('study').classList.add('open');$('study').setAttribute('aria-hidden','false');
  syncSelectedHighlights();
  if(scroll)scrollToRef(ref);
}
function scrollToRef(ref){
  let target;
  if(DATA.mode==='digital'){target=document.querySelector(`.digital-verse[data-verse="${ref}"]`)||$(`chapter-${chapterOf(ref)}`)}
  else{target=document.querySelector(`.hotspot[data-verse="${ref}"]`)||$(`printed-page-${pageFor(ref)}`)}
  if(target){target.scrollIntoView({block:'center',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
}
function clearSelection(){DATA.selected=null;$('study').classList.remove('open');$('study').setAttribute('aria-hidden','true');syncSelectedHighlights();}
function setMode(mode){
  if(!MODES[mode])return;
  const prior=DATA.mode;DATA.mode=mode;
  // Preserve selection but do not jump unexpectedly during visual experiments.
  // Render when replacing the DOM, otherwise only change image layers in place.
  const needsRerender=(prior==='digital')!==(mode==='digital');
  if(!needsRerender&&mode!=='digital'){
    $('activeTitle').textContent=MODES[mode].title;$('modeDescription').textContent=MODES[mode].desc;
    $('paperOptions').classList.toggle('is-hidden',mode!=='processed');
    document.querySelectorAll('.mode-card').forEach(x=>{const yes=x.dataset.mode===mode;x.classList.toggle('chosen',yes);x.setAttribute('aria-checked',String(yes))});
    if(DATA.compare){showView();return;}
    document.querySelectorAll('.historical-page,.column-image').forEach(x=>skin(x,mode,+x.dataset.page));
    return;
  }
  showView();
}
function init(){
  $('chapter').addEventListener('change',populateVerses);populateVerses();
  $('goVerse').addEventListener('click',()=>selectVerse(`${$('chapter').value}:${$('verse').value}`,false,true));
  $('clearSelection').addEventListener('click',clearSelection);
  $('closeStudy').addEventListener('click',clearSelection);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&DATA.selected)clearSelection()});
  $('appearance').addEventListener('click',e=>{const b=e.target.closest('[data-mode]');if(b)setMode(b.dataset.mode)});
  $('layout').addEventListener('change',e=>{DATA.layout=e.target.value;showView()});
  $('paper').addEventListener('change',e=>{DATA.paper=e.target.value;document.documentElement.style.setProperty('--paper',COLOR[DATA.paper])});
  $('themeToggle').addEventListener('click',()=>{document.body.classList.toggle('dark');DATA.theme=document.body.classList.contains('dark')?'dark':'light'});
  $('markers').addEventListener('change',e=>{DATA.showMarkers=e.target.checked;showView()});
  $('sideBySide').addEventListener('change',e=>{DATA.compare=e.target.checked;showView()});
  $('wordMode').addEventListener('click',()=>{$('studyDetail').textContent='Click any word in the displayed verse above. Language alignment is not yet validated.'});
  $('historicalRefs').addEventListener('click',()=>{
    if(DATA.selected==='1:1')$('studyDetail').textContent='Genesis 1:1, printed marker “a”: Psalm 102:25; Isaiah 40:21; John 1:1–2. This example was visually checked in the earlier pilot. Broader historical reference tagging remains incomplete.';
    else $('studyDetail').textContent='The printed reference column is visible in Complete historical pages. This verse’s original letter-to-destination linking is not certified in the demo.';
  });
  $('compareVerse').addEventListener('click',()=>{$('studyDetail').textContent='The expanded verse is an OpenBible.info comparison transcription. Use “Compare with original” above to display the 1901 print beside your chosen image treatment.'});
  const media=matchMedia('(max-width: 800px)');media.addEventListener?.('change',()=>{if(DATA.layout==='auto'&&DATA.mode!=='digital')showView()});
  showView();
}
document.addEventListener('DOMContentLoaded',init);
