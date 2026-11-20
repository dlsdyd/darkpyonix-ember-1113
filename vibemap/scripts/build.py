#!/usr/bin/env python3
"""
vibemap build: raw.json + map.json 을 뷰어 템플릿에 넣어 브라우저로 여는 HTML 한 파일을 만든다.

사용법 (프로젝트 루트에서):
  uv run vibemap/scripts/build.py              # → vibemap/out/vibemap.html
  uv run vibemap/scripts/build.py --card api   # 모듈 하나의 명함을 텍스트로 출력 (에이전트가 읽기용, 토큰 절약)
  uv run vibemap/scripts/build.py --symptom S3 # 증상 하나와 관련 모듈 명함 출력
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
DATA = os.path.join(KIT, "data")


def load(name, required=False):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        if required:
            print(f"{name}이 없습니다.", file=sys.stderr)
            sys.exit(1)
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def slim_raw(raw):
    if not raw:
        return None
    return {
        "generated": raw.get("generated"), "commit": raw.get("commit"), "totals": raw.get("totals"),
        "structure_hint": raw.get("structure_hint"),
        "modules": [{k: m[k] for k in ("id", "path", "files", "loc", "depth", "uses", "used_by", "tests", "todos")}
                    for m in raw.get("modules", [])],
        "module_edges": raw.get("module_edges", []),
        "files": [{"p": f["path"], "m": f["module"], "l": f["loc"], "fi": f["fan_in"],
                   "s": [[s[0], s[2]] for s in f["symbols"][:40]]} for f in raw.get("files", [])],
        "routes": raw.get("routes", [])[:300],
        "env": raw.get("env", {}),
        "signals": {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in raw.get("signals", {}).items()},
    }


def build():
    raw = load("raw.json")
    mp = load("map.json")
    if not raw and not mp:
        print("raw.json도 map.json도 없습니다. extract.py부터 실행하세요.", file=sys.stderr)
        sys.exit(1)
    payload = json.dumps({"raw": slim_raw(raw), "map": mp}, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/").replace("<!--", "<\\!--")
    with open(os.path.join(KIT, "viewer", "template.html"), encoding="utf-8") as fh:
        tpl = fh.read()
    marker = "/*__VIBEMAP_DATA__*/null"
    if marker not in tpl:
        print("템플릿에 데이터 자리표시자가 없습니다.", file=sys.stderr)
        sys.exit(1)
    html = tpl.replace(marker, payload)
    os.makedirs(os.path.join(KIT, "out"), exist_ok=True)
    out = os.path.join(KIT, "out", "vibemap.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"생성: vibemap/out/vibemap.html ({len(html) // 1024}KB): 브라우저로 여세요")


def card_text(m):
    L = [f"## {m['name']} ({m['id']}): {m.get('status', 'draft')}",
         f"경로: {m['path'] if isinstance(m['path'], str) else ', '.join(m['path'])}",
         f"하는 일: {m.get('one_line', '')}"]
    if m.get("uses") or m.get("used_by"):
        L.append(f"부르는 모듈: {', '.join(m.get('uses', [])) or '-'} / 나를 부르는 모듈: {', '.join(m.get('used_by', [])) or '-'}")
    if m.get("entry_points"):
        L.append("시작점:")
        L += [f"  - {e['name']} @ {e.get('at', '')}: {e.get('what', '')}" for e in m["entry_points"]]
    if m.get("contracts"):
        L.append("약속(밖에서 쓰는 것):")
        L += [f"  - {c['name']} @ {c.get('at', '')}: {c.get('what', '')} / 바꾸면: {c.get('breaks_if', '-')}" for c in m["contracts"]]
    if m.get("problems"):
        L.append("자주 나는 문제:")
        L += [f"  - {p['symptom']} → {p.get('check', '')}" for p in m["problems"]]
    if m.get("cautions"):
        L.append("주의:")
        L += [f"  - {c}" for c in m["cautions"]]
    return "\n".join(L)


def attach_links(mp):
    """raw.json의 모듈 간 import 관계를 map 모듈 단위로 바꿔 uses/used_by를 붙인다."""
    raw = load("raw.json")
    mods = mp.get("modules", [])
    if not raw:
        return
    def paths(m):
        p = m.get("path")
        return [x.rstrip("/") for x in ([p] if isinstance(p, str) else (p or []))]
    def owner(path):
        best, ln = None, -1
        for m in mods:
            for p in paths(m):
                if (p in ("", ".") or path == p or path.startswith(p + "/")) and len(p) > ln:
                    best, ln = m["id"], len(p)
        return best
    r2m = {r["id"]: owner("" if r["path"] == "(root)" else r["path"]) for r in raw.get("modules", [])}
    by = {m["id"]: m for m in mods}
    for m in mods:
        m["uses"], m["used_by"] = [], []
    for a, b, _ in raw.get("module_edges", []):
        A, B = r2m.get(a), r2m.get(b)
        if A and B and A != B:
            if B not in by[A]["uses"]:
                by[A]["uses"].append(B)
            if A not in by[B]["used_by"]:
                by[B]["used_by"].append(A)


def show_card(mid):
    mp = load("map.json", True)
    attach_links(mp)
    for m in mp.get("modules", []):
        if m["id"] == mid:
            print(card_text(m))
            return
    print(f"모듈 '{mid}' 없음: " + ", ".join(m["id"] for m in mp.get("modules", [])))


def show_symptom(sid):
    mp = load("map.json", True)
    attach_links(mp)
    mods = {m["id"]: m for m in mp.get("modules", [])}
    for s in mp.get("symptoms", []):
        if s["id"] == sid:
            print(f"# 증상 {sid}: {s['symptom']}")
            for l in s.get("look", []):
                print(f"- 볼 곳: {l.get('at')}: {l.get('why', '')}")
            for st in s.get("steps", []):
                print(f"- 확인: {st}")
            print()
            for mid in s.get("modules", []):
                if mid in mods:
                    print(card_text(mods[mid]) + "\n")
            return
    print(f"증상 '{sid}' 없음: " + ", ".join(s["id"] for s in mp.get("symptoms", [])))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--card")
    ap.add_argument("--symptom")
    a = ap.parse_args()
    if a.card:
        show_card(a.card)
    elif a.symptom:
        show_symptom(a.symptom)
    else:
        build()
