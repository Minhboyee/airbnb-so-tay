# HANDOFF — Sổ tay ôn vấn đáp Airbnb Sydney

Tài liệu này để một agent (hoặc người) ở máy local làm tiếp sổ tay. Đọc hết trước khi bắt đầu.

Ngày bàn giao: 25/11/2026. Sổ tay giờ nằm ở repo public riêng `Minhboyee/airbnb-so-tay` (trước ở nhánh `claude/amazing-cerf-qthrk1` của repo nhóm, đã xoá). Code được chú giải là code ở tag `final` (commit `e5bf1cb`) của repo nhóm, đặt ở thư mục anh em `../2627-LTXLDL-Airbnb-dse2049_2-Nhom6`. Đường dẫn `so-tay/...` trong tài liệu này giờ là gốc repo sổ tay.

---

## 1. Mục tiêu (yêu cầu gốc của người dùng)

1. Làm một trang web **giống hệt kiểu** [chesslab-so-tay](https://github.com/Minhboyee/chesslab-so-tay) (xem `index.html` của repo đó: tab trên cùng, code liền khối, bấm đoạn nào mở giải thích ngay dưới, pane luồng dính bên phải, chế độ sáng/tối) cho code ở **tag `final`**.
2. **Luồng chính lấy từ `airbnb_flow.pdf`** (text đã trích ở `so-tay/ref/airbnb_flow.txt`). Trang chính có luồng chính; **bấm vào bước nào thì nhảy tới trang và source code tương ứng**.
3. Web giúp **ôn tập mọi dòng code**: mỗi dòng có code phải nằm trong một khối có giải thích.
4. Các trang/tab đầu: hiểu **luồng chung** và **câu chuyện** nhóm muốn truyền tải (căn “ảo”). Có trang giới thiệu tổng quát.
5. Giọng văn: **giảng viên giải thích cho sinh viên**. Làm cẩn thận, **kiểm chứng kỹ**: tài liệu đi kèm có thể đã lỗi thời, **code và CSV ở tag `final` là sự thật**.
6. Ràng buộc người dùng đặt khi làm: đừng chạy quá nhiều agent cùng lúc. **Tối đa 2 subagent Claude cùng lúc**; muốn nhiều hơn thì dùng opencode (ưu tiên) hoặc codex. (Trong môi trường cloud cũ không có opencode/codex nên chỉ chạy 2.)

---

## 2. Trạng thái hiện tại

### Hạ tầng: xong
- `build.py` dựng `index.html` (≈ 4,3 MB, ảnh nhúng base64), có chế độ `--check`.
- `FORMAT.md`: định dạng chú giải + giọng văn + cách kiểm chứng. Mẫu chuẩn: `notes/config.md`.
- `diagrams.py`: 8 sơ đồ SVG bấm được (overview, step1, step2, step3, step4, step4bc, step5, step6).
- `app.js`: tab, mở/đóng giải thích, pane luồng theo từng file, **máy phân nhóm 7 nhóm** (bản sao `classify()`), **máy IQR** (bản sao `_check_price_outlier_iqr`).
- Kiểm bằng Playwright: trang mở được, không lỗi JS.

### Trang viết tay
| Trang | Trạng thái |
|---|---|
| `pages/cau-chuyen.html` | Xong, số liệu đã đối chiếu CSV (xem mục 4). |
| `pages/luong.html` | Xong (sơ đồ Mức 0, bảng Mức 1, cờ chạy, bản đồ file). |
| `pages/buoc-0..6.html`, `buoc-4bc.html` | Xong phần mở đầu + sơ đồ Mức 2 + bảng tóm tắt. |
| `pages/kiem-thu.html` | Xong (bảng 17 file test, 453 test). |
| `pages/ly-thuyet.html` | Xong (12 mục). |
| `pages/hoi-dap.html` | Xong: câu hỏi tổng quát + tự gom từ notes. |

### Chú giải từng file (`notes/<id>.md`)
| id | File | Dòng | Trạng thái |
|---|---|---|---|
| config | src/config.py | 93 | ✅ xong (mẫu chuẩn) |
| download | src/download.py | 557 | ✅ xong, `--check` OK |
| check_assignment | scripts/check_assignment_data.py | 300 | ✅ xong, `--check` OK |
| qa | src/qa.py | 156 | ✅ xong |
| qa_constraints | src/qa_constraints.py | 135 | ✅ xong |
| qa_rules | src/qa_rules.py | 605 | ✅ xong |
| baseline | src/baseline.py | 97 | ✅ có 13 khối (agent bị dừng giữa chừng, nên đọc lại một lượt) |
| metrics | src/metrics.py | 145 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| run_pipeline | run_pipeline.py | 213 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| sydney_yaml | configs/sydney.yaml | 93 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| pyproject | pyproject.toml | ~50 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| ci | .github/workflows/ci.yml | 94 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| seg_init, seg_load, seg_rules, seg_transitions, seg_report | src/segments/*.py | 521 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| llm | src/llm.py | 440 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| label_additional | scripts/label_additional_reviews.py | 247 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| llm_segments | src/llm_segments.py | 268 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| evaluate | src/evaluate.py | 456 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| eval_report | src/eval_report.py | 245 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| kpi | src/kpi.py | 1.007 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| viz | src/viz.py | 439 | ✅ xong (opencode, 25/11/2026), `--check` OK |
| viz_phantom | src/viz_phantom.py | 980 | ✅ xong (opencode, 25/11/2026), `--check` OK |

File chưa có chú giải vẫn hiện đủ code trên trang, chỉ chưa bấm ra giải thích được.

---

## 3. Việc còn lại (theo thứ tự ưu tiên)

### 3.1 Viết chú giải cho các file ❌ (việc chính)
Thứ tự gợi ý (quan trọng cho câu chuyện trước):
1. `run_pipeline` + `sydney_yaml` (luồng chính, trang 0)
2. `seg_*` (lõi câu chuyện 7 nhóm)
3. `kpi` (1.007 dòng; chia hai lượt nếu cần: KPI thường + LLM / `run_phantom` + KPI căn ảo)
4. `metrics` (vá nốt), `evaluate`, `eval_report`
5. `llm`, `llm_segments`, `label_additional`
6. `viz`, `viz_phantom`
7. `pyproject`, `ci`

**Cách giao cho một agent** (mỗi agent 1 nhóm file, tối đa 2 agent Claude chạy cùng lúc; thêm nữa thì dùng opencode):

> Đọc `so-tay/FORMAT.md` và mẫu `so-tay/notes/config.md`. Viết `so-tay/notes/<id>.md` cho `<file>`, phủ MỌI dòng có code. Đọc test liên quan trong `tests/`. Khi khẳng định hành vi không hiển nhiên thì chạy thử (Python có pandas, ...). Số liệu phải tự tính lại từ CSV đã commit trong `data/processed/`, `reports/`, không chép từ tài liệu. Code và CSV ở tag `final` là sự thật; tài liệu lệch code thì ghi vào `--- review`. Chỉ sửa file notes của mình, không commit. Xong khi `python so-tay/build.py --check <id>` báo OK. Báo cáo cuối: số khối, nhận xét bug/mid đã kiểm chứng, chỗ tài liệu lệch code, số đã tự kiểm.

Gợi ý nội dung riêng từng file (đã chuẩn bị, đừng bỏ sót):
- **run_pipeline**: thứ tự bước; vì sao LLM trước KPI (KPI đọc cache LLM) và chia nhóm trước LLM (4b cần nhóm); `expected_applies`/`without_expected`; `seg`; `comparison`; `stale` ở bước 6b (không vẽ từ file cũ còn sót); cờ CLI.
- **sydney_yaml**: mỗi khoá được đọc ở dòng nào trong code (link tới dòng đó).
- **seg_***: khớp trước thì thắng (`np.select`, `rules.py` dòng 84–93); `has_recent = days <= 365` với NaN → False; `seen_before_ids` trả `None` khi không có mốc đủ cũ → hai mốc 2025 có 0 D_never; mốc gap 2026-03-21; `VANG` (hàm `track`) và `BIEN_MAT` (ma trận) là **hai tên cho cùng một hiện tượng**; ma trận 7×8 chuẩn hoá theo hàng.
- **kpi**: lọc `qa_has_error_excl_price`; đồng bộ calendar theo listing còn lại; mỗi KPI trả `(giá trị, n_obs)`; định nghĩa tử/mẫu số (đã kiểm ở mục 4); 2 KPI LLM mẫu số khác nhau; `run_phantom`; giá so hàng xóm tách ≤ 20 đêm và ≥ 90 đêm (bẫy gộp nhóm / Simpson); license trống không tính `Exempt`.
- **evaluate/metrics**: Wilson CI, bootstrap 2.000 lần, Cohen’s kappa, macro-F1 chỉ trên lớp có support > 0, micro-F1 aspect trên cặp (khen/chê, aspect); cổng an toàn (`min_gold_size`, cache chưa phủ).
- **viz/viz_phantom**: mỗi hàm vẽ hình nào, đọc cột nào; “đọc hình thế nào” dựa trên ảnh thật trong `figures/`.

### 3.2 Viết `pages/ly-thuyet.html`
Theo kiểu trang “Lý thuyết” của chesslab: mỗi mục có giải thích ngắn, công thức, ví dụ số từ chính dữ liệu nhóm, link về dòng code dùng nó. Các mục:
1. Snapshot và dữ liệu “ảnh chụp” (vì sao không suy ra xu hướng từ 4 mốc).
2. QA gắn cờ vs xoá dòng; cờ tổng; vì sao tách cờ trừ giá.
3. IQR và ngoại lệ (k = 1,5 vs 3; với phân phối chuẩn k = 1,5 ≈ ±2,7σ, k = 3 ≈ ±4,7σ). Máy IQR đã có ở trang bước 2.
4. Trung vị vs trung bình (QA mốc cuối: TB 490,01 → 464,16 → 370,56; trung vị 343 → 342,84 → 333,33).
5. Phân loại theo luật ưu tiên (decision list), “khớp trước thì thắng”.
6. Ma trận chuyển trạng thái, chuẩn hoá theo hàng.
7. Bẫy gộp nhóm / nghịch lý Simpson (giá căn ảo: gộp chung trông rẻ, tách ra thì ngắn ngày đắt hơn).
8. Mẫu không đại diện (8,4% vs 21,2%).
9. Accuracy, precision, recall, F1; macro vs micro; Cohen’s kappa (có ví dụ ma trận nhầm lẫn thật trong `reports/evaluation/eval_perclass.csv`).
10. Khoảng tin cậy Wilson và bootstrap.
11. LLM có đầu ra cấu trúc (pydantic), cache, tính tái lập; vì sao không sinh nhãn giả.
12. Tương quan ≠ nhân quả (luật NSW chỉ “khớp với”).

### 3.3 Bổ sung `pages/hoi-dap.html`
Thêm 10–15 câu tổng quát lên đầu trang (trước `{{auto_qa}}`), dạng `<details class="qa"><summary>…</summary><div class="ans">…</div></details>`. Nguồn câu hỏi: kịch bản thuyết trình (`script.docx`, mục “Câu hỏi vấn đáp”), nhưng **phải sửa theo trạng thái `final`** (xem mục 5): F1 đã công bố; `run_phantom` đã nối; tag đã gắn; giá 1,32×/1,85×/0,96×.

### 3.4 Rà soát và đánh bóng
- Đọc lại `notes/baseline.md` và `notes/metrics.md` (agent dừng giữa chừng).
- Chạy `python so-tay/build.py` phải ra **0 vấn đề**.
- Mở trang bằng trình duyệt và kiểm: bấm từng ô trong mọi sơ đồ; bấm link trong giải thích (phải mở đúng khối); “Mở hết giải thích”; pane luồng tô đúng bước khi cuộn; chế độ tối; màn hình hẹp 390 px (không cuộn ngang toàn trang; sơ đồ được cuộn ngang trong khung của nó).
- Kiểm điều hướng khi đổi hash thủ công: `app.js` hiện chỉ nghe `popstate` và click; nên thêm `addEventListener("hashchange", …)` để dán link `#qa_rules-L180` vào thanh địa chỉ cũng mở đúng khối.
- Hình `figures/evaluation/eval_confusion_matrices.png` và các hình khác đang nhúng ở kích thước gốc; có thể nén nếu muốn file nhẹ hơn.

### 3.5 Xuất bản (khi đã xong)
Người dùng muốn một **repo public** riêng. Môi trường cloud cũ không có quyền tạo repo, nên làm ở local:

```bash
python so-tay/build.py
mkdir ../airbnb-so-tay && cp so-tay/index.html ../airbnb-so-tay/ && touch ../airbnb-so-tay/.nojekyll
cd ../airbnb-so-tay && git init -b main && git add . && git commit -m "Sổ tay ôn vấn đáp Airbnb Sydney"
gh repo create airbnb-so-tay --public --source . --push
gh api -X POST repos/{owner}/airbnb-so-tay/pages -f "source[branch]=main" -f "source[path]=/"
```

Kèm một README ngắn (có thể lấy phần đầu của `so-tay/README.md`). **Trước khi public, cân nhắc nội dung**: trang hiện có tên thành viên ở chỗ nào thì kiểm lại (code repo nhóm là private; README nhóm có MSSV). Trang hiện tại không chứa MSSV; nếu thêm bảng phân công thì bỏ MSSV.

Nếu muốn public cả mã nguồn sổ tay (không chỉ `index.html`): chép thư mục `so-tay/` sang repo mới, nhưng `build.py` cần code của repo nhóm ở thư mục cha, nên ghi rõ điều đó trong README.

---

## 4. Số liệu đã kiểm chứng (dùng được ngay)

Tất cả tính lại từ file đã commit ở tag `final`.

**Chia nhóm** (`data/processed/segments_counts_{full,sample}.csv`), mốc 16/06/2026:

| Nhóm | Cả TP | Mẫu |
|---|---|---|
| B_ghost | 918 | 1 |
| B_booked | 1.159 | 15 |
| D_dormant | 1.913 | 58 |
| D_never | 1.528 | 25 |
| N_new | 1.525 | 0 |
| L_low | 1.623 | 55 |
| H_healthy | 11.907 (57,9%) | 846 (84,6%) |
| Tổng | 20.573 | 1.000 |

- Căn ảo: 4.359/20.573 = **21,19%**; mẫu 84/1.000 = **8,4%**.
- Theo mốc, cả TP: 13,1% / 12,0% / 6,5% / 21,2%. Mẫu: 3,6% / 4,1% / 7,6% / 8,4%.
- Hai mốc 2025: D_never = 0 (không có mốc cũ ≥ 150 ngày).
- Gap audit (`segments_gap_audit_full.csv`, `segments_gap_summary_full.csv`): số căn 17.730 / 20.436 / 13.563 / 20.573; `max_minimum_nights` 999 / 500 / 7 / 500; kín lịch 9,98% / 7,73% / 0,18% / 10,10%. Tháng 3 thiếu 4.645, giải thích được 3.569 (76,84%), chưa rõ 1.076.
- Chuyển nhóm (`segments_transitions_full.csv`): D_dormant → D_dormant 65,44% (09/2025→06/2026), 67,12% (12/2025→06/2026); D_dormant → BIEN_MAT 15,99% / 14,07%; H_healthy giữ 69,41% / 72,81%.

**KPI căn ảo** (`data/processed/kpi_phantom.csv`, 16/06/2026):
- `phantom_listing_rate` 21,188% (n = 20.573). Theo khu: Pittwater 36,49% (918), Mosman 36,16% (271, dưới ngưỡng 300), Woollahra 32,20% (615), Warringah 31,10% (881), Sydney 15,88% (5.014), Auburn 12,29% (667).
- `long_stay_90_rate`: B_ghost 47,06%, D_dormant 55,41%, D_never 60,60%, H_healthy 1,14%, L_low 5,98%, N_new 1,64%, B_booked 10,69% (n = 1.151, khác 1.159 vì có căn thiếu `minimum_nights`).
- `missing_registration_rate` 6,1683% (1.269 căn). Theo số đêm tối thiểu: 1–7: 21; 8–20: 4; 21–89: **0**; 90+: 1.244 (98,03%).
- Giá ngắn ngày (≤ 20 đêm): D_dormant **1,3203×** (n 791), D_never **1,8549×** (529), H_healthy **0,9639×** (11.584), L_low 1,10×, N_new 0,9683×. Giá ≥ 90 đêm: D_dormant 0,9583× (836), D_never 1,0706× (740), H_healthy 0,9761× (66).

**KPI thường** (`data/processed/kpi_metrics.csv`, scope overall; 09/25, 12/25, 03/26, 06/26):
- availability_rate 49,65 / 50,08 / 52,18 / 50,76 (n 365.000)
- long_stay_restriction_rate (≥ 7 đêm) 7,2 / 8,0 / 3,5 / 4,4 (n 1.000)
- high_utilization_listing_rate (occupancy ước tính ≥ 180) 23,2 / 25,6 / 24,3 / 22,8
- professional_host_presence (host > 1 listing, tính trên host) 50,95 / 51,69 / 47,97 / 52,03 (n 738/739/740/738)
- high_rated_listing_share (rating ≥ 4,9) 36,53 / 35,46 / 34,46 / 32,82 (n 950/970/975/975)
- commercialized (Entire home + host > 1 listing) theo analysis_area, mốc cuối: A05 70,63, A02 69,05, … A08 38,10
- LLM: complaint 14,0% (1.000 review); top aspect amenities 50,0% (176 lượt). Mở rộng: 4.000 review 14,175%, amenities 48,05% (795); 5.000 review 14,14%, 48,40% (971).

**QA** (`reports/qa_report.csv`): 48 dòng luật (11 + 11 + 13 + 13; hai mốc đầu không chạy luật giá). 03/2026: price_unusable 3, price_outlier 51. 06/2026: price_unusable 22 (20 thiếu + 2 trên 10.000 AUD), price_outlier 52. Mốc cuối: 1.000 → 978 (bỏ lỗi) → 928 (bỏ thêm cảnh báo).

**Đánh giá LLM** (`reports/evaluation/eval_summary.csv`): gold 85 positive / 15 mixed / 0 negative. Gemini vs baseline: accuracy 0,970 vs 0,870; macro-F1 0,936 vs 0,622; kappa 0,872 vs 0,270; aspect micro-F1 0,904 vs 0,602. (Agent làm evaluate chưa chạy lại xong để đối chiếu; nên chạy lại `evaluate.run` vào thư mục tạm để xác nhận.)

**Test**: `pytest` ở tag `final`: 453 pass, coverage 97,92%.

**Không kiểm được** (không có trong CSV đã commit, chỉ có trong tài liệu): superhost 12,4% / 33,4% / 44,8%; “khoảng 4.067 căn Exempt”; “79 triệu AUD”. Nếu dùng phải nói là số tính ngoài pipeline.

---

## 5. Tài liệu đi kèm và chỗ đã lỗi thời

Người dùng đính kèm 5 file (không có trong repo; xin lại người dùng nếu cần):
- `airbnb_flow.pdf`: **luồng chính**. Text ở `so-tay/ref/airbnb_flow.txt`. Khớp code `final`.
- `Bao_cao_..._dinh_dang_lai-1.pdf`: báo cáo **bản cũ `a5539a7`**. Báo cáo mới nhất nằm trong repo: `reports/Bao_cao_Inside_Airbnb_Sydney_Nhom06.pdf` (bản `14c7963`), **khớp CSV** → dùng bản trong repo.
- `Ke-hoach-dinh-huong-moi-...pdf`: kế hoạch 11/11, nhiều số cũ.
- `script.docx`: kịch bản thuyết trình + 12 câu vấn đáp + bảng số cần thuộc (số liệu ngày 20/11, commit `fae4dca`).
- `nhom6-cau-chuyen.html`: trang “hồ sơ căn ảo” nội bộ (giọng thám tử), cùng mạch với kịch bản.

| Tài liệu cũ nói | Ở tag `final` |
|---|---|
| `run_phantom` chưa nối, PR #27 chưa merge | Đã nối (bước 5b, `run_pipeline.py` dòng 181); bước 6b vẽ 8 hình căn ảo |
| Không công bố F1 vì thiếu lớp negative | Có công bố; thiếu lớp chỉ là cảnh báo, macro-F1 trên lớp có support > 0 |
| 4 cohort LLM bổ sung đã gỡ | Được khôi phục (`d224e3a`) làm phân tích mở rộng |
| Giá ngắn ngày 1,42× / 1,98× / 1,01× | 1,32× / 1,85× / 0,96× (commit `5e5eb69` tách trung vị theo chế độ lưu trú) |
| QA “19 luật”, tên `price_missing`, `price_above_cap` | 7 cờ theo dòng, 13 luật theo bảng, 21 mục con trong cột `detail`; thêm cờ trùng giữa mốc |
| Tag `final` chưa gắn | Đã gắn ở `e5bf1cb` |
| Phân công trong kế hoạch (Linh làm docs, Hoàng làm viz…) | Phân công thật ở README nhóm và báo cáo `14c7963` (khác kế hoạch) |

---

## 6. Phát hiện từ các agent đã chạy (đã kiểm chứng, đã ghi vào `--- review` của notes)

- **check_assignment_data.py — bug**: script đọc yaml thô (không qua `load_config`), nên `qa.expected.snapshots` là kiểu `date` và `json.dumps` báo `TypeError` với yaml hiện tại (CSV vẫn được ghi). Khoá này thêm ở commit `852416b`, sau khi audit được tạo.
- **check_assignment_data.py — bug**: thiếu file thô thì nhánh `missing_input` không thêm vào `failures`, script vẫn thoát mã 0.
- **check_assignment_data.py**: số kỳ vọng (365000, 5000, 875, 125) viết cứng; `[None] * 4` lỗi nếu > 4 mốc; cột `code` đọc nhưng không dùng. Không có test, không trong mypy/coverage.
- **download.py**: lỗi `\r` trong comment có thật trên Python 3.10 (một review thành 3 dòng; commit `0aa866e` ghi 5.015 dòng thay vì 5.000); Python ≥ 3.11 không tái hiện. `verify_raw` chỉ đọc header nên không bắt gzip bị cắt đuôi. Docstring nói “ID đọc dạng số sẽ bị làm tròn” chưa chính xác: hỏng thật khi thành `float64` (3.613/5.000 review_id và 705/1.000 listing_id sai chữ số cuối, ví dụ `383502732966388018` → `383502732966388032`) hoặc khi so chuỗi với `int64`.
- **qa_rules.py — bug**: `apply_rules` ném `KeyError: 'date'` khi reviews thiếu cột `date`/`listing_id` mà có reviews mốc trước, vì `_detail` (dòng 549–557) gọi thẳng `_check_review_cross_snapshot_conflict` không qua kiểm `needs`. Dữ liệu thật đủ cột nên không gặp.
- **qa.py**: `write_report` chạy sau vòng lặp; mốc nào vỡ ràng buộc thì không ghi báo cáo mới, file cũ vẫn nằm đó.
- **qa_constraints.py**: tham số `reviews` không dùng; `n_reviews` kiểm ở `download.py` dòng 439 chứ không ở đây; “thiếu giá” ở ràng buộc tính cả chuỗi rỗng còn mục con `price_missing` chỉ tính NaN; giá > 10.000 bật cả `price_unusable` lẫn `price_outlier`; `calendar_incomplete` không bắt listing không có dòng lịch nào.

Các phát hiện này hiện trong bảng “Nhận xét code” của trang Hỏi đáp. **Không sửa code pipeline** (tag `final` đã nộp); chỉ ghi nhận để trả lời vấn đáp.

---

## 7. Mẹo kỹ thuật

- Môi trường Python cho pipeline: `pip install -r requirements.lock.txt` (thêm `tomli` nếu Python ≥ 3.11 mà test hygiene đòi). Chạy test: `pytest -q -p no:cacheprovider`.
- Chỉ dựng trang thì chỉ cần `pygments`.
- Link trong chú giải: `<a href="#<id>-L<dòng>">` với dòng bất kỳ; `build.py` tự trỏ về khối chứa dòng đó. Link tới đầu file: `#f-<id>`. Link tới trang: `#cau-chuyen`, `#luong`, `#buoc-0`…`#buoc-6`, `#buoc-4bc`, `#kiem-thu`, `#ly-thuyet`, `#hoi-dap`.
- Sơ đồ: sửa toạ độ trong `diagrams.py`; mỗi ô có `href` thì bấm được. Thêm sơ đồ mới: viết hàm mới rồi chèn `{{diagram:tên_hàm}}` vào trang.
- `app.js`: máy phân nhóm dùng số dòng cứng của `rules.py` (85–93) trong biến `LINE`; nếu code đổi thì sửa theo.
- `data/processed/sydney/` bị gitignore: các bảng `llm_segment_aspects*.csv`, `segments_<scope>.csv` chỉ có sau khi chạy pipeline (cần `data/raw`, tải từ Inside Airbnb, hoặc scope `sample`).
