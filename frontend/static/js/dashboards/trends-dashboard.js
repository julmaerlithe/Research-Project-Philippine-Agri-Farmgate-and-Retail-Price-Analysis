function buildTrendMetrics(){
  const byYear = {};
  DATA.trends.forEach(row=>{
    const year=String(row.date).slice(0,4);
    byYear[year] ||= [];
    byYear[year].push(row.avg_margin);
  });
  const years=Object.keys(byYear).sort();
  const first=years[0], last=years[years.length-1];
  const firstAvg=avg(byYear[first] || []);
  const lastAvg=avg(byYear[last] || []);
  const peak=DATA.trends.reduce((best,row)=>row.avg_margin > best.avg_margin ? row : best, DATA.trends[0]);
  const change=firstAvg ? ((lastAvg-firstAvg)/firstAvg)*100 : 0;
  document.getElementById('trend-metrics').innerHTML=`
    <div class="metric-card blue"><div class="metric-label">${first} Avg Margin</div><div class="metric-value">${peso(firstAvg)}</div><div class="metric-sub">All commodities combined</div></div>
    <div class="metric-card amber"><div class="metric-label">${last} Avg Margin</div><div class="metric-value">${peso(lastAvg)}</div><div class="metric-sub">${change>=0?'+':''}${change.toFixed(1)}% since ${first}</div></div>
    <div class="metric-card red"><div class="metric-label">Peak Margin Month</div><div class="metric-value">${peak?.date || '-'}</div><div class="metric-sub">${peso(peak?.avg_margin)} avg across commodities</div></div>`;
}

function buildTrendCharts(){
  buildTrendMetrics();
  const labels=DATA.trends.map(t=>t.date);
  destroyChart('trendChart');
  charts.trendChart=new Chart(document.getElementById('trendChart'),{
    type:'line',
    data:{labels,datasets:[
      {label:'Avg Retail',data:DATA.trends.map(t=>t.avg_retail),borderColor:'#2f6690',backgroundColor:'rgba(47,102,144,0.08)',fill:true,tension:.3,pointRadius:0,borderWidth:2},
      {label:'Avg Farmgate',data:DATA.trends.map(t=>t.avg_farmgate),borderColor:'#2f7d32',backgroundColor:'transparent',tension:.3,pointRadius:0,borderWidth:2,borderDash:[5,3]},
      {label:'Avg Margin',data:DATA.trends.map(t=>t.avg_margin),borderColor:'#d97924',backgroundColor:'transparent',tension:.3,pointRadius:0,borderWidth:2,borderDash:[3,3]}
    ]},
    options:chartBase({interaction:{mode:'index',intersect:false},scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS,maxTicksLimit:14,autoSkip:true}}}})
  });
  const years=[...new Set(Object.values(DATA.yearly).flat().map(y=>y.year))].sort();
  destroyChart('multiCommChart');
  charts.multiCommChart=new Chart(document.getElementById('multiCommChart'),{
    type:'line',
    data:{labels:years,datasets:DATA.commodities.map(c=>({label:c,data:(DATA.yearly[c]||[]).map(y=>y.farmgate),borderColor:COLORS[c],backgroundColor:'transparent',tension:.3,pointRadius:4,borderWidth:2}))},
    options:chartBase({scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS}}}})
  });
  destroyChart('yearlyMarginChart');
  charts.yearlyMarginChart=new Chart(document.getElementById('yearlyMarginChart'),{
    type:'bar',
    data:{labels:years,datasets:DATA.commodities.map(c=>({label:c,data:(DATA.yearly[c]||[]).map(y=>y.margin),backgroundColor:COLORS[c]+'99',borderColor:COLORS[c],borderWidth:1}))},
    options:chartBase({scales:{x:{grid:{display:false},ticks:{color:AXIS}},y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}}}})
  });
}
