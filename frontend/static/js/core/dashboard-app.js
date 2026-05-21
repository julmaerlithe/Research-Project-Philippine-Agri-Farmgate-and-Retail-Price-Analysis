const API_BASE = window.location.port === '5000'
  ? '/api'
  : `${window.location.protocol}//${window.location.hostname}:5000/api`;

const COLORS = {
  Banana:'#d4a22a', Cassava:'#6fa34f', Coconut:'#3b8b73',
  Corn:'#d97924', Mango:'#c9483d', Pineapple:'#7b5fb2',
  Rice:'#557d99'
};
const AXIS = '#65765e';
const GRID = '#e6eee0';
let DATA = {commodities:[], margin:{}, granger:{}, trends:[], yearly:{}};
let currentComm = '';
let charts = {};

function setLoading(on){document.getElementById('loading').classList.toggle('hidden', !on)}
function showError(message){
  const el = document.getElementById('errorToast');
  el.textContent = message;
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 4500);
}
function destroyChart(id){ if(charts[id]){charts[id].destroy();delete charts[id];} }
function peso(value){ return `PHP ${Number(value || 0).toFixed(2)}`; }
function pct(value){ return `${Number(value || 0).toFixed(1)}%`; }
function avg(values){ return values.length ? values.reduce((sum, value) => sum + Number(value || 0), 0) / values.length : 0; }
function minP(granger){ return granger?.min_p_value ?? Math.min(...Object.values(granger?.p_values || {1:1}).map(Number)); }
function significant(granger){ return Boolean(granger?.significant ?? granger?.is_significant ?? minP(granger) < 0.05); }
function chartBase(extra = {}){
  return {
    responsive:true,
    maintainAspectRatio:false,
    plugins:{legend:{labels:{color:AXIS,boxWidth:12,font:{size:11}}}},
    scales:{
      x:{grid:{display:false},ticks:{color:AXIS,maxRotation:45,minRotation:0}},
      y:{grid:{color:GRID},ticks:{color:AXIS}}
    },
    ...extra
  };
}

async function loadDashboardData(){
  const response = await fetch(`${API_BASE}/analysis/dashboard-data?max_lag=3`);
  if(!response.ok) throw new Error(`Backend returned ${response.status}`);
  DATA = await response.json();
  currentComm = DATA.commodities[0] || '';
  document.getElementById('view-badge').textContent = `${DATA.commodities.length} commodities - ${DATA.trends.length} months`;
}

function showView(v){
  document.querySelectorAll('.content').forEach(c=>c.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
  document.querySelectorAll('.cpill,.comm-btn').forEach(el=>el.classList.remove('active'));
  document.getElementById(`view-${v}`).classList.add('active');
  document.querySelectorAll('.nav-item').forEach(n=>{
    if(n.getAttribute('onclick')===`showView('${v}')`) n.classList.add('active');
  });
  const titles={overview:'Dashboard Overview',margin:'Marketing Margin Analysis',commodity:`${currentComm} Commodity Analysis`,trends:'Time-Series Trends',granger:'Granger Causality Test'};
  document.getElementById('view-title').textContent=titles[v];
  if(v==='trends') buildTrendCharts();
  if(v==='granger') buildGrangerView();
}

function buildSidebarPills(){
  const el=document.getElementById('sidebar-pills');
  el.innerHTML='';
  DATA.commodities.forEach(c=>{
    const d=document.createElement('div');
    d.className='cpill';
    d.textContent=c;
    d.onclick=()=>selectComm(c);
    el.appendChild(d);
  });
}

function selectComm(c){
  currentComm=c;
  document.querySelectorAll('.content').forEach(el=>el.classList.remove('active'));
  document.getElementById('view-commodity').classList.add('active');
  document.querySelectorAll('.nav-item').forEach(el=>el.classList.remove('active'));
  document.querySelectorAll('.cpill,.comm-btn').forEach(el=>{
    el.classList.toggle('active', el.textContent===c);
  });
  document.getElementById('view-title').textContent=`${currentComm} Commodity Analysis`;
  buildCommodityView();
}


async function init(){
  try{
    setLoading(true);
    await loadDashboardData();
    buildSidebarPills();
    buildOverview();
    buildMarginView();
  }catch(error){
    console.error(error);
    showError(`Failed to load dashboard data. ${error.message}`);
  }finally{
    setLoading(false);
  }
}
window.addEventListener('DOMContentLoaded', init);
