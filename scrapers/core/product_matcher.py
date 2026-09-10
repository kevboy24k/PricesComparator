import re, unicodedata
from difflib import SequenceMatcher

def normalize(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii','ignore').decode().lower()
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()
def confidence(a: str, b: str) -> float:
    left, right = normalize(a), normalize(b)
    return 100.0 if left == right else round(SequenceMatcher(None,left,right).ratio()*100,2)
def classify(score: float) -> str: return 'automatico' if score >= 90 else 'revision' if score >= 70 else 'nuevo'
def match(detected: dict, catalog: list[dict]) -> dict | None:
    scored=[{'product':p,'confidence':confidence(detected.get('name',''),p.get('name',''))} for p in catalog]
    best=max(scored,key=lambda x:x['confidence'],default=None)
    return best if best and best['confidence'] >= 70 else None
