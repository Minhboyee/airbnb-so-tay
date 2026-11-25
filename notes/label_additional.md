--- meta
title: label_additional_reviews.py
lead: Script phụ (không nằm trong pipeline) gán nhãn thêm 1.000 review ngoài mẫu chính thức, lưu vào cache riêng, để làm phân tích mở rộng 4.000/5.000 review. Mỗi cohort có file metadata ghi model, bộ khía cạnh, mã băm prompt và mã băm danh sách ID; <code>llm_segments.run_cohorts</code> dựa vào metadata đó để từ chối cache lạ. Chạy theo 10 checkpoint 100 review, có backup và kiểm cache không bị sửa từ ngoài.

--- blocks
=== 1
<p>Docstring một dòng nhưng đủ ba thông tin: đây là 1.000 review ngoài mẫu chính thức, cache riêng, và gắn với prompt hiện tại. Chữ "hiện tại" là lý do có <code>manifest</code>: đổi prompt mà dùng lại cache cũ là trộn hai định nghĩa nhãn.</p>

=== 3-10
<p>Tám import: <code>argparse</code>, <code>hashlib</code> (băm prompt/ID), <code>json</code>, <code>os</code> (đọc key), <code>tempfile</code> (backup), <code>time</code> (nhịp gọi), <code>Path</code>, <code>copy2</code> (sao lưu giữ metadata file).</p>

=== 12
<p><code>pandas</code> để đọc <code>reviews.csv</code> và cắt cohort.</p>

=== 13
<p><code>load_dotenv</code> nạp <code>.env</code> để lấy key, chỉ dùng trong <a href="#label_additional-L102">run</a>.</p>

=== 15-16
<p>Dùng lại <code>llm</code> (build prompt, cache, gọi batch) và <code>load_config</code>. Không viết lại logic LLM, script này chỉ tổ chức cohort và checkpoint.</p>

=== 18-23
<p>Sáu hằng số cấu hình. <code>CACHE</code>/<code>META</code> là đường dẫn cache và metadata của cohort 1 (đổi trong <code>main</code> khi chạy cohort 2–4). <code>BLOCK_SIZE = 100</code> và <code>BATCH_SIZE = 10</code> cho 10 block × 100 = 1.000 review, mỗi block 10 lô 10 review. <code>INTERVAL = 5.0</code> là nghỉ 5s giữa hai lô. <code>TEMP_DIR = gettempdir()/"opencode"</code> là nơi ghi backup; tên "opencode" là dấu vết môi trường tạo ra script, xem mục review.</p>

=== 26-27
<p><code>select_cohort</code> chọn 1.000 review ngoài mẫu. Docstring nói rõ "đoạn tuần tự"; đây là chỗ dễ hiểu nhầm thành mẫu ngẫu nhiên, nhưng nó không ngẫu nhiên.</p>

=== 28-30
<p>Đọc <code>reviews.csv</code> của mốc cuối với <code>keep_default_na=False</code>: ô trống thành <code>""</code> chứ không thành NaN, để <code>.str.strip().str.len()</code> không lỗi trên NaN. <code>official</code> là tập 1.000 ID mẫu chính thức, lấy qua đúng hàm của <a href="#llm-L92">llm.load_sample_reviews</a>.</p>

=== 31-32
<p>Trùng ID trong <code>reviews.csv</code> là lỗi dữ liệu, vì không thể cắt cohort sạch.</p>

=== 33
<p><code>others</code> = review không thuộc mẫu chính thức và comment dài ít nhất 15 ký tự, cùng ngưỡng với <a href="#llm-L89">llm._read_usable_reviews</a>. Giữ thứ tự file.</p>

=== 34
<p>Cắt đoạn thứ <code>segment</code>: cohort 1 là dòng 0–999, cohort 2 là 1.000–1.999… <code>reset_index</code> để vị trí bắt đầu lại từ 0. Vì là cắt tuần tự nên bốn cohort rời nhau và phụ thuộc thứ tự file; mã băm ở <a href="#label_additional-L52">manifest</a> sẽ chặn nếu thứ tự đổi.</p>

=== 35-36
<p>Ba điều kiện phải đúng: mẫu chính thức đủ 1.000, cohort đủ 1.000, và hai tập rời nhau. Không đủ review ngoài mẫu thì dừng, không lấy bừa review đã có nhãn. Đã chạy thử trên dữ liệu thật: cả 4 cohort đều đúng 1.000 và rời nhau, tổng với mẫu chính thức là 5.000.</p>

=== 37
<p>Trả DataFrame 1.000 dòng theo thứ tự file.</p>

=== 40-41
<p><code>manifest</code> tạo "dấu vân tay" của một lần chạy. Docstring nói mục đích: lần chạy lại không trộn kết quả của phiên bản khác.</p>

=== 42-44
<p>Dựng prompt với một review giả <code>placeholder</code>, chỉ cần phần tĩnh của prompt (vai trò, luật, định dạng) để băm; nội dung review không nằm trong hash. <code>ids</code> là JSON của danh sách ID theo đúng thứ tự cohort.</p>

=== 45-54
<p>Tám trường metadata. Bốn trường kiểm được bằng mắt: <code>city</code>, <code>snapshot</code>, <code>model</code>, <code>schema_version</code>. Hai trường băm: <code>prompt_sha256</code> (đổi luật khía cạnh là đổi hash) và <code>cohort_sha256</code> (đổi danh sách hoặc thứ tự ID là đổi hash). <code>cohort_size</code> để so nhanh.</p>
<p>Đã kiểm trên repo: <code>manifest</code> tính lại cho cả 4 cohort khớp hoàn toàn với 4 file <code>llm_additional_v4*_meta.json</code> đã commit, gồm cả <code>prompt_sha256</code> (700c676c…) và <code>cohort_sha256</code>.</p>

=== 57-58
<p><code>prepare_cache</code> chặn ba kiểu trộn: cache thiếu metadata, metadata đã đổi, và cache chứa ID không thuộc cohort hoặc trùng mẫu chính thức.</p>

=== 59-60
<p>Chỉ có một trong hai file là trạng thái nửa vời, nên dừng ngay. Không tự "sửa" bằng cách tạo file thiếu.</p>

=== 61-63
<p>Có metadata rồi thì phải giống hệt manifest hiện tại. So cả dict, nên đổi model, prompt hay danh sách ID đều bị bắt. Test <code>test_prepare_cache_refuses_new_prompt_without_mutating_cache</code> kiểm cache không bị sửa khi từ chối.</p>

=== 64-67
<p>Lần đầu: tạo metadata rồi tạo cache rỗng. Thứ tự này để nếu chết giữa chừng thì không bao giờ có cache mà thiếu metadata.</p>

=== 69-74
<p>Đọc cache bổ sung và cache chính thức (cùng kiểm schema/aspect). Hai điều kiện: không có ID ngoài cohort, không giao với mẫu chính thức. Nhờ vậy <code>kpi.compute_extended_llm_kpis</code> không phải khử trùng giữa hai cache, nó sẽ báo lỗi nếu có.</p>

=== 77-78
<p><code>ObservedClient</code> là lớp bọc mỏng quanh client Google. Docstring nói mục đích: ghi lại mã HTTP để phân biệt 429 (quota) với lỗi nhãn, và không in API key.</p>

=== 80-81
<p>Chỉ thay <code>interactions</code> bằng phiên bản quan sát; mọi thuộc tính khác đi thẳng qua object gốc.</p>

=== 83-87
<p>Lưu client gốc, danh sách mã lỗi, và số lần gọi. <code>calls</code> dùng cho hai việc: giới hạn 50 request/checkpoint và in tổng request cuối.</p>

=== 89-95
<p>Mỗi lần gọi tăng <code>calls</code>; lỗi thì ghi <code>error.code</code> (có thể <code>None</code> nếu exception không có thuộc tính này) rồi raise lại. Lớp bọc không tự xử lý lỗi, chỉ ghi nhận, nên <code>llm.call_gemini_batch</code> vẫn là nơi quyết định thử lại.</p>

=== 98-99
<p><code>run</code> ghi nhãn cho cả cohort. Docstring nói 10 block, mỗi block 100 review, tức 5 đợt 200 review (2 checkpoint mỗi đợt). Chỉ nhãn của batch hợp lệ mới được ghi.</p>

=== 100
<p>Import trễ <code>google.genai</code>: chỉ cần khi thật sự gọi API, nên <code>--dry-run</code> và test không cần cài SDK.</p>

=== 102-105
<p><code>load_dotenv(dotenv_path=Path(".env"))</code> nạp đúng file trong thư mục repo. Thiếu key thì <code>ValueError</code> trước khi mở client, không gọi API nửa vời.</p>

=== 107-110
<p><code>last_end</code> giữ mốc kết thúc lô trước để giữ nhịp 5s; <code>start</code> để in tổng thời gian. Mở client một lần cho cả 10 block, bọc <code>ObservedClient</code>.</p>

=== 111-117
<p>Vòng 10 block, mỗi block 100 review. Trước khi gửi, đọc lại cache và chỉ lấy phần thiếu, nên chạy lại sau khi đứt giữa chừng là tiếp tục chứ không làm lại. Block đã đủ thì in <code>already_cached=100</code> và bỏ qua.</p>

=== 119-120
<p><code>before</code> là ảnh chụp byte của cache trước block, dùng làm mốc "cache chưa bị ai sửa". Tạo thư mục backup nếu chưa có.</p>

=== 121-123
<p>Tạo file tạm có tên chứa số block, <code>delete=False</code> để file không bị xoá khi đóng handle, cần giữ làm bản sao lưu.</p>

=== 124-126
<p><code>copy2</code> giữ nguyên metadata file. <code>expected_bytes</code> = nội dung cache ngay sau backup; mọi lần ghi phải nối tiếp đúng từ mốc này.</p>

=== 127-131
<p>Chia phần thiếu thành lô 10. <code>calls_before</code> đếm request của riêng block này; <code>block_started</code>/<code>transient_retries</code> phục vụ thống kê và backoff. Dòng in ghi cả đường dẫn backup để có thể khôi phục bằng tay.</p>

=== 133-139
<p><code>while queue</code> xử lý từng lô, có thể chèn lại đầu hàng khi lỗi. Hai chi tiết:</p>
<ul><li>Giới hạn 50 request/block 100: bình thường cần 10, dư cho vài lần chia lô; vượt là dấu hiệu bất thường nên dừng.</li>
<li>Giữ nhịp <code>INTERVAL</code> tính từ lần gọi trước, kể cả sau khi chờ backoff.</li></ul>

=== 141-143
<p>Gọi <a href="#llm-L247">llm.call_gemini_batch</a>, hàm này đã tự thử 3 lần cho mỗi lô. Ghi lại mốc kết thúc để tính nhịp cho lô sau.</p>

=== 144-152
<p>Khi lô thành công, bốn bước theo thứ tự:</p>
<ol><li>đặt lại <code>transient_retries</code>;</li>
<li>kiểm tập ID trả về bằng đúng tập ID đã gửi;</li>
<li>kiểm cache trên đĩa vẫn đúng là <code>expected_bytes</code>, nếu file bị sửa từ ngoài thì không ghi;</li>
<li>mới <code>append_to_cache</code> và cập nhật <code>expected_bytes</code>.</li></ol>
<p>Nhờ bốn bước này, cache không bị tiến trình khác trộn vào.</p>

=== 153-160
<p>Nhánh 429: thử lại tối đa 3 lần với backoff 30s, 60s, 120s; lô được chèn lại đầu hàng để chạy lại ngay. Quá 3 lần thì dừng và giữ cache, vì 429 lặp thường là hết quota ngày, chờ tiếp vô ích.</p>

=== 161-168
<p>Nhánh 408/5xx: cùng cơ chế backoff nhưng thông điệp khác. Tách khỏi 429 vì nguyên nhân khác (lỗi phía server so với hết quota) và cách xử lý của người chạy khác.</p>

=== 169-170
<p>Một review đơn lẻ vẫn thất bại sau 3 lượt của <code>call_gemini_batch</code> thì dừng. Không thể chia nhỏ hơn nữa, và không được bỏ qua vì sẽ làm mẫu số hụt mà không báo.</p>

=== 171-175
<p>Lô nhiều review thất bại: chia đôi rồi chèn lại đầu hàng, nhờ vậy một review "độc" làm hỏng cả lô 10 không kéo theo 9 review tốt. Nhờ cách chia để trị, giới hạn 50 request/block mới có ý nghĩa.</p>

=== 176-187
<p><code>finally</code> luôn in checkpoint, kể cả khi lỗi:</p>
<ul><li><code>total</code>: số nhãn trong cache;</li>
<li><code>in_block</code>: bao nhiêu/100 review của block đã có nhãn;</li>
<li><code>old_unchanged</code>: cache vẫn bắt đầu bằng <code>before</code> và mọi bản ghi cũ giữ nguyên giá trị;</li>
<li><code>backup_ok</code>: file backup bằng đúng <code>before</code>;</li>
<li><code>elapsed</code>: thời gian block.</li></ul>
<p>Bốn chỉ số này đủ để biết có cần khôi phục backup hay không.</p>

=== 189-195
<p>Sau 10 block: đọc cache cuối, in <code>completed</code>, tổng request, tổng thời gian. Không đủ 1.000 là <code>RuntimeError</code>, script không tuyên bố thành công khi thiếu nhãn.</p>

=== 198-199
<p><code>main</code> cho cohort cụ thể. Hai tham số: <code>--dry-run</code> và <code>--segment</code> (1–4).</p>

=== 200-202
<p><code>choices=(1,2,3,4)</code> chặn cohort không tồn tại ngay ở argparse.</p>

=== 203-209
<p><code>global CACHE, META</code> rồi đổi đường dẫn theo cohort. Quy ước tên không đều: cohort 1 dùng tên gốc <code>llm_cache_additional_v4.jsonl</code>, cohort 2 thêm <code>_2</code>, cohort 3–4 thêm <code>_3</code>/<code>_4</code>.</p>

=== 210-212
<p>Đọc config Sydney, và với cohort 3–4 đổi model sang <code>gemini-3.5-flash-lite</code>. Đổi này phải khớp metadata đã commit; đã kiểm: <code>v4_3</code>/<code>v4_4</code> ghi <code>gemini-3.5-flash-lite</code>, hai cohort đầu ghi <code>gemini-3.1-flash-lite</code>.</p>

=== 213-218
<p>Chọn cohort, tạo manifest, rồi đòi cache chính thức đủ 1.000. Không có mẫu chính thức thì không thể bảo đảm cohort "ngoài mẫu".</p>

=== 219-235
<p>Với mọi cohort trước cohort đang chạy: dựng lại manifest của cohort đó và so với metadata trên đĩa. Nếu prompt/cohort đã đổi thì dừng, vì các cohort phải được tạo dưới cùng một prompt để bảng gộp có nghĩa. Kèm ba kiểm tra cache cũ: cohort 1 phải đủ 1.000, không có ID ngoài cohort của nó, không giao với cohort hiện tại.</p>
<p>Chi tiết dễ bỏ qua: <code>prior_config["llm"]["model"]</code> chỉ đổi khi <code>previous == 3</code>; vòng lặp chạy tới <code>segment-1</code> nên không bao giờ cần xét cohort 4 như "cohort trước".</p>

=== 236-240
<p><code>--dry-run</code> in ba dòng: cohort có nằm ngoài mẫu chính thức, hai mã băm, cache đã tồn tại chưa, rồi thoát trước khi mở client. Cách này kiểm được "prompt đã đổi chưa" mà không tốn request.</p>

=== 241-243
<p>Chuẩn bị cache (kiểm/tạo metadata), chọn tên biến môi trường: cohort 3 dùng <code>2nd_GEMINI</code>, cohort 4 dùng <code>3rd_GEMINI</code>, còn lại <code>GEMINI_API_KEY</code>, tức ba key riêng để không đụng quota của nhau. Rồi gọi <a href="#label_additional-L98">run</a>.</p>

=== 246-247
<p>Chỉ chạy <code>main</code> khi gọi trực tiếp: <code>python scripts/label_additional_reviews.py --segment 2</code>.</p>

--- flow
## Chọn cohort
fn 0 26 | select_cohort | 1.000 review ngoài mẫu, cắt tuần tự theo segment
st 1 33 | Lọc ngoài mẫu | Không thuộc 1.000 mau_llm, comment ≥ 15 ký tự
st 1 35 | Kiểm đủ và rời nhau | Sai là dừng
## Dấu vân tay
fn 0 40 | manifest | city, mốc, model, schema, sha256 prompt và ID
## Chặn trộn phiên bản
fn 0 57 | prepare_cache | Cache/meta phải cùng tồn tại và khớp manifest
st 1 69 | Đọc hai cache | Bổ sung không giao mẫu chính thức
## Gọi API
fn 0 77 | ObservedClient | Ghi mã lỗi và số request, không lộ key
fn 0 98 | run | 10 checkpoint × 100, backup từng block
st 1 111 | Đọc lại cache mỗi block | Chạy lại là tiếp tục
st 1 121 | Backup | Ảnh chụp byte trước block
st 1 133 | Vòng lô | Giới hạn 50 request/block, nhịp 5s
st 1 144 | Ghi an toàn | Kiểm ID, kiểm cache không đổi, mới append
st 1 153 | 429 | Backoff 30/60/120, quá 3 lần dừng
st 1 161 | 408/5xx | Cùng backoff, thông điệp riêng
st 1 171 | Chia đôi lô lỗi | Cô lập review hỏng
st 1 176 | Checkpoint | total, in_block, old_unchanged, backup_ok
fn 0 198 | main | --segment 1..4, --dry-run, ba key riêng
chips 1 | llm:195 build_prompt ; llm:247 call_gemini_batch ; llm:158 load_cache ; llm_segments:171 run_cohorts ; kpi:811 compute_extended_llm_kpis

--- review
mid | Thử lại lồng nhau tới 9 request/lô | <code>llm.call_gemini_batch</code> đã thử 3 lần, vòng ngoài ở <a href="#label_additional-L153">dòng 153–168</a> thử thêm 3 lần, nên một lô 10 review có thể gọi API tới 9 lần trước khi bỏ. Với 429 là chủ ý (chờ quota), nhưng chi phí thực tế cao hơn con số "3 lần" trong docstring của <code>llm.py</code>.
mid | 10 block viết cứng | <code>range(10)</code> + <code>BLOCK_SIZE=100</code> giả định cohort đúng 1.000. <code>select_cohort</code> hiện bảo đảm điều đó, nhưng nếu cohort nhỏ hơn thì các block rỗng vẫn in <code>already_cached=100</code> (sai) và chỉ tới <a href="#label_additional-L194">dòng 194</a> mới báo lỗi.
low | <code>TEMP_DIR</code> gắn tên môi trường | <code>gettempdir()/"opencode"</code> là dấu vết của công cụ tạo script; chạy trên máy khác vẫn tạo được thư mục, nhưng tên không có nghĩa với người đọc code.
low | <code>prepare_cache</code> chỉ được gọi trong <code>main</code> | Gọi <code>run</code> trực tiếp khi cache chưa tồn tại sẽ <code>FileNotFoundError</code> ở <code>CACHE.read_bytes()</code> (<a href="#label_additional-L119">dòng 119</a>). Test chỉ gọi <code>prepare_cache</code>/<code>select_cohort</code>, không gọi <code>run</code>.
low | Cohort phụ thuộc thứ tự file | <code>select_cohort</code> cắt đoạn tuần tự, không ngẫu nhiên và không theo seed; đổi thứ tự <code>reviews.csv</code> là đổi cohort. Rủi ro được chặn gián tiếp bằng <code>cohort_sha256</code> trong metadata.
ok | Manifest khớp dữ liệu đã commit | Tính lại <code>manifest</code> cho cả 4 cohort: <code>prompt_sha256</code> và <code>cohort_sha256</code> khớp đúng 4 file metadata, các cohort rời nhau và không giao mẫu chính thức (tổng 5.000).

--- qa
? Script này có nằm trong pipeline không?
<p>Không. <code>run_pipeline.py</code> không gọi nó. Nó là script chạy tay để tạo dữ liệu mở rộng; kết quả được commit thành 4 cache và 4 metadata, rồi <a href="#llm_segments-L171">llm_segments.run_cohorts</a> đọc lại. Pipeline chính chỉ dùng cache chính thức 1.000 review.</p>
? Vì sao cần metadata riêng cho từng cohort?
<p>Vì bốn cohort có thể dùng model khác nhau và phải cùng một prompt. Metadata ghi <code>model</code>, <code>aspects</code>, <code>schema_version</code>, <code>prompt_sha256</code>, <code>cohort_sha256</code>. Không có nó thì không biết một file cache 1.000 dòng thuộc lần chạy nào, và bảng gộp 5.000 sẽ trộn dữ liệu không so sánh được.</p>
? <code>cohort_sha256</code> băm cái gì?
<p>Băm <code>json.dumps(cohort["id"].tolist())</code>, tức danh sách ID theo thứ tự, không băm nội dung review. Vì vậy nó phát hiện đổi danh sách hoặc đổi thứ tự, không phát hiện review bị sửa nội dung. <a href="#llm_segments-L237">llm_segments</a> tính lại đúng công thức này để đối chiếu.</p>
? Vì sao phải backup từng block 100?
<p>Vì cache là file nối thêm: một block có thể ghi 30 nhãn rồi chết ở lô sau. Backup cho phép quay lại trạng thái trước block nếu phát hiện cache bị trộn hoặc ghi sai. Checkpoint in <code>backup_ok</code> để biết bản backup còn đúng.</p>
? Một lô lỗi thì xử lý thế nào?
<p>Ba mức: <code>call_gemini_batch</code> thử 3 lần; nếu vẫn lỗi và là 429/5xx thì vòng ngoài backoff 30/60/120 rồi thử lại; nếu lô nhiều review vẫn hỏng thì <a href="#label_additional-L171">chia đôi</a> để cô lập review xấu. Chỉ khi còn đúng 1 review mà vẫn hỏng mới dừng.</p>
? Vì sao cohort 3 và 4 dùng key khác?
<p>Để không đụng quota. <code>main</code> chọn <code>2nd_GEMINI</code> cho cohort 3 và <code>3rd_GEMINI</code> cho cohort 4 (<a href="#label_additional-L242">dòng 242</a>). Cùng lý do script chạy từng cohort một thay vì song song.</p>
? Kết quả mở rộng cho ra số gì?
<p>Bốn cohort 1.000 review có số review bị phàn nàn lần lượt 101, 138, 155, 173 (từ 10,1% đến 17,3%); gộp 4.000 là 567/4.000 = 14,175%, khía cạnh bị chê nhiều nhất <code>amenities</code> 382/795 = 48,05%. Gộp với mẫu chính thức: 707/5.000 = 14,14% và 470/971 = 48,40%. Khớp <code>kpi_metrics.csv</code> scope <code>llm_additional_4000</code>/<code>llm_combined_5000</code>.</p>
