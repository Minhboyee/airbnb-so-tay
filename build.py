"""Sinh sổ tay ôn tập (một file index.html) từ code ở tag `final` và các file chú giải.

Chạy từ thư mục gốc repo:
    python build.py              # dựng index.html
    python build.py --check qa   # chỉ kiểm file chú giải notes/qa.md (phủ dòng, link)

Định dạng file chú giải: xem FORMAT.md.
"""

from __future__ import annotations

import argparse
import base64
import os
import html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from pygments import lex
from pygments.lexers import PythonLexer, TOMLLexer, YamlLexer
from pygments.token import Comment, Keyword, Name, Number, Operator, String, Token

HERE = Path(__file__).resolve().parent
# Code repo nhóm (tag final): biến AIRBNB_REPO, mặc định là thư mục anh em cạnh repo sổ tay.
REPO = Path(os.environ.get("AIRBNB_REPO", HERE.parent / "2627-LTXLDL-Airbnb-dse2049_2-Nhom6")).resolve()
if not (REPO / "run_pipeline.py").exists():
    sys.exit(f"Không thấy code repo nhóm ở {REPO}; đặt biến AIRBNB_REPO.")
sys.stdout.reconfigure(encoding="utf-8")  # Windows console mặc định cp1252
sys.path.insert(0, str(HERE))

import diagrams  # noqa: E402

# ---------------------------------------------------------------- danh mục file
# id -> (đường dẫn trong repo, lexer)
FILES: dict[str, tuple[str, str]] = {
    "run_pipeline": ("run_pipeline.py", "py"),
    "config": ("src/config.py", "py"),
    "sydney_yaml": ("configs/sydney.yaml", "yaml"),
    "pyproject": ("pyproject.toml", "toml"),
    "ci": (".github/workflows/ci.yml", "yaml"),
    "download": ("src/download.py", "py"),
    "check_assignment": ("scripts/check_assignment_data.py", "py"),
    "qa": ("src/qa.py", "py"),
    "qa_constraints": ("src/qa_constraints.py", "py"),
    "qa_rules": ("src/qa_rules.py", "py"),
    "seg_init": ("src/segments/__init__.py", "py"),
    "seg_load": ("src/segments/load.py", "py"),
    "seg_rules": ("src/segments/rules.py", "py"),
    "seg_transitions": ("src/segments/transitions.py", "py"),
    "seg_report": ("src/segments/report.py", "py"),
    "llm": ("src/llm.py", "py"),
    "label_additional": ("scripts/label_additional_reviews.py", "py"),
    "llm_segments": ("src/llm_segments.py", "py"),
    "baseline": ("src/baseline.py", "py"),
    "metrics": ("src/metrics.py", "py"),
    "evaluate": ("src/evaluate.py", "py"),
    "eval_report": ("src/eval_report.py", "py"),
    "kpi": ("src/kpi.py", "py"),
    "viz": ("src/viz.py", "py"),
    "viz_phantom": ("src/viz_phantom.py", "py"),
}

# Trang (tab). kind: page = trang viết tay; step = trang bước có code.
# step: (id, nhãn tab, tiêu đề h1, danh sách file)
STEPS: list[tuple[str, str, str, list[str]]] = [
    ("buoc-0", "0 · Điều phối", "Điều phối: một lệnh chạy cả pipeline",
     ["run_pipeline", "config", "sydney_yaml", "pyproject", "ci"]),
    ("buoc-1", "1 · Tải & lọc", "Bước 1 — Tải và lọc dữ liệu", ["download", "check_assignment"]),
    ("buoc-2", "2 · QA", "Bước 2 — Kiểm tra chất lượng (QA)", ["qa", "qa_constraints", "qa_rules"]),
    ("buoc-3", "3 · 7 nhóm căn", "Bước 3 — Chia listing thành 7 nhóm",
     ["seg_init", "seg_load", "seg_rules", "seg_transitions", "seg_report"]),
    ("buoc-4", "4 · LLM", "Bước 4 — LLM gán nhãn review", ["llm", "label_additional"]),
    ("buoc-4bc", "4b·4c · Chấm LLM", "Bước 4b và 4c — LLM theo nhóm căn, chấm LLM bằng nhãn tay",
     ["llm_segments", "baseline", "metrics", "evaluate", "eval_report"]),
    ("buoc-5", "5 · KPI", "Bước 5 — KPI", ["kpi"]),
    ("buoc-6", "6 · Hình", "Bước 6 — Vẽ hình", ["viz", "viz_phantom"]),
]

PAGES_BEFORE = [("cau-chuyen", "Câu chuyện"), ("luong", "Luồng chính")]
PAGES_AFTER = [("kiem-thu", "Kiểm thử"), ("ly-thuyet", "Lý thuyết"), ("hoi-dap", "Hỏi đáp")]

STEP_OF = {fid: sid for sid, _, _, fids in STEPS for fid in fids}


# ---------------------------------------------------------------- tô màu code
def css_class(tok) -> str | None:
    if tok in Comment or tok is Comment:
        return "com"
    if tok in String:
        return "str"
    if tok in Number:
        return "num"
    if tok in Name.Builtin.Pseudo:
        return "kw"
    if tok in Keyword or tok in Operator.Word or tok in Name.Decorator:
        return "kw"
    if tok in Name.Builtin or tok in Name.Exception:
        return "bi"
    if tok in Name.Function or tok in Name.Class or tok in Name.Function.Magic:
        return "fn"
    if tok in Name.Tag:  # khoá yaml/toml
        return "fn"
    return None


def highlight(text: str, kind: str) -> list[str]:
    lexer = {"py": PythonLexer, "yaml": YamlLexer, "toml": TOMLLexer}[kind](stripnl=False, ensurenl=False)
    lines: list[str] = [""]
    for tok, val in lex(text, lexer):
        cls = css_class(tok)
        parts = val.split("\n")
        for i, part in enumerate(parts):
            if i:
                lines.append("")
            if part:
                esc = html.escape(part, quote=False)
                lines[-1] += f'<span class="{cls}">{esc}</span>' if cls else esc
    if text.endswith("\n") and lines and lines[-1] == "":
        lines.pop()
    return lines


# ---------------------------------------------------------------- đọc chú giải
@dataclass
class Note:
    fid: str
    title: str = ""
    lead: str = ""
    blocks: list[tuple[int, int, str]] = field(default_factory=list)
    flow: list[str] = field(default_factory=list)
    review: list[tuple[str, str, str]] = field(default_factory=list)
    qa: list[tuple[str, str]] = field(default_factory=list)


SECTION_RE = re.compile(r"^--- (meta|blocks|flow|review|qa)\s*$")
BLOCK_RE = re.compile(r"^=== (\d+)(?:-(\d+))?\s*$")


def parse_note(fid: str) -> Note:
    path = HERE / "notes" / f"{fid}.md"
    note = Note(fid)
    if not path.exists():
        return note
    section = None
    cur_block: list | None = None
    cur_q: list | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = SECTION_RE.match(raw)
        if m:
            section = m.group(1)
            cur_block = None
            cur_q = None
            continue
        if section == "meta":
            if raw.startswith("title:"):
                note.title = raw[6:].strip()
            elif raw.startswith("lead:"):
                note.lead = raw[5:].strip()
            elif raw.strip() and note.lead:
                note.lead += " " + raw.strip()
        elif section == "blocks":
            m = BLOCK_RE.match(raw)
            if m:
                a = int(m.group(1))
                b = int(m.group(2) or a)
                cur_block = [a, b, []]
                note.blocks.append(cur_block)  # type: ignore[arg-type]
            elif cur_block is not None:
                cur_block[2].append(raw)
        elif section == "flow":
            if raw.strip():
                note.flow.append(raw.rstrip())
        elif section == "review":
            if raw.strip():
                parts = [p.strip() for p in raw.split("|", 2)]
                if len(parts) == 3:
                    note.review.append((parts[0], parts[1], parts[2]))
                elif note.review:
                    t, ti, d = note.review[-1]
                    note.review[-1] = (t, ti, d + " " + raw.strip())
        elif section == "qa":
            if raw.startswith("? "):
                cur_q = [raw[2:].strip(), []]
                note.qa.append(cur_q)  # type: ignore[arg-type]
            elif cur_q is not None:
                cur_q[1].append(raw)
    note.blocks = [(a, b, "\n".join(body).strip()) for a, b, body in note.blocks]  # type: ignore[misc]
    note.qa = [(q, "\n".join(a).strip()) for q, a in note.qa]  # type: ignore[misc]
    return note


# ---------------------------------------------------------------- kiểm tra
class Problems(list):
    def add(self, msg: str) -> None:
        self.append(msg)


def source_lines(fid: str) -> list[str]:
    return (REPO / FILES[fid][0]).read_text(encoding="utf-8").splitlines()


def check_coverage(note: Note, probs: Problems) -> None:
    src = source_lines(note.fid)
    n = len(src)
    owner = [None] * (n + 1)
    prev_end = 0
    for a, b, body in note.blocks:
        if a < 1 or b > n or a > b:
            probs.add(f"{note.fid}: khối {a}-{b} ngoài phạm vi 1..{n}")
            continue
        if a <= prev_end:
            probs.add(f"{note.fid}: khối {a}-{b} chồng hoặc lùi so với khối trước (kết thúc {prev_end})")
        prev_end = max(prev_end, b)
        if not body:
            probs.add(f"{note.fid}: khối {a}-{b} chưa có giải thích")
        if not src[a - 1].strip():
            probs.add(f"{note.fid}: khối {a}-{b} bắt đầu bằng dòng trống (nên bắt đầu ở dòng có code)")
        for i in range(a, b + 1):
            owner[i] = a
    missing = [i for i in range(1, n + 1) if owner[i] is None and src[i - 1].strip()]
    if missing:
        # gom thành khoảng cho dễ đọc
        rng, start, last = [], missing[0], missing[0]
        for x in missing[1:]:
            if x != last + 1:
                rng.append((start, last))
                start = x
            last = x
        rng.append((start, last))
        txt = ", ".join(f"{s}" if s == e else f"{s}-{e}" for s, e in rng)
        probs.add(f"{note.fid}: dòng có code chưa được giải thích: {txt}")


# ---------------------------------------------------------------- dựng HTML
NOTES: dict[str, Note] = {}
BLOCK_STARTS: dict[str, list[tuple[int, int]]] = {}


def block_for(fid: str, line: int) -> int | None:
    src_n = len(source_lines(fid))
    if line < 1 or line > src_n:
        return None
    best = None
    for a, b in BLOCK_STARTS.get(fid, []):
        if a <= line:
            best = a
        if a > line:
            break
    return best or 1


LINK_RE = re.compile(r'href="#([a-z0-9_]+)-L(\d+)"')


def resolve_links(text: str, probs: Problems, where: str) -> str:
    def sub(m: re.Match) -> str:
        fid, line = m.group(1), int(m.group(2))
        if fid not in FILES:
            probs.add(f"{where}: link tới file lạ #{fid}-L{line}")
            return m.group(0)
        b = block_for(fid, line)
        if b is None:
            probs.add(f"{where}: link #{fid}-L{line} ngoài phạm vi file")
            return m.group(0)
        return f'href="#{fid}-L{b}"'

    return LINK_RE.sub(sub, text)


def where_label(a: int, b: int) -> str:
    return f"Dòng {a}" if a == b else f"Dòng {a}–{b}"


def render_code(fid: str, probs: Problems) -> str:
    path, kind = FILES[fid]
    text = (REPO / path).read_text(encoding="utf-8")
    hl = highlight(text, kind)
    src = text.splitlines()
    if len(hl) != len(src):
        probs.add(f"{fid}: lệch số dòng khi tô màu ({len(hl)} vs {len(src)})")
    note = NOTES[fid]
    blocks = {a: (b, body) for a, b, body in note.blocks}
    out = [f'<div class="code" data-file="{fid}">']
    i = 1
    n = len(src)
    open_blk = False

    def line_html(k: int) -> str:
        code = hl[k - 1] if k - 1 < len(hl) else ""
        return f'<span class="l"><span class="ln">{k}</span>{code or " "}</span>'

    while i <= n:
        if i in blocks:
            if open_blk:
                out.append("</div>")
            b, body = blocks[i]
            rng = f"dòng {i}" if i == b else f"dòng {i}–{b}"
            out.append(
                f'<div class="blk" id="{fid}-L{i}"><div class="lines" role="button" tabindex="0" '
                f'aria-expanded="false" aria-label="{rng}: xem giải thích">'
            )
            out.extend(line_html(k) for k in range(i, b + 1))
            body = resolve_links(body, probs, f"{fid} khối {i}")
            out.append(f'</div><div class="expl" hidden><p class="where">{where_label(i, b)}</p>{body}</div>')
            open_blk = True
            i = b + 1
        else:
            if not open_blk:
                # dòng ngoài khối ở đầu file (chỉ có thể là dòng trống)
                out.append(f'<div class="blk plain" id="{fid}-L{i}">')
                open_blk = True
            out.append(line_html(i))
            i += 1
    if open_blk:
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def render_flow(fid: str, probs: Problems) -> str:
    note = NOTES[fid]
    if not note.flow:
        return ""
    name = Path(FILES[fid][0]).name
    items = []
    for line in note.flow:
        if line.startswith("## "):
            items.append(f'<div class="grp">{html.escape(line[3:].strip())}</div>')
            continue
        m = re.match(r"^(fn|st)\s+(\d+)\s+(\d+)\s*\|\s*(.*?)\s*\|\s*(.*)$", line)
        if m:
            kind, d, ln, title, desc = m.groups()
            b = block_for(fid, int(ln))
            if b is None:
                probs.add(f"{fid} flow: dòng {ln} ngoài phạm vi")
                continue
            items.append(
                f'<a class="node fp {kind}" style="--d:{d}" href="#{fid}-L{b}"><b>{title}</b>'
                f"<span>{desc}</span></a>"
            )
            continue
        m = re.match(r"^chips\s+(\d+)\s*\|\s*(.*)$", line)
        if m:
            d, rest = m.groups()
            chips = []
            for part in rest.split(";"):
                part = part.strip()
                if not part:
                    continue
                mm = re.match(r"^(?:([a-z0-9_]+):)?(\d+)\s+(.+)$", part)
                if not mm:
                    probs.add(f"{fid} flow: chip sai định dạng '{part}'")
                    continue
                cf, ln, label = mm.group(1) or fid, int(mm.group(2)), mm.group(3)
                if cf not in FILES:
                    probs.add(f"{fid} flow: chip tới file lạ '{cf}'")
                    continue
                b = block_for(cf, ln)
                if b is None:
                    probs.add(f"{fid} flow: chip {cf}:{ln} ngoài phạm vi")
                    continue
                chips.append(f'<a class="chip fp" href="#{cf}-L{b}">{html.escape(label)}</a>')
            items.append(f'<div class="chips" style="--d:{d}">{"".join(chips)}</div>')
            continue
        probs.add(f"{fid} flow: dòng không hiểu '{line}'")
    return (
        f'<aside class="flowpane" aria-label="Luồng của {name}"><h3>Luồng của {name}</h3>'
        '<div class="legend"><span><i class="f"></i>hàm</span><span><i class="s"></i>bước trong hàm</span></div>'
        f'<div class="flow">{"".join(items)}</div></aside>'
    )


def render_file(fid: str, probs: Problems) -> str:
    path = FILES[fid][0]
    note = NOTES[fid]
    n = len(source_lines(fid))
    lead = resolve_links(note.lead, probs, f"{fid} lead")
    return (
        f'<section class="filesec" id="f-{fid}">'
        f'<div class="filehead"><h2><code class="fname">{html.escape(path)}</code></h2>'
        f'{f"<p class=lead>{lead}</p>" if lead else ""}</div>'
        f'<div class="split"><section class="code-col">'
        f'<div class="codebar"><span class="path">{html.escape(path)} · {n} dòng</span>'
        '<span class="btns"><button class="b" data-all="open">Mở hết giải thích</button>'
        '<button class="b" data-all="close">Đóng hết</button></span></div>'
        f"{render_code(fid, probs)}</section>{render_flow(fid, probs)}</div></section>"
    )


FIG_RE = re.compile(r"\{\{fig:([^|}]+)(?:\|([^}]*))?\}\}")
DIAG_RE = re.compile(r"\{\{diagram:([a-z0-9_]+)\}\}")


def expand(text: str, probs: Problems, where: str) -> str:
    def fig(m: re.Match) -> str:
        rel, cap = m.group(1).strip(), (m.group(2) or "").strip()
        p = REPO / rel
        if not p.exists():
            probs.add(f"{where}: thiếu hình {rel}")
            return ""
        data = base64.b64encode(p.read_bytes()).decode()
        alt = html.escape(re.sub(r"<[^>]+>", "", cap) or rel)
        return (
            f'<figure class="fig"><img loading="lazy" src="data:image/png;base64,{data}" alt="{alt}">'
            f'<figcaption>{cap}<span class="src"><code>{html.escape(rel)}</code></span></figcaption></figure>'
        )

    def diag(m: re.Match) -> str:
        name = m.group(1)
        fn = getattr(diagrams, name, None)
        if fn is None:
            probs.add(f"{where}: thiếu sơ đồ {name}")
            return ""
        return fn()

    text = FIG_RE.sub(fig, text)
    text = DIAG_RE.sub(diag, text)
    return resolve_links(text, probs, where)


def page(pid: str, probs: Problems) -> str:
    p = HERE / "pages" / f"{pid}.html"
    if not p.exists():
        probs.add(f"thiếu trang pages/{pid}.html")
        return ""
    return expand(p.read_text(encoding="utf-8"), probs, f"pages/{pid}.html")


TAG = {"mid": ("tag mid", "Nên xem"), "low": ("tag", "Nhỏ"), "ok": ("tag ok", "Ổn"), "bug": ("tag bad", "Lỗi")}


def render_auto_qa(probs: Problems) -> tuple[str, str]:
    qa_parts, rev_rows = [], []
    for sid, label, title, fids in STEPS:
        qs = []
        for fid in fids:
            for q, a in NOTES[fid].qa:
                a = resolve_links(a, probs, f"{fid} qa")
                qs.append(
                    f'<details class="qa"><summary>{q}</summary><div class="ans">{a}'
                    f'<p class="muted">Xem: <a href="#f-{fid}">{html.escape(FILES[fid][0])}</a></p></div></details>'
                )
        if qs:
            qa_parts.append(f'<h3 class="qa-step"><a href="#{sid}">{html.escape(label)}</a></h3>'
                            f'<div class="qa-list">{"".join(qs)}</div>')
        for fid in fids:
            for t, ti, d in NOTES[fid].review:
                cls, txt = TAG.get(t, ("tag", t))
                d = resolve_links(d, probs, f"{fid} review")
                rev_rows.append(
                    f'<tr><td><span class="{cls}">{txt}</span></td><td>{ti}<br>'
                    f'<a class="muted" href="#f-{fid}">{html.escape(Path(FILES[fid][0]).name)}</a></td><td>{d}</td></tr>'
                )
    return "".join(qa_parts), "".join(rev_rows)


def build(out_path: Path) -> Problems:
    probs = Problems()
    for fid in FILES:
        NOTES[fid] = parse_note(fid)
        BLOCK_STARTS[fid] = sorted((a, b) for a, b, _ in NOTES[fid].blocks)
        check_coverage(NOTES[fid], probs)

    tabs = []
    views = []
    for pid, label in PAGES_BEFORE:
        tabs.append(f'<a href="#{pid}">{label}</a>')
        views.append(f'<div class="view" id="{pid}" data-view hidden>{page(pid, probs)}</div>')
    for sid, label, title, fids in STEPS:
        tabs.append(f'<a href="#{sid}">{html.escape(label)}</a>')
        intro = page(sid, probs)
        filenav = "".join(
            f'<a class="chip" href="#f-{f}"><code>{html.escape(Path(FILES[f][0]).name)}</code>'
            f'<span>{len(source_lines(f))} dòng</span></a>'
            for f in fids
        )
        files_html = "".join(render_file(f, probs) for f in fids)
        views.append(
            f'<div class="view file" id="{sid}" data-view hidden><div class="intro">{intro}'
            f'<nav class="filenav" aria-label="Các file của bước">{filenav}</nav></div>{files_html}</div>'
        )
    qa_html, rev_html = render_auto_qa(probs)
    for pid, label in PAGES_AFTER:
        tabs.append(f'<a href="#{pid}">{label}</a>')
        body = page(pid, probs).replace("{{auto_qa}}", qa_html).replace("{{auto_review}}", rev_html)
        views.append(f'<div class="view" id="{pid}" data-view hidden>{body}</div>')

    css = (HERE / "base.css").read_text(encoding="utf-8") + (HERE / "extra.css").read_text(encoding="utf-8")
    js = (HERE / "app.js").read_text(encoding="utf-8")
    shell = (HERE / "shell.html").read_text(encoding="utf-8")
    doc = (
        shell.replace("{{css}}", css)
        .replace("{{tabs}}", "\n".join(tabs))
        .replace("{{views}}", "\n".join(views))
        .replace("{{js}}", js)
    )

    # kiểm mọi link nội bộ
    ids = set(re.findall(r'\bid="([^"]+)"', doc))
    for target in set(re.findall(r'href="#([^"]*)"', doc)):
        if target and "${" not in target and target not in ids:
            probs.add(f"link hỏng: #{target}")
    out_path.write_text(doc, encoding="utf-8")
    return probs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", nargs="*", help="chỉ kiểm các file chú giải này (id)")
    ap.add_argument("--out", default=str(HERE / "index.html"))
    args = ap.parse_args()
    if args.check is not None:
        probs = Problems()
        ids = args.check or list(FILES)
        for fid in FILES:
            NOTES[fid] = parse_note(fid)
            BLOCK_STARTS[fid] = sorted((a, b) for a, b, _ in NOTES[fid].blocks)
        for fid in ids:
            note = NOTES[fid]
            check_coverage(note, probs)
            render_code(fid, probs)
            render_flow(fid, probs)
            resolve_links(note.lead, probs, f"{fid} lead")
            for _, _, d in note.review:
                resolve_links(d, probs, f"{fid} review")
            for _, a in note.qa:
                resolve_links(a, probs, f"{fid} qa")
            # thẻ HTML cân bằng (kiểm thô)
            for a, b, body in note.blocks:
                for tag in ("p", "ul", "ol", "li", "code", "b", "a", "table", "em"):
                    o = len(re.findall(rf"<{tag}[\s>]", body))
                    c = body.count(f"</{tag}>")
                    if o != c:
                        probs.add(f"{fid} khối {a}: thẻ <{tag}> mở {o} đóng {c}")
            print(f"{fid}: {len(note.blocks)} khối, {len(note.flow)} dòng flow, "
                  f"{len(note.review)} nhận xét, {len(note.qa)} câu hỏi")
        for p in probs:
            print("  !", p)
        print("OK" if not probs else f"{len(probs)} vấn đề")
        sys.exit(1 if probs else 0)
    probs = build(Path(args.out))
    for p in probs:
        print("  !", p)
    size = Path(args.out).stat().st_size
    print(f"Đã ghi {args.out} ({size/1e6:.2f} MB), {len(probs)} vấn đề")


if __name__ == "__main__":
    main()
