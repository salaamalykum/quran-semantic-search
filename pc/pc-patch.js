(function(){
  try{
    // Use window.SURA_NAMES if available (sura-names.js), otherwise try to load sura-names.js dynamically.
    function applyNames(names){
      if(!names) return;
      const candidates = document.querySelectorAll('[data-sura], .sura, .sura-item, nav a');
      candidates.forEach(el=>{
        let n = el.getAttribute('data-sura') || el.dataset.sura;
        if(!n){
          const m = (el.textContent||'').match(/^\s*(\d{1,3})\s*$/);
          if(m) n = m[1];
        }
        if(n && names[String(n)]){
          if(!/第\s*\d+\s*章/.test(el.textContent)){
            el.textContent = `第 ${n} 章 ${names[String(n)]}`;
          }
        }
      });
    }
    if(window.SURA_NAMES){
      applyNames(window.SURA_NAMES);
    }else{
      // try to load sura-names.js
      var s = document.createElement('script');
      s.src = './sura-names.js';
      s.onload = function(){ applyNames(window.SURA_NAMES || {}); };
      s.onerror = function(){ console.warn('pc-patch: failed to load sura-names.js'); };
      document.head.appendChild(s);
    }
  }catch(e){
    console.warn('pc-patch failed:', e);
  }
})();