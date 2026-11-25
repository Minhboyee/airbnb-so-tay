--- meta
title: download.py
lead: Bước 1 của pipeline. Mỗi mốc tải 3 bảng <code>.csv.gz</code> và một <code>neighbourhoods.geojson</code> từ Inside Airbnb về <code>data/raw/sydney/&lt;mốc&gt;/</code>, kiểm tệp và cột khoá, rồi lọc về đúng 1.000 listing và 5.000 review của nhóm, ghi <code>data/processed/sydney/&lt;mốc&gt;/*.csv</code>. Ba điều hay bị hỏi: mọi ID đọc dạng chuỗi (ID dài 18–19 chữ số), review lọc theo <code>review_id</code> chứ không theo <code>listing_id</code>, và calendar đọc theo chunk. Bước này chỉ <b>cảnh báo</b> khi số lượng lệch đề; dừng hẳn là việc của QA.

--- blocks
=== 1-18
<p>Docstring tóm tắt vị trí, đầu vào, đầu ra và luồng. Đây là bước chạy đầu tiên: <code>run_pipeline.py</code> gọi <code>run(config)</code> ở <a href="#run_pipeline-L136">dòng 136</a>, trừ khi có cờ <code>--skip-download</code>.</p>
<p>Hai thư mục cần phân biệt khi vấn đáp:</p>
<ul><li><code>data/raw/sydney/&lt;mốc&gt;/</code>: file gốc, giữ nguyên, không sửa. Bị gitignore (nặng: riêng <code>reviews.csv.gz</code> mỗi mốc 69–85 MB, theo <code>reports/check_DSE2049-C02-G06-sydney.csv</code>).</li>
<li><code>data/processed/sydney/&lt;mốc&gt;/</code>: bảng đã lọc về mẫu của nhóm, thêm cột <code>snapshot</code>. Cũng không commit (<code>.gitignore</code> có <code>data/processed/*/</code>).</li></ul>
<p>Lệch nhỏ: dòng 7 ghi <code>snapshots</code> “(4 mốc)”, nhưng code chạy với số mốc bất kỳ; số 4 chỉ là số mốc nhóm được giao.</p>

=== 20-27
<p>Bốn ghi chú của trợ giảng, mỗi cái có chỗ áp dụng riêng trong file:</p>
<ol><li>ID dạng chuỗi: <a href="#download-L55">ID_DTYPES</a>, và <code>dtype=str</code> ở mọi chỗ đọc file ID.</li>
<li>Review lọc theo <code>review_id</code>: <a href="#download-L368">filter_reviews</a>.</li>
<li>Calendar đọc theo chunk, bỏ cột giá: <a href="#download-L382">read_calendar_filtered</a>.</li>
<li><code>analysis_area</code> lấy từ danh sách của đề: <a href="#download-L360">filter_listings</a>.</li></ol>
<p>Câu “ID đọc dạng số sẽ dễ bị làm tròn” chỉ đúng một phần. Pandas đọc cột ID không có ô trống thành <code>int64</code> và vẫn đúng từng chữ số: ID 19 chữ số của nhóm vẫn nhỏ hơn giới hạn int64 ≈ 9,22 tỉ tỉ, tức 19 chữ số. Hỏng thật xảy ra khi cột thành <code>float64</code>, chỉ cần một ô trống hoặc ID đi qua Excel. Xem ví dụ số ở <a href="#download-L53">dòng 53</a>.</p>

=== 29
<p>Cho phép viết chú thích kiểu <code>str | Path</code>, <code>dict | None</code> trên Python 3.10, phiên bản ghi trong <code>.python-version</code>.</p>

=== 31-40
<p>Import:</p>
<ul><li><code>json</code>: đọc geojson trong <code>check_raw_snapshot</code>.</li>
<li><code>os</code>: chỉ dùng <code>os.replace</code> (đổi tên <code>.part</code> thành tên thật).</li>
<li><code>time</code>: ngủ giữa các lần thử tải lại.</li>
<li><code>zlib</code>: để bắt <code>zlib.error</code> khi file gzip hỏng.</li>
<li><code>Hashable</code>: chỉ cho chú thích kiểu của <code>ID_DTYPES</code> (mypy đòi khoá của dtype dict là Hashable).</li>
<li><code>lru_cache</code>: nhớ kết quả đọc workbook đề bài.</li>
<li><code>requests</code>: HTTP. Không dùng <code>urllib</code> vì cần stream, timeout và các lớp lỗi rõ ràng.</li></ul>

=== 42
<p><code>expected_applies</code> (<a href="#config-L70">config.py dòng 70</a>) trả <code>True</code> chỉ khi mốc trong config trùng 4 mốc được giao. Dùng ở <a href="#download-L513">dòng 513</a> để không đối chiếu số lượng của đề khi đã đổi mốc.</p>

=== 44-51
<p>Hằng số nguồn dữ liệu:</p>
<ul><li>URL đầy đủ ghép từ <code>BASE_URL</code>, <code>data_root</code> (<code>australia/nsw/sydney</code>), mốc và tên file. Ví dụ: <code>https://data.insideairbnb.com/australia/nsw/sydney/2025-09-12/data/listings.csv.gz</code>.</li>
<li><code>DATA_FILES</code>: 3 bảng của đề. Geojson tải riêng vì nằm ở thư mục con khác (<code>visualisations</code>).</li>
<li>Hai file ID mặc định trong <code>data/samples/</code> (đã commit): <code>listing_ids.csv</code> 1.000 dòng, <code>review_ids.csv</code> 5.000 dòng, có cột <code>mau_llm</code> (1.000 dấu <code>x</code>) và <code>nhan_tay</code> (100 dấu <code>x</code>). Đã kiểm: không ID trùng, mọi <code>listing_id</code> của review đều thuộc 1.000 listing (713 listing có review được chọn).</li></ul>

=== 53-55
<p>Bộ dtype dùng chung cho mọi lần đọc bảng thô: <code>id</code>, <code>listing_id</code>, <code>host_id</code> luôn là chuỗi. Khoá không có trong file thì pandas bỏ qua, nên một dict dùng được cho cả listings, calendar, reviews. <code>run_pipeline.py</code> cũng import hằng này để đọc lại bảng đã xử lý (<a href="#run_pipeline-L36">dòng 36</a>).</p>
<p>Vì sao bắt buộc, có số thật: trong <code>review_ids.csv</code>, 3.634/5.000 review_id dài 18–19 chữ số. Đổi sang <code>float64</code> thì 3.613 ID sai chữ số cuối; trong <code>listing_ids.csv</code> là 705/1.000. Ví dụ đã chạy:</p>
<ul><li><code>383502732966388018</code> → <code>float</code> → <code>383502732966388032</code>.</li>
<li><code>385677313037790725</code> → <code>385677313037790720</code>.</li></ul>
<p>float64 chỉ giữ khoảng 15–17 chữ số có nghĩa. ID sai thì lọc <code>isin</code> không khớp dòng nào, và không có lỗi nào báo ra. Thêm một bẫy: nếu một bên là chuỗi, một bên là <code>int64</code>, thì <code>isin</code> cũng trả toàn <code>False</code> (đã chạy thử). Nên cả hai phía phải cùng là chuỗi.</p>
<p>Không có <code>reviewer_id</code> trong dict: cột này không dùng để lọc hay nối bảng.</p>

=== 57-60
<p>Calendar chỉ giữ 5 cột: khoá (<code>listing_id</code>, <code>date</code>) và ba cột phân tích dùng (<code>available</code>, <code>minimum_nights</code>, <code>maximum_nights</code>). <code>price</code>, <code>adjusted_price</code> cố ý bỏ: docstring nói calendar không có giá; giá lấy từ listings.</p>
<p>Calendar là bảng lớn nhất theo số dòng: file gốc mốc cuối có 7.509.145 dòng = 20.573 listing × 365 ngày (<code>raw_rows</code> trong <code>reports/assignment_data_audit.json</code>). Đọc 200.000 dòng một lần thì mỗi lúc RAM chỉ giữ một chunk, cộng các dòng đã lọc.</p>

=== 62-65
<p>Tên cột trong workbook Excel của đề (tiếng Việt). Chỉ dùng khi config có <code>ids.workbook</code>; config hiện tại để dòng đó dạng comment (<a href="#sydney_yaml-L66">sydney.yaml dòng 66</a>), nên đường này không chạy với Sydney.</p>

=== 68-70
<p>Đường dẫn gốc tương đối <code>data/raw/sydney</code> hoặc <code>data/processed/sydney</code>. Tương đối nghĩa là phải chạy từ thư mục gốc repo; test dùng <code>monkeypatch.chdir(tmp_path)</code> để mọi file ghi vào thư mục tạm.</p>

=== 73-75
<p>Ghép URL. <code>subdir</code> mặc định <code>data</code> cho 3 bảng; geojson truyền <code>visualisations</code>. Test <code>test_download_snapshots_fetches_three_tables_and_geojson</code> khẳng định đúng 4 URL này cho một mốc.</p>

=== 78-79
<p>Lỗi riêng cho trường hợp “tải xong không báo lỗi nhưng thiếu byte”. Kế thừa <code>OSError</code> để cùng họ với lỗi I/O. Được ném ở <a href="#download-L105">dòng 105</a> và nằm trong danh sách thử lại.</p>

=== 82-89
<p>Chỉ thử lại lỗi tạm thời: mất kết nối, hết thời gian chờ, đứt giữa luồng dữ liệu (<code>ChunkedEncodingError</code>), thiếu byte. Lỗi HTTP (<code>HTTPError</code> từ <code>raise_for_status</code>) không có ở đây: 403/404 nghĩa là sai mốc hoặc sai <code>data_root</code>, thử lại cũng vậy. Test <code>test_download_file_does_not_retry_http_errors</code>: 403 chỉ gọi GET đúng 1 lần.</p>
<p>5xx (máy chủ quá tải) cũng là <code>HTTPError</code> nên cũng không được thử lại.</p>

=== 90-92
<p>3 lần thử. Lần 1 lỗi chờ 5 giây, lần 2 lỗi chờ 10 giây, lần 3 lỗi thì ném lỗi ra. Tổng chờ tối đa 15 giây mỗi file. Test đặt <code>RETRY_WAIT_SECONDS = 0</code> (fixture <code>no_wait</code>) để không ngủ thật.</p>

=== 95-103
<p>Tải một lần (một “attempt”):</p>
<ul><li><code>stream=True</code> + <code>iter_content(1 MB)</code>: nhận và ghi từng khúc 1 MB, không nạp cả file 85 MB vào RAM.</li>
<li><code>timeout=120</code>: chờ tối đa 120 giây cho kết nối và giữa hai lần nhận dữ liệu (không phải tổng thời gian tải).</li>
<li><code>raise_for_status()</code>: mã 4xx/5xx thành <code>HTTPError</code> ngay, trước khi mở file.</li>
<li><code>if chunk</code>: bỏ khúc rỗng (keep-alive). Test <code>test_download_file_refetches_when_size_differs</code> có khúc <code>b""</code> ở giữa.</li></ul>

=== 104-105
<p>Kiểm đủ byte: so kích thước file vừa ghi với <code>Content-Length</code> lấy từ HEAD. Thiếu thì ném <code>IncompleteDownloadError</code>, và lỗi này được thử lại. <code>if expected</code>: nếu không biết dung lượng nguồn (HEAD lỗi hoặc không có header) thì bỏ qua phép so này.</p>

=== 108-116
<p>Hàm tải chính, docstring nêu 3 quy tắc. Tạo thư mục cha nếu chưa có (<code>parents=True</code>: tạo cả <code>data/raw/sydney/&lt;mốc&gt;</code>). <code>Path(path)</code> để nhận cả chuỗi.</p>

=== 118-128
<p>Gửi HEAD (chỉ lấy header, không tải nội dung) để biết <code>Content-Length</code>. Đã thử trên nguồn thật: HEAD <code>listings.csv.gz</code> mốc 2025-09-12 trả 200 và 10.561.421 byte, đúng bằng <code>listings_bytes</code> trong <code>reports/check_DSE2049-C02-G06-sydney.csv</code>.</p>
<p>HEAD lỗi (mất mạng): nếu file đã có và không rỗng thì in <code>[OFFLINE]</code> và dùng luôn. File chỉ xuất hiện ở <code>path</code> sau khi tải trọn (cơ chế <code>.part</code>), nên “có file” đồng nghĩa “file đã tải xong”. Chạy lại khi mất mạng không làm chết pipeline. Test <code>test_download_file_uses_local_copy_when_offline</code>: không gọi GET, file giữ nguyên.</p>
<p>HEAD lỗi mà chưa có file: không <code>return</code>, đi tiếp xuống GET với <code>expected = 0</code> (test <code>test_download_file_ignores_head_errors</code>).</p>

=== 130-132
<p>Đã có file và đúng dung lượng nguồn thì in <code>[SKIP]</code> và không tải lại. Nhờ vậy chạy lại pipeline không tải lại khoảng 400 MB. Test <code>test_download_file_skips_when_size_matches_content_length</code>.</p>
<p>Điều kiện cần <code>expected</code> khác 0. Nếu nguồn không gửi <code>Content-Length</code>, file đã có vẫn bị tải lại mỗi lần chạy (không sai, chỉ tốn thời gian).</p>

=== 134-135
<p>File tạm là <code>listings.csv.gz.part</code> cạnh file thật. Mọi lần ghi đều vào file tạm; file thật chỉ bị thay ở <a href="#download-L154">dòng 154</a>.</p>

=== 136-147
<p>Vòng thử lại. Khi gặp lỗi tạm thời:</p>
<ol><li>Xoá <code>.part</code> dở dang (<code>missing_ok=True</code>: không lỗi nếu chưa kịp tạo).</li>
<li>Lần cuối thì in <code>[FAIL]</code> và <code>raise</code> lại đúng lỗi gốc.</li>
<li>Chưa phải lần cuối: in <code>[RETRY] lần k/3</code>, ngủ <code>5 × k</code> giây, <code>continue</code>.</li></ol>
<p>Test <code>test_download_file_retries_transient_errors</code> tái hiện đủ: lần 1 <code>ConnectionError</code>, lần 2 nhận 2/4 byte (<code>IncompleteDownloadError</code>), lần 3 đủ 4 byte. Test <code>test_download_file_gives_up_and_keeps_old_file</code>: hết 3 lần thì file cũ (<code>b"old"</code>) vẫn nguyên và không còn <code>.part</code>.</p>

=== 148-153
<p>Mọi lỗi khác (HTTP, Ctrl+C, đĩa đầy…) cũng xoá <code>.part</code> rồi ném tiếp. Dùng <code>BaseException</code> chứ không <code>Exception</code> để bắt cả <code>KeyboardInterrupt</code>: người dùng bấm Ctrl+C giữa chừng cũng không để lại file dở. Riêng <code>HTTPError</code> in gợi ý kiểm tra <code>data_root</code> và mốc.</p>
<p>Hai nhánh <code>except</code> theo thứ tự: lỗi tạm thời rơi vào nhánh trên trước, nên nhánh này chỉ nhận lỗi không thử lại.</p>

=== 154-155
<p><code>os.replace</code> đổi tên <code>.part</code> thành tên thật. Trên cùng một ổ đĩa, phép đổi tên là nguyên tử: chương trình khác chỉ thấy file cũ hoặc file mới trọn vẹn, không bao giờ thấy nửa file. <code>os.replace</code> (khác <code>os.rename</code>) ghi đè được file cũ cả trên Windows. <code>break</code> thoát vòng sau lần thành công.</p>

=== 157-158
<p>In dung lượng MB và trả về đường dẫn (dùng trong test và để gọi lồng).</p>

=== 161-166
<p>Điều phối tải: tiêu đề in ra rồi lặp từng mốc. Trả về <code>data/raw/sydney</code> cho <code>run</code> dùng tiếp.</p>

=== 168-176
<p>Mỗi mốc 4 lần gọi <code>download_file</code>: 3 bảng theo <code>DATA_FILES</code>, rồi geojson. 4 mốc cho ra 16 file. <code>str(snapshot)</code> phòng khi mốc còn là <code>datetime.date</code> (gọi <code>run</code> không qua <code>load_config</code>); test <code>test_run_orchestration</code> truyền <code>date(2025, 9, 12)</code> và kiểm URL vẫn đúng.</p>
<p>Geojson (ranh giới khu, khoảng 4,3 MB) không được lọc hay dùng trong bước 1; nó được tải vì đề yêu cầu và để kiểm ở <code>verify_raw</code>.</p>

=== 178
<p>Trả gốc thư mục raw.</p>

=== 181-188
<p>Cột khoá từng bảng thô: thiếu cột nào thì không lọc hay nối bảng được.</p>
<ul><li>listings: <code>id</code>.</li>
<li>calendar: <code>listing_id</code>, <code>date</code> (khoá một ngày lịch).</li>
<li>reviews: <code>id</code> (review_id) và <code>listing_id</code>.</li></ul>
<p>Đây là phần “kiểm tệp tồn tại và có cột khoá” của đề.</p>

=== 191-192
<p>Lỗi riêng để dừng pipeline khi dữ liệu thô hỏng. Nguyên tắc: không lọc trên dữ liệu sai rồi sinh bảng sai mà không ai biết.</p>

=== 195-203
<p>Kiểm một mốc, trả danh sách lỗi thay vì ném lỗi ngay, để gom được nhiều lỗi. Bảng nào thiếu file hoặc file rỗng (0 byte) thì ghi “thiếu tệp” và chuyển bảng khác.</p>

=== 204-212
<p>Đọc header bằng <code>nrows=0</code>: pandas chỉ giải nén đoạn đầu file, nhanh dù file 85 MB. Bắt 4 loại lỗi: <code>OSError</code> (gzip sai định dạng), <code>EOFError</code>, <code>zlib.error</code>, <code>ValueError</code> (gồm <code>EmptyDataError</code>). Rồi so header với cột khoá.</p>
<p>Đã chạy thử: file gzip bị cắt mất nửa sau vẫn qua phép kiểm này, vì phần header còn nguyên; chỉ khi đọc cả file mới ra <code>EOFError: Compressed file ended before the end-of-stream marker</code>. Trong luồng bình thường điều này không xảy ra vì <code>download_file</code> đã so dung lượng và dùng <code>.part</code>; chỉ xảy ra nếu ai đó tự chép file dở vào <code>data/raw</code>.</p>

=== 214-224
<p>Geojson: phải tồn tại, là JSON hợp lệ, và có ít nhất một <code>feature</code> (ranh giới khu). <code>AttributeError</code> để bắt trường hợp JSON hợp lệ nhưng không phải object (ví dụ một mảng: mảng không có <code>.get</code>).</p>

=== 225
<p>Danh sách rỗng nghĩa là mốc đạt.</p>

=== 228-237
<p>Kiểm mọi mốc, mốc đạt in <code>[CHECK]</code>. Có lỗi thì gom tất cả vào một <code>RawDataError</code>, mỗi lỗi một dòng, để sửa một lượt thay vì chạy đi chạy lại. Test <code>test_verify_raw_reports_every_problem_at_once</code>: một mốc thiếu cột <code>date</code>, reviews hỏng gzip, geojson rỗng, mốc kia thiếu cả 4 tệp, thì một thông báo chứa đủ.</p>

=== 240-249
<p>Đọc ID từ workbook gốc của đề (Excel khoảng 18 MB, chứa cả 84 nhóm). <code>@lru_cache(maxsize=4)</code>: cùng (đường dẫn, mã nhóm) chỉ đọc file một lần trong một lần chạy. Tham số phải hashable nên <code>path</code> là <code>str</code>/<code>Path</code>, không phải DataFrame.</p>

=== 250-252
<p><code>dtype=str</code> ở <code>read_excel</code>: nếu không, ô số trong Excel thành <code>float64</code> và ID 18–19 chữ số mất chữ số cuối (cùng hiện tượng ở <a href="#download-L53">dòng 53</a>). Nếu chính file Excel đã lưu ID dạng số thì chữ số đã mất ngay trong Excel (Excel chỉ giữ 15 chữ số); <code>dtype=str</code> chỉ cứu được khi ô lưu dạng văn bản. Test <code>test_load_group_ids_from_workbook_uses_dtype_str</code> kiểm mọi lần gọi đều có <code>dtype is str</code>.</p>

=== 253-257
<p>Lọc theo cột <code>Mã dữ liệu</code> = <code>group_code</code> (<code>DSE2049-C02-G06-sydney</code>), đổi tên cột tiếng Việt, giữ đúng các cột code cần. Trả về cùng dạng với hai file CSV trong <code>data/samples/</code>.</p>

=== 260-265
<p>Nguồn ID của nhóm. Mặc định đọc CSV đã trích sẵn; chỉ đọc workbook khi config có <code>ids.workbook</code>.</p>

=== 266-272
<p>Nhánh workbook. Mã nhóm không có trong workbook thì <code>ValueError</code> (test <code>test_load_group_ids_rejects_unknown_group_code</code>), thay vì lọc ra 0 dòng rồi chạy tiếp. Trả <code>.copy()</code> vì <code>lru_cache</code> trả cùng một đối tượng cho mọi lần gọi: nơi gọi sửa bảng thì bản trong cache cũng hỏng theo.</p>

=== 273-275
<p>Nhánh mặc định (Sydney đang dùng): đọc hai CSV với <code>dtype=str</code> cho mọi cột. Test <code>test_load_group_ids_reads_every_id_as_exact_string</code>: ID 19 chữ số giữ nguyên, ID <code>"1000"</code> không thành <code>1000.0</code>.</p>

=== 278-283
<p>Chia khu thay thế, chỉ dùng khi chọn mẫu theo seed (thành phố khác, không có <code>analysis_area</code> của đề). Mục tiêu giống đề: 8 khu, số căn xấp xỉ bằng nhau.</p>

=== 284-287
<p>Cách chia:</p>
<ol><li><code>north</code>: vĩ độ ≥ trung vị thì gán 1 (bắc), còn lại 0 (nam). Ở Sydney vĩ độ âm, số lớn hơn (ít âm hơn) là phía bắc.</li>
<li>Trong mỗi nửa, chia kinh độ thành 4 phần bằng <code>qcut</code>, ra 0..3 (tây sang đông).</li>
<li>Mã khu = <code>north*4 + quarter + 1</code>, tức 1..8, rồi đổi thành <code>A01</code>..<code>A08</code>.</li></ol>
<p><code>rank(method="first")</code> trước khi <code>qcut</code>: nếu nhiều căn trùng kinh độ, <code>qcut</code> trên giá trị gốc báo lỗi “bin edges must be unique”; trên thứ hạng thì mọi giá trị khác nhau nên luôn chia được. Test <code>test_assign_areas_makes_eight_near_equal_areas</code>: 80 điểm, kinh độ chỉ 11 giá trị, vẫn ra 8 khu mỗi khu 9–11 căn.</p>

=== 290-298
<p>Mẫu dự phòng khi ID của nhóm không thuộc thành phố đang tải (giảng viên đổi config sang thành phố khác). Docstring nêu 3 quy tắc: listing phải có ở mọi mốc, seed cố định, review lấy ở mốc cuối vì review tích luỹ.</p>

=== 299-305
<ul><li>Chỉ đọc 3 cột <code>id</code>, <code>latitude</code>, <code>longitude</code> của listings mỗi mốc.</li>
<li><code>set.intersection</code>: giữ listing có ở mọi mốc, giống mẫu của đề (1.000 căn có mặt cả 4 mốc).</li>
<li><code>sort_values("id")</code> trước <code>sample</code>: cùng seed phải ra cùng mẫu dù thứ tự dòng trong file thay đổi. Test chạy hai lần, so <code>equals</code>.</li>
<li><code>min(n_listings, len(last))</code>: thành phố nhỏ hơn 1.000 căn thì lấy hết, không lỗi.</li></ul>

=== 306
<p>Gắn <code>analysis_area</code> bằng <code>assign_areas</code>. Cột ra giống file ID của nhóm (<code>listing_id</code>, <code>analysis_area</code>), nên phần sau không cần biết mẫu từ đâu.</p>

=== 308-310
<p>Review: mọi review của các listing đã chọn ở mốc cuối, đổi <code>id</code> thành <code>review_id</code>. Khác mẫu của đề: không giới hạn 5.000 và không có cột <code>mau_llm</code>/<code>nhan_tay</code>. Bước LLM xử lý trường hợp này: không có <code>mau_llm</code> thì lấy mẫu ngẫu nhiên theo seed (<a href="#llm-L115">llm.py dòng 115</a>).</p>

=== 313-316
<p>Phát hiện “ID của nhóm thuộc thành phố khác”: chỉ cần một listing của nhóm có trong file thô là coi như đúng thành phố. Chỉ đọc cột <code>id</code> của mốc đầu (gọi ở <a href="#download-L518">dòng 518</a>).</p>

=== 319-322
<p>Nơi lưu mẫu đã dùng: <code>data/processed/sydney/sample_listing_ids.csv</code> và <code>sample_review_ids.csv</code>.</p>

=== 325-333
<p>Các bước sau (KPI, LLM, so sánh LLM theo nhóm căn) gọi hàm này thay vì <code>load_group_ids</code>, để dùng đúng mẫu bước 1 đã dùng, kể cả khi chạy lại với <code>--skip-download</code>. Chưa có file mẫu (chưa chạy bước 1) thì dùng ID của nhóm. Test <code>test_load_sample_ids_falls_back_to_group_ids_before_step_one</code>.</p>

=== 336-344
<p>True khi mọi dòng của file mẫu có <code>sample_source == "seed"</code>. <code>run_pipeline.py</code> dùng nó ở <a href="#run_pipeline-L140">dòng 140</a> để bỏ <code>qa.expected</code> trước QA: các số 875/125, 50/30/25/25 chỉ đúng cho mẫu của nhóm, áp lên mẫu theo seed thì QA dừng oan.</p>

=== 347-352
<p>Đọc một bảng thô với <code>ID_DTYPES</code>. <code>low_memory=False</code>: pandas đọc cả file rồi mới đoán kiểu mỗi cột, tránh cảnh báo <code>DtypeWarning</code> và tránh một cột bị đoán kiểu khác nhau giữa các khúc (listings có hơn 80 cột, nhiều cột lẫn chữ và số).</p>

=== 355-357
<p>Lọc chung: <code>isin</code> trên một <code>set</code> chuỗi. <code>astype(str)</code> phòng khi danh sách ID truyền vào chưa là chuỗi. <code>.copy()</code> để bảng trả về độc lập, gán cột <code>snapshot</code> sau đó không gây <code>SettingWithCopyWarning</code>.</p>

=== 360-365
<p>Listings dùng <code>merge</code> (inner) chứ không <code>isin</code>, vì cần gắn thêm cột <code>analysis_area</code> của đề vào từng căn. Inner join: chỉ giữ căn có trong cả file thô và danh sách nhóm. Sau đó bỏ cột <code>listing_id</code> thừa (đã có <code>id</code>).</p>
<p>Không tự tính khu bằng toạ độ, để chỉ có một nguồn sự thật. Theo <code>data/samples/listing_ids.csv</code>, 8 khu có 120–130 căn: A01 123, A02 126, A03 130, A04 120, A05 126, A06 120, A07 129, A08 126.</p>

=== 368-371
<p>Ghi chú trợ giảng số 2: review lọc theo <code>review_id</code> (cột <code>id</code> của <code>reviews.csv.gz</code>). Nếu lọc theo <code>listing_id</code> thì lấy mọi review của 713 listing, nhiều hơn 5.000 review đề giao, và lẫn review không thuộc mẫu. Test <code>test_filter_reviews_uses_review_id_not_listing_id</code>: một review thuộc listing của nhóm nhưng không có trong danh sách review_id bị loại.</p>

=== 374-379
<p>Hàm truyền cho <code>usecols</code>: pandas gọi nó với từng tên cột trong header, giữ cột trả <code>True</code>. Dùng hàm thay vì danh sách vì danh sách sẽ báo lỗi nếu file thiếu một cột; hàm thì bỏ qua cột không có.</p>

=== 382-390
<p>Đọc calendar: <code>chunksize</code> làm <code>read_csv</code> trả về một bộ lặp, mỗi lần một <code>DataFrame</code> 200.000 dòng. <code>usecols</code> bỏ cột giá ngay khi đọc; <code>listing_id</code> dạng chuỗi.</p>

=== 391-395
<p>Lọc ngay trong từng chunk, chỉ giữ dòng của nhóm. Mốc cuối: 7.509.145 dòng gốc còn 365.000 dòng (1.000 × 365). <code>if not parts</code>: file không có dòng dữ liệu nào thì trả bảng rỗng đúng 5 cột, để <code>concat</code> không lỗi (test <code>test_read_calendar_filtered_empty_file_returns_empty_frame</code>).</p>

=== 398-414
<p>Đối chiếu số lượng một mốc với <code>qa.expected</code>. Docstring nói rõ: chỗ này chỉ cảnh báo, trả danh sách chuỗi. Nơi dừng hẳn là <a href="#qa_constraints-L22">qa_constraints.py</a> ở bước 2. Tách ra vậy vì bước 1 vẫn ghi CSV để người chạy mở ra xem lệch ở đâu.</p>

=== 415-421
<p>Đếm số listing (1.000) và số căn từng loại phòng (875 <code>Entire home/apt</code>, 125 <code>Private room</code>, <a href="#sydney_yaml-L26">sydney.yaml dòng 26</a>).</p>

=== 423-428
<p>Số căn 0 review theo vị trí mốc: 50, 30, 25, 25. <code>position</code> đếm từ 1 nên lấy <code>no_reviews[position - 1]</code>. <code>position &lt;= len(no_reviews)</code>: có thêm mốc thứ 5 thì bỏ qua phép này thay vì <code>IndexError</code>.</p>

=== 430-434
<p>Số căn thiếu giá chỉ kiểm ở mốc cuối (20 căn). Ở mốc 1 và 2, cả 1.000 căn của nhóm đều trống giá (cột <code>thieu_price</code> = 1000 trong <code>reports/check_DSE2049-C02-G06-sydney.csv</code>), nên kiểm ở đó vô nghĩa. Test <code>test_check_expected_price_only_checked_on_last_snapshot</code>.</p>
<p>“Mốc cuối” ở đây là <code>position == len(no_reviews)</code>, tức suy từ độ dài danh sách 0 review, không từ số mốc trong config. Với 4 mốc thì hai cách trùng nhau.</p>

=== 436-440
<p>Calendar phải đủ <code>n_listings × calendar_days</code> = 365.000 dòng.</p>
<p>Review: <code>n_reviews</code> = 5.000 là tổng của nhóm qua các mốc, nên ở từng mốc chỉ báo khi vượt tổng. Ít hơn 5.000 ở một mốc là bình thường (review bị gỡ). Test <code>test_check_expected_per_snapshot_reviews_below_total_is_fine</code>. Với Sydney, theo audit, cả 4 mốc đều có đủ 5.000 review.</p>

=== 442-448
<p>Phân bố khu: đúng 8 khu và mỗi khu nằm trong [120, 130] căn (<code>between</code> tính cả hai đầu). Chỉ kiểm khi bảng có cột <code>analysis_area</code>.</p>

=== 451-455
<p>Kiểm tổng review: hợp các <code>review_id</code> gặp ở mọi mốc phải đúng 5.000. Dùng tập hợp vì một review có mặt ở nhiều mốc chỉ tính một lần. Test <code>test_check_review_total_is_a_group_total</code>.</p>

=== 458-468
<p>Ghi CSV với <code>lineterminator="\r\n"</code>. Vấn đề có thật (commit <code>0aa866e</code>): comment review có ký tự <code>\r</code> đứng một mình; đọc lại CSV ra 5.015 dòng thay vì 5.000.</p>
<p>Cơ chế, đã chạy thử: module <code>csv</code> của Python 3.10 với <code>lineterminator="\n"</code> ghi <code>a\rb</code> không có ngoặc kép; <code>pd.read_csv</code> coi <code>\r</code> là xuống dòng nên một review thành 3 dòng. Khi <code>lineterminator</code> chứa <code>\r</code>, writer bắt buộc đặt ngoặc kép quanh trường có <code>\r</code>, nên đọc lại đúng.</p>
<p>Docstring nói hơi quá: trên Python 3.11, 3.12, 3.13 (đã chạy thử), writer tự đặt ngoặc kép quanh <code>\r</code> dù dùng <code>"\n"</code>. Nên lỗi chỉ tái hiện trên Python 3.10, đúng phiên bản trong <code>.python-version</code>. Test <code>test_write_csv_quotes_carriage_return_and_newline_comments</code> chạy trong CI trên cả 3.10.22 và 3.12.</p>

=== 471-484
<p>Xử lý trọn một mốc: lọc 3 bảng, gắn cột <code>snapshot</code>, đối chiếu, ghi CSV. <code>expected</code> có thể là <code>None</code> (mẫu theo seed hoặc mốc khác mốc được giao).</p>

=== 485-490
<p>Lọc 3 bảng theo 3 quy tắc khác nhau: listings theo <code>id</code> + gắn khu, calendar theo <code>listing_id</code> (đọc chunk), reviews theo <code>review_id</code>. Rồi thêm cột <code>snapshot</code> = tên mốc vào cả ba: sau này gộp nhiều mốc vẫn biết dòng thuộc mốc nào.</p>

=== 492-493
<p>Có <code>expected</code> thì đối chiếu, gộp cảnh báo thành chuỗi <code>WARN: …</code>; không thì <code>OK</code>.</p>

=== 495-502
<p>Ghi 3 CSV qua <code>_write_csv</code> và in một dòng tóm tắt. Với Sydney mỗi mốc phải in <code>listings=1000 calendar=365000 reviews=5000 | OK</code>. Ghi cả khi có cảnh báo, để mở file xem lệch ở đâu.</p>

=== 505-510
<p>Điểm vào của bước 1. Thứ tự: tải (bỏ qua file đã đủ), đổi mốc về chuỗi, rồi <code>verify_raw</code>. Kiểm trước khi lọc: test <code>test_run_stops_before_filtering_when_raw_is_broken</code> cho listings thiếu cột <code>id</code> và khẳng định thư mục processed không được tạo.</p>

=== 511
<p>Đọc ID của nhóm (mặc định từ <code>data/samples/</code>).</p>

=== 512-515
<ul><li><code>expected</code>: chỉ lấy khi mốc trong config trùng <code>qa.expected.snapshots</code>. <code>run_pipeline.py</code> đã bỏ <code>qa.expected</code> trong trường hợp này rồi (<a href="#run_pipeline-L125">dòng 125</a>); kiểm lại ở đây để gọi <code>download.run</code> trực tiếp cũng an toàn.</li>
<li><code>calendar_days</code>: mặc định 365.</li>
<li><code>out_root</code>: <code>data/processed/sydney</code>.</li></ul>

=== 517-526
<p>Quyết định nguồn mẫu. Mặc định <code>"group"</code>. Nếu không listing nào của nhóm có trong file listings mốc đầu thì:</p>
<ul><li>Cỡ mẫu = <code>n_listings</code> của <code>expected</code> nếu có, không thì 1.000.</li>
<li><code>seed</code> từ config (Sydney: 42).</li>
<li>Gọi <code>sample_ids_by_seed</code>, đặt <code>source = "seed"</code> và <code>expected = None</code>: không đối chiếu số của đề nữa.</li></ul>
<p>Test <code>test_run_uses_seed_sample_when_group_ids_belong_to_another_city</code> giả thành phố Vienna: lấy 8 listing, <code>expected</code> truyền xuống là <code>None</code>, in <code>[SAMPLE]</code>.</p>

=== 528-532
<p>Ghi mẫu đã dùng, kèm cột <code>sample_source</code>. Đây là “hợp đồng” giữa bước 1 và các bước sau (<code>load_sample_ids</code>, <code>is_seed_sample</code>). Hai file này dùng <code>to_csv</code> thường, không qua <code>_write_csv</code>, vì chỉ chứa ID và nhãn, không có văn bản tự do.</p>

=== 534-547
<p>Lặp từng mốc với <code>position</code> đếm từ 1 (dùng cho 50/30/25/25). Sau mỗi mốc, gom <code>id</code> review vào một tập hợp để kiểm tổng cuối cùng.</p>

=== 549-557
<p>Kiểm tổng review và in <code>[TOTAL] reviews=5000 | OK</code>. Test <code>test_run_warns_when_group_review_total_differs</code>: tổng 2 so với kỳ vọng 5.000 thì in <code>WARN</code> nhưng không dừng. Kết thúc bằng thông báo <code>DONE</code>.</p>

--- flow
## Lúc import
st 0 53 | ID_DTYPES | id, listing_id, host_id luôn là chuỗi
st 0 84 | RETRYABLE_ERRORS | Lỗi mạng tạm thời được thử lại
## Điểm vào
fn 0 505 | run | Tải → kiểm → lọc → ghi → kiểm tổng
fn 1 161 | download_snapshots | 4 mốc × (3 bảng + geojson)
fn 2 108 | download_file | HEAD, SKIP/OFFLINE, .part, thử lại
st 3 118 | HEAD lấy Content-Length | Mất mạng mà có file: dùng file cũ
st 3 136 | Vòng 3 lần thử | Chờ 5 s, 10 s; lỗi HTTP không thử lại
fn 3 95 | _stream_to | GET stream 1 MB, kiểm đủ byte
st 3 154 | os.replace | .part → tên thật
fn 1 228 | verify_raw | Gom mọi lỗi tệp/cột khoá, dừng một lần
fn 2 195 | check_raw_snapshot | Header (nrows=0), geojson có features
fn 1 260 | load_group_ids | CSV data/samples (dtype=str) hoặc workbook
st 1 517 | ID nhóm có trong thành phố? | Không thì chọn mẫu theo seed
fn 2 290 | sample_ids_by_seed | Listing có ở mọi mốc, seed, 8 khu
st 1 528 | Ghi mẫu đã dùng | sample_source = group / seed
## Mỗi mốc
fn 1 471 | process_snapshot | Lọc 3 bảng, thêm snapshot, ghi CSV
fn 2 360 | filter_listings | merge id, gắn analysis_area của đề
fn 2 382 | read_calendar_filtered | Chunk 200k, 5 cột, lọc listing_id
fn 2 368 | filter_reviews | Lọc theo review_id
fn 2 401 | check_expected | 1000; 875/125; 50/30/25/25; 365000 (chỉ cảnh báo)
fn 2 461 | _write_csv | CRLF để quote ký tự \r
## Cuối
fn 1 451 | check_review_total | Hợp review_id = 5000
chips 1 | run_pipeline:136 gọi từ main ; run_pipeline:140 is_seed_sample ; 325 load_sample_ids

--- review
mid | Docstring _write_csv nói quá | Lỗi <code>\r</code> chỉ tái hiện trên Python 3.10: đã chạy, csv writer 3.11–3.13 tự đặt ngoặc kép quanh <code>\r</code> dù <code>lineterminator="\n"</code>. Bản sửa vẫn đúng và cần thiết vì dự án khai báo 3.10.
mid | verify_raw không bắt gzip bị cắt đuôi | Chỉ đọc header (<code>nrows=0</code>); đã thử file gzip cắt nửa: qua kiểm tra, đọc cả file mới ra <code>EOFError</code>. Luồng tải bình thường được che bởi so Content-Length và <code>.part</code>, nhưng nhánh <code>[OFFLINE]</code> chấp nhận mọi file không rỗng.
low | Không thử lại lỗi 5xx | <code>HTTPError</code> không nằm trong <code>RETRYABLE_ERRORS</code>, nên 503 tạm thời cũng dừng ngay như 404.
low | Thiếu Content-Length thì tải lại mãi | Điều kiện SKIP cần <code>expected</code> khác 0; nguồn không gửi header này thì mỗi lần chạy tải lại cả 16 file. Inside Airbnb hiện có gửi (HEAD thử: 10.561.421 byte).
low | Docstring ghi “4 mốc” | Code chạy với số mốc bất kỳ; check_expected còn tự bỏ phép kiểm 0 review khi có mốc thứ 5.
ok | ID luôn là chuỗi | <code>ID_DTYPES</code> và <code>dtype=str</code> ở mọi nơi đọc ID; với dữ liệu nhóm, float64 sẽ làm sai 3.613/5.000 review_id và 705/1.000 listing_id.
ok | Tải an toàn | File thật chỉ bị thay bằng <code>os.replace</code> sau khi tải đủ byte; lỗi nào cũng xoá <code>.part</code>; có test cho thử lại, mất mạng, hết lượt thử.

--- qa
? Vì sao phải đọc ID dạng chuỗi? Đọc số nguyên có sao không?
<p>Cột không có ô trống thì pandas đọc thành <code>int64</code>, vẫn đúng. Hỏng khi thành <code>float64</code>: một ô trống, hay đi qua Excel. Ví dụ <code>383502732966388018</code> thành <code>383502732966388032</code>; với dữ liệu nhóm là 3.613/5.000 review_id sai. Ngoài ra chuỗi với int64 không khớp nhau trong <code>isin</code>. Nên mọi chỗ đều đọc chuỗi (<a href="#download-L55">dòng 55</a>).</p>
? Vì sao review lọc theo review_id chứ không theo listing_id?
<p>Đề giao đúng 5.000 review cụ thể. Lọc theo listing_id sẽ lấy mọi review của 713 listing, nhiều hơn và lẫn review ngoài mẫu (<a href="#download-L368">dòng 368</a>).</p>
? File .part để làm gì?
<p>Tải vào <code>listings.csv.gz.part</code>, đủ byte mới <code>os.replace</code> thành tên thật. Nên file ở tên thật luôn là bản trọn; nhờ vậy khi mất mạng có thể yên tâm dùng file cũ, và tải hỏng không đè mất bản cũ (<a href="#download-L135">dòng 135</a>).</p>
? Khi nào thử tải lại, khi nào không?
<p>Thử lại tối đa 3 lần (chờ 5 s rồi 10 s) với lỗi mạng tạm thời và tải thiếu byte. Lỗi HTTP như 403/404 không thử lại vì là sai mốc hoặc sai <code>data_root</code> (<a href="#download-L84">dòng 84</a>).</p>
? Calendar mấy triệu dòng thì đọc thế nào?
<p>Đọc 200.000 dòng mỗi chunk, chỉ 5 cột, lọc ngay trong từng chunk. Mốc cuối 7.509.145 dòng gốc còn 365.000 dòng của nhóm (<a href="#download-L382">dòng 382</a>).</p>
? Số lượng lệch đề thì bước 1 có dừng không?
<p>Không. <code>check_expected</code> chỉ in <code>WARN</code> và vẫn ghi CSV. QA ở bước 2 mới dừng (<a href="#qa_constraints-L22">qa_constraints.py</a>). Bước 1 chỉ dừng khi dữ liệu thô thiếu tệp hoặc cột khoá (<code>RawDataError</code>).</p>
? Đổi sang thành phố khác thì mẫu lấy ở đâu?
<p>ID của nhóm không có ở thành phố mới thì chọn ngẫu nhiên 1.000 listing có ở mọi mốc theo <code>seed</code>, chia 8 khu theo vĩ độ/kinh độ, bỏ đối chiếu số lượng của đề. Mẫu ghi ở <code>sample_listing_ids.csv</code> với <code>sample_source = seed</code> (<a href="#download-L517">dòng 517</a>).</p>
? Vì sao ghi CSV bằng CRLF?
<p>Comment review có <code>\r</code> trần. Trên Python 3.10, ghi bằng <code>"\n"</code> thì trường đó không được bọc ngoặc kép, đọc lại ra 5.015 dòng thay vì 5.000. Có <code>\r</code> trong lineterminator thì writer buộc bọc ngoặc kép (<a href="#download-L461">dòng 461</a>).</p>
