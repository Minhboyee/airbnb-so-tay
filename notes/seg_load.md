--- meta
title: segments/load.py
lead: Nạp listing của một mốc và thêm hai cột dẫn xuất: <code>days_since_review</code> (số ngày từ lần review cuối tới lần scrape) và <code>stay_type</code> (ngắn/trung/dài ngày theo <code>minimum_nights</code>). Chỉ đọc và chuẩn bị dữ liệu, không biết luật 7 nhóm. Điểm dễ bị hỏi: vì sao <code>id</code>/<code>host_id</code> đọc dạng chuỗi, vì sao phải <code>to_datetime</code> lại, và NaN rơi vào nhánh nào.

--- blocks
=== 1-6
<p>Docstring tóm tắt hợp đồng: vào là file listing của một mốc (đường dẫn tuỳ scope) và <code>config["segments"]</code> (<code>short_stay_max_nights</code>, <code>long_stay_min_nights</code>); ra là một DataFrame trong RAM, không ghi file. Luật chia nhóm nằm ở <code>rules.py</code>, module này không đụng tới.</p>

=== 8
<p><code>from __future__ import annotations</code> để chú thích kiểu dạng <code>dict[str, Any]</code>, <code>str | None</code> chạy được từ Python 3.10.</p>

=== 10-12
<p>Ba import kiểu: <code>Hashable</code> để gõ kiểu cho dict <code>dtypes</code> (pandas khai báo khoá dtype là <code>Hashable</code>), <code>Path</code> để ghép đường dẫn, <code>Any</code> cho config.</p>

=== 14-15
<p><code>numpy</code> để điền <code>np.nan</code> cho cột thiếu và dùng <code>np.select</code> phân loại; <code>pandas</code> để đọc CSV và xử lý cột.</p>

=== 17
<p><code>cfg_get</code> là hàm đọc tham số <code>segments.&lt;key&gt;</code>, thiếu thì báo lỗi rõ (xem <a href="#seg_rules-L35">seg_rules dòng 35</a>). Ở đây dùng để lấy hai ngưỡng <code>stay_type</code>.</p>

=== 19-31
<p>Chỉ đọc 10 cột cần cho phân nhóm. File full có khoảng 70 cột nên lọc bằng <code>usecols</code> giúp nhẹ RAM và nhanh hơn nhiều. Danh sách gồm khoá <code>id</code>/<code>host_id</code>, ngày (<code>last_scraped</code>, <code>last_review</code>), mô tả (<code>neighbourhood_cleansed</code>, <code>room_type</code>), và các cột số dùng cho luật (<code>minimum_nights</code>, <code>availability_365</code>, <code>number_of_reviews</code>, <code>number_of_reviews_ltm</code>).</p>

=== 33-34
<p>Hai cột ngày cần parse sang <code>datetime</code> để trừ nhau tính <code>days_since_review</code>.</p>

=== 37-42
<p><code>_path</code> quyết định file theo scope: <code>full</code> đọc <code>data/raw/&lt;city&gt;/&lt;mốc&gt;/listings.csv.gz</code>, còn lại (sample) đọc <code>data/processed/&lt;city&gt;/&lt;mốc&gt;/listings.csv</code>. Đường dẫn <b>tương đối</b> (<code>Path("data")</code>), nên phải chạy từ gốc repo; xem review.</p>

=== 45-50
<p>Hàm chính. Docstring nêu hai quyết định: (1) <code>id</code>/<code>host_id</code> đọc dạng <code>str</code> vì <code>id</code> là khoá nối giữa các mốc, đọc dạng số sẽ mất số 0 đầu hoặc bị đổi sang <code>float</code>; (2) cột không có trong file thì bỏ qua, không lỗi.</p>

=== 51-59
<p>Kiểm file tồn tại trước khi đọc. Nếu thiếu, thông báo <code>FileNotFoundError</code> có gợi ý riêng: scope <code>full</code> nhắc chạy <code>run_pipeline.py</code> không kèm <code>--skip-download</code> để tải <code>data/raw</code>; scope <code>sample</code> thì không thêm gợi ý đó (vì sample không tải từ mạng). Test <code>test_load_reports_missing_file_with_scope_specific_hint</code> kiểm đúng chuỗi <code>không có --skip-download</code> chỉ xuất hiện ở scope full.</p>

=== 61-62
<p>Đọc <b>header</b> trước bằng <code>nrows=0</code> (chỉ lấy tên cột, không đọc dòng nào), rồi lọc <code>COLUMNS</code> theo cột thực có. Nhờ vậy file thiếu cột không làm <code>usecols</code> lỗi. Cái giá là file bị mở hai lần (dòng 61 và 67); xem review.</p>

=== 63-65
<p><code>dtypes</code> ép <code>id</code>/<code>host_id</code> thành <code>str</code> ngay lúc đọc, chỉ với cột có mặt. Chú thích dòng 63 nói rõ lý do gõ <code>dict[Hashable, str]</code>: stub kiểu của pandas khai báo khoá là <code>Hashable</code>, gõ <code>str</code> sẽ trượt mypy. <code>dates</code> là danh sách cột ngày thực có để truyền <code>parse_dates</code>.</p>

=== 67
<p>Đọc thật một lần với <code>usecols</code>, <code>dtype</code>, <code>parse_dates</code>. Đây là chỗ tốn thời gian nhất của hàm; mốc cuối scope full đọc khoảng 20.573 dòng.</p>

=== 68-70
<p>Điền <code>np.nan</code> cho mọi cột trong <code>COLUMNS</code> mà file không có. Nhờ bước này các dòng sau luôn thấy đủ cột, khỏi phải kiểm <code>if "x" in df.columns</code> rải rác. Hệ quả: cột thiếu toàn NaN, và NaN sẽ được xử lý ở các bước sau (ví dụ <code>stay_type</code> thành <code>trung_han</code>).</p>

=== 72-73
<p>Một <code>id</code> có thể lặp trong file; giữ bản ghi đầu, bỏ bản sau, rồi đặt lại index. Nhờ vậy mỗi <code>id</code> đúng một dòng, mà ma trận đổi nhóm dựa vào việc index theo <code>id</code> nên cần đúng như thế. Test <code>test_load_reads_sample_scope_and_derives_columns</code> có hai dòng cùng id <code>001</code> và kiểm còn 4 dòng (không phải 5).</p>

=== 75-78
<p>Tính <code>days_since_review = last_scraped − last_review</code> theo ngày. Phải <code>to_datetime</code> lại vì cột ngày thiếu trong file đã bị điền <code>NaN</code> kiểu object ở dòng 68–70; <code>errors="coerce"</code> biến giá trị hỏng thành <code>NaT</code>. Khi <code>last_review</code> trống, hiệu là <code>NaT</code>, rồi <code>.dt.days</code> cho <code>NaN</code>. NaN này về sau được hiểu là "không có review gần đây" (xem <a href="#seg_rules-L79">seg_rules dòng 79</a>).</p>

=== 80-82
<p>Lấy hai ngưỡng từ config: <code>short_stay_max_nights = 20</code>, <code>long_stay_min_nights = 90</code> (yaml). <code>minimum_nights</code> ép số, giá trị hỏng thành NaN.</p>

=== 83-88
<p><code>np.select</code> xét theo thứ tự: <code>nights &lt;= 20</code> thì <code>ngan_ngay</code>; ngược lại <code>nights &gt;= 90</code> thì <code>dai_han</code>; còn lại <code>trung_han</code>. Vì NaN so sánh với số luôn <code>False</code> ở cả hai điều kiện, căn không rõ <code>minimum_nights</code> rơi vào <code>trung_han</code> (đúng như comment dòng 83). Ví dụ thật trong test: <code>minimum_nights</code> 20 thành ngắn, 21 thành trung, 90 thành dài; căn chỉ có <code>id</code> thành trung_han.</p>
<p>Ngưỡng dài ngày ở đây là <b>90</b>, còn audit mốc gap dùng ngưỡng riêng <code>gap_explain_min_nights = 7</code> ở <a href="#seg_transitions-L105">seg_transitions dòng 105</a>. Hai ngưỡng phục vụ hai việc khác nhau, đừng lẫn.</p>

=== 89
<p>Trả DataFrame đã sẵn sàng cho <code>classify</code> (có <code>segment</code> sẽ được gán sau) và cho bảng chi tiết của report.</p>

--- flow
## Đường dẫn
fn 0 37 | _path | raw .csv.gz (full) / processed .csv (sample)
## Nạp một mốc
fn 0 45 | load_listings | Đọc + thêm cột dẫn xuất
st 1 51 | Kiểm file | Thiếu thì FileNotFoundError kèm gợi ý
st 1 61 | Lọc cột | Đọc header rồi chỉ lấy cột cần
st 1 67 | Đọc thật | usecols + dtype id/host_id str + parse_dates
st 1 68 | Điền cột thiếu | Cột vắng thành np.nan
st 1 72 | Bỏ id trùng | Giữ bản ghi đầu
st 1 75 | days_since_review | last_scraped − last_review
st 1 80 | stay_type | ≤20 ngắn, ≥90 dài, còn lại trung
chips 1 | seg_rules:35 cfg_get ; seg_init:42 run

--- review
mid | Đường dẫn phụ thuộc cwd | <code>_path</code> ghép <code>Path("data")</code> tương đối, nên chỉ chạy đúng khi cwd là gốc repo. Gọi từ thư mục khác sẽ <code>FileNotFoundError</code> dù file có thật.
mid | File thiếu cột id sẽ mất dòng | Nếu listing không có cột <code>id</code>, dòng 68–70 điền toàn NaN rồi <code>drop_duplicates(subset="id")</code> coi mọi NaN là trùng và chỉ giữ 1 dòng (đã chạy thử với pandas). File thật luôn có <code>id</code> nên không gặp.
low | Đọc header hai lần | Mở file ở dòng 61 (<code>nrows=0</code>) rồi mở lại ở dòng 67. Có thể gộp nhưng đọc header riêng giúp lọc <code>usecols</code> an toàn.
ok | Giữ id dạng chuỗi | Ép <code>id</code>/<code>host_id</code> thành <code>str</code> ngay lúc đọc, tránh mất số 0 đầu và tránh lỗi nối khoá giữa các mốc.
ok | NaN xử lý nhất quán | Thiếu <code>minimum_nights</code> thì <code>trung_han</code>; thiếu <code>last_review</code> thì <code>days_since_review = NaN</code>, về sau được hiểu là "không review gần đây".

--- qa
? Vì sao đọc id và host_id dạng chuỗi?
<p><code>id</code> là khoá nối giữa 4 mốc. Đọc dạng số dễ bị đổi sang <code>float</code> hoặc mất số 0 đầu, làm hai mốc không khớp cùng một căn. Dòng 64 ép <code>dtype="str"</code> cho hai cột này ngay khi đọc.</p>
? Căn có minimum_nights = 20 và 21 được xếp loại gì?
<p>20 thành <code>ngan_ngay</code> (vì <code>&lt;= 20</code>); 21 thành <code>trung_han</code> (chưa tới 90). Căn 90 thành <code>dai_han</code>. Căn thiếu <code>minimum_nights</code> (NaN) cũng vào <code>trung_han</code> vì cả hai điều kiện đều False.</p>
? days_since_review được tính thế nào khi không có review?
<p><code>last_review</code> trống thì <code>NaT</code>, hiệu với <code>last_scraped</code> là <code>NaT</code>, <code>.dt.days</code> cho <code>NaN</code>. Ở <code>rules.py</code>, <code>NaN &lt;= 365</code> là False nên căn đó được coi là "không có review gần đây".</p>
? Vì sao phải gọi to_datetime lần nữa ở dòng 76?
<p>Vì các cột ngày thiếu trong file đã bị điền <code>np.nan</code> (kiểu object) ở dòng 68–70, nên phải ép lại sang datetime trước khi trừ. <code>errors="coerce"</code> biến giá trị hỏng thành <code>NaT</code> thay vì ném lỗi.</p>
