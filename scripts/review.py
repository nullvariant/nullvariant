import os, json, yaml
from pathlib import Path
from jsonschema import Draft202012Validator
from anthropic import Anthropic
from sentence_transformers import SentenceTransformer, util

MODEL_DEFAULT = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")
ROOT = Path(__file__).resolve().parents[1]
JA = ROOT / "content" / "AGENT.ja.md"
EN = ROOT / "AGENT.md"
SPEC = ROOT / "spec" / "agent.spec.yaml"
SCHEMA = ROOT / "spec" / "agent.schema.json"
GLOSS = ROOT / "i18n" / "glossary.yml"
PROMPTS = ROOT / "scripts" / "prompts" / "90_self_review.txt"
BACKPROMPT = ROOT / "scripts" / "prompts" / "99_backtranslate.txt"

def load(p: Path): return p.read_text(encoding="utf-8")

def backtranslate(en_md: str):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    system = load(BACKPROMPT)
    rsp = client.messages.create(
        model=MODEL_DEFAULT,
        max_tokens=8192,
        temperature=0.0,
        system=system,
        messages=[{"role":"user","content":en_md}]
    )
    return rsp.content[0].text

def llm_review(jp: str, en: str, spec: str):
    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    system = load(PROMPTS)
    prompt = f"# JA\n{jp}\n\n# EN\n{en}\n\n# YAML\n{spec}"
    rsp = client.messages.create(
        model=MODEL_DEFAULT,
        max_tokens=8192,
        temperature=0.0,
        system=system,
        messages=[{"role":"user","content":prompt}]
    )
    return rsp.content[0].text

def ensure_keys(ja: str, en: str, gloss_obj: dict):
    must_ja, must_en = [], []
    for t in gloss_obj.get("terms", []):
        if t.get("id") == "personas":
            for it in t.get("items", []):
                must_ja.append(it["ja"]); must_en.append(it["en"]["term"])
        else:
            must_ja.append(t["ja"]); must_en.append(t["en"]["term"])
    miss_ja = [k for k in must_ja if k not in ja]
    miss_en = [k for k in must_en if k not in en]
    return miss_ja, miss_en

def embed_similarity(a: str, b: str):
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    ea = model.encode(a, convert_to_tensor=True, normalize_embeddings=True)
    eb = model.encode(b, convert_to_tensor=True, normalize_embeddings=True)
    return float(util.cos_sim(ea, eb).item())

def main(strict=False):
    ja = load(JA)
    en = load(EN)
    spec_txt = load(SPEC)
    spec_obj = yaml.safe_load(spec_txt)
    schema = json.loads(load(SCHEMA))
    gloss_obj = yaml.safe_load(load(GLOSS))

    Draft202012Validator(schema).validate(spec_obj)

    miss_ja, miss_en = ensure_keys(ja, en, gloss_obj)
    if miss_ja: raise SystemExit(f"[CRITICAL] JA missing glossary terms: {miss_ja}")
    if miss_en: raise SystemExit(f"[CRITICAL] EN missing glossary terms: {miss_en}")

    back_ja = backtranslate(en)
    sim = embed_similarity(ja, back_ja)
    print(f"[INFO] JA↔EN back-translation similarity: {sim:.4f}")
    if sim < 0.86: raise SystemExit(f"[CRITICAL] Semantic similarity below threshold: {sim:.4f}")

    review = llm_review(ja, en, spec_txt)
    print("=== LLM SELF-REVIEW ==="); print(review)
    if strict and ("[CRITICAL]" in review or "重大" in review):
        raise SystemExit("[CRITICAL] Self-review reported critical issues.")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    main(strict=args.strict)
