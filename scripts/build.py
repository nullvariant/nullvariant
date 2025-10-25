import os, re, json, yaml
from pathlib import Path
from anthropic import Anthropic

MODEL_DEFAULT = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
ROOT = Path(__file__).resolve().parents[1]
JA = ROOT / "content" / "AGENT.ja.md"
EN = ROOT / "AGENT.md"                     # ← root-level output
SPEC = ROOT / "spec" / "agent.spec.yaml"
SCHEMA = ROOT / "spec" / "agent.schema.json"
GLOSS = ROOT / "i18n" / "glossary.yml"
PROMPTS = ROOT / "scripts" / "prompts"

def load(p: Path): return p.read_text(encoding="utf-8")
def save(p: Path, s: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s, encoding="utf-8")

def compile_glossary(gloss):
    data = yaml.safe_load(gloss)
    entries = []
    for t in data.get("terms", []):
        if t.get("id") == "personas":
            for it in t.get("items", []):
                entries.append((it["ja"], f'personas:{it["emoji"]}', it["en"]["term"]))
        else:
            entries.append((t["ja"], t["id"], t["en"]["term"]))
    entries.sort(key=lambda x: len(x[0]), reverse=True)
    return entries, data

def inject_anchors(text: str, entries):
    out = text
    for ja, id_, _en in entries:
        out = re.sub(rf'(?<!\{{\#){re.escape(ja)}(?!\}})', f'{ja}{{#{id_}}}', out)
    return out

def chat(model, system, prompt, temperature=0.0):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    rsp = client.messages.create(
        model=model,
        max_tokens=8192,
        temperature=temperature,
        system=system,
        messages=[{"role":"user","content":prompt}]
    )
    return rsp.content[0].text

def main():
    ja = load(JA)
    gloss = load(GLOSS)
    entries, gloss_obj = compile_glossary(gloss)
    ja_anchored = inject_anchors(ja, entries)

    # glossary map for translator
    glossary_map = {}
    for t in yaml.safe_load(gloss).get("terms", []):
        if t.get("id") == "personas":
            for it in t.get("items", []):
                glossary_map[f'personas:{it["emoji"]}'] = it["en"]["term"]
        else:
            glossary_map[t["id"]] = t["en"]["term"]

    # 1) JA -> EN
    sys_trans = load(PROMPTS / "01_en_translate.txt")
    en_md = chat(MODEL_DEFAULT, sys_trans,
                 f"### Glossary Map (id->EN)\n{json.dumps(glossary_map, ensure_ascii=False)}\n\n### JA (anchored)\n{ja_anchored}")

    # 2) YAML spec
    sys_yaml = load(PROMPTS / "02_yaml_extract.txt")
    yaml_out = chat(MODEL_DEFAULT, sys_yaml, f"### JA (truth)\n{ja}")
    spec_obj = yaml.safe_load(yaml_out)

    save(EN, en_md.strip()+"\n")
    save(SPEC, yaml.dump(spec_obj, allow_unicode=True, sort_keys=False))

if __name__ == "__main__":
    main()
