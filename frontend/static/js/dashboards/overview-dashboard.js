function buildOverview(){
  const comms=DATA.commodities;
  const margins=comms.map(c=>DATA.margin[c].avg_margin);
  const shares=comms.map(c=>DATA.margin[c].avg_farmers_share);
  const significantCount=comms.filter(c=>significant(DATA.granger[c])).length;
  const highest=comms.reduce((best,c)=>DATA.margin[c].avg_margin > DATA.margin[best].avg_margin ? c : best, comms[0]);

  document.getElementById('overview-metrics').innerHTML=`
    <div class="metric-card amber"><div class="metric-label">Avg Marketing Margin</div><div class="metric-value">${peso(avg(margins))}</div><div class="metric-sub">Retail minus farmgate</div></div>
    <div class="metric-card blue"><div class="metric-label">Avg Farmer's Share</div><div class="metric-value">${pct(avg(shares))}</div><div class="metric-sub">Of retail price</div></div>
    <div class="metric-card green"><div class="metric-label">Granger Significant</div><div class="metric-value">${significantCount} / ${comms.length}</div><div class="metric-sub">p &lt; 0.05</div></div>
    <div class="metric-card red"><div class="metric-label">Highest Margin</div><div class="metric-value">${peso(DATA.margin[highest].avg_margin)}</div><div class="metric-sub">${highest} average</div></div>`;

  destroyChart('marginBarChart');
  charts.marginBarChart=new Chart(document.getElementById('marginBarChart'),{
    type:'bar',
    data:{labels:comms,datasets:[{label:'Avg Margin',data:margins,backgroundColor:comms.map(c=>COLORS[c]+'bb'),borderColor:comms.map(c=>COLORS[c]),borderWidth:1}]},
    options:chartBase({plugins:{legend:{display:false}},scales:{y:{grid:{color:GRID},ticks:{color:AXIS,callback:v=>'PHP '+v}},x:{grid:{display:false},ticks:{color:AXIS}}}})
  });
  destroyChart('shareBarChart');
  charts.shareBarChart=new Chart(document.getElementById('shareBarChart'),{
    type:'bar',
    data:{labels:comms,datasets:[{label:"Farmer's Share",data:shares,backgroundColor:comms.map(c=>COLORS[c]+'88'),borderColor:comms.map(c=>COLORS[c]),borderWidth:1}]},
    options:chartBase({plugins:{legend:{display:false}},scales:{y:{max:100,grid:{color:GRID},ticks:{color:AXIS,callback:v=>v+'%'}},x:{grid:{display:false},ticks:{color:AXIS}}}})
  });

  const el=document.getElementById('granger-overview-list');
  el.innerHTML='';
  comms.forEach(c=>{
    const g=DATA.granger[c];
    const p=minP(g);
    const sig=significant(g);
    const width=Math.max(2,Math.min(100,(1-p)*100));
    el.innerHTML+=`<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid #e7eee2">
      <span style="width:90px;font-size:13px;color:var(--text);font-weight:600">${c}</span>
      <span class="badge ${sig?'sig':'nosig'}">${sig?'p < 0.05':'p >= 0.05'}</span>
      <div style="flex:1;background:#edf2e8;border-radius:4px;height:8px"><div style="width:${width.toFixed(1)}%;height:8px;border-radius:4px;background:${sig?'var(--green)':'#9aa794'}"></div></div>
      <span style="font-family:'Manrope',sans-serif;font-size:12px;color:${sig?'var(--green)':'var(--muted)'};min-width:68px;text-align:right">p=${Number(p).toFixed(4)}</span>
      <span style="font-size:11px;color:var(--muted);max-width:220px">${g.interpretation || ''}</span>
    </div>`;
  });
}
