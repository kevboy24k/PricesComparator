const API='api/';
const FALLBACK_IMAGE='https://placehold.co/480x360/e8f0ff/21457a?text=Producto';
const $=s=>document.querySelector(s);
const money=v=>v?new Intl.NumberFormat('es-GT',{style:'currency',currency:'GTQ',maximumFractionDigits:0}).format(v):'—';
let latestSearch=0;

document.head.insertAdjacentHTML('beforeend','<style>.search-loading{display:flex;align-items:center;gap:9px;margin-top:12px;color:#3867f4;font-size:13px;font-weight:700}.search-loading.hidden{display:none}.search-spinner{width:18px;height:18px;border:3px solid #cbd8ff;border-top-color:#3867f4;border-radius:50%;animation:search-spin .7s linear infinite}@keyframes search-spin{to{transform:rotate(360deg)}}.search button:disabled{cursor:wait;opacity:.72}.offer-thumbnail{width:58px;height:58px;flex:0 0 58px;object-fit:contain;background:#eef3ff;border-radius:6px}.offer-info{flex:1;min-width:0}</style>');
$('#search-form').insertAdjacentHTML('afterend','<div id="search-loading" class="search-loading hidden" role="status" aria-live="polite"><span class="search-spinner" aria-hidden="true"></span><span>Buscando y comparando precios...</span></div>');
$('#resultados')||Object.assign(document.querySelector('.results-section'),{id:'resultados',tabIndex:-1});
$('#search-form button').type='submit';

async function get(path){const r=await fetch(API+path);const j=await r.json();if(!j.success)throw Error(j.message);return j.data}

function setSearchLoading(active){
 const status=$('#search-loading'),button=$('#search-form button[type="submit"]');
 status.classList.toggle('hidden',!active);
 button.disabled=active;
 $('#search-form').setAttribute('aria-busy',String(active));
}

function focusResults(){
 const section=$('#resultados');
 section.scrollIntoView({behavior:'smooth',block:'start'});
 section.focus({preventScroll:true});
}

async function loadProducts(q='',options={}){
 const query=q.trim(),shouldFocus=Boolean(options.focusWhenDone),requestId=++latestSearch,box=$('#results');
 setSearchLoading(Boolean(query));
 box.setAttribute('aria-busy','true');
 box.innerHTML='<div class="loading">Buscando precios...</div>';
 try{
  const data=await get('productos'+(query?'?q='+encodeURIComponent(query):''));
  if(requestId!==latestSearch)return;
  $('#results-title').textContent=query?`Resultados para “${query}”`:'Productos destacados';
  box.innerHTML=data.length?data.map(p=>`<article class="product-card"><img class="product-image" src="${p.imagen||FALLBACK_IMAGE}" alt="${p.nombre}"><div class="product-body"><h3>${p.nombre}</h3><p>${p.marca||''} · ${p.categoria||''}</p><div class="product-meta"><div><div class="price">${money(p.precio_minimo)}</div><div class="stores">${p.tiendas||0} tiendas comparadas</div></div></div><button class="card-button" onclick="showDetail(${p.idproducto})">Comparar precios ↗</button></div></article>`).join(''):'<div class="loading">No encontramos productos con ese término.</div>';
 }catch(e){
  if(requestId!==latestSearch)return;
  box.innerHTML='<div class="loading">No se pudo conectar con la API. Verifica la configuración de la base de datos.</div>';
 }finally{
  if(requestId!==latestSearch)return;
  box.setAttribute('aria-busy','false');
  setSearchLoading(false);
  if(shouldFocus)focusResults();
 }
}

async function showDetail(id){const d=$('#detail');d.classList.remove('hidden');d.scrollIntoView({behavior:'smooth'});d.innerHTML='<div class="loading">Cargando detalle...</div>';try{const p=await get('productos/'+id),h=await get('productos/'+id+'/historial');d.innerHTML=`<div class="detail-grid"><div><p class="eyebrow">DETALLE DEL PRODUCTO</p><h2>${p.nombre}</h2><p class="lede">${p.descripcion||''}</p><div class="specs">${(p.especificaciones||[]).map(s=>`<span class="spec"><b>${s.atributo}:</b> ${s.valor}</span>`).join('')}</div></div><div><p class="eyebrow">COMPARACIÓN EN TIENDAS</p><div class="offers">${p.tiendas.map(o=>`<div class="offer"><img class="offer-thumbnail" src="${o.imagen||p.imagen||FALLBACK_IMAGE}" alt="Miniatura de ${p.nombre}"><div class="offer-info"><b>${o.tienda}</b><br><small>${o.disponibilidad?'Disponible':'Agotado'} · actualizado ${o.actualizado?new Date(o.actualizado).toLocaleDateString('es-GT'):''}</small></div><strong>${money(o.precio)}</strong><a href="${o.url}" target="_blank" rel="noopener">Ver oferta</a></div>`).join('')}</div><canvas id="history-chart" height="110"></canvas></div></div>`;new Chart($('#history-chart'),{type:'line',data:{labels:h.map(x=>x.fecha),datasets:[{label:'Precio GTQ',data:h.map(x=>x.precio),borderColor:'#3867f4',backgroundColor:'#3867f422',fill:true,tension:.35}]},options:{plugins:{legend:{display:false}},scales:{y:{ticks:{callback:v=>'Q '+v}}}}})}catch(e){d.innerHTML='<div class="loading">No se pudo cargar el detalle.</div>'}}

$('#search-form').addEventListener('submit',e=>{e.preventDefault();loadProducts($('#search').value,{focusWhenDone:true})});
document.querySelectorAll('[data-query]').forEach(b=>b.onclick=()=>{$('#search').value=b.dataset.query;loadProducts(b.dataset.query,{focusWhenDone:true})});
$('#sort').addEventListener('change',()=>loadProducts($('#search').value.trim()));
get('categorias').then(cs=>$('#category-list').innerHTML=cs.map(c=>`<button onclick="document.querySelector('#search').value='${c.nombre}';loadProducts('${c.nombre}',{focusWhenDone:true})">${c.nombre}</button>`).join('')).catch(()=>{});
loadProducts();
