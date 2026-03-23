const EXAMPLE = `UNEF
1. Edmille (volta)
2. Kamilly (volta)
3. marina
4. Maine
5. Cássia (volta)
6. Mariana
7. Amanda
8. kemilly

UNIFAN
1. Gabriel
2. Laura (ida)
3. Letícia
4. Isabela
5. Maria Beatriz
6. Duda
7. Danielle
8. Fernanda Brito
9. Giselle
10. Isabelli
11. Clara
12. João
13. Yuri
14. Ellen
15. Bruna
16. Andressa
17. Alisson
18. Luiz Henrique (volta)
19. Hellen

UEFS
1. Gabriel
2. Larissa
3. Ícaro (ida)
4. Victor
5. Luan
6. Tiago
7. Julia
8. Kaylanne
9. Lavínya
10. Samuel
11. André
12. Léo (volta)
13. Sérgio

SENAI
1. Trindade
2. Yasmin
3. Guilherme
4. Denver`;

// ── frota ─────────────────────────────────────────────────────
const COLORS = ['#1d5ce5','#2f72ff','#5592ff','#7eb3ff','#38bdf8','#22d3ee','#34d399','#a78bfa'];
let _uid = 2;
let VEHICLES = [
  {id:'v1', name:'Ônibus 1', cap:50, color:'#1d5ce5'},
];

const $ = id => document.getElementById(id);

function fleetCount(){
  const el = $('fleetCount');
  if(el) el.textContent = VEHICLES.length + ' veículo' + (VEHICLES.length!==1?'s':'');
}

function renderFleet(){
  const list = $('fleetList');
  if(!list) return;
  list.innerHTML = VEHICLES.map((v,i)=>`
    <div class="fleet-item" id="fi-${v.id}" style="animation-delay:${i*.04}s">
      <div class="fleet-dot" style="background:${v.color}"></div>
      <input class="fleet-name-input" type="text" value="${v.name}"
        placeholder="nome do veículo"
        onchange="updateName('${v.id}',this.value)" title="Nome">
      <div class="fleet-cap-wrap">
        <span class="fleet-cap-lbl">cap.</span>
        <input class="fleet-cap-input" type="number" min="1" max="200" value="${v.cap}"
          onchange="updateCap('${v.id}',this.value)" title="Capacidade">
      </div>
      <button class="btn-del" onclick="removeVehicle('${v.id}')" title="Remover">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
      </button>
    </div>`).join('');
  fleetCount();
}

function addVehicle(){
  VEHICLES.push({id:'v'+(_uid++), name:'', cap:50, color:COLORS[VEHICLES.length%COLORS.length]});
  renderFleet();
  const inputs = document.querySelectorAll('.fleet-name-input');
  if(inputs.length) inputs[inputs.length-1].focus();
}

function removeVehicle(id){
  if(VEHICLES.length<=1){ showToast("É necessário ter pelo menos 1 veículo na frota."); return;}
  VEHICLES = VEHICLES.filter(v=>v.id!==id);
  renderFleet();
}

function updateName(id,val){ const v=VEHICLES.find(v=>v.id===id); if(v) v.name=val.trim(); }
function updateCap(id,val){  const v=VEHICLES.find(v=>v.id===id); if(v) v.cap=Math.max(1,parseInt(val)||1); }

function fillExample(){ $('listInput').value = EXAMPLE; }

document.addEventListener('DOMContentLoaded', renderFleet);

// ── icons ─────────────────────────────────────────────────────
const IC = {
  bus:      `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13" rx="1"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>`,
  users:    `<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  up:       `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>`,
  down:     `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>`,
  pin:      `<svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
  warn:     `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  alert:    `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
};

// ── render ───────────────────────────────────────────────────── 
function showErr(msg){
  $('results').innerHTML = `<div class="err-box">${IC.alert}<span>${msg}</span></div>`;
  $('resultTag').textContent = 'erro';
}

function render(data){
  const {veiculos, sem_veiculo, totais} = data;
  const ativos = veiculos.filter(v=>v.ocupado>0);

  $('resultTag').textContent = `${ativos.length} veículo${ativos.length!==1?'s':''}`;

  // stats
  const sColors = ['#5592ff','#93c5fd','#f59e0b','#22c55e'];
  const sLabels = ['alunos','ida','volta','veículos'];
  const sIcons  = [IC.users, IC.up, IC.down, IC.bus];
  const sVals   = [totais.alunos, totais.ida, totais.volta, totais.veiculos_usados];

  let html = `<div class="stats-grid">`;
  for(let i=0;i<4;i++) html+=`
    <div class="stat-box" style="animation-delay:${i*.05}s">
      <div class="stat-lbl">${sIcons[i]} ${sLabels[i]}</div>
      <div class="stat-val" style="color:${sColors[i]}">${sVals[i]}</div>
    </div>`;
  html += `</div>`;

  // overflow alert
  if(sem_veiculo && sem_veiculo.length > 0){
    const totalSem = sem_veiculo.reduce((s,f)=>s+f.total,0);
    html += `
    <div class="overflow-card" style="animation-delay:.08s">
      <div class="overflow-hd">
        <span style="color:var(--amber)">${IC.warn}</span>
        <span class="overflow-hd-txt">sem veículo disponível</span>
        <span class="overflow-hd-count">${totalSem} aluno${totalSem!==1?'s':''}</span>
      </div>
      ${sem_veiculo.map(f=>`
        <div class="overflow-row">
          <span class="school-idx">—</span>
          <span class="overflow-name">${f.nome}</span>
          <div class="chips">
            <span class="chip chip-b">${IC.up} ${f.ida}</span>
            <span class="chip chip-t">${IC.down} ${f.volta}</span>
            <span class="chip" style="background:rgba(245,158,11,.12);color:#fbbf24">${IC.users} ${f.total} total</span>
          </div>
        </div>`).join('')}
      <p class="overflow-hint">Adicione mais veículos na frota e recalcule.</p>
    </div>`;
  }

  // veículos
  if(ativos.length) html += `<div class="sec-divider">veículos alocados</div>`;

  ativos.forEach((v,i)=>{
    const cor = VEHICLES.find(x=>x.name===v.nome)?.color || COLORS[i%COLORS.length];
    const pct = Math.round(v.ocupado/v.capacidade*100);
    const bc  = pct>90?'#ef4444':pct>70?'#f59e0b':cor;

    html += `
    <div class="vcard" style="animation-delay:${.1+i*.08}s;border-left:3px solid ${cor}">
      <div class="vcard-hd">
        <div class="vcard-ico" style="background:${cor}1f;color:${cor}">${IC.bus}</div>
        <span class="vcard-name">${v.nome}</span>
        <span class="vcard-cap" style="color:${bc}">${v.ocupado}/${v.capacidade}</span>
      </div>
      <div class="pbar-wrap">
        <div class="pbar-meta"><span>ocupação</span><span style="color:${bc}">${pct}%</span></div>
        <div class="pbar-bg"><div class="pbar-fill" style="width:${pct}%;background:${bc}"></div></div>
      </div>
      <div class="school-list">
        ${v.faculdades.map((f,idx)=>`
          <div class="school-row">
            <span class="school-idx">${idx+1}</span>
            <span class="school-name">${f.nome}</span>
            <div class="chips">
              <span class="chip chip-b">${IC.up} ${f.ida}</span>
              <span class="chip chip-t">${IC.down} ${f.volta}</span>
              <span class="chip chip-g">${IC.pin} ${f.distancia_m?Math.round(f.distancia_m/1000)+'km':'—'}</span>
            </div>
          </div>`).join('')}
      </div>
    </div>`;
  });

  $('results').innerHTML = html;
}

// ── export ────────────────────────────────────────────────────
let _lastData = null;

function gerarTexto(data){
  const { veiculos, sem_veiculo } = data;
  const ativos = veiculos.filter(v => v.ocupado > 0);
  const tipoLabel = nome => {
    const n = nome.toLowerCase();
    if(n.includes('van'))   return 'VAN';
    if(n.includes('micro')) return 'MICRO-ÔNIBUS';
    return 'ÔNIBUS';
  };

  let linhas = [];
  ativos.forEach((v, i) => {
    const tipo = tipoLabel(v.nome);
    linhas.push(`*ROTA ${i+1} - ${tipo} (${v.nome.toUpperCase()})*`);
    let totIda = 0, totVolta = 0;
    v.faculdades.forEach(f => {
      // capitaliza só a primeira letra de cada palavra
      const nome = f.nome.charAt(0).toUpperCase() + f.nome.slice(1).toLowerCase();
      linhas.push(`${nome}- ${f.ida} ida / ${f.volta} volta`);
      totIda   += f.ida;
      totVolta += f.volta;
    });
    linhas.push(`Total: ${totIda} ida / ${totVolta} volta`);
    if(i < ativos.length - 1) linhas.push('');
  });

  if(sem_veiculo && sem_veiculo.length > 0){
    linhas.push('');
    linhas.push(' *SEM VEÍCULO DISPONÍVEL*');
    sem_veiculo.forEach(f => {
      linhas.push(`${f.nome}- ${f.ida} ida / ${f.volta} volta`);
    });
  }

  return linhas.join('\n');
}

function abrirExport(){
  if(!_lastData) return;
  $('exportText').value = gerarTexto(_lastData);
  $('exportModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
}

function fecharExport(e){
  if(e && e.target !== e.currentTarget) return;
  $('exportModal').style.display = 'none';
  document.body.style.overflow = '';
  // reset botão copiar
  $('copyBtn').classList.remove('copied');
  $('copyTxt').textContent = 'copiar texto';
}

async function copiarTexto(){
  const txt = $('exportText').value;
  try {
    await navigator.clipboard.writeText(txt);
  } catch {
    $('exportText').select();
    document.execCommand('copy');
  }
  $('copyBtn').classList.add('copied');
  $('copyTxt').textContent = '✓ copiado!';
  setTimeout(()=>{
    $('copyBtn').classList.remove('copied');
    $('copyTxt').textContent = 'copiar texto';
  }, 2500);
}

document.addEventListener('keydown', e => {
  if(e.key === 'Escape') fecharExport();
});

//const API = 'http://localhost:5000';
const API = 'https://student-transport-planner-py.onrender.com';

async function processar(){
  // flush inputs antes de enviar
  document.querySelectorAll('.fleet-name-input').forEach(el=>{
    const id = el.closest('.fleet-item')?.id?.replace('fi-','');
    if(id) updateName(id, el.value);
  });
  document.querySelectorAll('.fleet-cap-input').forEach(el=>{
    const id = el.closest('.fleet-item')?.id?.replace('fi-','');
    if(id) updateCap(id, el.value);
  });

  const txt = $('listInput').value.trim();
  const btn = $('runBtn');

  if(!txt){showToast("Cole a lista de alunos antes de calcular as rotas.");  return;}
  if(VEHICLES.some(v=>!v.name)){showToast("Todos os veículos precisam ter um nome antes de calcular."); return;
  }

  btn.classList.add('loading'); btn.disabled=true;
  $('resultTag').textContent = 'calculando...';

  try {
    const res = await fetch(`${API}/planejar`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        lista:    txt,
        veiculos: VEHICLES.map(v=>({nome:v.name, capacidade:v.cap})),
      }),
    });
    const data = await res.json();
    if(!res.ok){showToast(data.erro || "O servidor não conseguiu processar a lista."); return;}
    _lastData = data;
    render(data);
    $('exportBtn').style.display = 'flex';
  } catch(e){
    showToast("Não foi possível conectar ao servidor. Verifique sua internet.");
  } finally {
    btn.classList.remove('loading'); btn.disabled=false;
  }
}

function showToast(msg, type="error"){

  let container = document.getElementById("toastContainer");

  if(!container){
    container = document.createElement("div");
    container.id = "toastContainer";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = msg;

  container.appendChild(toast);

  setTimeout(()=>{
    toast.remove();
  },4000);
}

/* TUTORIAL */
const tutorialSteps = [
  {
    title: "Bem-vindo ao planejador",
    text: "Este sistema organiza alunos em veículos automaticamente."
  },
  {
    title: "Cole a lista de alunos",
    text: "Cole a lista das faculdades e alunos na caixa principal."
  },
  {
    title: "Adicione veículos",
    text: "Clique em 'Adicionar veículo' para incluir ônibus ou vans."
  },
  {
    title: "Defina capacidade",
    text: "Informe quantos alunos cabem em cada veículo."
  },
  {
    title: "Calcule as rotas",
    text: "Clique em calcular e o sistema distribuirá os alunos automaticamente."
  }
];

let tutorialIndex = 0;

function startTutorial(){
  tutorialIndex = 0;
  showTutorialStep();
}

function showTutorialStep(){
  const step = tutorialSteps[tutorialIndex];

  document.getElementById("tutorialTitle").textContent = step.title;
  document.getElementById("tutorialText").textContent = step.text;
}

function nextTutorial(){
  tutorialIndex++;

  if(tutorialIndex >= tutorialSteps.length){
    document.getElementById("tutorialOverlay").style.display = "none";
    localStorage.setItem("tutorial_seen","true");
    return;
  }

  showTutorialStep();
}

function skipTutorial(){
  document.getElementById("tutorialOverlay").style.display = "none";
  localStorage.setItem("tutorial_seen","true");
}

/* APARECER SO UMA VEZ */
document.addEventListener("DOMContentLoaded", ()=>{

  if(!localStorage.getItem("tutorial_seen")){
    startTutorial();
  } else {
    document.getElementById("tutorialOverlay").style.display = "none";
  }

});