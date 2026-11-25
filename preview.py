"""Sinh pages/du-lieu.html: xem trước dữ liệu tải về, dữ liệu đã xử lý và đầu ra từng bước.

Chỉ ĐỌC repo nhóm (AIRBNB_REPO, mặc định thư mục anh em); QA và chia nhóm chạy lại trong bộ nhớ,
không ghi file nào vào repo nhóm. Cần data/raw và data/processed/sydney (bị gitignore, có ở máy
đã chạy pipeline).

    python preview.py      # rồi python build.py
"""

from __future__ import annotations

import gzip
import html
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # không để lại __pycache__ trong repo nhóm
HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("AIRBNB_REPO", HERE.parent / "2627-LTXLDL-Airbnb-dse2049_2-Nhom6")).resolve()
sys.path.insert(0, str(REPO))
os.chdir(REPO)  # code nhóm dùng đường dẫn tương đối

import pandas as pd  # noqa: E402

from run_pipeline import load_processed_tables  # noqa: E402
from src.config import load_config  # noqa: E402
from src.qa_rules import apply_rules  # noqa: E402
from src.segments.load import load_listings  # noqa: E402
from src.segments.rules import classify, seen_before_ids  # noqa: E402

CFG = load_config("configs/sydney.yaml")
SNAPS = [str(s) for s in CFG["snapshots"]]
LAST = SNAPS[-1]
RAW = Path("data/raw/sydney")
PROC = Path("data/processed/sydney")
ID = {"id": str, "listing_id": str, "host_id": str, "review_id": str, "reviewer_id": str}


def vn(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def cell(v, width: int = 38) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return '<td class="na">trống</td>'
    if isinstance(v, (bool,)) or str(v) in ("True", "False"):
        on = str(v) == "True"
        return f'<td class="flag{" on" if on else ""}">{"True" if on else "False"}</td>'
    s = str(v).replace("\n", " ")
    if len(s) > width:
        return f'<td title="{html.escape(s)}">{html.escape(s[:width - 1])}…</td>'
    return f"<td>{html.escape(s)}</td>"


def table(df: pd.DataFrame, widths: dict[str, int] | None = None, cls: str = "") -> str:
    widths = widths or {}
    head = "".join(f"<th>{html.escape(str(c))}</th>" for c in df.columns)
    body = "".join(
        "<tr>" + "".join(cell(v, widths.get(c, 38)) for c, v in zip(df.columns, row)) + "</tr>"
        for row in df.itertuples(index=False)
    )
    return f'<div class="tablewrap dp"><table class="dt {cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def meta(*parts: str) -> str:
    return '<p class="dmeta">' + " · ".join(parts) + "</p>"


def columns_list(cols) -> str:
    items = " ".join(f"<code>{html.escape(c)}</code>" for c in cols)
    return f'<details class="cols"><summary>Xem đủ {len(cols)} cột</summary><div>{items}</div></details>'


def size(p: Path) -> str:
    return f"{p.stat().st_size / 1e6:.1f} MB".replace(".", ",")


def gz_rows(p: Path) -> int:
    with gzip.open(p, "rt", encoding="utf-8") as f:
        return sum(1 for _ in f) - 1


out: list[str] = []
add = out.append

add("""<section class="head">
  <span class="kicker">Xem trước dữ liệu</span>
  <h1>Dữ liệu trông như thế nào</h1>
  <p class="lead">Mỗi bảng dưới đây chỉ lấy vài dòng và vài cột để xem hình dạng. Đi theo đúng thứ tự pipeline: file tải về, mẫu của đề, bảng sau bước 1, rồi bảng sau khi QA gắn cờ, chia nhóm, LLM gán nhãn và tính KPI.</p>
  <p class="muted">Ô có chữ cắt bằng dấu … thì rê chuột để xem đủ. Cột tên người (chủ nhà, người viết review) không đưa lên trang.</p>
</section>""")

# ---------------------------------------------------------------- 1. tải về
rows = []
for s in SNAPS:
    d = RAW / s
    lst = pd.read_csv(d / "listings.csv.gz", usecols=["id"], dtype=str)
    rows.append({"Mốc": s, "listings": vn(len(lst)), "calendar": vn(gz_rows(d / "calendar.csv.gz")),
                 "reviews": vn(gz_rows(d / "reviews.csv.gz")),
                 "Dung lượng (3 file nén)": f"{sum((d / f).stat().st_size for f in ['listings.csv.gz', 'calendar.csv.gz', 'reviews.csv.gz']) / 1e6:.0f} MB"})
raw_counts = pd.DataFrame(rows)

lst = pd.read_csv(RAW / LAST / "listings.csv.gz", dtype=ID, low_memory=False)
sample_ids = pd.read_csv("data/samples/listing_ids.csv", dtype=str)
pick = lst[lst["id"].isin(sample_ids["listing_id"])].head(5)
cal = pd.read_csv(RAW / LAST / "calendar.csv.gz", dtype=ID, nrows=400)
rev = pd.read_csv(RAW / LAST / "reviews.csv.gz", dtype=ID, nrows=4)
geo = json.load(open(RAW / LAST / "neighbourhoods.geojson", encoding="utf-8"))
areas = sorted(f["properties"]["neighbourhood"] for f in geo["features"])

add(f"""<section class="block">
  <h2>1. File tải về từ Inside Airbnb</h2>
  <p class="text">Mỗi mốc có 4 file: ba bảng nén <code>.csv.gz</code> và bản đồ ranh giới khu. Đây là toàn bộ thành phố, chưa lọc gì. Thư mục <code>data/raw/</code> bị gitignore theo yêu cầu đề, nên chỉ có ở máy đã tải (<a href="#download-L1">download.py</a>).</p>
  {table(raw_counts, cls="num")}
  <h3>listings.csv.gz</h3>
  <p class="text">Một dòng là một căn, chụp vào ngày của mốc. Cột giá ở hai mốc 2025 trống hoàn toàn.</p>
  {meta(f"mốc {LAST}", f"{vn(len(lst))} dòng × {lst.shape[1]} cột", size(RAW / LAST / "listings.csv.gz"))}
  {table(pick[["id", "name", "neighbourhood_cleansed", "room_type", "price", "minimum_nights", "availability_365", "number_of_reviews", "last_review", "license"]], {"name": 30})}
  {columns_list(lst.columns)}
  <h3>calendar.csv.gz</h3>
  <p class="text">Một dòng là một ngày của một căn, 365 ngày tới tính từ ngày chụp. <code>available</code> là <code>t</code> hoặc <code>f</code>: còn trống hay không.</p>
  {meta(f"{vn(int(raw_counts.iloc[-1]['calendar'].replace('.', '')))} dòng × {cal.shape[1]} cột", size(RAW / LAST / "calendar.csv.gz"))}
  {table(cal.head(5))}
  <h3>reviews.csv.gz</h3>
  <p class="text">Một dòng là một review, từ trước tới ngày chụp. File nặng nhất vì chứa toàn văn bình luận.</p>
  {meta(f"{raw_counts.iloc[-1]['reviews']} dòng × {rev.shape[1]} cột", size(RAW / LAST / "reviews.csv.gz"))}
  {table(rev[["listing_id", "id", "date", "comments"]], {"comments": 90}, cls="wide-last")}
  <h3>neighbourhoods.geojson</h3>
  <p class="text">{len(areas)} khu (LGA) của Sydney, dùng để nối căn với khu. Ví dụ: {", ".join(areas[:6])}…</p>
</section>""")

# ---------------------------------------------------------------- 2. mẫu đề
rid = pd.read_csv("data/samples/review_ids.csv", dtype=str)
hand = pd.read_csv("data/samples/hand_labels.csv", dtype=str)
area_counts = sample_ids["analysis_area"].value_counts().sort_index()
add(f"""<section class="block">
  <h2>2. Mẫu của đề</h2>
  <p class="text">Đề giao sẵn danh sách ID trong <code>data/samples/</code>. Bước 1 chỉ giữ đúng các căn và review có trong danh sách này.</p>
  <div class="dgrid">
    <div><h3>listing_ids.csv</h3>{meta(f"{vn(len(sample_ids))} căn", f"{len(area_counts)} vùng phân tích A01–A08")}{table(sample_ids.head(4))}</div>
    <div><h3>review_ids.csv</h3>{meta(f"{vn(len(rid))} review", f"mau_llm đánh x: {vn(rid['mau_llm'].notna().sum())}", f"nhan_tay đánh x: {vn(rid['nhan_tay'].notna().sum())}")}{table(pd.concat([rid[rid['nhan_tay'].notna()].head(2), rid[rid['mau_llm'].notna() & rid['nhan_tay'].isna()].head(1), rid[rid['mau_llm'].isna()].head(1)]))}</div>
  </div>
  <h3>hand_labels.csv</h3>
  <p class="text">100 review do nhóm gán nhãn tay, làm đáp án để chấm LLM (<a href="#f-evaluate">evaluate.py</a>).</p>
  {meta(f"{len(hand)} dòng", "positive " + str((hand['sentiment'] == 'positive').sum()), "mixed " + str((hand['sentiment'] == 'mixed').sum()), "negative " + str((hand['sentiment'] == 'negative').sum()))}
  {table(hand[["review_id", "comments", "sentiment", "aspects_positive", "aspects_negative"]].head(4), {"comments": 70}, cls="wide-2")}
</section>""")

# ---------------------------------------------------------------- 3. processed
tables = load_processed_tables(CFG)
proc_counts = pd.DataFrame([{"Mốc": s, "listings": vn(len(t["listings"])), "calendar": vn(len(t["calendar"])),
                             "reviews": vn(len(t["reviews"]))} for s, t in tables.items()])
pl = tables[LAST]["listings"]
extra_cols = [c for c in pl.columns if c not in lst.columns]
add(f"""<section class="block">
  <h2>3. Sau bước 1: bảng đã lọc theo mẫu</h2>
  <p class="text">Bước 1 lọc file thô theo danh sách ID của đề rồi ghi CSV thường vào <code>data/processed/sydney/&lt;mốc&gt;/</code>. Mỗi mốc còn đúng 1.000 căn, 365.000 ngày lịch và 5.000 review. Bảng listings thêm cột {", ".join(f"<code>{c}</code>" for c in extra_cols)}.</p>
  {table(proc_counts, cls="num")}
  {meta(f"listings mốc {LAST}", f"{vn(len(pl))} dòng × {pl.shape[1]} cột")}
  {table(pl[["id", "snapshot", "analysis_area", "room_type", "price", "minimum_nights", "availability_365", "number_of_reviews"]].head(4) if "analysis_area" in pl.columns else pl.head(4).iloc[:, :8])}
</section>""")

# ---------------------------------------------------------------- 4. QA
seen: dict[str, list[pd.DataFrame]] = {"listings": [], "reviews": []}
flagged = None
for s in SNAPS:
    prev = {k: pd.concat(v, ignore_index=True) for k, v in seen.items() if v}
    f, _ = apply_rules(tables[s], CFG["qa"], s, prev)
    for k in seen:
        seen[k].append(tables[s][k])
    if s == LAST:
        flagged = f
fl = flagged["listings"]
qa_cols = [c for c in fl.columns if c.startswith("qa_")]
flag_cols = [c for c in qa_cols if fl[c].dtype == bool and c not in ("qa_has_error", "qa_has_warning", "qa_has_error_excl_price")]
ex = pd.concat([fl[fl["qa_price_unusable"]].head(2), fl[fl["qa_price_outlier"] & ~fl["qa_price_unusable"]].head(2),
                fl[~fl[flag_cols].any(axis=1)].head(1)])
show = ["id", "price", "minimum_nights"] + [c for c in ["qa_price_unusable", "qa_price_outlier", "qa_has_error", "qa_has_warning", "qa_detail"] if c in fl.columns]
counts = pd.DataFrame([{c: vn(fl[c].sum()) for c in qa_cols if fl[c].dtype == bool}])
rep = pd.read_csv("reports/qa_report.csv", dtype=str)
rep_last = rep[(rep["snapshot"] == LAST) & rep["rule"].notna()][["table", "rule", "severity", "action", "n_rows", "n_flagged", "pct_flagged"]]
add(f"""<section class="block">
  <h2>4. Bước 2: QA gắn cờ</h2>
  <p class="text">QA không xoá dòng nào. Nó thêm cột <code>qa_*</code> kiểu True/False vào từng bảng; KPI về sau tự lọc theo cờ (<a href="#qa_rules-L578">apply_rules</a>). Dưới đây là listings mốc {LAST} sau khi gắn cờ, chọn 2 dòng giá không dùng được, 2 dòng giá ngoại lệ và 1 dòng sạch.</p>
  {meta(f"{len(qa_cols)} cột cờ được thêm", f"listings còn {vn(len(fl))} dòng, không dòng nào bị xoá")}
  {table(ex[show], {"qa_detail": 46}, cls="flags")}
  <h3>Số dòng bật mỗi cờ ở mốc này</h3>
  {table(counts, cls="num")}
  <h3>reports/qa_report.csv</h3>
  <p class="text">Một dòng mỗi luật mỗi mốc ({vn(len(rep))} dòng cả file). Đây là các luật của mốc {LAST}.</p>
  {table(rep_last, cls="num")}
</section>""")

# ---------------------------------------------------------------- 5. chia nhóm
frames = {s: load_listings(CFG, s, "full") for s in SNAPS}
last = frames[LAST].copy()
last["segment"] = classify(last, seen_before_ids(frames, LAST, int(CFG["segments"]["never_seen_days"])), CFG).values
order = ["B_ghost", "B_booked", "D_dormant", "D_never", "N_new", "L_low", "H_healthy"]
one = pd.concat([last[last["segment"] == g].head(1) for g in order])
one["last_review"] = pd.to_datetime(one["last_review"]).dt.strftime("%Y-%m-%d")
cols5 = [c for c in ["id", "availability_365", "number_of_reviews", "number_of_reviews_ltm", "last_review", "segment"] if c in one.columns]
cnt = pd.read_csv("data/processed/segments_counts_full.csv", dtype=str)
cnt = cnt[cnt["snapshot"] == LAST][["segment", "label_vi", "n", "share", "is_phantom"]]
add(f"""<section class="block">
  <h2>5. Bước 3: chia 7 nhóm</h2>
  <p class="text">Chạy trên cả thành phố (file thô), mỗi căn nhận đúng một cột <code>segment</code>. Mỗi nhóm một căn làm ví dụ, kèm các cột luật dùng để xếp (<a href="#seg_rules-L50">classify</a>).</p>
  {meta(f"mốc {LAST}", f"{vn(len(last))} căn")}
  {table(one[cols5], cls="seg")}
  <h3>data/processed/segments_counts_full.csv</h3>
  {table(cnt, cls="num")}
</section>""")

# ---------------------------------------------------------------- 6. LLM
cache = [json.loads(x) for x in open("data/processed/llm_cache_pydantic.jsonl", encoding="utf-8")]
cdf = pd.DataFrame(cache)
revs = pd.concat([t["reviews"] for t in tables.values()]).drop_duplicates("id").set_index("id")["comments"]
picks = pd.concat([cdf[cdf["sentiment"] == "positive"].head(1), cdf[cdf["sentiment"] == "mixed"].head(1),
                   cdf[cdf["has_complaint"]].iloc[1:2]])
picks = picks.assign(comments=picks["review_id"].map(revs),
                     positive_aspects=picks["positive_aspects"].map(", ".join),
                     negative_aspects=picks["negative_aspects"].map(", ".join))
ev = pd.read_csv("reports/evaluation/eval_per_review.csv", dtype=str)
ev = ev[ev["method"] == "llm"]
mism = ev[ev["gold_sentiment"] != ev["predicted_sentiment"]]
# mỗi trường một dòng, danh sách giữ trên một dòng cho gọn
json_line = "{\n" + ",\n".join(f"  {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in cache[0].items()) + "\n}"
add(f"""<section class="block">
  <h2>6. Bước 4: LLM gán nhãn review</h2>
  <p class="text">Gemini đọc từng review và trả JSON theo khuôn pydantic. Mỗi kết quả là một dòng trong <code>data/processed/llm_cache_pydantic.jsonl</code>; chạy lại thì đọc cache, không gọi API (<a href="#llm-L158">load_cache</a>).</p>
  {meta(f"{vn(len(cdf))} dòng cache", f"6 khía cạnh: {', '.join(cache[0]['aspect_vocabulary'])}")}
  {table(picks[["review_id", "comments", "sentiment", "positive_aspects", "negative_aspects", "has_complaint"]], {"comments": 80}, cls="wide-2")}
  <p class="text">Một dòng cache gốc:</p>
  <pre class="json">{html.escape(json_line)}</pre>
  <h3>Chấm với nhãn tay (reports/evaluation/eval_per_review.csv)</h3>
  <p class="text">Mỗi review trong 100 nhãn tay có một dòng cho từng phương pháp. Dưới đây là các review Gemini đoán sai cảm xúc ({len(mism)} trên {len(ev)}).</p>
  {table(mism[["review_id", "gold_sentiment", "predicted_sentiment", "missing_aspects", "extra_aspects", "comment_excerpt"]].head(4), {"comment_excerpt": 60}, cls="wide-last")}
</section>""")

# ---------------------------------------------------------------- 7. KPI
km = pd.read_csv("data/processed/kpi_metrics.csv", dtype=str)
km = km[(km["snapshot"] == LAST) & (km["scope"] == "overall")]
kp = pd.read_csv("data/processed/kpi_phantom.csv", dtype=str)
kp = kp[(kp["snapshot"] == LAST) & (kp["scope"] == "overall")]
add(f"""<section class="block">
  <h2>7. Bước 5: KPI</h2>
  <p class="text">Hai file KPI cùng một khuôn dài: mỗi dòng là một chỉ số ở một mốc, một phạm vi, kèm <code>n_obs</code> là mẫu số. Đây là các dòng <code>scope = overall</code> của mốc {LAST}.</p>
  <h3>data/processed/kpi_metrics.csv</h3>
  {table(km, cls="num")}
  <h3>data/processed/kpi_phantom.csv</h3>
  {table(kp, cls="num")}
</section>""")

(HERE / "pages" / "du-lieu.html").write_text("\n\n".join(out) + "\n", encoding="utf-8")
print("Đã ghi pages/du-lieu.html")
