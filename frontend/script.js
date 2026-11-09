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

// A frota fica salva neste navegador (muda pouco de um dia pro outro).
// try/catch: aba anônima / armazenamento bloqueado não pode quebrar a página.
const FLEET_KEY = 'aerj_planner_frota';
function saveFleet(){
  try{ localStorage.setItem(FLEET_KEY, JSON.stringify(VEHICLES.map(({name,cap})=>({name,cap})))); }catch{}
}
function loadFleet(){
  try{
    const salvo = JSON.parse(localStorage.getItem(FLEET_KEY) || 'null');
    if(Array.isArray(salvo) && salvo.length){
      VEHICLES = salvo.map((v,i)=>({id:'v'+(i+1), name:String(v.name||''), cap:Math.max(1,parseInt(v.cap)||1), color:COLORS[i%COLORS.length]}));
      _uid = VEHICLES.length + 1;
    }
  }catch{}
}

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
      <div class="fleet-dot" style="background:${v.color}" aria-hidden="true"></div>
      <input class="fleet-name-input" type="text" value="${esc(v.name)}"
        name="veiculo-${v.id}" autocomplete="off" enterkeyhint="next"
        placeholder="Nome do veículo, ex.: Van 1…" aria-label="Nome do veículo ${i+1}"
        oninput="updateName('${v.id}',this.value)">
      <div class="fleet-cap-wrap">
        <span class="fleet-cap-lbl" aria-hidden="true">cap.</span>
        <input class="fleet-cap-input" type="number" min="1" max="200" value="${v.cap}"
          inputmode="numeric" name="capacidade-${v.id}" autocomplete="off" enterkeyhint="done"
          aria-label="Capacidade do veículo ${i+1}"
          oninput="updateCap('${v.id}',this.value)">
      </div>
      <button class="btn-del" type="button" onclick="removeVehicle('${v.id}')" aria-label="Remover ${esc(v.name || 'veículo ' + (i+1))}">
        <svg aria-hidden="true" focusable="false" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>
      </button>
    </div>`).join('');
  fleetCount();
}

function addVehicle(){
  VEHICLES.push({id:'v'+(_uid++), name:'', cap:50, color:COLORS[VEHICLES.length%COLORS.length]});
  renderFleet();
  saveFleet();
  const inputs = document.querySelectorAll('.fleet-name-input');
  if(inputs.length) inputs[inputs.length-1].focus();
}

function removeVehicle(id){
  if(VEHICLES.length<=1){ showToast("A frota precisa de pelo menos 1 veículo. Edite o nome e a capacidade deste em vez de removê-lo."); return;}
  const idx = VEHICLES.findIndex(v=>v.id===id);
  VEHICLES = VEHICLES.filter(v=>v.id!==id);
  renderFleet();
  saveFleet();
  // foco não pode sumir junto com o botão removido
  const dels = document.querySelectorAll('.btn-del');
  if(dels.length) dels[Math.min(idx, dels.length-1)].focus();
}

function updateName(id,val){ const v=VEHICLES.find(v=>v.id===id); if(v){ v.name=val.trim(); saveFleet(); } }
function updateCap(id,val){  const v=VEHICLES.find(v=>v.id===id); if(v){ v.cap=Math.max(1,parseInt(val)||1); saveFleet(); } }

function fillExample(){
  const el = $('listInput');
  if(el.value.trim() && el.value !== EXAMPLE && !confirm('Substituir a lista colada pelo exemplo?')) return;
  el.value = EXAMPLE;
  el.focus();
}

document.addEventListener('DOMContentLoaded', ()=>{
  loadFleet();
  renderFleet();
  // Ctrl/⌘ + Enter na lista calcula
  $('listInput').addEventListener('keydown', e=>{
    if(e.key === 'Enter' && (e.ctrlKey || e.metaKey)){ e.preventDefault(); processar(); }
  });
  checkServer();
});

// ── icons ─────────────────────────────────────────────────────
const IC = {
  bus:      `<svg aria-hidden="true" focusable="false" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="1" y="3" width="15" height="13" rx="1"/><path d="M16 8h4l3 5v3h-7V8z"/><circle cx="5.5" cy="18.5" r="2.5"/><circle cx="18.5" cy="18.5" r="2.5"/></svg>`,
  users:    `<svg aria-hidden="true" focusable="false" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>`,
  up:       `<svg aria-hidden="true" focusable="false" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>`,
  down:     `<svg aria-hidden="true" focusable="false" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>`,
  pin:      `<svg aria-hidden="true" focusable="false" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>`,
  warn:     `<svg aria-hidden="true" focusable="false" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>`,
  check:    `<svg aria-hidden="true" focusable="false" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`,
  alert:    `<svg aria-hidden="true" focusable="false" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>`,
};

// ── render ─────────────────────────────────────────────────────
// Textos vindos da lista (ex.: nome de faculdade desconhecida) entram no HTML escapados
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

function warningsHtml(warnings, critical){
  if(!warnings || !warnings.length) return '';
  return `
    <div class="overflow-card ${critical ? 'is-critical' : ''}">
      <div class="overflow-hd">
        <span class="overflow-hd-txt">${critical ? 'Não dá para cumprir as regras com essa frota' : 'Avisos'}</span>
      </div>
      ${warnings.map(w=>`<div class="overflow-row"><span class="overflow-name">${esc(w)}</span></div>`).join('')}
      ${critical ? '<p class="overflow-hint">Adicione veículos ou aumente a capacidade e calcule de novo.</p>' : ''}
    </div>`;
}

function renderCritical(resp){
  $('resultTag').textContent = 'Sem solução';
  $('results').innerHTML = warningsHtml(resp.warnings, true);
}

function showErr(msg){
  $('results').innerHTML = `<div class="err-box">${IC.alert}<span>${msg}</span></div>`;
  $('resultTag').textContent = 'Erro';
}

// ── plano: sugestão → ajuste manual → aprovação (mesmo fluxo do Planejamento Diário da AERJ) ──
// _plano é a distribuição atual; _sugestao guarda a original do motor para "desfazer ajustes".
let _plano = null;
let _sugestao = null;
let _listaCalculada = '';
let _avisos = [];
let _validacao = { estado: 'validando', erros: [] }; // 'ok' | 'erro' | 'validando' | 'falhou'
let _validacaoSeq = 0;
let _validacaoTimer = null;
const SEM_VEICULO = '__sem_veiculo__';

const copia = o => JSON.parse(JSON.stringify(o));
const nomeFac = n => n.replace(/_/g, ' ');

function iniciarPlano(sugestao, avisos, lista){
  _sugestao = copia(sugestao);
  _plano = copia(sugestao);
  _plano.status = 'sugestao';
  _listaCalculada = lista;
  _avisos = avisos || [];
  _lastData = _plano;
  recalcular();
  _validacao = { estado: 'validando', erros: [] };
  renderPlano(true);
  validarAjuste();
}

function recalcular(){
  _plano.veiculos.forEach(v => { v.ocupado = v.faculdades.reduce((s,f)=>s+f.total, 0); });
  _plano.totais.veiculos_usados = _plano.veiculos.filter(v=>v.ocupado>0).length;
}

// Ordem de parada: mais perto primeiro (sem distância conhecida vai pro fim)
function ordenarPorDistancia(facs){
  facs.sort((a,b)=>(a.distancia_m ?? Infinity) - (b.distancia_m ?? Infinity));
}

function moverBloco(origem, idx, destino){
  if(!_plano || _plano.status === 'aprovado' || origem === destino) return;
  const lista = origem === SEM_VEICULO ? _plano.sem_veiculo : _plano.veiculos[origem].faculdades;
  const [bloco] = lista.splice(idx, 1);
  const alvo = destino === SEM_VEICULO ? _plano.sem_veiculo : _plano.veiculos[destino].faculdades;
  const mesma = alvo.find(f => f.nome === bloco.nome);
  if(mesma){ // mesma faculdade já no destino: junta os alunos
    mesma.ida += bloco.ida; mesma.volta += bloco.volta; mesma.total += bloco.total;
  } else {
    alvo.push(bloco);
    ordenarPorDistancia(alvo);
  }
  _plano.status = 'ajustado';
  recalcular();
  _validacaoSeq++;
  _validacao = { estado: 'validando', erros: [] };
  renderPlano(false, {destino, fac: bloco.nome});
  agendarValidacao();
}

function desfazerAjustes(){
  if(!_sugestao || _plano?.status === 'aprovado') return;
  _plano = copia(_sugestao);
  _plano.status = 'sugestao';
  _lastData = _plano;
  recalcular();
  _validacao = { estado: 'validando', erros: [] };
  renderPlano(false);
  validarAjuste();
  showToast('Ajustes desfeitos — voltou para a sugestão do sistema.', 'success');
}

function agendarValidacao(){
  _validacaoSeq++; // qualquer validação em andamento ficou velha: a resposta dela será ignorada
  _validacao = { estado: 'validando', erros: [] };
  renderPainelAjuste();
  clearTimeout(_validacaoTimer);
  _validacaoTimer = setTimeout(()=>validarAjuste(), 350);
}

// O servidor revalida tudo (capacidade, ninguém de fora/sobrando, regras obrigatórias).
async function validarAjuste(){
  if(!_plano) return null;
  const seq = ++_validacaoSeq;
  _validacao = { estado: 'validando', erros: [] };
  renderPainelAjuste();
  try{
    const res = await fetch(`${API}/validar-ajuste`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ lista: _listaCalculada, veiculos: _plano.veiculos.map(v=>({
        nome: v.nome, capacidade: v.capacidade,
        faculdades: v.faculdades.map(({nome, ida, volta, total})=>({nome, ida, volta, total})),
      })) }),
    });
    const r = await res.json();
    if(seq !== _validacaoSeq) return null; // resposta velha: já houve outra mudança
    if(!res.ok) throw new Error(r.erro || 'falha');
    _validacao = { estado: r.valido ? 'ok' : 'erro', erros: r.erros || [] };
  }catch{
    if(seq !== _validacaoSeq) return null;
    _validacao = { estado: 'falhou', erros: [] };
  }
  renderPainelAjuste();
  return _validacao.estado === 'ok';
}

async function aprovarPlano(){
  if(!_plano || _plano.status === 'aprovado') return;
  const btn = $('approveBtn');
  if(btn) btn.disabled = true;
  clearTimeout(_validacaoTimer);
  const ok = await validarAjuste(); // valida de novo na hora de aprovar
  if(!ok){
    showToast('A distribuição ainda não pode ser aprovada. Corrija os pontos em vermelho e tente de novo.');
    return;
  }
  _plano.status = 'aprovado';
  _plano.aprovadoEm = new Intl.DateTimeFormat('pt-BR', {hour:'2-digit', minute:'2-digit'}).format(new Date());
  renderPlano(false);
  showToast(`Distribuição aprovada às ${_plano.aprovadoEm}. Use “Exportar” para mandar no WhatsApp.`, 'success');
  $('exportBtn')?.focus();
}

function seletorMover(origem, idx, f){
  if(_plano.status === 'aprovado') return '';
  const opcoes = _plano.veiculos.map((v,vi)=>
    `<option value="${vi}" ${vi===origem?'selected':''}>${esc(v.nome)} (${v.ocupado}/${v.capacidade})</option>`).join('');
  return `
    <label class="move-wrap">
      <span class="sr-only">Mover ${esc(nomeFac(f.nome))} (${f.total} aluno${f.total!==1?'s':''}) para</span>
      <span class="move-lbl" aria-hidden="true">Mover para</span>
      <select class="move-select" data-origem="${origem}" data-idx="${idx}" data-fac="${esc(f.nome)}"
        onchange="moverBloco(${origem===SEM_VEICULO?`'${SEM_VEICULO}'`:origem}, ${idx}, this.value==='${SEM_VEICULO}'?'${SEM_VEICULO}':Number(this.value))">
        ${opcoes}
        <option value="${SEM_VEICULO}" ${origem===SEM_VEICULO?'selected':''}>Sem veículo</option>
      </select>
    </label>`;
}

function linhaFaculdade(f, idx, origem){
  return `
    <div class="school-row">
      <span class="school-idx">${origem===SEM_VEICULO ? '—' : idx+1}</span>
      <span class="school-name">${esc(nomeFac(f.nome))}</span>
      <div class="chips">
        <span class="chip chip-b">${IC.up} ${f.ida}<span class="sr-only"> de ida</span></span>
        <span class="chip chip-t">${IC.down} ${f.volta}<span class="sr-only"> de volta</span></span>
        ${origem===SEM_VEICULO
          ? `<span class="chip" style="background:rgba(245,158,11,.12);color:#fbbf24">${IC.users} ${f.total}<span class="sr-only"> alunos</span></span>`
          : `<span class="chip chip-g" title="${f.rota_estimada?'estimada em linha reta':''}">${IC.pin} ${f.distancia_m?(f.rota_estimada?'~':'')+Math.round(f.distancia_m/1000)+'km':'—'}</span>`}
      </div>
      ${seletorMover(origem, idx, f)}
    </div>`;
}

function painelAjusteHtml(){
  const st = _plano.status;
  if(st === 'aprovado'){
    return `<div class="plan-bar plan-bar--ok">
      <span class="plan-status">${IC.check} <strong>Aprovada</strong> às ${esc(_plano.aprovadoEm)}</span>
      <span class="plan-hint">Para mudar, calcule de novo.</span>
    </div>`;
  }
  const v = _validacao;
  let msg;
  if(v.estado === 'validando') msg = `<span class="plan-status plan-status--wait">validando…</span>`;
  else if(v.estado === 'ok') msg = `<span class="plan-status plan-status--ok">${IC.check} ${st==='sugestao'?'Sugestão pronta para aprovar':'Ajuste válido, pronto para aprovar'}</span>`;
  else if(v.estado === 'falhou') msg = `<span class="plan-status plan-status--err">Não deu para conferir agora. Tente aprovar de novo em instantes.</span>`;
  else msg = `<span class="plan-status plan-status--err">Corrija antes de aprovar:</span>
    <ul class="plan-errs">${v.erros.map(e=>`<li>${esc(e)}</li>`).join('')}</ul>`;
  return `<div class="plan-bar ${v.estado==='erro'||v.estado==='falhou'?'plan-bar--err':''}">
    <div class="plan-msg">${msg}</div>
    <p class="plan-hint">Para trocar uma faculdade de veículo, use “Mover para”.</p>
    <div class="plan-actions">
      ${st==='ajustado' ? `<button type="button" class="btn-ghost" onclick="desfazerAjustes()">Desfazer ajustes</button>` : ''}
      <button type="button" class="btn-approve" id="approveBtn" onclick="aprovarPlano()" ${v.estado==='ok'?'':'disabled'}>${IC.check} Aprovar distribuição</button>
    </div>
  </div>`;
}

function renderPainelAjuste(){
  const el = $('planPanel');
  if(el && _plano) el.innerHTML = painelAjusteHtml();
}

function render(data, warnings){ iniciarPlano(data, warnings, _listaCalculada); }

function renderPlano(animar, focar){
  const {veiculos, sem_veiculo, totais} = _plano;
  const aprovado = _plano.status === 'aprovado';
  const visiveis = veiculos.map((v,vi)=>({v,vi})).filter(({v})=> !aprovado || v.ocupado>0);
  const usados = veiculos.filter(v=>v.ocupado>0).length;
  const rotulo = {sugestao:'Sugestão', ajustado:'Ajustada', aprovado:'Aprovada'}[_plano.status];

  $('resultTag').textContent = rotulo;

  // stats
  const sColors = ['#5592ff','#93c5fd','#f59e0b','#22c55e'];
  const sLabels = ['Alunos','Ida','Volta','Veículos'];
  const sIcons  = [IC.users, IC.up, IC.down, IC.bus];
  const sVals   = [totais.alunos, totais.ida, totais.volta, usados];

  let html = `<div class="stats-grid">`;
  for(let i=0;i<4;i++) html+=`
    <div class="stat-box" style="animation-delay:${i*.05}s">
      <div class="stat-lbl">${sIcons[i]} ${sLabels[i]}</div>
      <div class="stat-val" style="color:${sColors[i]}">${sVals[i]}</div>
    </div>`;
  html += `</div>`;

  html += `<div id="planPanel">${painelAjusteHtml()}</div>`;
  html += warningsHtml(_avisos, false);

  // sem veículo: também é uma "caixa" de onde (e para onde) dá pra mover
  if(sem_veiculo && sem_veiculo.length > 0){
    const totalSem = sem_veiculo.reduce((s,f)=>s+f.total,0);
    html += `
    <div class="overflow-card" style="animation-delay:.08s">
      <div class="overflow-hd">
        <span style="color:var(--amber)">${IC.warn}</span>
        <span class="overflow-hd-txt">Sem veículo</span>
        <span class="overflow-hd-count">${totalSem} aluno${totalSem!==1?'s':''}</span>
      </div>
      ${sem_veiculo.map((f,idx)=>linhaFaculdade(f, idx, SEM_VEICULO)).join('')}
      <p class="overflow-hint">Mova para um veículo com espaço ou adicione veículos na frota e recalcule.</p>
    </div>`;
  }

  if(visiveis.length) html += `<div class="sec-divider">Veículos</div>`;

  visiveis.forEach(({v, vi}, i)=>{
    const cor = VEHICLES.find(x=>x.name===v.nome)?.color || COLORS[vi%COLORS.length];
    const pct = v.capacidade ? Math.round(v.ocupado/v.capacidade*100) : 0;
    const bc  = pct>100?'#ef4444':pct>90?'#ef4444':pct>70?'#f59e0b':cor;
    // texto pequeno precisa de cor mais clara que a barra (contraste >= 4,5:1)
    const tc  = pct>90?'#f87171':pct>70?'#fbbf24':'#93c5fd';

    html += `
    <div class="vcard ${pct>100?'vcard--over':''}" style="animation-delay:${.1+i*.08}s;border-left:3px solid ${cor}">
      <div class="vcard-hd">
        <div class="vcard-ico" aria-hidden="true" style="background:${cor}1f;color:${cor}">${IC.bus}</div>
        <span class="vcard-name">${esc(v.nome)}</span>
        <span class="vcard-cap" style="color:${tc}">${v.ocupado}/${v.capacidade}${pct>100?' <span class="over-tag">acima</span>':''}</span>
      </div>
      <div class="pbar-wrap">
        <div class="pbar-meta"><span>ocupação</span><span style="color:${tc}">${pct}%</span></div>
        <div class="pbar-bg"><div class="pbar-fill" style="width:${Math.min(pct,100)}%;background:${bc}"></div></div>
      </div>
      <div class="school-list">
        ${v.faculdades.length
          ? v.faculdades.map((f,idx)=>linhaFaculdade(f, idx, vi)).join('')
          : `<p class="vcard-empty">Vazio</p>`}
      </div>
    </div>`;
  });

  const box = $('results');
  box.classList.toggle('no-anim', !animar);
  box.innerHTML = html;
  $('exportBtn').style.display = 'flex';

  // o <select> usado foi recriado: devolve o foco para a faculdade no destino
  if(focar){
    const sel = [...box.querySelectorAll('.move-select')]
      .find(s => s.dataset.fac === focar.fac && s.dataset.origem === String(focar.destino));
    sel?.focus();
  }
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
      const n = f.nome.replace(/_/g, ' ');
      const nome = n.charAt(0).toUpperCase() + n.slice(1).toLowerCase();
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
      linhas.push(f.ida == null
        ? `${f.nome}- ${f.total} aluno(s)`
        : `${f.nome}- ${f.ida} ida / ${f.volta} volta`);
    });
  }

  return linhas.join('\n');
}

// ── modal export (dialog acessível: foco entra, Tab fica dentro, Esc fecha, foco volta) ──
let _focoAntesDoModal = null;

function abrirExport(){
  if(!_lastData) return;
  // Safari não foca botão no clique: sem foco útil, volta pro próprio “exportar”
  _focoAntesDoModal = (document.activeElement && document.activeElement !== document.body) ? document.activeElement : $('exportBtn');
  $('exportText').value = gerarTexto(_lastData);
  $('exportModal').style.display = 'block';
  document.body.style.overflow = 'hidden';
  $('copyBtn').focus();
}

function fecharExport(e){
  if(e && e.target !== e.currentTarget) return;
  if($('exportModal').style.display === 'none') return;
  $('exportModal').style.display = 'none';
  document.body.style.overflow = '';
  // reset botão copiar
  $('copyBtn').classList.remove('copied');
  $('copyTxt').textContent = 'Copiar texto';
  if(_focoAntesDoModal && document.contains(_focoAntesDoModal)) _focoAntesDoModal.focus();
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
  $('copyTxt').textContent = 'Copiado';
  setTimeout(()=>{
    $('copyBtn').classList.remove('copied');
    $('copyTxt').textContent = 'Copiar texto';
  }, 2500);
}

// Tab/Shift+Tab presos dentro do dialog aberto
function prenderFoco(e, container){
  if(e.key !== 'Tab') return;
  const focaveis = [...container.querySelectorAll('button, textarea, input, [href], [tabindex]:not([tabindex="-1"])')]
    .filter(el => !el.disabled && el.offsetParent !== null);
  if(!focaveis.length) return;
  const primeiro = focaveis[0], ultimo = focaveis[focaveis.length-1];
  if(e.shiftKey && document.activeElement === primeiro){ e.preventDefault(); ultimo.focus(); }
  else if(!e.shiftKey && document.activeElement === ultimo){ e.preventDefault(); primeiro.focus(); }
}

document.addEventListener('keydown', e => {
  const tutorialAberto = !$('tutorialOverlay').hidden;
  const exportAberto = $('exportModal').style.display !== 'none';
  if(e.key === 'Escape'){
    if(tutorialAberto) skipTutorial();
    else if(exportAberto) fecharExport();
    return;
  }
  if(tutorialAberto) prenderFoco(e, $('tutorialOverlay'));
  else if(exportAberto) prenderFoco(e, document.querySelector('#exportModal .modal'));
});

// ── servidor ─────────────────────────────────────────────────
// Servido pelo próprio Flask (local) → mesma origem; publicado → API no Render.
const API = ['localhost','127.0.0.1'].includes(location.hostname) ? '' : 'https://student-transport-planner-py.onrender.com';

// O plano gratuito do Render "dorme": a primeira requisição pode levar ~30–60 s.
const ACORDANDO_APOS_MS = 3000;

function setServerStatus(estado){
  const badge = $('serverStatus');
  if(!badge) return;
  const textos = { online:'Servidor online', waking:'Servidor acordando…', offline:'Servidor fora do ar', checking:'Conectando…' };
  badge.classList.remove('waking','offline');
  if(estado === 'waking' || estado === 'checking') badge.classList.add('waking');
  if(estado === 'offline') badge.classList.add('offline');
  $('serverStatusTxt').textContent = textos[estado];
}

async function checkServer(){
  setServerStatus('checking');
  const lento = setTimeout(()=>setServerStatus('waking'), ACORDANDO_APOS_MS);
  try{
    const ctrl = new AbortController();
    const limite = setTimeout(()=>ctrl.abort(), 90000);
    const res = await fetch(`${API}/ping`, {signal: ctrl.signal, cache:'no-store'});
    clearTimeout(limite);
    setServerStatus(res.ok ? 'online' : 'offline');
  }catch{
    setServerStatus('offline');
  }finally{
    clearTimeout(lento);
  }
}

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

  if(!txt){
    showToast("Cole a lista do WhatsApp no campo “lista de transporte” antes de calcular.");
    $('listInput').focus();
    return;
  }
  const semNome = VEHICLES.findIndex(v=>!v.name);
  if(semNome !== -1){
    showToast(`Dê um nome ao veículo ${semNome+1} (ex.: “Van 1”) antes de calcular.`);
    document.querySelectorAll('.fleet-name-input')[semNome]?.focus();
    return;
  }

  btn.classList.add('loading'); btn.disabled=true;
  $('resultTag').textContent = 'Calculando…';
  $('results').setAttribute('aria-busy','true');
  const lento = setTimeout(()=>{
    $('resultTag').textContent = 'Servidor acordando…';
    setServerStatus('waking');
  }, ACORDANDO_APOS_MS);

  try {
    const res = await fetch(`${API}/planejar`,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({
        lista:    txt,
        veiculos: VEHICLES.map(v=>({nome:v.name, capacidade:v.cap})),
      }),
    });
    setServerStatus('online');
    const data = await res.json();
    if(!res.ok){
      const extra = (data.warnings || []).join(' ');
      showToast((data.erro || "O servidor não conseguiu processar a lista. Confira o formato e tente de novo.") + (extra ? ' ' + extra : ''));
      $('resultTag').textContent = 'Erro';
      return;
    }
    if(data.critical){
      _lastData = null; _plano = null;
      $('exportBtn').style.display = 'none';
      renderCritical(data);
      return;
    }
    iniciarPlano(data.suggestion, data.warnings, txt);
  } catch(e){
    setServerStatus('offline');
    $('resultTag').textContent = 'Erro';
    showToast("Não foi possível falar com o servidor. Confira a internet e tente de novo — se ele estava dormindo, a segunda tentativa costuma funcionar.");
  } finally {
    clearTimeout(lento);
    $('results').setAttribute('aria-busy','false');
    btn.classList.remove('loading'); btn.disabled=false;
  }
}

function showToast(msg, type="error"){
  let container = document.getElementById("toastContainer");
  if(!container){
    container = document.createElement("div");
    container.id = "toastContainer";
    container.setAttribute('aria-live','polite');
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.setAttribute('role', type === 'error' ? 'alert' : 'status');
  toast.textContent = msg;
  container.appendChild(toast);

  // mensagem longa fica mais tempo na tela
  setTimeout(()=>toast.remove(), Math.max(4000, msg.length * 60));
}

/* TUTORIAL */
// v2: a versão anterior já marcou "tutorial_seen" — chave nova para todo mundo ver este uma vez
const TUTORIAL_KEY = 'aerj_planner_tutorial_v2';
const tutorialSteps = [
  {
    title: "Como funciona",
    text: "Cole a lista do grupo, confira a frota e clique em Calcular rotas."
  },
  {
    title: "Regras",
    text: "UNEX e UNEF nunca vão juntas. UNIFAN vai com QUADRIVIUM e IFBA com UNEF. A UEFS completa as vagas que sobrarem."
  },
  {
    title: "Ajuste e aprovação",
    text: "Se não concordar com a sugestão, troque faculdades de veículo em “Mover para”. Cada mudança é conferida antes de liberar a aprovação."
  }
];

let tutorialIndex = 0;

function lembrarTutorialVisto(){
  try{ localStorage.setItem(TUTORIAL_KEY,"1"); }catch{}
}

function startTutorial(){
  tutorialIndex = 0;
  $('tutorialOverlay').hidden = false;
  showTutorialStep();
  $('tutorialNext').focus();
}

function showTutorialStep(){
  const step = tutorialSteps[tutorialIndex];
  $('tutorialStep').textContent = `${tutorialIndex+1}/${tutorialSteps.length}`;
  $('tutorialTitle').textContent = step.title;
  $('tutorialText').textContent = step.text;
  const ultimo = tutorialIndex === tutorialSteps.length-1;
  $('tutorialNext').textContent = ultimo ? 'Começar' : 'Próximo';
}

function fecharTutorial(){
  $('tutorialOverlay').hidden = true;
  lembrarTutorialVisto();
  $('listInput').focus({preventScroll:true});
}

function nextTutorial(){
  tutorialIndex++;
  if(tutorialIndex >= tutorialSteps.length){ fecharTutorial(); return; }
  showTutorialStep();
}

function skipTutorial(){ fecharTutorial(); }

/* APARECER SO UMA VEZ (overlay já começa escondido no HTML: sem piscar pra quem já viu) */
document.addEventListener("DOMContentLoaded", ()=>{
  let visto = false;
  try{ visto = !!localStorage.getItem(TUTORIAL_KEY); }catch{}
  if(!visto) startTutorial();
});
