import os
import re
import glob
import yaml
import json

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs', '_posts')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'repos.js')

KEYWORDS = [
    'ai', 'llm', 'llms', 'large language model', 'diffusion', 'ocr', 'model', 'gemini', 'genai', 'generation', 'language model', 'agents', 'agent', 'RAG', 'unstructured data', 'structured data', 'vector', 'vectors', 'embedding', 'embeddings', 'fine-tune', 'finetune', 'fine tuning', 'fine-tuning', 'transformer', 'transformers', 'chatbot', 'chatbots', 'chat gpt', 'chatgpt', 'gpt-4', 'gpt4', 'gpt-3.5', 'gpt3.5', 'gpt-3', 'gpt3', 'dalle-2', 'dalle2', 'dalle-3', 'dalle3', 'stable diffusion', 'midjourney', 'whisper', 'text-to-image', 'text to image', 'text-to-speech', 'text to speech'
]
EXCLUDE_WORDS = ['mac', 'sql', 'wearable']

repo_pattern = re.compile(r'\[View Repository\]\((.*?)\)', re.IGNORECASE)
link_pattern_md = re.compile(r'\[(.*?)\]\((https?://[^\)]+)\)')

# Compile regex for whole word matching
KEYWORD_REGEXES = [re.compile(r'(?<!\w)'+re.escape(k)+r'(?!\w)', re.IGNORECASE) for k in KEYWORDS]
EXCLUDE_REGEXES = [re.compile(r'(?<!\w)'+re.escape(w)+r'(?!\w)', re.IGNORECASE) for w in EXCLUDE_WORDS]

def matches_keywords(text):
    for regex in KEYWORD_REGEXES:
        if regex.search(text):
            return True
    return False

def matches_exclude(text):
    for regex in EXCLUDE_REGEXES:
        if regex.search(text):
            return True
    return False

repos = []

for md_file in glob.glob(os.path.join(POSTS_DIR, '*.md')):
    with open(md_file, encoding='utf-8') as f:
        content = f.read()
    # Extract YAML front matter
    if content.startswith('---'):
        end = content.find('---', 3)
        if end != -1:
            front_matter = yaml.safe_load(content[3:end])
            body = content[end+3:].strip()
        else:
            front_matter = {}
            body = content
    else:
        front_matter = {}
        body = content
    # Remove unwanted fields from front matter
    for key in ['image', 'layout', 'name', 'tags']:
        if key in front_matter:
            del front_matter[key]
    # Save cleaned markdown file
    new_front = yaml.dump(front_matter, allow_unicode=True, sort_keys=False).strip()
    cleaned = f"---\n{new_front}\n---\n\n{body}" if new_front else body
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    # Extract repo link
    repo_link = None
    m = repo_pattern.search(body)
    if m:
        repo_link = m.group(1)
    else:
        m2 = link_pattern_md.search(body)
        if m2 and 'github.com' in m2.group(2):
            repo_link = m2.group(2)
    # Get first non-empty line as description
    desc_lines = [l.strip() for l in body.split('\n') if l.strip() and not l.strip().startswith('#')]
    description = desc_lines[0] if desc_lines else ''
    # Only include if description matches AI keywords as whole words and does NOT match exclude words
    if repo_link and matches_keywords(description) and not matches_exclude(description):
        repos.append({
            'url': repo_link,
            'description': description
        })

# Write repos.js
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('// Auto-generated from docs/_posts. Do not edit manually.\n')
    f.write('const repos = ')
    json.dump(repos, f, indent=2, ensure_ascii=False)
    f.write(';\n')

print(f"Wrote {len(repos)} curated AI repos to {OUTPUT_FILE}")
