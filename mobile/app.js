
// Mobile App Logic - Optimized for Offline & Performance & Compatibility
(function () {
  // Strict check for QDATA
  window.QDATA = window.QDATA || {};

  const TRANSLATORS = [
    { key: 'mazhonggang', name: '马仲刚' },
    { key: 'majinpeng', name: '马金鹏' },
    { key: 'tongdaozhang', name: '仝道章' },
    { key: 'wangjingzhai', name: '王静斋' },
    { key: 'majian', name: '马坚' },
  ];

  const STATE = {
    filters: new Set(TRANSLATORS.map(function (t) { return t.key; })),
    suraNames: window.SURA_NAMES || {},
    activeSura: null,
    query: '',
    regexMode: false,
  };

  const $ = function (sel) { return document.querySelector(sel); };
  const $$ = function (sel) { return Array.from(document.querySelectorAll(sel)); };

  // --- UI Helpers ---
  function toggleDrawer(open) {
    const d = $('#drawer');
    if (!d) return;
    // Use both attribute and class for maximum compatibility
    if (open) {
      d.setAttribute('aria-hidden', 'false');
      d.classList.add('open');
    } else {
      d.setAttribute('aria-hidden', 'true');
      d.classList.remove('open');
    }
  }

  function showLoading(show) {
    const loader = $('#loading');
    if (!loader) return;

    // Use classList for visibility (checked against styles.css)
    if (show) {
      loader.classList.add('active');
      loader.style.display = 'flex'; // Force display if class fails
    } else {
      loader.classList.remove('active');
      loader.style.display = 'none'; // Force hide
    }

    if (show) {
      const res = $('#results');
      if (res) res.innerHTML = '';
      const nores = $('#noresults');
      if (nores) nores.hidden = true;
    }
  }

  // --- Theme ---
  function initTheme() {
    try {
      const saved = localStorage.getItem('theme') || 'light';
      document.documentElement.setAttribute('data-theme', saved);
      updateThemeIcon(saved);
    } catch (e) { console.error(e); }
  }

  function toggleTheme() {
    try {
      const current = document.documentElement.getAttribute('data-theme') || 'light';
      const next = current === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      updateThemeIcon(next);
    } catch (e) { console.error(e); }
  }

  function updateThemeIcon(theme) {
    const btn = $('#btn-theme');
    if (btn) btn.textContent = theme === 'light' ? '🌙' : '☀️';
  }

  // --- Data & Search Logic ---
  function getFilteredData(sura) {
    const keys = Array.from(STATE.filters);
    const map = new Map();

    for (const k of keys) {
      const list = (window.QDATA && window.QDATA[k]) || [];
      for (const rec of list) {
        if (rec.sura === sura) {
          if (!map.has(rec.aya)) map.set(rec.aya, {});
          map.get(rec.aya)[k] = rec.text;
        }
      }
    }
    return Array.from(map.entries()).sort(function (a, b) { return a[0] - b[0]; }).map(function (item) {
      return { aya: item[0], texts: item[1] };
    });
  }

  function escapeHtml(str) {
    return (str || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function highlight(text, query) {
    if (!query || !query.trim()) return escapeHtml(text);
    const tokens = query.split(/\s+/).filter(Boolean);
    let out = escapeHtml(text);
    for (const token of tokens) {
      const pattern = token.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const re = new RegExp('(' + pattern + ')', 'gi');
      out = out.replace(re, '<mark class="hl">$1</mark>');
    }
    return out;
  }

  // --- Rendering ---
  function renderCard(translatorKey, text, query) {
    let tObj = null;
    for (let i = 0; i < TRANSLATORS.length; i++) {
      if (TRANSLATORS[i].key === translatorKey) {
        tObj = TRANSLATORS[i];
        break;
      }
    }
    const tName = (tObj && tObj.name) ? tObj.name : translatorKey;

    return '<div class="card">' +
      '<div class="translator">' + tName + '</div>' +
      '<div class="text">' + highlight(text, query) + '</div>' +
      '</div>';
  }

  function renderRows(rows, query) {
    const container = $('#results');
    if (!container) return;

    const frag = document.createDocumentFragment();

    for (let i = 0; i < rows.length; i++) {
      const row = rows[i];
      const rowDiv = document.createElement('div');
      rowDiv.className = 'aya-row';

      const sName = (STATE.suraNames && STATE.suraNames[String(row.sura)]) || '';
      const meta = '<div class="meta"><span>' + row.sura + ':' + row.aya + '</span><span>' + sName + '</span></div>';

      const transDiv = document.createElement('div');
      transDiv.className = 'translations';

      let hasContent = false;
      for (const t of TRANSLATORS) {
        if (STATE.filters.has(t.key) && row.texts[t.key]) {
          transDiv.innerHTML += renderCard(t.key, row.texts[t.key], query);
          hasContent = true;
        }
      }

      if (hasContent) {
        rowDiv.innerHTML = meta;
        rowDiv.appendChild(transDiv);
        frag.appendChild(rowDiv);
      }
    }
    container.appendChild(frag);

    const nores = $('#noresults');
    if (nores) {
      if (container.children.length === 0) {
        nores.hidden = false;
      } else {
        nores.hidden = true;
      }
    }
  }

  function makeMatcher(query) {
    const tokens = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    if (!tokens.length) return function () { return true; };
    return function (text) {
      if (!text) return false;
      const t = text.toLowerCase();
      for (let i = 0; i < tokens.length; i++) {
        if (t.indexOf(tokens[i]) === -1) return false;
      }
      return true;
    };
  }

  function renderSura(sura) {
    STATE.activeSura = sura;
    STATE.query = '';
    showLoading(true);
    toggleDrawer(false);
    window.scrollTo({ top: 0 });

    setTimeout(function () {
      try {
        const rows = getFilteredData(sura);
        const mappedRows = rows.map(function (r) {
          return { sura: sura, aya: r.aya, texts: r.texts };
        });
        renderRows(mappedRows, null);
      } catch (e) {
        alert('Render Error: ' + e.message);
        console.error(e);
      } finally {
        showLoading(false);
      }
    }, 10);
  }

  function performSearch() {
    const qEl = $('#q');
    if (!qEl) return;
    const q = qEl.value.trim();
    if (!q) return;

    STATE.query = q;
    STATE.activeSura = null;
    showLoading(true);
    toggleDrawer(false);
    window.scrollTo({ top: 0 });

    setTimeout(function () {
      try {
        const matcher = makeMatcher(q);
        const matchedIDs = new Set();

        for (const k of STATE.filters) {
          const list = (window.QDATA && window.QDATA[k]) || [];
          for (let i = 0; i < list.length; i++) {
            if (matcher(list[i].text)) {
              matchedIDs.add(list[i].sura + ':' + list[i].aya);
            }
          }
        }

        const sortedIDs = Array.from(matchedIDs).map(function (s) {
          const parts = s.split(':');
          return { sura: Number(parts[0]), aya: Number(parts[1]), id: s };
        }).sort(function (a, b) {
          if (a.sura !== b.sura) return a.sura - b.sura;
          return a.aya - b.aya;
        });

        const finalRows = [];
        for (let i = 0; i < sortedIDs.length; i++) {
          const item = sortedIDs[i];
          const rowObj = { sura: item.sura, aya: item.aya, texts: {} };

          for (const k of STATE.filters) {
            const list = (window.QDATA && window.QDATA[k]) || [];
            for (let j = 0; j < list.length; j++) {
              if (list[j].sura === item.sura && list[j].aya === item.aya) {
                rowObj.texts[k] = list[j].text;
                break;
              }
            }
          }
          finalRows.push(rowObj);
        }

        renderRows(finalRows, q);
      } catch (e) {
        alert('Search Error: ' + e.message);
        console.error(e);
      } finally {
        showLoading(false);
      }

    }, 10);
  }

  // --- Initializer ---
  function bindUI() {
    const btnDrawer = $('#btn-drawer');
    if (btnDrawer) btnDrawer.addEventListener('click', function () { toggleDrawer(true); });

    const btnClose = $('#btn-close');
    if (btnClose) btnClose.addEventListener('click', function () { toggleDrawer(false); });

    const drawer = $('#drawer');
    if (drawer) drawer.addEventListener('click', function (e) {
      if (e.target === drawer) toggleDrawer(false);
    });

    const btnTheme = $('#btn-theme');
    if (btnTheme) btnTheme.addEventListener('click', toggleTheme);

    const btnGo = $('#go');
    if (btnGo) btnGo.addEventListener('click', performSearch);

    const inputQ = $('#q');
    if (inputQ) inputQ.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') performSearch();
    });

    // Populate Sura List
    const slist = $('#sura-list');
    if (slist) {
      const frag = document.createDocumentFragment();
      const names = STATE.suraNames || {};

      for (let i = 1; i <= 114; i++) {
        const row = document.createElement('div');
        row.className = 'sura-item';
        const n = names[String(i)] || '';
        row.innerHTML = '<div class="num">' + i + '</div><div class="name">' + n + '</div>';
        row.addEventListener('click', function () { renderSura(i); });
        frag.appendChild(row);
      }
      slist.appendChild(frag);
    }

    const checks = document.querySelectorAll('.filters input[type="checkbox"]');
    for (let i = 0; i < checks.length; i++) {
      checks[i].addEventListener('change', function (e) {
        const key = e.target.getAttribute('data-key');
        if (e.target.checked) STATE.filters.add(key);
        else STATE.filters.delete(key);

        if (STATE.activeSura) renderSura(STATE.activeSura);
        else if (STATE.query) performSearch();
      });
    }
  }

  function init() {
    initTheme();
    try {
      bindUI();
      // Auto open drawer logic - maybe nicer to keep closed on load to show clean home?
      // User complained it didn't open. Let's start closed but ensure it works.
      // setTimeout(function() { toggleDrawer(true); }, 300);
    } catch (e) {
      alert('Init Error: ' + e.message);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
