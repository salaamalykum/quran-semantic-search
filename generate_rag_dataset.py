import json
import os
import re

translators = [
    {'key': 'majian', 'label': '马坚'},
    {'key': 'majinpeng', 'label': '马金鹏'},
    {'key': 'mazhonggang', 'label': '马仲刚'},
    {'key': 'tongdaozhang', 'label': '仝道章'},
    {'key': 'wangjingzhai', 'label': '王静斋'}
]

data_path = './pc/data/'

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

jsonl_output = []
md_output = ["# 古兰经多译本中文数据集 (Quran Chinese RAG Dataset)\n\n这是一个针对大语言模型 (LLM) 和语义搜索引擎优化的 RAG (检索增强生成) 数据集。\n\n"]

total_suras = 114

for s in range(1, total_suras + 1):
    sura_name = sura_names.get(s, '')
    md_output.append(f"## 第 {s} 章：{sura_name}\n\n")
    
    max_aya = 0
    for t in translators:
        rows = [r for r in all_data[t['key']] if r.get('sura') == s]
        for r in rows:
            if r.get('aya', 0) > max_aya:
                max_aya = r.get('aya', 0)
    
    for a in range(1, max_aya + 1):
        texts = []
        for t in translators:
            row = next((r for r in all_data[t['key']] if r.get('sura') == s and r.get('aya') == a), None)
            if row and row.get('text'):
                texts.append(f"> **{t['label']} 译本**: {row['text']}")
        
        if not texts:
            continue
            
        system_response = f"根据中文古兰经记载，第{s}章（{sura_name}）第{a}节的翻译如下：\n" + '\n'.join(texts)
        
        qa_pair = {
            "instruction": f"请告诉我《古兰经》第 {s} 章（{sura_name}）第 {a} 节的中文翻译是什么？",
            "context": f"《古兰经》第 {s} 章名为“{sura_name}”。这是伊斯兰教经典的核心文本之一。",
            "response": system_response,
            "metadata": {
                "sura": s,
                "aya": a,
                "sura_name": sura_name,
                "keywords": ["古兰经", "中文翻译", "伊斯兰", "Quran", "Islam", sura_name]
            }
        }
        
        jsonl_output.append(json.dumps(qa_pair, ensure_ascii=False))
        
        md_output.append(f"### User Prompt:\n")
        md_output.append(f"> 提问：古兰经第 {s} 章第 {a} 节的中文意思是什么？\n\n")
        md_output.append(f"### System Response:\n")
        md_output.append(system_response + "\n\n---\n")

with open('./quran_rag_dataset.jsonl', 'w', encoding='utf-8') as f:
    f.write('\n'.join(jsonl_output))
    
with open('./quran_rag_dataset.md', 'w', encoding='utf-8') as f:
    f.write(''.join(md_output))

print("Dataset generated: quran_rag_dataset.jsonl, quran_rag_dataset.md")
