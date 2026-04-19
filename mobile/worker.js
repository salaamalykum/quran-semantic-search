// worker.js - search worker for mobile app
// Accepts: { type:'search', payload: { query, datasets, suraNames } }
// Sends progress: { type:'progress', payload:{ loaded, total } }
// Sends done: { type:'done', payload:{ records, query, suraNames } }
// Sends error: { type:'error', payload: message }

function parseQuery(q){
  q = (q||'').trim();
  if(/^\/.+\/[a-z]*$/i.test(q)){
    const m = q.match(/^\/(.+)\/([a-z]*)$/i);
    try{
      return { type: 'regex', re: new RegExp(m[1], m[2]) };
    }catch(e){
      return { type:'invalid', message: '非法正则表达式' };
    }
  }
  const toks = q.split(/\s+/).filter(Boolean);
  return { type: 'tokens', tokens: toks };
}

function escapeHtml(s){
  return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function highlightTextEscaped(escapedText, qobj){
  if(!qobj) return escapedText;
  if(qobj.type === 'regex'){
    try{
      return escapedText.replace(qobj.re, function(m){ return '<mark class="hl">'+m+'</mark>'; });
    }catch(e){
      return escapedText;
    }
  }else if(qobj.type === 'tokens'){
    // iterate tokens and replace (case-insensitive)
    let out = escapedText;
    for(const tok of qobj.tokens){
      if(!tok) continue;
      // escape regex metachars in token for literal search
      const re = new RegExp(tok.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'), 'gi');
      out = out.replace(re, function(m){ return '<mark class="hl">'+m+'</mark>'; });
    }
    return out;
  }
  return escapedText;
}

onmessage = function(ev){
  const { type, payload } = ev.data || {};
  if(type !== 'search' || !payload) {
    postMessage({ type:'error', payload: 'invalid message' });
    return;
  }
  try{
    const q = String(payload.query || '').trim();
    const datasets = Array.isArray(payload.datasets) ? payload.datasets : [];
    const suraNames = payload.suraNames || {};
    const qobj = parseQuery(q);
    if(qobj.type === 'invalid'){ postMessage({ type:'error', payload: qobj.message }); return; }
    const out = [];
    // compute total items for progress
    let total = 0;
    for(const ds of datasets){ total += (ds.data && ds.data.length) || 0; }
    let loaded = 0;
    // iterate datasets
    for(const ds of datasets){
      const dsName = ds.name || ds.key || '译本';
      const arr = Array.isArray(ds.data) ? ds.data : [];
      for(const rec of arr){
        loaded++;
        if(loaded % 200 === 0){ postMessage({ type:'progress', payload:{ loaded, total } }); }
        const text = String(rec.text || '');
        const textLower = text.toLowerCase();
        let matched = false;
        if(qobj.type === 'regex'){
          try{
            matched = qobj.re.test(text);
          }catch(e){
            matched = false;
          }
        }else if(qobj.type === 'tokens'){
          // AND search: all tokens must appear
          matched = true;
          for(const tok of qobj.tokens){
            if(!tok) { matched = false; break; }
            if(textLower.indexOf(tok.toLowerCase()) === -1){
              matched = false; break;
            }
          }
        }else{
          // empty query should not happen; skip
          matched = false;
        }
        if(matched){
          const escaped = escapeHtml(text);
          const highlighted = highlightTextEscaped(escaped, qobj);
          out.push({
            sura: rec.sura,
            aya: rec.aya,
            translator: rec.translator || dsName,
            highlighted: highlighted,
            text: rec.text
          });
        }
      }
    }
    postMessage({ type:'done', payload:{ records: out, query: q, suraNames } });
  }catch(err){
    postMessage({ type:'error', payload: String(err && err.message ? err.message : err) });
  }
};
