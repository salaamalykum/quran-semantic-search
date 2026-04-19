import json
import os
import re

translators = [
    {'key': 'mazhonggang', 'label': '马仲刚'},
    {'key': 'majinpeng', 'label': '马金鹏'},
    {'key': 'tongdaozhang', 'label': '仝道章'},
    {'key': 'wangjingzhai', 'label': '王静斋'},
    {'key': 'majian', 'label': '马坚'}
]

# Wiki KG Mappings
kg_map = {
    '安拉': 'https://zh.wikipedia.org/zh-hans/%E5%AE%89%E6%8B%89',
    '穆罕默德': 'https://zh.wikipedia.org/zh-hans/%E7%A9%86%E7%BD%95%E9%BB%98%E5%BE%B7',
    '古兰经': 'https://zh.wikipedia.org/zh-hans/%E5%8F%A4%E5%85%B0%E7%BB%8F',
    '麦加': 'https://zh.wikipedia.org/zh-hans/%E9%BA%A5%E5%8A%A0'
}

def inject_kg(text):
    for key, url in kg_map.items():
        # Only inject if not already part of an anchor tag
        text = re.sub(rf'(?<!<a href=")(?<!>){key}(?!</a>)', f'<a href="{url}" target="_blank" rel="noopener noreferrer" class="kg-link">{key}</a>', text)
    return text

data_path = './pc/data/'

print("Loading data...")
all_data = {}
for t in translators:
    with open(f'{data_path}{t["key"]}.json', 'r', encoding='utf-8') as f:
        all_data[t['key']] = json.load(f)

sura_names = {}
try:
    with open('./pc/sura-names.js', 'r', encoding='utf-8') as f:
        content = f.read()
        match = re.search(r'window\.SURA_NAMES\s*=\s*(\{.*?\});', content, re.DOTALL)
        if match:
            sura_names_raw = json.loads(match.group(1))
            sura_names = {int(k): v for k, v in sura_names_raw.items()}
except Exception as e:
    print(f"Error reading sura_names: {e}")

# Read templates
with open('./pc/index.html', 'r', encoding='utf-8') as f:
    pc_tpl = f.read()
with open('./mobile/index.html', 'r', encoding='utf-8') as f:
    mob_tpl = f.read()

# Make directories
os.makedirs('./pc/sura', exist_ok=True)
os.makedirs('./mobile/sura', exist_ok=True)

urls_for_sitemap = []

def generate_html(sura_id):
    sura_name = sura_names.get(sura_id, '')
    
    # Calculate max aya
    max_aya = 0
    for t in translators:
        rows = [r for r in all_data[t['key']] if r.get('sura') == sura_id]
        for r in rows:
            if r.get('aya', 0) > max_aya:
                max_aya = r.get('aya', 0)

    # 1. Generate DOM results
    pc_results_html = ""
    mob_results_html = ""
    faq_schema_items = []
    
    rag_context_content = f"<h2>《古兰经》第{sura_id}章（{sura_name}）中文翻译 RAG 语义索引库</h2>\n"

    for a in range(1, max_aya + 1):
        pc_wrapper = f'<div class="verse-row">'
        mob_wrapper = f'<div class="verse-row">'
        
        texts_for_this_aya = []
        for t in translators:
            row = next((r for r in all_data[t['key']] if r.get('sura') == sura_id and r.get('aya') == a), None)
            if row and row.get('text'):
                text = row['text']
                kg_text = inject_kg(text)
                texts_for_this_aya.append(f"{t['label']}: {text}")
                
                # PC Dom structure
                pc_wrapper += f'<div class="tcard"><div class="meta"><span>第 {sura_id}:{a}</span><span class="name">{t["label"]}</span></div><div class="text">{kg_text}</div></div>'
                # Mobile Dom structure assumes same or similar classes
                mob_wrapper += f'<div class="tcard"><div class="meta"><span>第 {sura_id}:{a}</span><span class="name">{t["label"]}</span></div><div class="text">{kg_text}</div></div>'
            else:
                pc_wrapper += f'<div class="tcard"><div class="meta"><span>第 {sura_id}:{a}</span><span class="name">{t["label"]}</span></div><div class="text">—</div></div>'
                mob_wrapper += f'<div class="tcard"><div class="meta"><span>第 {sura_id}:{a}</span><span class="name">{t["label"]}</span></div><div class="text">—</div></div>'

        pc_wrapper += '</div>'
        mob_wrapper += '</div>'
        pc_results_html += pc_wrapper
        mob_results_html += mob_wrapper
        
        if texts_for_this_aya:
            answer_text = "\n".join(texts_for_this_aya)
            # Add to FAQ Schema
            faq_schema_items.append({
                "@type": "Question",
                "name": f"《古兰经》第 {sura_id} 章第 {a} 节的中文翻译是什么？",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer_text
                }
            })
            
            # Add to RAG Context details
            rag_context_content += f"<article><h3>User Prompt: 提问：古兰经第 {sura_id} 章第 {a} 节的中文意思是什么？</h3><p><strong>System Response:</strong> 根据多版本中文古兰经记载，第{sura_id}章（{sura_name}）第{a}节的翻译如下：<br/>" + "<br/>".join(texts_for_this_aya) + "</p></article>"

    # 2. Build JSON-LD
    schema_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "FAQPage",
                "mainEntity": faq_schema_items
            },
            {
                "@type": "Article",
                "headline": f"《古兰经》第 {sura_id} 章：{sura_name} (多版本中文翻译对比)",
                "author": {"@type": "Organization", "name": "Salaam Alykum"},
                "publisher": {"@type": "Organization", "name": "Salaam Alykum"},
                "description": f"精良优化的古兰经第 {sura_id} 章 {sura_name} 中文多版本对比翻译。极其适合学术研究与LLM语义检索。"
            }
        ]
    }
    schema_script = f'<script type="application/ld+json">\n{json.dumps(schema_ld, ensure_ascii=False, indent=2)}\n</script>'
    
    # RAG Container (For Information Gain and Geo)
    rag_ui = f'''
    <details class="rag-container" style="margin:20px; padding:15px; background:var(--bg-card, #f9f9f9); border:1px solid var(--border, #eee); border-radius:8px;">
        <summary style="cursor:pointer; font-weight:bold; color:var(--primary, #2A5D34);">[+] 打开 AI & RAG 语义索引库 (LLM Dataset Context)</summary>
        <div class="rag-content" style="margin-top:15px; font-size:0.9em; line-height:1.6;">
            {rag_context_content}
        </div>
    </details>
    '''

    # Function to replace in template
    def build_html(tpl, results_html, base_level):
        # Adjust paths: since we are in /sura/, assets are in ../assets/
        html = tpl.replace('href="assets/', f'href="{base_level}assets/')
        html = html.replace('href="./assets/', f'href="{base_level}assets/')
        html = html.replace('src="assets/', f'src="{base_level}assets/')
        html = html.replace('src="./assets/', f'src="{base_level}assets/')
        html = html.replace('src="sura-names', f'src="{base_level}sura-names')
        html = html.replace('src="./sura-names', f'src="{base_level}sura-names')
        html = html.replace('src="data/', f'src="{base_level}data/')
        html = html.replace('src="./data/', f'src="{base_level}data/')
        html = html.replace('href="styles.css"', f'href="{base_level}styles.css"')
        html = html.replace('href="./styles.css"', f'href="{base_level}styles.css"')
        html = html.replace('src="app.js"', f'src="{base_level}app.js"')
        html = html.replace('src="./app.js"', f'src="{base_level}app.js"')
        html = html.replace('window.location.href = "../mobile/index.html"', 'return; /* SSR bypass */')
        html = html.replace('window.location.href = "../pc/index.html"', 'return; /* SSR bypass */')
        
        # Inject Script
        html = html.replace('</head>', schema_script + '\n</head>')
        
        # Inject Title
        html = re.sub(r'<title>.*?</title>', f'<title>第 {sura_id} 章：{sura_name} - 古兰经中文翻译搜索工具</title>', html)
        
        # Inject Results DOM
        if '<div class="results"></div>' in html:
            html = html.replace('<div class="results"></div>', f'<div class="results">{results_html}</div>{rag_ui}')
        elif '<div id="results" class="results"></div>' in html:
            html = html.replace('<div id="results" class="results"></div>', f'<div id="results" class="results">{results_html}</div>{rag_ui}')
        
        # Override active mode title
        html = html.replace('<h2 id="mode-title">请选择章节或进行搜索</h2>', f'<h2 id="mode-title">第 {sura_id} 章：{sura_name}</h2>')
        
        # Add script to set active chapter in JS
        init_script = f"<script>window.addEventListener('DOMContentLoaded', () => {{ window.location.hash = '#{sura_id}'; }});</script>"
        html = html.replace('</body>', init_script + '\n</body>')
        
        return html

    pc_html = build_html(pc_tpl, pc_results_html, '../')
    mob_html = build_html(mob_tpl, mob_results_html, '../')

    with open(f'./pc/sura/{sura_id}.html', 'w', encoding='utf-8') as f:
        f.write(pc_html)
    with open(f'./mobile/sura/{sura_id}.html', 'w', encoding='utf-8') as f:
        f.write(mob_html)
        
    urls_for_sitemap.append(f'https://salaamalykum.com/cn/qurancn/pc/sura/{sura_id}.html')
    urls_for_sitemap.append(f'https://salaamalykum.com/cn/qurancn/mobile/sura/{sura_id}.html')

print("Generating 114 SSR Pages for PC and Mobile...")
total_suras = 114
for s in range(1, total_suras + 1):
    generate_html(s)

# Create Sitemap
sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u in urls_for_sitemap:
    sitemap_xml += f'  <url>\n    <loc>{u}</loc>\n    <changefreq>weekly</changefreq>\n  </url>\n'
sitemap_xml += '</urlset>'

with open('./sitemap.xml', 'w', encoding='utf-8') as f:
    f.write(sitemap_xml)

print("SSR completely generated. sitemap.xml created.")
