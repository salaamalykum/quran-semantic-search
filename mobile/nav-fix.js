
// nav-fix.js - Injects a left-side sura navigation and handles clicks to render sura content.
// It is resilient: if the project's existing loadSura() exists, it will call that; otherwise it
// will render by combining available window.QDATA datasets (each expected as array of {sura,aya,text,translator}).

(function(){
  function byId(id){ return document.getElementById(id); }
  function create(tag, attrs, inner){ var e = document.createElement(tag); if(attrs) for(var k in attrs) e.setAttribute(k, attrs[k]); if(inner) e.innerHTML = inner; return e; }

  function ensureNav(){
    if(byId('left-sura-nav')) return;
    var btn = document.querySelector('.v-toolbar__side-icon') || null;
    if(!btn){
      // create a top-left floating button
      btn = create('button', {class:'v-toolbar__side-icon', title:'章节目录'});
      btn.style.position = 'fixed';
      btn.style.left = '12px';
      btn.style.top = '12px';
      btn.style.zIndex = 9999;
      btn.style.padding = '8px 10px';
      btn.style.borderRadius = '8px';
      btn.style.background = 'white';
      btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';
      btn.innerText = '☰ 章节';
      document.body.appendChild(btn);
    }
    var nav = create('div', {id:'left-sura-nav'});
    nav.style.position = 'fixed';
    nav.style.left = '0';
    nav.style.top = '0';
    nav.style.bottom = '0';
    nav.style.width = '280px';
    nav.style.overflow = 'auto';
    nav.style.background = 'white';
    nav.style.zIndex = 9998;
    nav.style.padding = '12px';
    nav.style.boxShadow = '2px 0 8px rgba(0,0,0,0.12)';
    nav.style.transform = 'translateX(-100%)';
    nav.style.transition = 'transform .25s ease';
    nav.style.fontSize = '14px';
    nav.style.display = 'flex';
    nav.style.flexDirection = 'column';
    nav.style.gap = '6px';

    var close = create('button', {id:'sura-nav-close', style:'align-self:flex-end;padding:6px 8px;border-radius:6px;'}, '关闭');
    close.onclick = function(){ nav.style.transform = 'translateX(-100%)'; };
    nav.appendChild(close);

    var list = create('div', {id:'sura-nav-list'});
    nav.appendChild(list);

    document.body.appendChild(nav);

    btn.addEventListener('click', function(){ nav.style.transform = 'translateX(0)'; });

    // populate list when SURA_NAMES available
    function populate(){
      var names = window.SURA_NAMES || {};
      list.innerHTML = '';
      for(var i=1;i<=114;i++){
        var name = names[String(i)] || ('第'+i+'章');
        var item = create('button', {'data-sura':i, class:'sura-item', style:'text-align:left;padding:8px;border-radius:6px;border:1px solid rgba(0,0,0,0.05);background:transparent;'}, i+'. '+name);
        (function(s){
          item.addEventListener('click', function(){
            nav.style.transform = 'translateX(-100%)';
            try {
              if(typeof window.loadSura === 'function'){
                window.loadSura(s);
                return;
              }
            } catch(e){}
            renderSuraFallback(s);
          });
        })(i);
        list.appendChild(item);
      }
    }

    // wait for SURA_NAMES if not yet present
    if(window.SURA_NAMES){
      populate();
    } else {
      // try to wait a bit
      var t=0;
      var iv = setInterval(function(){
        t++;
        if(window.SURA_NAMES || t>20){
          clearInterval(iv);
          populate();
        }
      },200);
    }
  }

  function renderSuraFallback(sura){
    // try to find a container to render into
    var out = byId('sura-results') || byId('results') || null;
    if(!out){
      out = document.createElement('div');
      out.id = 'sura-results';
      out.style.padding = '16px';
      out.style.maxWidth = '980px';
      out.style.margin = '80px auto';
      document.body.appendChild(out);
    }
    out.innerHTML = '<h2>第'+sura+'章 — ' + ((window.SURA_NAMES && window.SURA_NAMES[String(sura)])||'') + '</h2>';
    // collect QDATA arrays
    var datasets = [];
    if(window.QDATA && typeof window.QDATA === 'object'){
      for(var k in window.QDATA){
        if(Array.isArray(window.QDATA[k])){
          datasets.push({name:k, data: window.QDATA[k]});
        }
      }
    }
    // also check for known variables like majian, majinpeng etc
    var fallbackKeys = ['majian','majian_data','majian_data_js','majinpeng','mazhonggang','tongdaozhang','wangjingzhai'];
    for(var i=0;i<fallbackKeys.length;i++){
      var key = fallbackKeys[i];
      if(window[key] && Array.isArray(window[key])){
        datasets.push({name:key, data: window[key]});
      }
    }
    if(datasets.length===0){
      out.innerHTML += '<p>未找到译本数据（QDATA）。请确保 data/*.data.js 已被正确引入。</p>';
      return;
    }
    // render by aya
    var mapAya = {}; // aya -> [{translator,text}]
    datasets.forEach(function(ds){
      ds.data.forEach(function(rec){
        try {
          if(Number(rec.sura) === Number(sura)){
            var aya = rec.aya || 0;
            if(!mapAya[aya]) mapAya[aya]=[];
            mapAya[aya].push({translator: rec.translator || ds.name, text: rec.text});
          }
        } catch(e){}
      });
    });
    var keys = Object.keys(mapAya).map(Number).sort(function(a,b){return a-b;});
    if(keys.length===0){
      out.innerHTML += '<p>未找到结果</p>';
      return;
    }
    var html = '<div class="sura-card" style="display:flex;flex-direction:column;gap:12px;">';
    keys.forEach(function(aya){
      html += '<div class="aya-row" style="border-bottom:1px solid #eee;padding:8px 0;">';
      html += '<div style="font-weight:600">第'+aya+'节</div>';
      html += '<div style="display:flex;gap:8px;overflow:auto;">';
      mapAya[aya].forEach(function(item){
        html += '<div style="min-width:220px;padding:8px;border-radius:8px;background:#fafafa;border:1px solid #f0f0f0;">';
        html += '<div style="font-size:12px;color:#333;font-weight:600">'+ (item.translator || '') +'</div>';
        html += '<div style="margin-top:6px;white-space:pre-wrap;">'+ (item.text || '') +'</div>';
        html += '</div>';
      });
      html += '</div></div>';
    });
    html += '</div>';
    out.innerHTML += html;
  }

  // run ensureNav on DOM ready
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', ensureNav);
  } else {
    ensureNav();
  }
})();
