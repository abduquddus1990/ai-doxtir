"""Claude chat uchun ssenariy yozish promptlarini yasaydi: docs/PROMPT_DOXTIR.md, docs/PROMPT_OLMALIQ.md.
Har jadval ishida yangilanadi (mavjud mavzular ro'yxati dolzarb bo'lishi uchun)."""
import os, sys, json, ast, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.autogen import SPECS, SCHEMA_DOC

DIRS = {"doxtir": "episodes", "olmaliq": "channels/olmaliq/episodes"}

def builder_doc(name):
    if SPECS[name]["doc"]: return SPECS[name]["doc"]
    from tools.autogen import _spec
    class C: pass
    c = C(); c.name = name
    return _spec(c)["doc"]

def build(name):
    s = SPECS[name]
    eps = [json.load(open(p, encoding="utf-8")) for p in sorted(glob.glob(os.path.join(ROOT, DIRS[name], "*.json")))]
    ex = [e for e in eps if e.get("num", 99) <= 10][:2]
    for e in ex: e.pop("auto", None)
    used = "\n".join(f"- {e['title']}" for e in eps)
    return f"""# Claude chat uchun prompt — @ai_{name}

Quyidagi butun matnni (shu qatordan pastini) Claude chatga nusxalab yuboring. Claude 10 ta ssenariyni JSON qilib beradi.
Javobdagi JSON'ni `.json` fayl qilib saqlang va GitHub'da **inbox/{name}/** papkasiga yuklang (Add file → Upload files).
50 ta kerak bo'lsa, shu suhbatda "yana 10 ta, oldingilarini takrorlama" deb 5 marta so'rang — har javobni alohida faylga saqlang.

---

Siz {s['about']}

Siz video dvigateli uchun epizod JSON fayllarini yozasiz. Dvigatel faqat quyidagilarni tushunadi — boshqa quruvchi, parametr, sahna turi ishlatmang.

{builder_doc(name)}

{SCHEMA_DOC}

Allaqachon mavjud mavzular (takrorlamang):
{used}

Namuna epizodlar (format va uslub aynan shunday bo'lsin):
```json
{json.dumps(ex, ensure_ascii=False, indent=1)}
```

Vazifa: 10 ta YANGI epizod yozing (series: "{s['series']}"). Faktlarni veb-qidiruvda tekshiring.
"id" va "num" ni yozmasangiz ham bo'ladi — dastur o'zi raqamlaydi.
Javobni bitta ```json blokida {{"episodes": [ ... ]}} ko'rinishida qaytaring.
"""

if __name__ == "__main__":
    for n in SPECS:
        p = os.path.join(ROOT, "docs", f"PROMPT_{n.upper()}.md")
        open(p, "w", encoding="utf-8").write(build(n)); print("yozildi:", p)
