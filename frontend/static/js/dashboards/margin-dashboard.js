function buildMarginCommSelector(){
  const el=document.getElementById('margin-comm-sel');
  el.innerHTML='';
  DATA.commodities.forEach(c=>{
    const b=document.createElement('button');
    b.className='comm-btn'+(c===currentComm?' active':'');
    b.textContent=c;
    b.onclick=()=>selectComm(c);
    el.appendChild(b);
  });
}

function buildMarginView(){
  if(!currentComm) return;
  const d=DATA.margin[currentComm];
  const g=DATA.granger[currentComm];
  buildMarginCommSelector();
  document.getElementById('margin-chart-title').textContent=`${currentComm} - Monthly Farmgate vs Retail`;
  document.getElementById('margin-metrics').innerHTML=`
    <div class="metric-card blue"><div class="metric-label">Avg Farmgate</div><div class="metric-value">${peso(d.avg_farmgate)}</div><div class="metric-sub">Per kg, 2021-2025</div></div>
    <div class="metric-card red"><div class="metric-label">Avg Retail</div><div class="metric-value">${peso(d.avg_retail)}</div><div class="metric-sub">Per kg, 2021-2025</div></div>
    <div class="metric-card amber"><div class="metric-label">Avg Margin</div><div class="metric-value">${peso(d.avg_margin)}</div><div class="metric-sub">${peso(d.min_margin)} to ${peso(d.max_margin)}</div></div>
    <div class="metric-card ${d.avg_farmers_share>40?'green':'red'}"><div class="metric-label">Farmer's Share</div><div class="metric-value">${pct(d.avg_farmers_share)}</div><div class="metric-sub">${significant(g)?'Granger significant':'No significant transmission'}</div></div>`;

  const labels=d.monthly.map(m=>m.date);
  const fg=d.monthly.map(m=>m.farmgate);
  const rt=d.monthly.map(m=>m.retail);
  const mg=d.monthly.map(m=>m.margin);
  const sh=d.monthly.map(m=>m.farmers_share);
  const col=COLORS[currentComm] || '#4d8a35';

  destroyChart('marginLineChart');
  charts.marginLineChart=new Chart(document.getElementById('marginLineChart'),{
    type:'line',
    data:{labels,datasets:[
      {label:'Retail',data:rt,borderColor:'#2f6690',backgroundColor:'rgba(47,102,144,0.08)',fill:true,tension:.3,pointRadius:0,borderWidth:2},
      {label:'Farmgate',data:fg,borderColor:col,backgroundColor:'transparent',fill:false,tension:.3,pointRadius:0,borderWidth:2,borderDash:[6,3]}
    ]},
    options:chartBase({interaction:{mode:'index',intersect:false},scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS,maxTicksLimit:12,autoSkip:true}}}})
  });
  destroyChart('marginGapChart');
  charts.marginGapChart=new Chart(document.getElementById('marginGapChart'),{
    type:'line',
    data:{labels,datasets:[{label:'Margin',data:mg,borderColor:'#d97924',backgroundColor:'rgba(217,121,36,0.16)',fill:true,tension:.3,pointRadius:0,borderWidth:2}]},
    options:chartBase({plugins:{legend:{display:false}},scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS,maxTicksLimit:10,autoSkip:true}}}})
  });
  destroyChart('shareLineChart');
  charts.shareLineChart=new Chart(document.getElementById('shareLineChart'),{
    type:'line',
    data:{labels,datasets:[{label:"Farmer's Share",data:sh,borderColor:'#2f7d32',backgroundColor:'rgba(47,125,50,0.12)',fill:true,tension:.3,pointRadius:0,borderWidth:2}]},
    options:chartBase({plugins:{legend:{display:false}},scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>v+'%'}},x:{grid:{display:false},ticks:{color:AXIS,maxTicksLimit:10,autoSkip:true}}}})
  });
  const yd=DATA.yearly[currentComm] || [];
  destroyChart('yearlyBarChart');
  charts.yearlyBarChart=new Chart(document.getElementById('yearlyBarChart'),{
    type:'bar',
    data:{labels:yd.map(y=>y.year),datasets:[
      {label:'Farmgate',data:yd.map(y=>y.farmgate),backgroundColor:col+'99',borderColor:col,borderWidth:1},
      {label:'Retail',data:yd.map(y=>y.retail),backgroundColor:'rgba(47,102,144,0.48)',borderColor:'#2f6690',borderWidth:1}
    ]},
    options:chartBase({scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS}}}})
  });
}
