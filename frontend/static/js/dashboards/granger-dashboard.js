function buildGrangerView(){
  const el=document.getElementById('granger-cards');
  el.innerHTML='';
  DATA.commodities.forEach(c=>{
    const g=DATA.granger[c];
    const pvRows=Object.entries(g.p_values || {}).map(([lag,p])=>{
      const value=Number(p);
      const sig=value<0.05;
      const barW=Math.max(2,Math.min(100,(1-value)*100));
      return `<div class="pval-row"><span class="pval-lag">Lag ${lag}</span><div class="pval-bar-wrap"><div class="pval-bar ${sig?'sig':'nosig'}" style="width:${barW}%"></div></div><span class="pval-num ${sig?'sig':'nosig'}">${value.toFixed(4)}</span></div>`;
    }).join('');
    el.innerHTML+=`<div class="granger-card">
      <div class="granger-title" style="color:${COLORS[c]}">${c} <span class="badge ${significant(g)?'sig':'nosig'}">${significant(g)?'Significant':'Not significant'}</span></div>
      <div style="font-size:11px;color:var(--muted);margin-bottom:8px">${g.interpretation || ''}</div>
      ${pvRows || '<div style="font-size:12px;color:var(--muted)">No p-values available</div>'}
    </div>`;
  });

  const comms=DATA.commodities;
  const lags=[...new Set(comms.flatMap(c=>Object.keys(DATA.granger[c]?.p_values || {})))].sort((a,b)=>Number(a)-Number(b));
  destroyChart('grangerHeatChart');
  charts.grangerHeatChart=new Chart(document.getElementById('grangerHeatChart'),{
    type:'bar',
    data:{labels:comms,datasets:lags.map((lag,index)=>({
      label:`Lag ${lag}`,
      data:comms.map(c=>DATA.granger[c]?.p_values?.[lag] ?? null),
      backgroundColor:['rgba(47,102,144,.68)','rgba(47,125,50,.58)','rgba(217,121,36,.58)'][index] || 'rgba(101,118,94,.58)',
      borderColor:['#2f6690','#2f7d32','#d97924'][index] || '#65765e',
      borderWidth:1
    }))},
    options:chartBase({scales:{y:{max:1,grid:{color:GRID},ticks:{color:AXIS,callback:v=>Number(v).toFixed(2)}},x:{grid:{display:false},ticks:{color:AXIS}}}})
  });
  charts.grangerHeatChart.data.datasets.push({label:'p=0.05',data:new Array(comms.length).fill(0.05),type:'line',borderColor:'#b42318',borderWidth:1.5,borderDash:[4,4],pointRadius:0,fill:false});
  charts.grangerHeatChart.update();

  destroyChart('scatterChart');
  const scatterData=comms.map(c=>({x:DATA.margin[c].avg_farmers_share,y:minP(DATA.granger[c]),label:c}));
  charts.scatterChart=new Chart(document.getElementById('scatterChart'),{
    type:'scatter',
    data:{datasets:[{label:'Commodities',data:scatterData,backgroundColor:comms.map(c=>COLORS[c]+'bb'),borderColor:comms.map(c=>COLORS[c]),pointRadius:8,pointHoverRadius:11}]},
    options:chartBase({
      plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>{const d=scatterData[ctx.dataIndex];return `${d.label} - Share: ${d.x.toFixed(1)}%, p: ${d.y.toFixed(4)}`;}}}},
      scales:{x:{title:{display:true,text:"Farmer's Share (%)",color:AXIS},grid:{color:GRID},ticks:{color:AXIS,callback:v=>v+'%'}},y:{title:{display:true,text:'Minimum p-value',color:AXIS},grid:{color:GRID},ticks:{color:AXIS},min:0,max:.5}}
    })
  });
  charts.scatterChart.data.datasets.push({type:'line',label:'p=0.05',data:[{x:25,y:.05},{x:55,y:.05}],borderColor:'#b42318',borderDash:[4,4],pointRadius:0,borderWidth:1.5,fill:false});
  charts.scatterChart.update();
}
