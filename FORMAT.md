# Cách viết file chú giải `notes/<id>.md`

Sổ tay là trang ôn vấn đáp: hiện **toàn bộ code** ở tag `final`, bấm vào đoạn nào thì mở giải thích ngay dưới đoạn đó. Người đọc là sinh viên trong nhóm, sắp bị giảng viên hỏi về từng dòng. Người viết đóng vai **giảng viên giải thích cho sinh viên**: nói vì sao code làm thế, hệ quả gì, chỗ nào dễ bị hỏi, chỗ nào code lệch docstring/README.

Mẫu chuẩn (đọc kỹ trước khi viết): `notes/config.md`. Mẫu phong cách gốc: https://github.com/Minhboyee/chesslab-so-tay (đọc vài khối `<div class="expl">` để thấy giọng văn).

## Cấu trúc file

```
--- meta
title: qa_rules.py
lead: Một đoạn HTML (1–4 câu) tóm tắt file: vai trò trong pipeline, vào gì, ra gì, ý chính cần nhớ.

--- blocks
=== 1-17
<p>HTML giải thích dòng 1 đến 17.</p>
=== 19
<p>Giải thích riêng dòng 19.</p>

--- flow
## Tên nhóm (ví dụ: Lúc import / Hàm phụ / Mỗi mốc)
fn 0 31 | tên_hàm | mô tả rất ngắn
st 1 46 | Tên bước trong hàm | mô tả rất ngắn
chips 2 | 72 budget ; kpi:300 compute_regular_kpis

--- review
mid | Tiêu đề ngắn | Mô tả HTML (một dòng)

--- qa
? Câu hỏi vấn đáp
<p>Câu trả lời HTML, ngắn, có số cụ thể nếu có.</p>
```

### `--- blocks` (bắt buộc, phần chính)
- `=== a-b` (hoặc `=== a`) mở một khối gồm dòng a..b của file nguồn (đánh số từ 1, như `cat -n`). Nội dung HTML ở các dòng sau, tới khối kế tiếp.
- **Mọi dòng có code (không trống) phải thuộc đúng một khối.** Khối tăng dần, không chồng nhau. Khối phải bắt đầu ở dòng có code. Dòng trống giữa hai khối không cần phủ (tự gắn vào khối trước).
- Kích thước khối: thường 1–8 dòng; một hàm ngắn hoặc một docstring có thể 10–20 dòng; chỉ khối dữ liệu thuần (bảng hằng số, danh sách cột, prompt dài) mới được dài hơn. Câu lệnh quan trọng (điều kiện lọc, công thức, `groupby`, ngưỡng) nên có khối riêng.
- Không phải lặp lại code bằng lời. Nói: **làm gì, vì sao, hệ quả, ví dụ số thật**, liên hệ bước khác, chỗ lệch docstring/README/báo cáo.
- HTML cho phép: `<p> <ul> <ol> <li> <code> <b> <em> <a> <table>`. Thẻ phải đóng đủ. Ký tự `<`, `>`, `&` trong chữ phải viết `&lt; &gt; &amp;`.
- Link tới code: `<a href="#<id>-L<dòng>">…</a>`, dòng bất kỳ, build tự trỏ về khối chứa dòng đó. `<id>` là id file trong bảng dưới. Link tới trang: `#cau-chuyen`, `#luong`, `#buoc-0` … `#buoc-6`, `#buoc-4bc`, `#kiem-thu`, `#ly-thuyet`, `#hoi-dap`. Link tới đầu một file: `#f-<id>`.

### `--- flow` (bắt buộc)
Pane bên phải tóm tắt luồng file. `fn` = hàm (chấm đặc), `st` = bước bên trong hàm (chấm rỗng). Số thứ nhất là cấp thụt (0, 1, 2), số thứ hai là dòng code để nhảy tới. `chips` = các hàm/khối liên quan (cùng file: `72 nhãn`; file khác: `kpi:300 nhãn`), cách nhau bằng `;`. Thứ tự nên là **thứ tự chạy thật**, không phải thứ tự trong file, nếu hai cái khác nhau. 10–30 dòng là vừa.

### `--- review` (nhận xét code)
Mỗi dòng: `loại | tiêu đề | mô tả`. Loại: `bug` (lỗi thật, có ví dụ tái hiện), `mid` (nên xem: comment lỗi thời, lệch README/báo cáo, nhánh chết, rủi ro), `low` (nhỏ), `ok` (điểm làm tốt đáng khen). Chỉ ghi điều **đã kiểm chứng** (đọc code, chạy thử). 2–8 dòng mỗi file lớn.

### `--- qa` (hỏi đáp vấn đáp)
3–8 câu mà giảng viên dễ hỏi về file này, trả lời ngắn gọn, đúng số, chỉ vào dòng code.

## Giọng văn
- Tiếng Việt, câu ngắn, như giảng viên nói với sinh viên. Thuật ngữ tiếng Anh giữ nguyên trong `<code>` khi là tên trong code.
- Không khen sáo rỗng, không "rất quan trọng", không emoji.
- Số thật lấy từ repo (CSV trong `data/processed/`, `reports/`), từ chạy thử code, không bịa. Nếu dẫn số, nói nó từ file nào.
- Khi docstring/comment/README nói khác code: **code là sự thật**, ghi rõ chỗ lệch.
- Viết số kiểu Việt: 20.573; 21,2%.

## Kiểm chứng (bắt buộc)
- Code được chú giải nằm ở repo nhóm (private), thư mục anh em `../2627-LTXLDL-Airbnb-dse2049_2-Nhom6` (đang ở tag `final`). Chạy thử Python/pytest từ thư mục đó: `python -m pytest -q -p no:cacheprovider tests/test_xxx.py`.
- Khi khẳng định hành vi không hiển nhiên (ví dụ: "NaN rơi vào nhánh X", "ngưỡng này không bao giờ chạm"), hãy chạy thử một đoạn nhỏ hoặc tìm test chứng minh. Đừng đoán.
- `data/raw/` **không có** trong repo (bị gitignore); `data/processed/` có các CSV kết quả đã commit; `data/samples/` có ID và nhãn tay.
- Không sửa file nào ngoài `notes/<id>.md` của mình (trong repo sổ tay). Không sửa repo nhóm. Không commit, không push.

## Tự kiểm định dạng
```
python build.py --check <id> [<id> ...]   # chạy trong thư mục repo sổ tay
```
Phải ra `OK`. Lệnh báo dòng nào chưa phủ, link nào hỏng, thẻ nào chưa đóng.

## Bảng id file
| id | file |
|---|---|
| run_pipeline | run_pipeline.py |
| config | src/config.py |
| sydney_yaml | configs/sydney.yaml |
| pyproject | pyproject.toml |
| ci | .github/workflows/ci.yml |
| download | src/download.py |
| check_assignment | scripts/check_assignment_data.py |
| qa | src/qa.py |
| qa_constraints | src/qa_constraints.py |
| qa_rules | src/qa_rules.py |
| seg_init | src/segments/__init__.py |
| seg_load | src/segments/load.py |
| seg_rules | src/segments/rules.py |
| seg_transitions | src/segments/transitions.py |
| seg_report | src/segments/report.py |
| llm | src/llm.py |
| label_additional | scripts/label_additional_reviews.py |
| llm_segments | src/llm_segments.py |
| baseline | src/baseline.py |
| metrics | src/metrics.py |
| evaluate | src/evaluate.py |
| eval_report | src/eval_report.py |
| kpi | src/kpi.py |
| viz | src/viz.py |
| viz_phantom | src/viz_phantom.py |
