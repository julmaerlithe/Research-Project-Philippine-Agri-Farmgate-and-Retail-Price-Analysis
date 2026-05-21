function buildCommodityView(){
  if(!currentComm || !DATA.margin[currentComm]) return;
  const d=DATA.margin[currentComm];
  const g=DATA.granger[currentComm] || {};
  const monthly=d.monthly || [];
  const yearly=DATA.yearly[currentComm] || [];
  const labels=monthly.map(m=>m.date);
  const p=minP(g);
  const sig=significant(g);
  const col=COLORS[currentComm] || '#4d8a35';

  document.getElementById('commodity-price-title').textContent=`${currentComm} Price Movement`;
  document.getElementById('commodity-metrics').innerHTML=`
    <div class="metric-card amber"><div class="metric-label">Avg Marketing Margin</div><div class="metric-value">${peso(d.avg_margin)}</div><div class="metric-sub">${peso(d.min_margin)} to ${peso(d.max_margin)}</div></div>
    <div class="metric-card blue"><div class="metric-label">Avg Retail</div><div class="metric-value">${peso(d.avg_retail)}</div><div class="metric-sub">Per kg, 2021-2025</div></div>
    <div class="metric-card green"><div class="metric-label">Farmer's Share</div><div class="metric-value">${pct(d.avg_farmers_share)}</div><div class="metric-sub">Farmgate / retail price</div></div>
    <div class="metric-card ${sig?'green':'red'}"><div class="metric-label">Granger Result</div><div class="metric-value">p=${Number(p).toFixed(4)}</div><div class="metric-sub">${sig?'Significant':'Not significant'}</div></div>`;

  destroyChart('commodityPriceChart');
  charts.commodityPriceChart=new Chart(document.getElementById('commodityPriceChart'),{
    type:'line',
    data:{labels,datasets:[
      {label:'Retail',data:monthly.map(m=>m.retail),borderColor:'#2f6690',backgroundColor:'rgba(47,102,144,0.08)',fill:true,tension:.3,pointRadius:0,borderWidth:2},
      {label:'Farmgate',data:monthly.map(m=>m.farmgate),borderColor:col,backgroundColor:'transparent',fill:false,tension:.3,pointRadius:0,borderWidth:2,borderDash:[6,3]}
    ]},
    options:chartBase({interaction:{mode:'index',intersect:false},scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS,maxTicksLimit:12,autoSkip:true}}}})
  });

  destroyChart('commodityMarginChart');
  charts.commodityMarginChart=new Chart(document.getElementById('commodityMarginChart'),{
    type:'line',
    data:{labels,datasets:[{label:'Marketing Margin',data:monthly.map(m=>m.margin),borderColor:'#d97924',backgroundColor:'rgba(217,121,36,0.16)',fill:true,tension:.3,pointRadius:0,borderWidth:2}]},
    options:chartBase({plugins:{legend:{display:false}},scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS,maxTicksLimit:10,autoSkip:true}}}})
  });

  destroyChart('commodityTrendChart');
  charts.commodityTrendChart=new Chart(document.getElementById('commodityTrendChart'),{
    type:'bar',
    data:{labels:yearly.map(y=>y.year),datasets:[
      {label:'Farmgate',data:yearly.map(y=>y.farmgate),backgroundColor:col+'99',borderColor:col,borderWidth:1},
      {label:'Retail',data:yearly.map(y=>y.retail),backgroundColor:'rgba(47,102,144,0.48)',borderColor:'#2f6690',borderWidth:1},
      {label:'Margin',data:yearly.map(y=>y.margin),backgroundColor:'rgba(217,121,36,0.45)',borderColor:'#d97924',borderWidth:1}
    ]},
    options:chartBase({scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS}}}})
  });

  const pEntries=Object.entries(g.p_values || {});
  destroyChart('commodityGrangerChart');
  charts.commodityGrangerChart=new Chart(document.getElementById('commodityGrangerChart'),{
    type:'bar',
    data:{labels:pEntries.map(([lag])=>`Lag ${lag}`),datasets:[
      {label:'p-value',data:pEntries.map(([,value])=>Number(value)),backgroundColor:pEntries.map(([,value])=>Number(value)<0.05?'rgba(47,125,50,.62)':'rgba(180,35,24,.44)'),borderColor:pEntries.map(([,value])=>Number(value)<0.05?'#2f7d32':'#b42318'),borderWidth:1},
      {label:'p=0.05',data:pEntries.map(()=>0.05),type:'line',borderColor:'#b42318',borderWidth:1.5,borderDash:[4,4],pointRadius:0,fill:false}
    ]},
    options:chartBase({scales:{y:{min:0,max:1,grid:{color:GRID},ticks:{color:AXIS,callback:v=>Number(v).toFixed(2)}},x:{grid:{display:false},ticks:{color:AXIS}}}})
  });
  document.getElementById('commodity-granger-text').innerHTML =
    `<strong>${sig?'Significant':'Not significant'}:</strong> ${g.interpretation || 'No Granger interpretation available.'} Minimum p-value is ${Number(p).toFixed(4)}.`;
}
