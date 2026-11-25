--- meta
title: check_assignment_data.py
lead: Script kiểm tra độc lập, <b>ngoài pipeline</b>: đọc 12 file <code>.csv.gz</code> đã có trong <code>data/raw/sydney/</code> (không gọi mạng) và danh sách ID của nhóm xuất từ workbook đề bài dạng JSON, rồi đếm lại mọi con số đề cam kết: 1.000 listing, 875/125, 50/30/25/25 căn 0 review, 365.000 dòng lịch, 5.000 review, 20 căn thiếu giá ở mốc cuối. Kết quả là hai bằng chứng đã commit: <code>reports/check_DSE2049-C02-G06-sydney.csv</code> (1 dòng mỗi mốc) và <code>reports/assignment_data_audit.json</code> (chi tiết, <code>failures</code> rỗng). Viết lại logic lọc riêng, không import <code>src/download.py</code>, để là phép kiểm chéo thật.

--- blocks
=== 1
<p>Docstring một dòng: chỉ dùng file gzip local. Script được thêm ở commit <code>2a58a3f</code> (22/10/2026) cùng hai file bằng chứng; commit ghi “chạy lại auditor trên 4 mốc local cho CSV trùng khớp từng byte”. README nhắc nó ở mục “Kiểm tra dữ liệu được giao”. Không có test nào cho file này, và CI chỉ chạy ruff trên nó (mypy và coverage chỉ tính <code>run_pipeline.py</code>, <code>src</code>, <code>tests</code>, theo <code>pyproject.toml</code>).</p>

=== 3-12
<p>Import. <code>hashlib</code> để tính SHA-256 từng file (chứng minh đúng file nào đã được kiểm). <code>yaml</code> đọc config trực tiếp bằng <code>yaml.safe_load</code>, không qua <code>src/config.load_config</code>; hệ quả ở <a href="#check_assignment-L213">dòng 213</a>.</p>

=== 14-33
<p>Hằng số:</p>
<ul><li><code>TABLES</code>: 3 bảng. Geojson không được kiểm ở đây (khác <code>verify_raw</code> của bước 1).</li>
<li><code>CALENDAR_COLUMNS</code>: cùng 5 cột với <a href="#download-L58">download.py</a>, nhưng chép lại chứ không import.</li>
<li><code>CSV_COLUMNS</code>: 16 cột của file CSV bằng chứng, tên tiếng Việt không dấu theo mẫu đề: <code>tai_ve_ok</code> (co/khong), <code>*_bytes</code>, <code>*_dong</code>, <code>khong_co_review</code>, <code>thieu_price</code>, <code>so_cot_listings</code>, <code>so_cot_nan_90</code> (số cột thiếu ≥ 90%).</li></ul>

=== 36-37
<p>Chuẩn hoá ô: <code>None</code> thành chuỗi rỗng, còn lại <code>str()</code> rồi bỏ khoảng trắng hai đầu.</p>

=== 40-42
<p>Lấy mảng <code>values</code> của một sheet trong JSON, chỉ giữ các dòng là list. Dạng <code>{"range": ..., "values": [[...], ...]}</code> giống kết quả đọc một vùng của Google Sheets. JSON sai cấu trúc thì trả danh sách rỗng chứ không lỗi ở đây.</p>

=== 45-46
<p>Đọc file JSON của workbook. File này không có trong repo; theo <code>source_ranges</code> trong audit, nó chứa vùng <code>Listing!A17002:E18001</code> (đúng 1.000 dòng) và <code>Review!A85002:G90001</code> (đúng 5.000 dòng), ngày lấy <code>2026-10-17</code>.</p>

=== 47-59
<p>Sheet Listing: 5 cột theo vị trí (lớp, nhóm, mã, <code>listing_id</code>, <code>analysis_area</code>). Bỏ dòng ngắn hơn 5 ô. Mọi giá trị qua <code>_text</code> nên ID là chuỗi, đúng ghi chú trợ giảng; điều kiện là JSON lưu ID dạng chuỗi (nếu lưu dạng số 19 chữ số thì đã sai ngay khi <code>json.loads</code> chuyển thành float).</p>
<p>Cột <code>code</code> được đọc nhưng không dùng để lọc theo mã nhóm. Script tin rằng JSON chỉ chứa vùng của nhóm 06. Nếu đưa vào JSON của cả workbook (84 nhóm) thì “ID chính thức” sẽ là ID của mọi nhóm.</p>

=== 60-77
<p>Sheet Review: 7 cột, hai cột cuối <code>mau_llm</code>, <code>nhan_tay</code> có thể thiếu (ô trống cuối dòng thường bị cắt) nên kiểm <code>len(r)</code>. Thiếu một trong hai sheet thì <code>ValueError</code>: không kiểm với danh sách rỗng.</p>

=== 80-85
<p>SHA-256 đọc từng khúc 1 MB (<code>iter</code> với giá trị dừng <code>b""</code>), không nạp cả file 85 MB. Audit ghi hash mỗi file, ví dụ <code>listings.csv.gz</code> mốc 2025-09-12 bắt đầu <code>6d886ebee5f1</code>: ai tải lại có thể so để chắc cùng một bản dữ liệu.</p>

=== 88-89
<p>Chuyển mọi cột sang kiểu <code>string</code> của pandas và đổi ô rỗng hoặc chỉ có khoảng trắng thành <code>NA</code>. Nhờ vậy “thiếu” được đếm thống nhất, kể cả ô chỉ có dấu cách.</p>

=== 92-94
<p>Đọc listings toàn bộ cột với <code>dtype=str</code> (mọi cột, không chỉ ID). Trả thêm số cột gốc: audit ghi 79, 85, 90, 90 cột ở 4 mốc, tức Inside Airbnb đổi lược đồ giữa các mốc.</p>

=== 97-99
<p>Calendar: đọc header trước, chỉ giữ những cột trong 5 cột cần mà file thật sự có (tránh lỗi nếu thiếu cột).</p>

=== 100-106
<p>Đọc theo chunk 200.000 dòng như bước 1, đếm <code>raw_rows</code> (tổng dòng gốc) rồi lọc theo <code>listing_id</code>. Số dòng gốc trong audit: 6.471.450; 7.459.152; 4.950.495; 7.509.145. Chia 365 ra số listing cả thành phố: 17.730; khoảng 20.436; 13.563; 20.573. Mốc 2026-03-21 chỉ có 13.563 căn: đây là mốc bị lọc thiếu căn mà <code>segments.gap_snapshot</code> nhắc tới.</p>

=== 107-113
<p>Gộp các chunk đã lọc và trả thêm hai thông tin:</p>
<ul><li><code>filtered_dates</code>: danh sách ngày duy nhất. Audit có 365, 366, 365, 377 ngày. Mốc cuối chạy từ 2026-06-17 đến 2027-06-28: mỗi căn vẫn đúng 365 dòng, nhưng cửa sổ 365 ngày của các căn lệch nhau (cào vào các ngày khác nhau).</li>
<li><code>duplicate_listing_date_rows</code>: số dòng trùng (listing_id, date). Cả 4 mốc là 0.</li></ul>

=== 116-124
<p>Reviews: đọc chunk, mọi cột chuỗi, lọc theo cột <code>id</code> (review_id), cùng quy tắc với bước 1. Trả số cột gốc (6 ở cả 4 mốc).</p>

=== 127-133
<p>Cột thiếu từ 90% trở lên trên bảng đã lọc, kèm số ô thiếu và tỉ lệ. <code>if total</code> tránh chia cho 0. Audit: mốc 1 và 2 có 6 cột (trong đó <code>price</code>, <code>calendar_updated</code>, <code>estimated_revenue_l365d</code>); mốc 3 và 4 có 13 cột, thêm nhiều cột host như <code>host_since</code>, <code>host_response_time</code>. Calendar và reviews không có cột nào.</p>

=== 136-151
<p>Đếm trên listings đã lọc: số dòng, số căn <code>Entire home/apt</code>, <code>Private room</code>, số căn <code>number_of_reviews</code> = 0 (đổi số bằng <code>to_numeric(errors="coerce")</code> vì đang là chuỗi), số căn thiếu <code>price</code>. Cột không có thì trả 0 hoặc <code>None</code>, không lỗi.</p>

=== 154-156
<p>Kiểm trọn một mốc. Hai tập ID chính thức được dựng thành <code>set</code> để tra nhanh.</p>

=== 157-163
<p>Lọc listings theo <code>id</code> rồi <code>merge</code> để gắn <code>analysis_area</code>, giống <a href="#download-L360">filter_listings</a>. <code>listings.get("id", ...)</code>: nếu file thiếu cột <code>id</code> thì dùng Series rỗng thay vì <code>KeyError</code>.</p>

=== 164-167
<p>Lọc calendar và reviews, rồi lấy tập ID thực sự thấy được, để so với tập chính thức ở phần <code>key_integrity</code>.</p>

=== 168-171
<p>Thông tin file: đường dẫn, số byte, SHA-256. <code>path</code> trong audit đã commit có dạng <code>data\raw\sydney\...</code> vì script chạy trên Windows.</p>
<p>Hash bị tính hai lần cho mỗi file: ở đây và ở <a href="#check_assignment-L238">dòng 238</a>. Kết quả đúng, chỉ tốn thời gian (đọc lại khoảng 100 MB mỗi mốc).</p>

=== 172-181
<p>Cờ mẫu của đề: số review có <code>mau_llm = x</code> (1.000) và <code>nhan_tay = x</code> (100), và bao nhiêu trong đó có mặt ở mốc này. Audit: 1.000 và 100 ở cả 4 mốc, tức mẫu LLM và mẫu nhãn tay đều đọc được ở mọi mốc.</p>

=== 182-203
<p>Kết quả chi tiết của một mốc. Phần đáng hỏi là <code>key_integrity</code>:</p>
<ul><li>ID chính thức thiếu trong dữ liệu (<code>missing</code>) và ID lọt vào mà không chính thức (<code>unexpected</code>), cho cả listing và review.</li>
<li>Số ID trùng sau khi lọc.</li></ul>
<p>Audit: cả 6 giá trị đều rỗng hoặc 0 ở cả 4 mốc. Nghĩa là 1.000 listing và 5.000 review của đề đều có mặt ở mọi mốc, không thừa, không trùng.</p>

=== 206-212
<p>Tham số dòng lệnh: <code>--config</code> và <code>--workbook-json</code> bắt buộc; hai đường ra tuỳ chọn. Ví dụ chạy từ thư mục gốc: <code>python scripts/check_assignment_data.py --config configs/sydney.yaml --workbook-json &lt;file JSON&gt;</code>.</p>

=== 213-219
<p>Đọc yaml thô. Vì không qua <code>load_config</code>, các ngày trong yaml là <code>datetime.date</code>:</p>
<ul><li><code>config["snapshots"]</code>: không sao, có <code>str()</code> ở <a href="#check_assignment-L234">dòng 234</a>.</li>
<li><code>qa.expected.snapshots</code> (thêm vào yaml ở commit <code>852416b</code>, 21/11/2026, sau khi audit được tạo) nằm trong <code>expected</code> và đi vào JSON ở <a href="#check_assignment-L229">dòng 229</a>. Đã chạy thử với <code>configs/sydney.yaml</code> hiện tại: CSV vẫn được ghi, rồi <code>json.dumps</code> lỗi <code>TypeError: Object of type date is not JSON serializable</code>. Với yaml ở commit <code>2a58a3f</code> thì chạy được.</li></ul>
<p>Mặc định ghi <code>reports/check_&lt;group_code&gt;.csv</code> và <code>reports/assignment_data_audit.json</code>; thư mục dữ liệu thô là <code>data/raw/&lt;city&gt;</code> tương đối, nên phải chạy từ gốc repo.</p>

=== 220-232
<p>Khung của audit JSON: mã nhóm, ngày lấy workbook, vùng ô nguồn (<code>assignment</code> là dòng giao việc: lớp, nhóm 6, Sydney, AUD, 4 mốc, URL), kỳ vọng chép từ yaml, chi tiết từng mốc và danh sách <code>failures</code>.</p>
<p>Lệch nhỏ với yaml hiện tại: <code>expectations</code> trong file đã commit không có <code>n_reviews</code> và <code>snapshots</code>, vì hai khoá này được thêm vào yaml sau ngày tạo audit.</p>

=== 233-243
<p>Mỗi mốc: dựng 3 đường dẫn, ghi <code>exists</code>, số byte và hash của file nào có.</p>

=== 244-255
<p>Thiếu bất kỳ file nào: ghi trạng thái <code>missing_input</code>, thêm dòng CSV <code>tai_ve_ok = khong</code> với các cột số để trống, rồi sang mốc khác.</p>
<p>Nhánh này không thêm gì vào <code>failures</code>, đã kiểm chứng: chạy thử với yaml cũ khi không có file nào, cả 4 mốc <code>missing_input</code> mà <code>failures</code> vẫn là <code>[]</code>. Ai chỉ đọc <code>failures</code> sẽ tưởng đạt. Script cũng luôn thoát mã 0, kể cả khi có failure.</p>

=== 256-278
<p>Đủ file thì gọi <code>check_snapshot</code> và dựng một dòng CSV. Dòng thật đã commit, mốc 2026-06-16: 12.633.389 / 17.897.549 / 84.860.225 byte; 1000 listing; 365000 dòng lịch; 5000 review; 875/125; 25 căn 0 review; 20 thiếu giá; 90 cột; 13 cột thiếu ≥ 90%.</p>

=== 279-287
<p>So với kỳ vọng. Chỉ <code>n_listings</code> và số căn 0 review lấy từ yaml; các số còn lại viết cứng: <code>365000</code>, <code>5000</code>, <code>875</code>, <code>125</code>. Khác <code>download.check_expected</code>, nơi mọi số đều đọc từ <code>qa.expected</code>. Với Sydney kết quả như nhau; đổi đề thì phải sửa cả code.</p>
<ul><li>Review: đòi đủ 5.000 ở từng mốc, chặt hơn bước 1 (bước 1 chỉ đòi hợp qua các mốc bằng 5.000). Dữ liệu Sydney đạt cả hai.</li>
<li><code>expected.get(..., [None] * 4)[index]</code>: nhiều hơn 4 mốc thì <code>IndexError</code>; không có <code>qa.expected</code> thì so với <code>None</code> nên luôn báo sai.</li></ul>

=== 288-292
<p>Thiếu giá chỉ kiểm ở mốc cuối, mặc định 20. Ghi các phép kiểm vào chi tiết mốc, phép nào sai thì thêm <code>"&lt;mốc&gt;:&lt;tên&gt;"</code> vào <code>failures</code>. Audit đã commit: mọi phép đều <code>true</code>, <code>failures</code> rỗng.</p>
<p>Số thiếu giá ở các mốc khác (CSV đã commit): 1.000, 1.000, 1, 20. Hai mốc đầu thiếu giá toàn bộ, nên đề và pipeline chỉ dùng giá ở mốc cuối.</p>

=== 293-296
<p>Ghi CSV (giữ thứ tự <code>CSV_COLUMNS</code>) rồi JSON (<code>ensure_ascii=False</code> để giữ tiếng Việt, thụt 2). CSV ghi trước, nên khi bước JSON lỗi (xem dòng 213) vẫn có CSV mới mà JSON là bản cũ: hai bằng chứng lệch nhau.</p>

=== 299-300
<p>Chạy được như script. Không được <code>run_pipeline.py</code> gọi; đây là công cụ kiểm tay trước khi tin vào dữ liệu.</p>

--- flow
## Đầu vào
fn 0 206 | main | Đọc tham số, yaml thô, workbook JSON
fn 1 45 | load_workbook | 1.000 listing_id + 5.000 review_id (chuỗi)
## Mỗi mốc
st 1 233 | Kiểm file | Có đủ 3 .csv.gz? byte, SHA-256
st 2 244 | Thiếu file | missing_input, tai_ve_ok = khong
fn 1 154 | check_snapshot | Lọc và đếm một mốc
fn 2 92 | read_listings | dtype=str, đếm số cột gốc
fn 2 97 | read_calendar | Chunk 200k, raw_rows, ngày, trùng khoá
fn 2 116 | read_reviews | Chunk, lọc theo review_id
fn 2 136 | row_counts | 1000; 875/125; 0 review; thiếu giá
fn 2 127 | missing_columns | Cột thiếu ≥ 90%
st 2 193 | key_integrity | ID thiếu/thừa/trùng
st 1 279 | So kỳ vọng | 365000, 5000, 875, 125 viết cứng
## Ghi ra
st 1 293 | Ghi CSV + JSON | check_DSE2049-C02-G06-sydney.csv + audit JSON
chips 0 | download:401 check_expected ; download:228 verify_raw

--- review
bug | Lỗi JSON với yaml hiện tại | Yaml thô có <code>qa.expected.snapshots</code> kiểu <code>date</code>; đã chạy với <code>configs/sydney.yaml</code>: CSV được ghi rồi <code>json.dumps</code> báo <code>TypeError: Object of type date is not JSON serializable</code>. Audit đã commit được tạo trước khi yaml có khoá này.
bug | Thiếu file vẫn failures rỗng | Nhánh <code>missing_input</code> không thêm vào <code>failures</code>; chạy thử không có file nào: 4 mốc <code>missing_input</code>, <code>failures = []</code>, mã thoát 0.
mid | Số kỳ vọng viết cứng | 365000, 5000, 875, 125 nằm trong code, không đọc <code>calendar_days</code>, <code>n_reviews</code>, <code>room_type_counts</code> của yaml; <code>[None] * 4</code> gây <code>IndexError</code> khi có hơn 4 mốc.
mid | Không lọc theo mã nhóm | Cột <code>code</code> của workbook được đọc nhưng không dùng; đúng chỉ khi JSON chỉ chứa vùng của nhóm 06.
low | Hash tính hai lần | SHA-256 mỗi file được tính ở dòng 169 và dòng 238.
low | Không test, không mypy | Script nằm ngoài <code>tests/</code>, ngoài danh sách mypy và ngoài coverage; chỉ có ruff kiểm.
ok | Kiểm chéo độc lập | Viết lại logic lọc, không import <code>src/download.py</code>; ghi SHA-256 và ID thiếu/thừa/trùng, nên bằng chứng kiểm lại được.

--- qa
? Script này khác bước 1 thế nào? Sao phải có hai chỗ kiểm?
<p>Bước 1 vừa lọc vừa tự kiểm, nếu lọc sai thì tự kiểm cũng có thể sai theo. Script này đọc lại file gốc bằng code riêng, không mạng, ghi thêm hash, ID thiếu/thừa/trùng, cột thiếu ≥ 90%. Kết quả đã commit: cả 4 mốc đạt, <code>failures</code> rỗng.</p>
? Bằng chứng nói gì về mẫu của nhóm?
<p>Ở cả 4 mốc: 1.000 listing (875/125), 365.000 dòng lịch, đủ 5.000 review, không ID thiếu/thừa/trùng. Số căn 0 review 50/30/25/25, thiếu giá 1.000/1.000/1/20 (<code>reports/check_DSE2049-C02-G06-sydney.csv</code>).</p>
? Vì sao mốc 2026-03-21 bị coi là mốc lỗi?
<p>Calendar gốc của mốc này chỉ có 4.950.495 dòng = 13.563 căn, so với 20.436 và 20.573 ở mốc trước và sau (<code>raw_rows</code> trong audit, <a href="#check_assignment-L100">dòng 100</a>). Mẫu của nhóm vẫn đủ 1.000 căn, nhưng thành phố bị lọc thiếu.</p>
? Chạy lại script bây giờ có ra đúng file đã commit không?
<p>Không hẳn. Với yaml hiện tại, CSV ra được nhưng bước ghi JSON lỗi vì ngày trong <code>qa.expected.snapshots</code> không chuyển được sang JSON (<a href="#check_assignment-L213">dòng 213</a>). Phải dùng yaml của commit <code>2a58a3f</code> hoặc sửa script cho đổi ngày sang chuỗi.</p>
? Có số nào script viết cứng không?
<p>Có: 365000, 5000, 875, 125 (<a href="#check_assignment-L280">dòng 280</a>). Chỉ số listing, số căn 0 review và số thiếu giá đọc từ yaml.</p>
