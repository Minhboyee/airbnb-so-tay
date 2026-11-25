"""Sơ đồ luồng (SVG) vẽ lại từ airbnb_flow.pdf. Mỗi ô có href thì bấm được, nhảy tới dòng code.

Toạ độ tính bằng đơn vị viewBox. Kiểu ô: in (dữ liệu vào), proc (bước xử lý), llm (LLM / nhãn),
out (kết quả ghi ra), dec (điều kiện, hình thoi), note (ghi chú). Thêm "ph" để viền đỏ (căn ảo).
"""

from __future__ import annotations

import html

_uid = [0]


class D:
    def __init__(self, w: int, h: int, label: str, narrow: bool = False):
        self.w, self.h, self.label, self.narrow = w, h, label, narrow
        self.nodes: dict[str, tuple] = {}
        self.parts: list[str] = []
        self.edges: list[str] = []
        _uid[0] += 1
        self.mid = f"ar{_uid[0]}"

    # ---- ô
    def box(self, nid, x, y, w, h, kind, lines, href=None):
        self.nodes[nid] = ("box", x, y, w, h)
        kinds = kind.split()
        shape = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7"/>'
        self._node(nid, kinds, shape, x + w / 2, y + h / 2, lines, href)
        return self

    def dec(self, nid, cx, cy, w, h, lines, href=None):
        self.nodes[nid] = ("dec", cx - w / 2, cy - h / 2, w, h)
        pts = f"{cx},{cy - h / 2} {cx + w / 2},{cy} {cx},{cy + h / 2} {cx - w / 2},{cy}"
        self._node(nid, ["dec"], f'<polygon points="{pts}"/>', cx, cy, lines, href)
        return self

    def _node(self, nid, kinds, shape, cx, cy, lines, href):
        n = len(lines)
        lh = 15
        texts = []
        for i, line in enumerate(lines):
            cls = ""
            if line.startswith("`"):
                line, cls = line[1:], "mono"
            elif line.startswith("~"):
                line, cls = line[1:], "sm"
            elif line.startswith("*"):
                line, cls = line[1:], "b"
            y = cy + (i - (n - 1) / 2) * lh
            style = ' style="font-weight:700"' if cls == "b" else ""
            c = f' class="{cls}"' if cls in ("mono", "sm") else ""
            texts.append(f'<text x="{cx:.1f}" y="{y:.1f}"{c}{style}>{html.escape(line)}</text>')
        g = f'<g class="n {" ".join(kinds)}">{shape}{"".join(texts)}</g>'
        if href:
            title = html.escape(" ".join(l.lstrip("`~*") for l in lines))
            g = f'<a href="{href}" aria-label="{title}">{g}</a>'
        self.parts.append(g)

    # ---- cạnh
    def _anchor(self, nid, side):
        kind, x, y, w, h = self.nodes[nid]
        return {
            "r": (x + w, y + h / 2), "l": (x, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
        }[side]

    def edge(self, a, b, sa="r", sb="l", via=(), label=None, lpos=None, dash=False):
        pts = [self._anchor(a, sa), *via, self._anchor(b, sb)]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        cls = "e dash" if dash else "e"
        self.edges.append(f'<path class="{cls}" d="{d}" marker-end="url(#{self.mid})"/>')
        if label:
            if lpos is None:
                (x1, y1), (x2, y2) = pts[0], pts[1]
                lpos = ((x1 + x2) / 2, (y1 + y2) / 2 - 9)
            self.edges.append(f'<text class="lbl" x="{lpos[0]:.1f}" y="{lpos[1]:.1f}">{html.escape(label)}</text>')
        return self

    def svg(self):
        marker = (
            f'<defs><marker id="{self.mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>'
        )
        cls = "diagram narrow" if self.narrow else "diagram"
        return (
            f'<div class="{cls}"><svg class="dg" viewBox="0 0 {self.w} {self.h}" role="img" '
            f'aria-label="{html.escape(self.label)}">{marker}{"".join(self.edges)}{"".join(self.parts)}</svg></div>'
        )


LEGEND = (
    '<div class="dlegend"><span><i class="in"></i>dữ liệu vào</span><span><i class="proc"></i>bước xử lý</span>'
    '<span><i class="llm"></i>bước dùng LLM / nhãn</span><span><i class="out"></i>kết quả ghi ra</span>'
    '<span><i class="dec"></i>điều kiện</span><span>Nét liền: thứ tự chạy · nét đứt: file được ghi · bấm ô để xem code</span></div>'
)


# ---------------------------------------------------------------- Mức 0
def overview():
    d = D(1000, 470, "Toàn cảnh pipeline: tải, QA, chia nhóm, LLM, chấm LLM, KPI, vẽ hình")
    d.box("src", 10, 20, 180, 70, "in", ["Inside Airbnb", "~4 mốc × 3 bảng", "~listings · calendar · reviews"])
    d.box("ids", 10, 120, 180, 70, "in", ["ID chính thức của nhóm", "`data/samples/*.csv", "~1.000 listing · 5.000 review"])
    d.box("s1", 225, 70, 120, 54, "proc", ["*1. Tải & lọc", "`download.py"], "#buoc-1")
    d.box("s2", 375, 70, 100, 54, "proc", ["*2. QA", "`qa.py"], "#buoc-2")
    d.box("s3", 505, 70, 150, 54, "proc", ["*3. Chia 7 nhóm căn", "`segments/"], "#buoc-3")
    d.box("s4", 690, 62, 150, 70, "llm", ["*4. LLM gán nhãn", "`llm.py", "~Gemini"], "#buoc-4")
    d.box("s4b", 840, 215, 150, 54, "llm", ["*4b. LLM × nhóm căn", "`llm_segments.py"], "#f-llm_segments")
    d.box("s4c", 640, 207, 160, 70, "llm", ["*4c. Chấm LLM", "`evaluate.py", "~so với nhãn tay"], "#f-evaluate")
    d.box("s5", 490, 215, 110, 54, "proc", ["*5. KPI", "`kpi.py"], "#buoc-5")
    d.box("s6", 300, 207, 150, 70, "proc", ["*6. Vẽ hình", "`viz.py", "`viz_phantom.py"], "#buoc-6")
    d.box("o2", 330, 160, 190, 30, "out", ["`reports/qa_report.csv"], "#f-qa")
    d.box("o4c", 630, 320, 180, 34, "out", ["`reports/evaluation/"], "#f-eval_report")
    d.box("o5", 455, 315, 180, 62, "out", ["`data/processed/", "`kpi_metrics.csv", "`kpi_phantom.csv"], "#kpi-L898")
    d.box("o6", 300, 320, 150, 44, "out", ["`figures/", "16 hình PNG"], "#buoc-6")
    d.box("orc", 10, 260, 250, 70, "note", ["`run_pipeline.py", "chỉ điều phối, gọi lần lượt", "các bước theo thứ tự này"], "#buoc-0")
    d.edge("src", "s1", via=[(205, 55), (205, 90)], sb="l")
    d.edge("ids", "s1", via=[(205, 155), (205, 105)], sb="l")
    d.edge("s1", "s2").edge("s2", "s3").edge("s3", "s4")
    d.edge("s4", "s4b", sa="r", sb="t", via=[(915, 97)])
    d.edge("s4b", "s4c", sa="l", sb="r")
    d.edge("s4c", "s5", sa="l", sb="r")
    d.edge("s5", "s6", sa="l", sb="r")
    d.edge("s2", "o2", sa="b", sb="t", dash=True, via=[(425, 160)])
    d.edge("s4c", "o4c", sa="b", sb="t", dash=True)
    d.edge("s5", "o5", sa="b", sb="t", dash=True)
    d.edge("s6", "o6", sa="b", sb="t", dash=True)
    return d.svg() + LEGEND


# ---------------------------------------------------------------- 2A
def step1():
    d = D(1000, 260, "Bước 1: tải, kiểm raw, lọc theo ID")
    d.box("loop", 10, 95, 150, 54, "proc", ["Mỗi mốc × 4 file", "`download_file()"], "#download-L108")
    d.dec("have", 260, 122, 150, 84, ["Đã có file", "đúng dung lượng?"], "#download-L108")
    d.box("skip", 350, 20, 140, 44, "out", ["`[SKIP]", "dùng file cũ"], "#download-L108")
    d.box("get", 350, 180, 140, 60, "proc", ["Tải vào `.part`", "thử lại ≤ 3 lần", "rồi đổi tên"], "#download-L95")
    d.box("ver", 525, 95, 150, 60, "proc", ["`verify_raw()", "đủ 3 bảng + geojson,", "có cột khoá"], "#download-L228")
    d.dec("city", 750, 125, 130, 80, ["ID nhóm có", "trong thành phố?"], "#download-L313")
    d.box("grp", 820, 15, 130, 56, "proc", ["Lọc theo ID", "chính thức", "`source=group"], "#download-L471")
    d.box("seed", 820, 185, 130, 56, "proc", ["Chọn mẫu theo", "`seed=42", "`source=seed"], "#download-L290")
    d.box("out", 870, 98, 125, 56, "out", ["`data/processed/", "`sydney/<mốc>/", "~3 bảng + snapshot"], "#download-L461")
    d.edge("loop", "have", sb="l")
    d.edge("have", "skip", sa="t", sb="l", via=[(260, 42)], label="có", lpos=(300, 32))
    d.edge("have", "get", sa="b", sb="l", via=[(260, 210)], label="chưa", lpos=(300, 222))
    d.edge("skip", "ver", sa="r", sb="t", via=[(600, 42)])
    d.edge("get", "ver", sa="r", sb="b", via=[(600, 210)])
    d.edge("ver", "city", sb="l")
    d.edge("city", "grp", sa="t", sb="l", via=[(750, 43)], label="có", lpos=(770, 60))
    d.edge("city", "seed", sa="b", sb="l", via=[(750, 213)], label="không", lpos=(778, 196))
    d.edge("grp", "out", sa="b", sb="t", via=[(885, 85), (932, 85)])
    d.edge("seed", "out", sa="t", sb="b", via=[(885, 168), (932, 168)])
    return d.svg() + LEGEND


# ---------------------------------------------------------------- 2B
def step2():
    d = D(1000, 220, "Bước 2: ràng buộc mẫu rồi gắn cờ")
    d.box("in", 10, 80, 140, 54, "in", ["Bảng đã lọc", "của mốc k"])
    d.dec("ok", 270, 107, 170, 90, ["Khớp ràng buộc", "mẫu của đề?"], "#qa_constraints-L113")
    d.box("stop", 380, 10, 170, 50, "proc", ["`QAConstraintError", "dừng pipeline"], "#qa_constraints-L18")
    d.box("rules", 420, 80, 150, 54, "proc", ["`apply_rules()", "7 cờ theo dòng"], "#qa_rules-L578")
    d.box("agg", 610, 80, 150, 54, "proc", ["Gộp 3 cờ tổng", "~error · excl_price · warning"], "#qa_rules-L532")
    d.box("rep", 800, 30, 190, 54, "out", ["`qa_report.csv", "~nhật ký luật + KPI trước/sau"], "#qa-L103")
    d.box("ram", 800, 120, 190, 64, "out", ["Bảng có cờ (trong RAM)", "→ KPI bước 5 mới loại dòng"], "#run_pipeline-L144")
    d.edge("in", "ok", sb="l")
    d.edge("ok", "stop", sa="t", sb="l", via=[(270, 35)], label="không", lpos=(300, 25))
    d.edge("ok", "rules", label="có", lpos=(375, 96))
    d.edge("rules", "agg")
    d.edge("agg", "rep", sb="l", via=[(780, 107), (780, 57)], dash=True)
    d.edge("agg", "ram", sb="l", via=[(780, 107), (780, 152)])
    return d.svg() + LEGEND


# ---------------------------------------------------------------- 2C
def step3():
    d = D(1000, 560, "Bước 3: luật 7 nhóm, điều kiện nào đúng trước thì thắng", narrow=True)
    x = 230
    d.dec("c1", x, 60, 220, 84, ["`availability_365", "≤ 0 (kín lịch)?"], "#seg_rules-L80")
    d.dec("c1b", 560, 60, 190, 80, ["Có review trong", "365 ngày?"], "#seg_rules-L79")
    d.box("ghost", 760, 8, 190, 46, "out ph", ["*B_ghost", "~khoá lịch, không review"], "#seg_rules-L85")
    d.box("booked", 760, 68, 190, 46, "out", ["*B_booked", "~kín lịch, vẫn có review"], "#seg_rules-L86")
    d.dec("c2", x, 175, 240, 84, ["Có review nhưng review", "cuối > 365 ngày?"], "#seg_rules-L87")
    d.box("dorm", 560, 152, 160, 46, "out ph", ["*D_dormant", "~ngủ đông"], "#seg_rules-L87")
    d.dec("c3", x, 285, 150, 64, ["0 review?"], "#seg_rules-L88")
    d.dec("c3b", 560, 285, 190, 80, ["Đã thấy ở mốc", "cách ≥ 150 ngày?"], "#seg_rules-L96")
    d.box("never", 760, 238, 190, 46, "out ph", ["*D_never", "~chưa từng có review"], "#seg_rules-L88")
    d.box("new", 760, 298, 190, 46, "out", ["*N_new", "~mới / chưa đủ dữ liệu"], "#seg_rules-L89")
    d.dec("c4", x, 400, 240, 84, ["Mở ≥ 180 ngày và", "1–3 review / 12 tháng?"], "#seg_rules-L90")
    d.box("low", 560, 377, 160, 46, "out", ["*L_low", "~mở nhiều, ít review"], "#seg_rules-L90")
    d.box("ok", x - 85, 490, 170, 46, "out", ["*H_healthy", "~khoẻ mạnh (phần còn lại)"], "#seg_rules-L93")
    d.edge("c1", "c1b", label="có", lpos=(400, 50))
    d.edge("c1b", "ghost", sa="r", sb="l", via=[(675, 60), (720, 60), (720, 31)], label="không", lpos=(740, 22))
    d.edge("c1b", "booked", sa="r", sb="l", via=[(675, 60), (720, 60), (720, 91)], label="có", lpos=(735, 104))
    d.edge("c1", "c2", sa="b", sb="t", label="không", lpos=(x + 22, 118))
    d.edge("c2", "dorm", label="có", lpos=(450, 165))
    d.edge("c2", "c3", sa="b", sb="t", label="không", lpos=(x + 22, 232))
    d.edge("c3", "c3b", label="có", lpos=(395, 275))
    d.edge("c3b", "never", sa="r", sb="l", via=[(675, 285), (720, 285), (720, 261)], label="có", lpos=(735, 250))
    d.edge("c3b", "new", sa="r", sb="l", via=[(675, 285), (720, 285), (720, 321)], label="không", lpos=(740, 334))
    d.edge("c3", "c4", sa="b", sb="t", label="không", lpos=(x + 22, 336))
    d.edge("c4", "low", label="có", lpos=(450, 390))
    d.edge("c4", "ok", sa="b", sb="t", label="không", lpos=(x + 22, 462))
    return d.svg() + (
        '<div class="dlegend"><span><i class="ph"></i>căn ảo (B_ghost, D_dormant, D_never)</span>'
        '<span><i class="dec"></i>điều kiện, xét từ trên xuống</span><span>Bấm ô để xem đúng dòng điều kiện trong <code>rules.py</code></span></div>'
    )


# ---------------------------------------------------------------- 2D
def step4():
    d = D(1000, 220, "Bước 4: LLM gán nhãn có cache")
    d.box("in", 10, 70, 170, 66, "in", ["Mẫu 1.000 review", "`mau_llm = x", "~bỏ review rỗng / quá ngắn"], "#llm-L92")
    d.dec("hit", 290, 103, 170, 84, ["Review đã có", "trong cache?"], "#llm-L158")
    d.box("reuse", 420, 10, 160, 50, "out", ["Dùng nhãn cũ", "không gọi API"], "#llm-L338")
    d.box("call", 420, 130, 160, 66, "llm", ["Lô 10 review", "→ Gemini", "~nghỉ 4,2 giây / lô"], "#llm-L247")
    d.box("val", 620, 120, 170, 76, "llm", ["Kiểm bằng pydantic:", "JSON, aspect hợp lệ,", "đủ id, không lặp"], "#llm-L67")
    d.box("cache", 820, 75, 170, 66, "out", ["`llm_cache_pydantic", "`.jsonl", "~ghi nối, 1 dòng / review"], "#llm-L186")
    d.edge("in", "hit", sb="l")
    d.edge("hit", "reuse", sa="t", sb="l", via=[(290, 35)], label="có", lpos=(320, 25))
    d.edge("hit", "call", sa="b", sb="l", via=[(290, 163)], label="chưa", lpos=(325, 176))
    d.edge("call", "val")
    d.edge("val", "cache", sa="r", sb="b", via=[(905, 158)], dash=True)
    return d.svg() + LEGEND


# ---------------------------------------------------------------- 2E
def step4bc():
    d = D(1000, 330, "Bước 4b nối nhãn với nhóm căn; 4c chấm LLM bằng nhãn tay")
    d.box("t4b", 10, 5, 400, 24, "note", ["*4b · Khía cạnh bị chê, theo nhóm căn"])
    d.box("c", 10, 50, 130, 54, "in", ["Cache LLM", "`review_id"])
    d.box("j1", 175, 50, 140, 54, "proc", ["`review_id", "→ `listing_id"], "#llm_segments-L31")
    d.box("j2", 350, 42, 170, 70, "proc", ["Nhóm căn ở mốc cuối", "`segments_<scope>.csv"], "#llm_segments-L114")
    d.box("sum", 555, 42, 170, 70, "proc", ["`summarize()", "đếm review chê", "từng aspect / nhóm"], "#llm_segments-L31")
    d.box("o4b", 760, 42, 230, 70, "out", ["`llm_segment_aspects.csv", "mẫu số = số review", "của nhóm (không phải số căn)"], "#llm_segments-L139")
    d.box("t4c", 10, 145, 400, 24, "note", ["*4c · Chấm điểm trên 100 nhãn tay"])
    d.box("gold", 10, 210, 150, 66, "llm", ["Nhãn tay", "`hand_labels.csv", "~100 review"], "#evaluate-L51")
    d.box("bl", 220, 180, 170, 54, "proc", ["Baseline từ khoá", "`baseline.py"], "#baseline-L51")
    d.box("llm", 220, 255, 170, 54, "llm", ["LLM (đọc cache)", "`llm_predictions()"], "#evaluate-L161")
    d.box("score", 450, 200, 210, 90, "proc", ["`score_method()", "accuracy sentiment", "micro P/R/F1 aspect", "kappa · Wilson · bootstrap"], "#evaluate-L191")
    d.box("o4c", 720, 195, 270, 100, "out", ["`reports/evaluation/", "`eval_summary.csv", "`eval_aspects.csv · eval_errors.md", "`figures/evaluation/"], "#eval_report-L135")
    d.edge("c", "j1").edge("j1", "j2").edge("j2", "sum").edge("sum", "o4b", dash=True)
    d.edge("gold", "bl", sb="l", via=[(190, 243), (190, 207)])
    d.edge("gold", "llm", sb="l", via=[(190, 243), (190, 282)])
    d.edge("bl", "score", sb="l", via=[(420, 207), (420, 245)])
    d.edge("llm", "score", sb="l", via=[(420, 282), (420, 245)])
    d.edge("score", "o4c", dash=True)
    return d.svg() + LEGEND


# ---------------------------------------------------------------- 2F (bước 5)
def step5():
    d = D(1000, 300, "Bước 5: KPI thường, KPI LLM và KPI căn ảo")
    d.box("in", 10, 30, 190, 54, "in", ["Bảng listings, calendar", "đã gắn cờ QA (RAM)"], "#run_pipeline-L180")
    d.box("keep", 240, 22, 200, 70, "proc", ["Giữ dòng", "`qa_has_error_excl_price", "= False"], "#kpi-L849")
    d.box("reg", 480, 22, 200, 70, "proc", ["`compute_regular_kpis", "mỗi KPI một hàm nhỏ", "→ (giá trị, n_obs)"], "#kpi-L613")
    d.box("cache", 240, 120, 200, 54, "llm", ["Cache LLM", "~chỉ review của nhóm"], "#kpi-L835")
    d.box("llmk", 480, 120, 200, 54, "llm", ["2 KPI LLM", "`compute_llm_kpis"], "#kpi-L776")
    d.box("km", 740, 60, 250, 70, "out", ["`kpi_metrics.csv", "~snapshot, scope, group_name,", "~kpi_name, value, n_obs"], "#kpi-L898")
    d.box("segf", 240, 215, 200, 60, "in", ["`segments_full.csv", "+ `data/raw"], "#kpi-L81")
    d.box("ph", 480, 215, 200, 60, "proc", ["`run_phantom", "~chỉ khi scope full"], "#kpi-L980")
    d.box("kp", 740, 215, 250, 60, "out", ["`kpi_phantom.csv"], "#kpi-L525")
    d.edge("in", "keep").edge("keep", "reg").edge("reg", "km", dash=True, sb="l", via=[(710, 57), (710, 95)])
    d.edge("cache", "llmk").edge("llmk", "km", dash=True, sb="l", via=[(710, 147), (710, 95)])
    d.edge("segf", "ph").edge("ph", "kp", dash=True)
    return d.svg() + LEGEND


# ---------------------------------------------------------------- 2F (bước 6)
def step6():
    d = D(1000, 200, "Bước 6: vẽ hình từ CSV")
    d.box("km", 10, 20, 200, 54, "out", ["`kpi_metrics.csv"])
    d.box("viz", 260, 20, 200, 54, "proc", ["`viz.run()", "8 hình KPI"], "#viz-L373")
    d.box("f1", 510, 20, 230, 54, "out", ["`figures/01..08_*.png"], "#viz-L59")
    d.box("ins", 10, 110, 200, 76, "out", ["CSV bước 3, 4b, 5b", "~segments_*, llm_segment_aspects,", "~kpi_phantom"])
    d.box("vp", 260, 115, 200, 64, "proc", ["`viz_phantom.run()", "8 hình câu chuyện", "~thiếu file thì bỏ hình đó"], "#viz_phantom-L929")
    d.box("f2", 510, 120, 230, 54, "out", ["`figures/phantom/*.png"], "#viz_phantom-L894")
    d.box("rule", 780, 40, 210, 120, "note", ["Quy tắc:", "chỉ đọc CSV do pipeline ghi,", "không gõ số tay;", "file có mà sai cột thì dừng"])
    d.edge("km", "viz").edge("viz", "f1", dash=True)
    d.edge("ins", "vp").edge("vp", "f2", dash=True)
    return d.svg() + LEGEND
