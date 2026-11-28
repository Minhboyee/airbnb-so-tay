# Sổ tay ôn vấn đáp — Airbnb Sydney (Nhóm 06)

Trang web một file (`index.html`) giúp cả nhóm ôn vấn đáp đồ án Inside Airbnb Sydney:

- **Câu chuyện**: căn “ảo” là gì, các con số chính (đã đối chiếu CSV ở tag `final`), ba cái bẫy dữ liệu, cách nói đúng khi vấn đáp.
- **Sơ đồ chi tiết**: mỗi trang bước có thêm bản TikZ gốc ngay dưới sơ đồ giản lược. Vùng bấm trong suốt phủ lên đúng tên hàm trong ảnh; nút **Toàn màn hình** mở overlay có kéo thả và pinch để thu phóng.
- **Luồng chính**: sơ đồ pipeline vẽ lại từ `airbnb_flow.pdf`. Bấm vào ô nào thì nhảy tới trang và dòng code của bước đó.
- **Trang 0 → 6**: hiện **toàn bộ code ở tag `final`** của repo nhóm, chia theo bước. Bấm vào đoạn code để mở giải thích ngay dưới đoạn đó. Pane bên phải tóm tắt luồng của file và tô bước đang đọc.
- **Kiểm thử, Lý thuyết, Hỏi đáp**: bảng test, kiến thức nền, câu hỏi vấn đáp và nhận xét code.

Giao diện và cách tương tác lấy theo [chesslab-so-tay](https://github.com/Minhboyee/chesslab-so-tay).

## Trạng thái

Đủ chú giải cho 25/25 file (mọi dòng code), trang Lý thuyết và Hỏi đáp đã viết; `python build.py` báo 0 vấn đề. Ghi chú lịch sử và số liệu đã kiểm chứng ở [`HANDOFF.md`](HANDOFF.md).

## Cách dựng

`build.py` đọc code thật của repo nhóm (private) ở tag `final`. Đặt repo nhóm cạnh repo này, hoặc trỏ biến `AIRBNB_REPO` tới nó:

```bash
git -C ../2627-LTXLDL-Airbnb-dse2049_2-Nhom6 checkout final
pip install pygments
python build.py                     # ghi index.html
python build.py --check qa_rules    # kiểm một file chú giải
python build.py --check             # kiểm tất cả
```

Mở `index.html` bằng trình duyệt là xem được, không cần server (ảnh nhúng base64, file 4–5 MB). Trang công khai qua GitHub Pages từ nhánh `main`.

## Cấu trúc

| File | Vai trò |
|---|---|
| `build.py` | Đọc code + chú giải, tô màu bằng Pygments, kiểm phủ dòng và link, ghi `index.html`. Danh sách file và trang ở biến `FILES`, `STEPS`. |
| `FORMAT.md` | Định dạng file chú giải và giọng văn. **Đọc trước khi viết chú giải.** |
| `notes/<id>.md` | Chú giải cho từng file code (khối dòng → giải thích HTML, luồng, nhận xét, hỏi đáp). |
| `pages/*.html` | Các trang viết tay: `cau-chuyen`, `luong`, phần mở đầu của `buoc-*`, `kiem-thu`, `ly-thuyet`, `hoi-dap`. Có thể chèn `{{diagram:tên}}` và `{{fig:đường/dẫn.png|chú thích}}`. |
| `preview.py` | Sinh `pages/du-lieu.html` (tab Dữ liệu): đọc `data/raw`, `data/processed` và các bảng kết quả của repo nhóm, chạy lại QA và chia nhóm trong bộ nhớ, lấy vài dòng mỗi bảng. Chạy trước `build.py` khi dữ liệu đổi; cần dữ liệu thô ở máy (bị gitignore). |
| `diagrams.py` | Sơ đồ SVG bấm được (mỗi ô có `href` tới dòng code). |
| `base.css` | CSS gốc lấy từ chesslab-so-tay. |
| `extra.css` | CSS thêm cho sơ đồ, hình, thẻ, máy phân nhóm. |
| `app.js` | Chuyển tab, mở giải thích, pane luồng, máy phân nhóm 7 nhóm, máy IQR. |
| `shell.html` | Khung trang. |
| `index.html` | Kết quả dựng (sinh ra, không sửa tay). |
