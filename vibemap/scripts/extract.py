#!/usr/bin/env python3
"""
vibemap extract: 코드베이스에서 기계적으로 뽑을 수 있는 사실을 추출한다.
LLM 토큰을 쓰지 않고 파일 목록, 라인 수, import 관계, 공개 심볼, 라우트,
환경 변수, TODO, 비밀값 의심 위치, 중복 이름 등을 모은다.

사용법 (프로젝트 루트에서):
  uv run vibemap/scripts/extract.py                 # 전체 추출 → vibemap/data/raw.json, raw_summary.md
  uv run vibemap/scripts/extract.py --module api    # 모듈 하나의 상세 (화면 출력만, 명함 작성용)
  uv run vibemap/scripts/extract.py --find 결제하기  # 문자열이 나오는 위치 (증상 지도 작성용)

표준 라이브러리만 사용한다.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)  # vibemap/
DATA = os.path.join(KIT, "data")

LANG_BY_EXT = {
    ".py": "python", ".js": "js", ".jsx": "js", ".mjs": "js", ".cjs": "js",
    ".ts": "ts", ".tsx": "ts", ".mts": "ts", ".cts": "ts", ".vue": "vue", ".svelte": "svelte",
    ".go": "go", ".rs": "rust", ".java": "java", ".kt": "kotlin", ".kts": "kotlin",
    ".rb": "ruby", ".php": "php", ".cs": "csharp", ".swift": "swift", ".dart": "dart",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".hpp": "cpp",
    ".sql": "sql", ".sh": "shell", ".css": "css", ".scss": "css", ".html": "html",
}
EXCLUDE_DIRS = {
    "node_modules", ".git", ".venv", "venv", "env", "__pycache__", "dist", "build", "out",
    ".next", ".nuxt", ".svelte-kit", "coverage", "target", ".turbo", ".cache", "vendor",
    ".idea", ".vscode", ".pytest_cache", ".mypy_cache", ".ruff_cache", "vibemap",
    "docs/analysis", ".gradle", "Pods", ".dart_tool",
}
EXCLUDE_FILE_RE = re.compile(
    r"(\.min\.(js|css)$|\.map$|\.lock$|lock\.json$|lock\.yaml$|\.d\.ts$|\.gen\.|_pb2\.py$|\.pb\.go$|routeTree\.gen)"
)
CONTAINER_DIRS = {"src", "packages", "apps", "libs", "lib", "crates", "cmd", "internal", "pkg",
                  "services", "modules", "app", "server", "source"}
TEST_RE = re.compile(r"(^|/)(tests?|__tests__|spec|e2e)(/|$)|(\.|_)(test|spec)\.[a-z]+$|^test_.*\.py$|/test_[^/]*\.py$")
ENTRY_RE = re.compile(r"(^|/)(main|index|app|server|cli|__main__|manage|wsgi|asgi|lib|mod)\.[a-z]+$")

SECRET_RES = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"""(?i)\b(api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*["'][^"'\s]{8,}["']"""),
]
ENV_RES = [
    re.compile(r"process\.env\.([A-Z_][A-Z0-9_]*)"),
    re.compile(r"import\.meta\.env\.([A-Z_][A-Z0-9_]*)"),
    re.compile(r"""os\.environ(?:\.get)?\s*[\[(]\s*["']([A-Z_][A-Z0-9_]*)"""),
    re.compile(r"""os\.getenv\(\s*["']([A-Z_][A-Z0-9_]*)"""),
    re.compile(r"""os\.Getenv\(\s*"([A-Z_][A-Z0-9_]*)"""),
    re.compile(r"""env::var\(\s*"([A-Z_][A-Z0-9_]*)"""),
    re.compile(r"""System\.getenv\(\s*"([A-Z_][A-Z0-9_]*)"""),
]
ROUTE_RES = [
    # FastAPI / Flask / Express / Hono / Gin / Echo / Spring
    re.compile(r"""@\w+\.(get|post|put|patch|delete|route|websocket)\(\s*["']([^"']*)["']"""),
    re.compile(r"""\b(?:app|router|r|e|g|api|server)\.(get|post|put|patch|delete|all|use|GET|POST|PUT|PATCH|DELETE|Handle|HandleFunc)\(\s*["'`](/[^"'`]*)["'`]"""),
    re.compile(r"""@(Get|Post|Put|Patch|Delete|Request)Mapping\(\s*(?:value\s*=\s*)?["']([^"']*)["']"""),
    re.compile(r"""APIRouter\([^)]*prefix\s*=\s*["']([^"']*)["']()"""),
]
TODO_RE = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")

SYMBOL_RES = {
    "python": [
        (re.compile(r"^(?:async\s+)?def\s+([A-Za-z_]\w*)"), "function"),
        (re.compile(r"^class\s+([A-Za-z_]\w*)"), "class"),
        (re.compile(r"^([A-Z][A-Z0-9_]{2,})\s*(?::[^=]+)?=(?!=)"), "const"),
    ],
    "js": [
        (re.compile(r"^export\s+(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)"), "function"),
        (re.compile(r"^export\s+(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)"), "class"),
        (re.compile(r"^export\s+(?:const|let|var)\s+([A-Za-z_$][\w$]*)"), "const"),
        (re.compile(r"^export\s+(?:declare\s+)?(?:interface|type)\s+([A-Za-z_$][\w$]*)"), "type"),
        (re.compile(r"^export\s+(?:const\s+)?enum\s+([A-Za-z_$][\w$]*)"), "enum"),
        (re.compile(r"^export\s+default\s+([A-Za-z_$][\w$]*)\s*;?\s*$"), "default"),
    ],
    "go": [
        (re.compile(r"^func\s+(?:\([^)]*\)\s*)?([A-Z]\w*)"), "function"),
        (re.compile(r"^type\s+([A-Z]\w*)\s+(?:struct|interface)"), "type"),
        (re.compile(r"^type\s+([A-Z]\w*)\b"), "type"),
    ],
    "rust": [
        (re.compile(r"^\s*pub(?:\([^)]*\))?\s+(?:async\s+)?(?:unsafe\s+)?fn\s+([A-Za-z_]\w*)"), "function"),
        (re.compile(r"^pub(?:\([^)]*\))?\s+(?:struct|enum|trait|type)\s+([A-Za-z_]\w*)"), "type"),
        (re.compile(r"^pub(?:\([^)]*\))?\s+(?:const|static)\s+([A-Z_][A-Z0-9_]*)"), "const"),
    ],
    "java": [
        (re.compile(r"^\s*public\s+(?:abstract\s+|final\s+)*(?:class|interface|enum|record)\s+([A-Za-z_]\w*)"), "class"),
    ],
    "kotlin": [
        (re.compile(r"^(?:(?:public|internal|data|sealed|abstract|open|enum)\s+)*(?:class|interface|object)\s+([A-Za-z_]\w*)"), "class"),
        (re.compile(r"^(?:(?:public|internal|suspend)\s+)*fun\s+(?:<[^>]+>\s*)?([A-Za-z_]\w*)"), "function"),
    ],
}
SYMBOL_RES["ts"] = SYMBOL_RES["js"]
SYMBOL_RES["vue"] = SYMBOL_RES["js"]
SYMBOL_RES["svelte"] = SYMBOL_RES["js"]

JS_IMPORT_RES = [
    re.compile(r"""(?:^|[\s}*])from\s+["']([^"']+)["']"""),          # import ... from "x" (여러 줄 import의 마지막 줄 포함)
    re.compile(r"""^\s*import\s+["']([^"']+)["']"""),                  # import "x" (부수효과 import)
    re.compile(r"""require\(\s*["']([^"']+)["']\s*\)"""),
    re.compile(r"""import\(\s*["']([^"']+)["']\s*\)"""),
]
PY_IMPORT_RES = [
    re.compile(r"^\s*from\s+(\.*[\w.]*)\s+import\s+(.+)"),
    re.compile(r"^\s*import\s+([\w.]+(?:\s*,\s*[\w.]+)*)"),
]
GO_IMPORT_RE = re.compile(r'^\s*(?:import\s+)?(?:\w+\s+)?"([^"]+)"')
RUST_USE_RE = re.compile(r"^\s*(?:pub\s+)?use\s+(crate|super|self)::([\w:]+)")
RUST_MOD_RE = re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?mod\s+(\w+)\s*;")
JAVA_IMPORT_RE = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)")


# ---------------------------------------------------------------- 파일 수집
def load_config(root):
    p = os.path.join(KIT, "config.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def list_files(root, extra_exclude):
    files = None
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=root,
                             capture_output=True, text=True, timeout=60)
        if out.returncode == 0:
            files = [l for l in out.stdout.splitlines() if l]
    except Exception:
        pass
    if files is None:
        files = []
        for d, dirs, fs in os.walk(root):
            dirs[:] = [x for x in dirs if x not in EXCLUDE_DIRS and not x.startswith(".")]
            for f in fs:
                files.append(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/"))
    res = []
    for f in files:
        parts = f.split("/")
        if any(p in EXCLUDE_DIRS for p in parts[:-1]):
            continue
        if any(f.startswith(x.rstrip("/") + "/") or f == x for x in extra_exclude):
            continue
        if "docs/analysis/" in f:
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext not in LANG_BY_EXT or EXCLUDE_FILE_RE.search(f):
            continue
        full = os.path.join(root, f)
        if not os.path.isfile(full):
            continue
        try:
            if os.path.getsize(full) > 1_500_000:
                continue
        except OSError:
            continue
        res.append(f)
    return sorted(res)


def read_lines(root, f):
    try:
        with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
            return fh.read().splitlines()
    except Exception:
        return []


# ---------------------------------------------------------------- import 해석
class Resolver:
    def __init__(self, root, files):
        self.root = root
        self.fileset = set(files)
        self.by_dir = defaultdict(list)
        for f in files:
            self.by_dir[os.path.dirname(f)].append(f)
        # python 패키지 루트 후보
        self.py_roots = [""]
        for f in files:
            if f.endswith(".py"):
                parts = f.split("/")
                # 최상위 패키지의 부모 폴더를 루트 후보로
                for i in range(len(parts) - 1):
                    d = "/".join(parts[: i + 1])
                    if d + "/__init__.py" in self.fileset:
                        parent = "/".join(parts[:i])
                        if parent not in self.py_roots:
                            self.py_roots.append(parent)
                        break
        # tsconfig paths alias
        self.aliases = self._load_aliases()
        # go module
        self.go_mods = {}
        for f in files:
            pass
        for d, _, fs in os.walk(root):
            if any(x in d.split(os.sep) for x in ("node_modules", ".git", "vendor")):
                continue
            if "go.mod" in fs:
                try:
                    with open(os.path.join(d, "go.mod"), encoding="utf-8") as fh:
                        m = re.search(r"^module\s+(\S+)", fh.read(), re.M)
                    if m:
                        self.go_mods[m.group(1)] = os.path.relpath(d, root).replace(os.sep, "/").lstrip(".").lstrip("/")
                except Exception:
                    pass
        # java suffix index
        self.java_idx = {}
        for f in files:
            if f.endswith((".java", ".kt")):
                key = os.path.splitext(f)[0].replace("/", ".")
                self.java_idx[key] = f

    def _load_aliases(self):
        aliases = []
        for d, dirs, fs in os.walk(self.root):
            dirs[:] = [x for x in dirs if x not in EXCLUDE_DIRS and not x.startswith(".")]
            for name in ("tsconfig.json", "tsconfig.app.json", "jsconfig.json"):
                if name in fs:
                    try:
                        with open(os.path.join(d, name), encoding="utf-8") as fh:
                            txt = re.sub(r"//.*|/\*[\s\S]*?\*/", "", fh.read())
                            txt = re.sub(r",(\s*[}\]])", r"\1", txt)
                            cfg = json.loads(txt)
                        co = cfg.get("compilerOptions", {})
                        base = os.path.normpath(os.path.join(d, co.get("baseUrl", ".")))
                        for k, vs in (co.get("paths") or {}).items():
                            for v in vs[:1]:
                                prefix = k.rstrip("*")
                                target = os.path.normpath(os.path.join(base, v.rstrip("*")))
                                rel = os.path.relpath(target, self.root).replace(os.sep, "/")
                                aliases.append((prefix, rel if rel != "." else ""))
                    except Exception:
                        pass
        # 흔한 기본 alias
        if not any(a[0] == "@/" for a in aliases):
            for cand in ("src", "frontend/src", "client/src", "web/src", "app"):
                if any(f.startswith(cand + "/") for f in self.fileset):
                    aliases.append(("@/", cand))
                    break
        return aliases

    def _try_js(self, base):
        base = os.path.normpath(base).replace(os.sep, "/")
        if base.startswith("../"):
            return None
        cands = [base]
        for ext in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".vue", ".svelte", ".mts"):
            cands.append(base + ext)
        for ext in (".ts", ".tsx", ".js", ".jsx"):
            cands.append(base + "/index" + ext)
        # .js 로 적었지만 실제는 .ts 인 경우
        if base.endswith(".js"):
            cands += [base[:-3] + ".ts", base[:-3] + ".tsx"]
        for c in cands:
            if c in self.fileset:
                return c
        return None

    def js(self, src, spec):
        if spec.startswith("."):
            return self._try_js(os.path.join(os.path.dirname(src), spec)), None
        for prefix, target in self.aliases:
            if prefix and spec.startswith(prefix):
                r = self._try_js(os.path.join(target, spec[len(prefix):]))
                if r:
                    return r, None
        pkg = spec.split("/")[0] if not spec.startswith("@") else "/".join(spec.split("/")[:2])
        return None, pkg

    def py(self, src, mod, names):
        out = []
        if mod.startswith("."):
            dots = len(mod) - len(mod.lstrip("."))
            base = os.path.dirname(src)
            for _ in range(dots - 1):
                base = os.path.dirname(base)
            rest = mod.lstrip(".")
            path = os.path.join(base, rest.replace(".", "/")) if rest else base
            candidates = [path]
            if not rest:
                candidates = [os.path.join(base, n.strip().split(" ")[0]) for n in names]
            for c in candidates:
                c = c.replace(os.sep, "/")
                for t in (c + ".py", c + "/__init__.py"):
                    if t in self.fileset:
                        out.append(t)
                        break
            return out, None
        for r in self.py_roots:
            path = (r + "/" if r else "") + mod.replace(".", "/")
            for t in (path + ".py", path + "/__init__.py"):
                if t in self.fileset:
                    # from pkg import submodule 인 경우 서브모듈까지
                    if t.endswith("__init__.py"):
                        for n in names:
                            n = n.strip().split(" ")[0]
                            if (path + "/" + n + ".py") in self.fileset:
                                out.append(path + "/" + n + ".py")
                    out.append(t)
                    return out, None
        return [], mod.split(".")[0]

    def go(self, src, spec):
        for modname, moddir in self.go_mods.items():
            if spec == modname or spec.startswith(modname + "/"):
                sub = spec[len(modname):].lstrip("/")
                d = "/".join(x for x in (moddir, sub) if x)
                fs = [f for f in self.by_dir.get(d, []) if f.endswith(".go") and not f.endswith("_test.go")]
                return fs, None  # Go는 패키지 단위 import라 패키지의 모든 파일에 연결
        return [], spec.split("/")[0] if "." in spec.split("/")[0] else None

    def rust(self, src, kind, path):
        # crate 루트 찾기
        parts = src.split("/")
        crate_src = None
        for i in range(len(parts) - 1, 0, -1):
            if parts[i - 1] == "src" or parts[i] == "src":
                idx = parts.index("src") if "src" in parts else None
                if idx is not None:
                    crate_src = "/".join(parts[: idx + 1])
                break
        if not crate_src:
            return []
        segs = path.split("::")
        if kind == "crate":
            base = crate_src
        else:
            base = os.path.dirname(src)
            if kind == "super":
                base = os.path.dirname(base)
        out = []
        cur = base
        for s in segs:
            cur = cur + "/" + s
            for t in (cur + ".rs", cur + "/mod.rs"):
                if t in self.fileset:
                    out = [t]
        return out

    def rust_mod(self, src, name):
        d = os.path.dirname(src)
        stem = os.path.splitext(os.path.basename(src))[0]
        bases = [d] if stem in ("mod", "lib", "main") else [d + "/" + stem, d]
        for b in bases:
            for t in (b + "/" + name + ".rs", b + "/" + name + "/mod.rs"):
                if t in self.fileset:
                    return t
        return None

    def java(self, spec):
        if spec in self.java_idx:
            return self.java_idx[spec]
        for k, v in self.java_idx.items():
            if k.endswith("." + spec) or k.endswith(spec):
                return v
        return None


# ---------------------------------------------------------------- 모듈 분할
def propose_modules(files, loc, overrides):
    if overrides:
        mods = {}
        for f in files:
            best = None
            for mid, path in overrides.items():
                p = path.rstrip("/")
                if f == p or f.startswith(p + "/"):
                    if best is None or len(p) > len(overrides[best].rstrip("/")):
                        best = mid
            mods[f] = best or "(root)"
        return mods
    total = sum(loc.values()) or 1
    limit = max(800, min(3000, total * 0.12))

    def split(prefix, depth):
        sub = defaultdict(list)
        direct = []
        for f in files:
            if prefix and not f.startswith(prefix + "/"):
                continue
            rest = f[len(prefix) + 1:] if prefix else f
            if "/" in rest:
                sub[rest.split("/")[0]].append(f)
            else:
                direct.append(f)
        result = {}
        for name, fs in sub.items():
            path = (prefix + "/" if prefix else "") + name
            size = sum(loc[f] for f in fs)
            has_subdirs = any("/" in f[len(path) + 1:] for f in fs)
            subnames = {f[len(path) + 1:].split("/")[0] for f in fs if "/" in f[len(path) + 1:]}
            # 컨테이너 폴더이거나 너무 크면 한 단계 더 내려간다
            if depth < 4 and has_subdirs and (
                name in CONTAINER_DIRS or (size > limit and len(subnames) >= 2)
                or (len(subnames) == 1 and all("/" in f[len(path) + 1:] for f in fs))
            ):
                result.update(split(path, depth + 1))
            else:
                for f in fs:
                    result[f] = path
        for f in direct:
            result[f] = prefix or "(root)"
        return result

    mods = split("", 0)
    # 너무 작은 모듈(<40줄, 파일 1개)은 부모로 합친다
    sizes = Counter()
    for f, m in mods.items():
        sizes[m] += loc[f]
    for f, m in list(mods.items()):
        if sizes[m] < 40 and m not in ("(root)",) and "/" in m:
            parent = m.rsplit("/", 1)[0]
            mods[f] = parent
    return mods


def module_id(path):
    if path == "(root)":
        return "root"
    return path.replace("/", ".")


# ---------------------------------------------------------------- 메인 추출
def extract(root):
    cfg = load_config(root)
    files = list_files(root, cfg.get("exclude", []))
    if not files:
        print("분석할 소스 파일을 찾지 못했습니다. 프로젝트 루트에서 실행했는지 확인하세요.", file=sys.stderr)
        sys.exit(1)
    res = Resolver(root, files)
    loc, lang, symbols, todos, secrets, envs, routes = {}, {}, {}, {}, [], defaultdict(list), []
    edges = Counter()
    file_edges = defaultdict(set)
    ext_deps = Counter()

    for f in files:
        lines = read_lines(root, f)
        lg = LANG_BY_EXT[os.path.splitext(f)[1].lower()]
        lang[f] = lg
        loc[f] = sum(1 for l in lines if l.strip())
        syms = []
        for i, line in enumerate(lines, 1):
            for rx, kind in SYMBOL_RES.get(lg, []):
                m = rx.match(line)
                if m:
                    name = m.group(1)
                    if lg == "python" and name.startswith("_"):
                        break
                    syms.append([name, kind, i])
                    break
            if TODO_RE.search(line):
                todos[f] = todos.get(f, 0) + 1
            for rx in SECRET_RES:
                if rx.search(line):
                    secrets.append(f"{f}:{i}")
                    break
            for rx in ENV_RES:
                for m in rx.finditer(line):
                    if len(envs[m.group(1)]) < 5:
                        envs[m.group(1)].append(f"{f}:{i}")
            if lg in ("python", "js", "ts", "go", "java", "kotlin", "vue", "svelte"):
                for rx in ROUTE_RES:
                    m = rx.search(line)
                    if m:
                        method = m.group(1).upper() if m.group(1) else "PREFIX"
                        if rx.pattern.startswith("APIRouter"):
                            method = "PREFIX"
                        p = m.group(2) if m.group(2) else m.group(1)
                        if rx.pattern.startswith("APIRouter"):
                            p = m.group(1)
                        routes.append([method, p, f"{f}:{i}"])
                        break
            # imports
            targets = []
            if lg in ("js", "ts", "vue", "svelte"):
                for rx in JS_IMPORT_RES:
                    for m in rx.finditer(line):
                        t, pkg = res.js(f, m.group(1))
                        if t:
                            targets.append(t)
                        elif pkg and not m.group(1).startswith("."):
                            ext_deps[pkg] += 1
            elif lg == "python":
                m = PY_IMPORT_RES[0].match(line)
                if m:
                    names = [n for n in m.group(2).strip("()\\ ").split(",") if n.strip()]
                    ts, pkg = res.py(f, m.group(1), names)
                    targets += ts
                    if pkg:
                        ext_deps[pkg] += 1
                else:
                    m = PY_IMPORT_RES[1].match(line)
                    if m:
                        for mod in m.group(1).split(","):
                            ts, pkg = res.py(f, mod.strip(), [])
                            targets += ts
                            if pkg:
                                ext_deps[pkg] += 1
            elif lg == "go":
                if line.strip().startswith(("import", '"')) or re.match(r'^\s*\w+\s+"', line):
                    m = GO_IMPORT_RE.match(line)
                    if m and ("." in m.group(1).split("/")[0] or res.go_mods):
                        ts, pkg = res.go(f, m.group(1))
                        targets += ts
                        if pkg:
                            ext_deps[pkg] += 1
            elif lg == "rust":
                m = RUST_USE_RE.match(line)
                if m:
                    targets += res.rust(f, m.group(1), m.group(2))
                m = RUST_MOD_RE.match(line)
                if m:
                    t = res.rust_mod(f, m.group(1))
                    if t:
                        targets.append(t)
            elif lg in ("java", "kotlin"):
                m = JAVA_IMPORT_RE.match(line)
                if m:
                    t = res.java(m.group(1))
                    if t:
                        targets.append(t)
            for t in targets:
                if t != f:
                    file_edges[f].add(t)
        symbols[f] = syms

    modmap = propose_modules(files, loc, cfg.get("modules"))
    fan_in = Counter()
    seen_pairs = set()
    for a, bs in file_edges.items():
        for b in bs:
            fan_in[b] += 1
            ma, mb = modmap[a], modmap[b]
            if ma != mb and (a, mb) not in seen_pairs:
                seen_pairs.add((a, mb))
                edges[(module_id(ma), module_id(mb))] += 1

    # 모듈 집계
    modules = {}
    for f in files:
        mid = module_id(modmap[f])
        m = modules.setdefault(mid, {"id": mid, "path": modmap[f], "files": 0, "loc": 0,
                                    "langs": Counter(), "exports": 0, "tests": 0, "todos": 0})
        m["files"] += 1
        m["loc"] += loc[f]
        m["langs"][lang[f]] += loc[f]
        m["exports"] += len(symbols[f])
        m["todos"] += todos.get(f, 0)
        if TEST_RE.search(f):
            m["tests"] += 1
    for m in modules.values():
        m["langs"] = [k for k, _ in m["langs"].most_common(3)]
        m["uses"] = sorted({b for (a, b) in edges if a == m["id"]})
        m["used_by"] = sorted({a for (a, b) in edges if b == m["id"]})

    # 의존 깊이로 층 추정 (많이 쓰이는 쪽이 아래)
    depth = {}

    def calc(mid, seen):
        if mid in depth:
            return depth[mid]
        if mid in seen:
            return 0
        seen.add(mid)
        uses = modules[mid]["uses"]
        d = 0 if not uses else 1 + max(calc(u, seen) for u in uses if u in modules) if any(u in modules for u in uses) else 0
        depth[mid] = d
        return d

    for mid in modules:
        calc(mid, set())
    for mid, m in modules.items():
        m["depth"] = depth.get(mid, 0)

    # 이름 중복 (서로 다른 파일에 같은 공개 이름)
    by_name = defaultdict(list)
    for f, syms in symbols.items():
        if TEST_RE.search(f):
            continue
        for name, kind, line in syms:
            if kind in ("function", "class", "const") and len(name) > 3 and name not in ("default", "main", "init", "setup", "router", "config", "Props", "app"):
                by_name[name].append(f"{f}:{line}")
    duplicates = {k: v for k, v in by_name.items() if len(v) >= 2 and len({x.split(':')[0] for x in v}) >= 2}

    orphans = [f for f in files if fan_in[f] == 0 and not TEST_RE.search(f) and not ENTRY_RE.search(f)
               and lang[f] in ("python", "js", "ts", "go", "rust", "vue", "svelte")
               and not f.endswith(("config.ts", "config.js", "__init__.py", "conftest.py", "setup.py"))
               and "/" in f and not re.search(r"(^|/)(pages|routes|app|migrations|alembic|scripts|bin)/", f)]
    leftovers = [f for f in files if re.search(r"(?i)(^|[/_\-.])(old|backup|bak|copy|tmp|temp|v2|new2|test2|unused|deprecated)([/_\-.]|$)", f)]
    big = sorted([f for f in files if loc[f] >= 500], key=lambda f: -loc[f])

    by_lang = Counter()
    for f in files:
        by_lang[lang[f]] += loc[f]
    raw = {
        "generated": date.today().isoformat(),
        "commit": git_commit(root),
        "totals": {"files": len(files), "loc": sum(loc.values()),
                   "by_lang": dict(by_lang.most_common())},
        "modules": sorted(modules.values(), key=lambda m: (m["depth"], m["id"])),
        "module_edges": [[a, b, n] for (a, b), n in edges.most_common()],
        "files": [{"path": f, "module": module_id(modmap[f]), "lang": lang[f], "loc": loc[f],
                   "fan_in": fan_in[f], "symbols": symbols[f][:60], "todos": todos.get(f, 0),
                   "imports": sorted(file_edges[f])} for f in files],
        "routes": routes[:400],
        "env": {k: v for k, v in sorted(envs.items())},
        "external_deps": dict(ext_deps.most_common(60)),
        "signals": {
            "secrets_suspect": secrets[:100],
            "duplicates": dict(sorted(duplicates.items(), key=lambda kv: -len(kv[1]))[:80]),
            "orphans": orphans[:150],
            "leftovers": leftovers[:100],
            "big_files": [[f, loc[f]] for f in big[:50]],
            "todo_files": sorted(([f, n] for f, n in todos.items()), key=lambda x: -x[1])[:50],
        },
        "structure_hint": structure_hint(modules),
    }
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "raw.json"), "w", encoding="utf-8") as fh:
        json.dump(raw, fh, ensure_ascii=False, indent=1)
    summary = render_summary(raw)
    with open(os.path.join(DATA, "raw_summary.md"), "w", encoding="utf-8") as fh:
        fh.write(summary)
    print(f"추출 완료: 파일 {len(files)}개, {raw['totals']['loc']}줄, 모듈 후보 {len(modules)}개")
    print("요약: vibemap/data/raw_summary.md  (에이전트는 이 파일만 읽으면 됩니다)")


def git_commit(root):
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=root, capture_output=True, text=True)
        return out.stdout.strip() or None
    except Exception:
        return None


def structure_hint(modules):
    names = {m["path"].split("/")[-1].lower() for m in modules.values()}
    tech = {"components", "utils", "hooks", "services", "api", "lib", "helpers", "types", "models",
            "controllers", "views", "routes", "store", "stores", "pages", "styles", "assets", "schemas", "crud"}
    layer = {"transport", "network", "core", "infra", "proxy", "hub", "node", "gateway", "protocol",
             "runtime", "engine", "client", "server", "worker", "agent", "daemon", "storage"}
    t, l = len(names & tech), len(names & layer)
    if t >= max(2, l + 1):
        return "tech"
    if l >= 2:
        return "layer"
    return "feature"


def render_summary(raw):
    L = []
    t = raw["totals"]
    L.append(f"# raw 요약 (자동 생성, {raw['generated']}, commit {raw['commit']})\n")
    L.append(f"- 파일 {t['files']}개 / {t['loc']}줄 (빈 줄 제외)")
    L.append("- 언어: " + ", ".join(f"{k} {v}" for k, v in sorted(t["by_lang"].items(), key=lambda kv: -kv[1]) if v))
    L.append(f"- 구조 추정: **{raw['structure_hint']}** (tech=기술 종류별, feature=기능별, layer=역할·계층별)")
    L.append("")
    L.append("## 모듈 후보 (depth 0 = 다른 모듈에 의존하지 않음, 아래층)")
    L.append("| id | 경로 | 파일 | 줄 | 공개심볼 | depth | uses | used_by |")
    L.append("|---|---|---|---|---|---|---|---|")
    for m in raw["modules"]:
        L.append(f"| {m['id']} | {m['path']} | {m['files']} | {m['loc']} | {m['exports']} | {m['depth']} | "
                 f"{', '.join(m['uses'][:6])}{'…' if len(m['uses']) > 6 else ''} | "
                 f"{', '.join(m['used_by'][:6])}{'…' if len(m['used_by']) > 6 else ''} |")
    L.append("")
    entries = [f["path"] for f in raw["files"] if ENTRY_RE.search(f["path"]) and not TEST_RE.search(f["path"])]
    L.append("## 진입점 후보")
    L.append(", ".join(entries[:30]) or "(없음)")
    L.append("")
    if raw["routes"]:
        L.append(f"## 라우트 ({len(raw['routes'])}개, 앞 40개)")
        for r in raw["routes"][:40]:
            L.append(f"- {r[0]} {r[1]}: {r[2]}")
        L.append("")
    if raw["env"]:
        L.append("## 환경 변수")
        L.append(", ".join(f"{k}({len(v)})" for k, v in list(raw["env"].items())[:60]))
        L.append("")
    L.append("## 외부 패키지 (import 횟수 상위)")
    L.append(", ".join(f"{k}({v})" for k, v in list(raw["external_deps"].items())[:30]))
    L.append("")
    s = raw["signals"]
    L.append("## 신호 (이슈 후보, 개수)")
    L.append(f"- 비밀값 의심: {len(s['secrets_suspect'])} / 중복 이름: {len(s['duplicates'])} / "
             f"고아 파일: {len(s['orphans'])} / 잔해 파일: {len(s['leftovers'])} / 500줄+ 파일: {len(s['big_files'])} / "
             f"TODO 있는 파일: {len(s['todo_files'])}")
    L.append("- 상세는 `uv run vibemap/scripts/extract.py --signals` 로 확인")
    L.append("")
    return "\n".join(L) + "\n"


def load_raw():
    p = os.path.join(DATA, "raw.json")
    if not os.path.exists(p):
        print("raw.json이 없습니다. 먼저 인자 없이 extract.py를 실행하세요.", file=sys.stderr)
        sys.exit(1)
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def show_module(mid, max_syms, max_files=25):
    raw = load_raw()
    mods = {m["id"]: m for m in raw["modules"]}
    if mid not in mods:
        print(f"모듈 '{mid}' 없음. 가능한 id: {', '.join(mods)}")
        sys.exit(1)
    m = mods[mid]
    files = [f for f in raw["files"] if f["module"] == mid]
    print(f"# 모듈 {mid}  ({m['path']}, 파일 {m['files']}, {m['loc']}줄)")
    print(f"uses: {', '.join(m['uses']) or '-'}")
    print(f"used_by: {', '.join(m['used_by'][:12]) or '-'}{' 외 ' + str(len(m['used_by']) - 12) if len(m['used_by']) > 12 else ''}\n")
    is_test = lambda f: TEST_RE.search(f["path"]) or re.search(r"(^|/)(mocks?|fixtures?|testdata)(/|$)|_mock\.|\.mock\.", f["path"])
    main_files = sorted([f for f in files if not is_test(f)], key=lambda f: (-f["fan_in"], -f["loc"]))
    test_files = [f for f in files if is_test(f)]
    print(f"## 파일 (팬인 높은 순, 상위 {min(max_files, len(main_files))}개): 경로 | 줄 | 팬인 | 공개 심볼(이름:줄)")
    for f in main_files[:max_files]:
        syms = ", ".join(f"{s[0]}:{s[2]}" for s in f["symbols"][:max_syms])
        more = f" …+{len(f['symbols']) - max_syms}" if len(f["symbols"]) > max_syms else ""
        print(f"- {f['path']} | {f['loc']} | {f['fan_in']} | {syms}{more}")
    if len(main_files) > max_files:
        rest = main_files[max_files:]
        print(f"- … 나머지 {len(rest)}개 파일, {sum(f['loc'] for f in rest)}줄 (--max-files 로 더 보기)")
    if test_files:
        print(f"- (테스트·mock 파일 {len(test_files)}개, {sum(f['loc'] for f in test_files)}줄은 생략)")
    # 경계: 다른 모듈에서 이 모듈의 어떤 파일을 쓰나
    inbound = Counter()
    users = defaultdict(set)
    allf = {f["path"]: f for f in raw["files"]}
    for f in raw["files"]:
        if f["module"] == mid:
            continue
        for t in f["imports"]:
            if allf.get(t, {}).get("module") == mid:
                inbound[t] += 1
                users[t].add(f["module"])
    def grouped(counter, extra):
        """같은 폴더에서 숫자와 사용처가 똑같은 파일들(Go 패키지 등)은 한 줄로 묶는다."""
        groups = defaultdict(list)
        for t, n in counter.items():
            groups[(os.path.dirname(t), n, extra(t))].append(t)
        rows = []
        for (d, n, ex), ts in groups.items():
            label = ts[0] if len(ts) == 1 else f"{d}/ (패키지 전체, 파일 {len(ts)}개)"
            rows.append((n, label, ex))
        return sorted(rows, key=lambda r: -r[0])[:15]

    def short(names):
        names = sorted(names)
        return ", ".join(names[:6]) + (f" 외 {len(names) - 6}" if len(names) > 6 else "")

    if inbound:
        print("\n## 다른 모듈이 쓰는 파일 (= 이 모듈의 경계/약속 후보)")
        for n, label, ex in grouped(inbound, lambda t: tuple(sorted(users[t]))):
            print(f"- {label} ← {n}곳 ({short(ex)})")
    outbound = Counter()
    for f in files:
        for t in f["imports"]:
            if allf.get(t, {}).get("module") not in (mid, None):
                outbound[t] += 1
    if outbound:
        print("\n## 이 모듈이 쓰는 다른 모듈 파일")
        for n, label, ex in grouped(outbound, lambda t: allf[t]["module"]):
            print(f"- {label} ({ex}) ×{n}")
    rs = [r for r in raw["routes"] if any(r[2].startswith(f["path"] + ":") for f in files)]
    if rs:
        print("\n## 라우트")
        for r in rs[:30]:
            print(f"- {r[0]} {r[1]}: {r[2]}")
    ev = [k for k, v in raw["env"].items() if any(x.split(":")[0] in {f["path"] for f in files} for x in v)]
    if ev:
        print("\n## 환경 변수: " + ", ".join(ev))


def show_signals():
    raw = load_raw()
    s = raw["signals"]
    print("## 비밀값 의심 위치 (값은 직접 열어 확인, 문서에 값 기록 금지)")
    print("\n".join("- " + x for x in s["secrets_suspect"][:40]) or "- 없음")
    print("\n## 같은 이름이 여러 파일에 정의됨 (중복 구현 후보)")
    for k, v in list(s["duplicates"].items())[:40]:
        print(f"- {k}: {', '.join(v[:5])}")
    print("\n## 아무도 import하지 않는 파일 (죽은 코드 후보, 동적 로딩일 수 있음)")
    print("\n".join("- " + x for x in s["orphans"][:60]) or "- 없음")
    print("\n## 잔해 파일 이름 (old/backup/copy/v2 등)")
    print("\n".join("- " + x for x in s["leftovers"][:40]) or "- 없음")
    print("\n## 큰 파일")
    print("\n".join(f"- {f} ({n}줄)" for f, n in s["big_files"][:25]) or "- 없음")
    print("\n## TODO/FIXME 많은 파일")
    print("\n".join(f"- {f} ({n})" for f, n in s["todo_files"][:25]) or "- 없음")


def find_text(root, text, limit):
    raw = load_raw()
    hits = 0
    for f in raw["files"]:
        for i, line in enumerate(read_lines(root, f["path"]), 1):
            if text in line:
                print(f"{f['path']}:{i} [{f['module']}] {line.strip()[:120]}")
                hits += 1
                if hits >= limit:
                    print(f"... {limit}개에서 멈춤 (--limit 로 조정)")
                    return
    if not hits:
        print("찾지 못함")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="vibemap 추출기")
    ap.add_argument("--root", default=".", help="프로젝트 루트 (기본: 현재 폴더)")
    ap.add_argument("--module", help="모듈 하나의 상세를 출력")
    ap.add_argument("--signals", action="store_true", help="이슈 후보 상세 출력")
    ap.add_argument("--find", help="문자열이 나오는 위치 찾기 (화면 문구, 에러 메시지 등)")
    ap.add_argument("--limit", type=int, default=30)
    ap.add_argument("--max-syms", type=int, default=10)
    ap.add_argument("--max-files", type=int, default=25)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if a.module:
        show_module(a.module, a.max_syms, a.max_files)
    elif a.signals:
        show_signals()
    elif a.find:
        find_text(root, a.find, a.limit)
    else:
        extract(root)
