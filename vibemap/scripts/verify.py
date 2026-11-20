#!/usr/bin/env python3
"""
vibemap verify: 에이전트가 쓴 map.json이 형식에 맞고, 적힌 위치(path:line)가 실제 코드와 맞는지 검사한다.
LLM 대신 스크립트가 검증하므로 토큰이 들지 않는다.

사용법 (프로젝트 루트에서):
  uv run vibemap/scripts/verify.py            # 전체 검사
  uv run vibemap/scripts/verify.py --quiet    # 오류만 출력
종료 코드: 오류가 있으면 1
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
DATA = os.path.join(KIT, "data")

AT_RE = re.compile(r"^(.+?):(\d+)$")
SECRET_RE = re.compile(r"(AKIA[0-9A-Z]{16}|\bsk-[A-Za-z0-9_\-]{20,}|\bgh[pousr]_[A-Za-z0-9]{30,}|PRIVATE KEY-----)")

# 사람이 읽기 편하도록 글자 수 상한 (넘으면 경고)
LIMITS = {"one_line": 60, "what": 80, "why": 80, "breaks_if": 90, "symptom": 60, "check": 90,
          "meaning": 70, "caution": 90, "fix": 90, "summary": 160, "desc": 80, "step": 90}
MAX_LIST = {"entry_points": 6, "contracts": 6, "problems": 6, "cautions": 4, "look": 4, "steps": 6}

errors, warns = [], []
_line_cache = {}


def lines_of(root, path):
    if path not in _line_cache:
        full = os.path.join(root, path)
        if not os.path.isfile(full):
            _line_cache[path] = None
        else:
            with open(full, encoding="utf-8", errors="replace") as fh:
                _line_cache[path] = fh.read().splitlines()
    return _line_cache[path]


def check_at(root, where, at, name=None):
    if not at:
        return
    m = AT_RE.match(at.strip())
    if not m:
        # 파일 경로만 적은 경우 허용
        if lines_of(root, at.strip()) is None:
            errors.append(f"{where}: 위치 형식 오류 또는 없는 파일 '{at}' (형식: path:line)")
        return
    path, line = m.group(1), int(m.group(2))
    ls = lines_of(root, path)
    if ls is None:
        errors.append(f"{where}: 없는 파일 '{path}'")
        return
    if line < 1 or line > len(ls):
        errors.append(f"{where}: '{path}'는 {len(ls)}줄인데 {line}줄을 가리킴")
        return
    if name:
        key = re.split(r"[(\s.]", name.strip().strip("`"))[0]
        if key and len(key) > 1:
            window = "\n".join(ls[max(0, line - 4): line + 3])
            if key not in window:
                errors.append(f"{where}: '{key}'가 {path}:{line} 근처(±3줄)에 없음")


def check_len(where, field, value):
    lim = LIMITS.get(field)
    if lim and isinstance(value, str) and len(value) > lim:
        warns.append(f"{where}.{field}: {len(value)}자 (권장 {lim}자 이하): 더 짧게")


def walk_text(where, obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str):
                check_len(where, k, v)
                if SECRET_RE.search(v):
                    errors.append(f"{where}.{k}: 비밀값으로 보이는 문자열이 있음: 지우세요")
            elif isinstance(v, list):
                if k in MAX_LIST and len(v) > MAX_LIST[k]:
                    warns.append(f"{where}.{k}: {len(v)}개 (권장 {MAX_LIST[k]}개 이하): 중요한 것만")
                for i, x in enumerate(v):
                    if isinstance(x, str):
                        check_len(f"{where}.{k}[{i}]", "step" if k == "steps" else "caution", x)
                    else:
                        walk_text(f"{where}.{k}[{i}]", x)
            elif isinstance(v, dict):
                walk_text(f"{where}.{k}", v)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    mp = os.path.join(DATA, "map.json")
    if not os.path.exists(mp):
        print("map.json이 없습니다 (vibemap/data/map.json).")
        sys.exit(1)
    try:
        with open(mp, encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as e:
        print(f"map.json JSON 문법 오류: {e}")
        sys.exit(1)

    for key in ("project", "modules"):
        if key not in data:
            errors.append(f"필수 키 없음: {key}")
    proj = data.get("project", {})
    if proj.get("structure") not in (None, "tech", "feature", "layer"):
        errors.append("project.structure는 tech | feature | layer 중 하나")

    mods = data.get("modules", [])
    ids = [m.get("id") for m in mods]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        errors.append(f"모듈 id 중복: {', '.join(map(str, dup))}")
    idset = set(ids)
    status_count = {}
    for m in mods:
        w = f"modules[{m.get('id')}]"
        for k in ("id", "name", "path", "one_line"):
            if not m.get(k):
                errors.append(f"{w}: '{k}' 없음")
        st = m.get("status", "draft")
        if st not in ("draft", "carded", "verified"):
            errors.append(f"{w}: status는 draft | carded | verified")
        status_count[st] = status_count.get(st, 0) + 1
        for p in ([m.get("path")] if isinstance(m.get("path"), str) else m.get("path") or []):
            if p and not os.path.exists(os.path.join(root, p)):
                errors.append(f"{w}: 경로 '{p}' 없음")
        for i, e in enumerate(m.get("entry_points", [])):
            check_at(root, f"{w}.entry_points[{i}]", e.get("at"), e.get("name"))
        for i, c in enumerate(m.get("contracts", [])):
            check_at(root, f"{w}.contracts[{i}]", c.get("at"), c.get("name"))
            for j, u in enumerate(c.get("used_at", [])):
                check_at(root, f"{w}.contracts[{i}].used_at[{j}]", u)
        for i, p in enumerate(m.get("problems", [])):
            if AT_RE.match(str(p.get("check", ""))):
                check_at(root, f"{w}.problems[{i}]", p.get("check"))
        walk_text(w, m)

    for i, l in enumerate(data.get("layers", [])):
        for mid in l.get("modules", []):
            if mid not in idset:
                errors.append(f"layers[{i}]: 없는 모듈 id '{mid}'")
    for s in data.get("symptoms", []):
        w = f"symptoms[{s.get('id')}]"
        for mid in s.get("modules", []):
            if mid not in idset:
                errors.append(f"{w}: 없는 모듈 id '{mid}'")
        for i, l in enumerate(s.get("look", [])):
            check_at(root, f"{w}.look[{i}]", l.get("at"), l.get("name"))
        walk_text(w, s)
    for f in data.get("flows", []):
        w = f"flows[{f.get('id')}]"
        for i, st in enumerate(f.get("steps", [])):
            if st.get("module") and st["module"] not in idset:
                errors.append(f"{w}.steps[{i}]: 없는 모듈 id '{st['module']}'")
            check_at(root, f"{w}.steps[{i}]", st.get("at"), st.get("name"))
        walk_text(w, f)
    for it in data.get("issues", []):
        w = f"issues[{it.get('id')}]"
        if it.get("severity") not in ("high", "mid", "low"):
            errors.append(f"{w}: severity는 high | mid | low")
        check_at(root, w, it.get("at"))
        walk_text(w, it)
    for n in data.get("names", []):
        w = f"names[{n.get('name')}]"
        if n.get("module") and n["module"] not in idset:
            errors.append(f"{w}: 없는 모듈 id '{n['module']}'")
        check_at(root, w, n.get("at"), n.get("name"))
        walk_text(w, n)

    # raw 모듈 커버리지
    rp = os.path.join(DATA, "raw.json")
    uncovered = []
    if os.path.exists(rp):
        with open(rp, encoding="utf-8") as fh:
            raw = json.load(fh)
        paths = []
        for m in mods:
            ps = m.get("path")
            paths += [ps] if isinstance(ps, str) else (ps or [])
        paths = [p.rstrip("/") for p in paths if p]
        for f in raw.get("files", []):
            if not any(f["path"] == p or f["path"].startswith(p + "/") or p in ("", ".") for p in paths):
                uncovered.append(f["path"])

    total_refs = sum(1 for _ in _line_cache)
    print(f"모듈 {len(mods)}개 (" + ", ".join(f"{k} {v}" for k, v in sorted(status_count.items())) + ")"
          f" / 증상 {len(data.get('symptoms', []))} / 흐름 {len(data.get('flows', []))}"
          f" / 이슈 {len(data.get('issues', []))} / 이름 {len(data.get('names', []))} / 확인한 파일 {total_refs}개")
    if uncovered:
        print(f"\n[미배정] 어느 모듈 path에도 속하지 않는 파일 {len(uncovered)}개: " + ", ".join(uncovered[:10])
              + (" …" if len(uncovered) > 10 else ""))
    if errors:
        print(f"\n[오류 {len(errors)}] 반드시 고치세요")
        for e in errors[:80]:
            print(" - " + e)
        if len(errors) > 80:
            print(f" … 외 {len(errors) - 80}개")
    if warns and not a.quiet:
        print(f"\n[경고 {len(warns)}] 읽기 편하도록 줄이세요")
        for w in warns[:40]:
            print(" - " + w)
        if len(warns) > 40:
            print(f" … 외 {len(warns) - 40}개")
    if not errors:
        print("\n통과: 모든 위치가 실제 코드와 일치합니다.")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
