--- meta
title: llm.py
lead: Bước 4 của pipeline: gửi review cho Gemini để gán <code>sentiment</code> và hai danh sách khía cạnh khen/chê, rồi lưu mọi nhãn vào một cache JSONL. Thiếu cache là không có nhãn, và module không sinh dữ liệu giả khi thiếu API key. Cache chính thức đã commit có 1.000 review, 140 review bị tính là có phàn nàn (14,0%), khía cạnh bị chê nhiều nhất là <code>amenities</code> (88/176 lượt = 50,0%).

--- blocks
=== 1-17
<p>Docstring đặt module vào đúng chỗ: chạy sau khi chia nhóm (bước 3) và trước khi so sánh theo nhóm (4b), đánh giá (4c) và KPI (bước 5). KPI phải sau vì <code>kpi.py</code> đọc chính file cache do module này ghi (<a href="#kpi-L747">kpi.py dòng 747</a>), không tự gọi LLM.</p>
<p>Docstring cũng liệt kê đầu vào, đầu ra và lý do có cache. Đầu vào gồm <code>config["llm"]</code> (model, sample_size, aspects, cache, request_interval_seconds), <code>config["seed"]</code>, <code>reviews.csv</code> của mốc cuối, <code>data/samples/review_ids.csv</code> (cột <code>mau_llm = "x"</code>) và biến môi trường <code>GEMINI_API_KEY</code>. Đầu ra là cache JSONL, mỗi dòng một nhãn; module không ghi bảng CSV nào, bảng theo nhóm là việc của <a href="#f-llm_segments">llm_segments.py</a>. Có cache để chạy lại không tốn tiền gọi API và kết quả tái lập được trên máy khác, nhờ vậy repo có nhãn LLM dù không ai giữ key.</p>

=== 19
<p><code># ruff: noqa: E501</code> tắt luật "dòng quá 80 ký tự" cho cả file. Cần vì prompt và luật khía cạnh là văn bản dài, ngắt dòng sẽ khó đọc và dễ đổi nghĩa.</p>

=== 21-27
<p>Sáu import chuẩn: <code>argparse</code> cho CLI, <code>json</code> cho cache JSONL, <code>os</code> đọc biến môi trường, <code>sys</code> để ép encoding stdout, <code>time</code> để nghỉ giữa các lô, <code>Path</code> cho đường dẫn. <code>Any</code>/<code>Literal</code> dùng ở chú thích kiểu và lớp pydantic.</p>

=== 29-34
<p>Ba thư viện ngoài: <code>pandas</code> đọc <code>reviews.csv</code>, lọc rồi trả DataFrame; <code>dotenv.load_dotenv</code> nạp <code>.env</code> để lấy key nhưng chỉ gọi trong <a href="#llm-L353">run</a>, không gọi lúc import; <code>pydantic</code> kiểm cấu trúc JSON Gemini trả về. Hai module nội bộ: <code>load_config</code> chỉ dùng cho <code>main()</code>, <code>load_sample_ids</code> lấy mẫu review của nhóm và đọc đúng một nguồn với <a href="#download-L325">download.py</a>.</p>

=== 36-37
<p>Trên Windows, console mặc định là cp1252 nên in tiếng Việt và emoji sẽ ném <code>UnicodeEncodeError</code>. Đổi stdout sang UTF-8 và <code>errors="replace"</code> để ký tự lạ thành dấu hỏi thay vì làm sập pipeline. <code>hasattr</code> để chạy được cả khi stdout bị thay bằng đối tượng khác (pytest, Jupyter).</p>

=== 39-40
<p>Sáu khía cạnh được phép gán, trùng khít <code>config["llm"]["aspects"]</code> trong <code>configs/sydney.yaml</code>. Danh sách này đóng: nhãn ngoài sáu tên bị <a href="#llm-L142">validate_aspect_lists</a> từ chối. Pydantic cũng ép bằng <code>Literal</code> ở <a href="#llm-L64">dòng 64</a>.</p>

=== 41-49
<p><code>ASPECT_RULES</code> định nghĩa phạm vi từng khía cạnh, chèn vào prompt ở <a href="#llm-L203">dòng 203–204</a>. Sáu mục này quyết định nhãn nên đọc kỹ:</p>
<ul><li><code>location</code>: khoảng cách, đi lại, khu phố; không tính view từ căn hộ.</li>
<li><code>cleanliness</code>: sạch/bẩn, mùi, côn trùng; "cũ/dated" chỉ vào đây khi khách nói nó gây bẩn, còn không thì là <code>amenities</code>.</li>
<li><code>host</code>: liên lạc, đón tiếp, giúp đỡ; tính cả khi gọi tên hay dùng đại từ ("she met us").</li>
<li><code>value</code>: đáng tiền/đắt/rẻ; không suy từ lời khen chung.</li>
<li><code>amenities</code>: trang bị cụ thể và "had everything we needed"; không tính "spacious/beautiful/as described".</li>
<li><code>noise</code>: nguồn ồn và yên tĩnh; nêu nguồn ồn rồi kết luận "không làm phiền" vẫn là khen noise.</li></ul>

=== 50-58
<p><code>ASPECT_HINTS</code> là phần phân xử ca khó, chèn ở <a href="#llm-L218">dòng 218–219</a>. Nó dài hơn RULES vì mỗi mục giải quyết một lỗi cụ thể từng gặp khi rà prompt. Ví dụ: chỉ nhắc tên chủ ("stayed with Tom and Elaine") không tính host; "peaceful/relaxing/tranquil" không đủ để gán noise; giường/nệm thoải mái thuộc <code>amenities</code> chứ không phải <code>noise</code>.</p>
<p>Test <code>test_build_prompt_follows_labeling_rules_without_gold_answers</code> kiểm đúng các câu này có mặt trong prompt.</p>

=== 59-62
<p>Hai hằng số. <code>CACHE_PATH</code> là đường dẫn mặc định khi config không ghi <code>llm.cache</code>. <code>CACHE_SCHEMA_VERSION = 3</code> phải đổi khi cấu trúc bản ghi đổi; cache cũ bị từ chối (<a href="#llm-L175">dòng 175–180</a>) thay vì trộn nhãn hai schema, nếu không KPI sẽ đếm lẫn hai định nghĩa.</p>

=== 64
<p><code>Aspect</code> là alias <code>Literal[...]</code> dùng trong pydantic. Nhờ nó, Gemini trả <code>"safety"</code> hay <code>"parking"</code> sẽ làm <code>ValidationError</code> ngay ở <a href="#llm-L275">dòng 275</a>, trước khi ta kịp ghi cache.</p>

=== 67-68
<p><code>ReviewInfo</code> mô tả một nhãn. Docstring nhấn "hai danh sách khía cạnh độc lập", nghĩa là một review vừa khen vừa chê cùng một khía cạnh vẫn giữ được cả hai phía.</p>

=== 70-74
<p>Năm trường, đều bắt buộc: <code>review_id</code> (chuỗi), <code>sentiment</code> đúng ba giá trị, hai list aspect, <code>language</code>. Không có trường nào mặc định, thiếu là lỗi, xem <code>test_call_gemini_batch_requires_schema_fields</code>.</p>

=== 77-78
<p><code>ReviewBatch</code> bọc list lại để JSON trả về có dạng <code>{"reviews": [...]}</code>. Cần lớp bọc vì mỗi lần gọi là nhiều review; nếu để list trần thì không phân biệt được "model trả rỗng" với "model trả sai".</p>

=== 80
<p>Một trường duy nhất. Pydantic sẽ từ chối object thiếu khoá <code>reviews</code>.</p>

=== 83-89
<p>Đọc <code>reviews.csv</code> với <code>dtype=str</code> để <code>review_id</code> dài 18 chữ số không bị làm tròn khi đọc dạng số (xem <a href="#f-download">download.py</a>).</p>
<p>Chấp nhận cả cột <code>id</code> và <code>review_id</code> rồi đổi về <code>id</code>: file do <code>download.py</code> ghi dùng <code>id</code>, còn file mẫu của đề dùng <code>review_id</code>.</p>
<p>Bỏ review rỗng (<code>dropna</code>) và review dưới 15 ký tự. Trên dữ liệu thật mốc 2026-06-16 (<code>data/processed/sydney/2026-06-16/reviews.csv</code>, 5.000 dòng) không dòng nào bị loại: 0 comment rỗng, 0 comment dưới 15 ký tự. Ngưỡng này để phòng, không phải để lọc thật.</p>

=== 92-98
<p>Docstring nói rõ hai đường lấy mẫu: ưu tiên đúng 1.000 review đề đánh dấu <code>mau_llm == "x"</code>; không có cột đó thì lấy ngẫu nhiên theo <code>seed</code>. Đường thứ hai dành cho "đổi thành phố chỉ sửa yaml".</p>

=== 99-103
<p>Bốn giá trị mặc định: 1.000 review, seed 42, city <code>sydney</code>, và mốc cuối <code>snapshots[-1]</code>. Luôn đọc <code>reviews.csv</code> của mốc cuối vì review là dữ liệu tích luỹ. Đường dẫn ghép thủ công <code>data/processed/&lt;city&gt;/&lt;mốc&gt;/reviews.csv</code>.</p>

=== 105-106
<p>Không có file thì <code>FileNotFoundError</code> kèm đường dẫn. Test <code>test_load_sample_reviews_never_uses_other_city</code> khẳng định hàm không lặng lẽ đọc thư mục khác.</p>

=== 108
<p>Đọc và lọc bằng <a href="#llm-L83">_read_usable_reviews</a>.</p>

=== 110-116
<p><code>load_sample_ids(config)</code> trả <code>(listing_ids, review_ids)</code>; lỗi <code>FileNotFoundError</code> bị nuốt để rơi xuống nhánh lấy mẫu ngẫu nhiên.</p>
<p>Điều kiện thứ hai <code>"mau_llm" in ids_df.columns</code> mới là cổng chính: file mẫu có nhưng thiếu cột đánh dấu thì vẫn lấy ngẫu nhiên. Khi có cột, <code>target_ids</code> là tập ID có <code>"x"</code> (đúng 1.000 dòng trên dữ liệu thật).</p>

=== 117-119
<p>Comment WHY giải thích vì sao phải gộp thêm các mốc trước. 1.000 review của mẫu là hợp qua 4 mốc; review bị chủ nhà/Airbnb gỡ sẽ vắng ở mốc cuối. Comment nêu ví dụ mốc 2026-09-16 chỉ còn 971/1.000, mốc đó không có trong config hiện tại nên đây là phòng cho lần chạy sau.</p>

=== 120-126
<p>Thứ tự ghép quyết định kết quả: <code>df</code> (mốc cuối) đứng đầu, rồi các mốc trước theo thứ tự ngược thời gian; <code>drop_duplicates(keep="first")</code> nên bản của mốc cuối thắng. Test <code>test_load_sample_reviews_finds_mau_llm_reviews_missing_from_last_snapshot</code> kiểm đúng thứ tự <code>["3","2","1"]</code> và nội dung của review "2" lấy từ mốc cuối.</p>
<p>Thiếu quá nhiều thì <code>ValueError</code>: thà dừng còn hơn chấm KPI trên mẫu thiếu. <code>head(target_n)</code> cắt theo thứ tự file, với mẫu đúng 1.000 dòng thì không cắt gì.</p>

=== 128
<p>Nhánh dự phòng: lấy ngẫu nhiên <code>min(target_n, len(df))</code> dòng với <code>random_state=seed</code>. Cùng seed và cùng file thì cùng mẫu, nên kết quả tái lập được. Đường này dùng khi đổi sang thành phố không có file ID của nhóm.</p>

=== 131-136
<p><code>missing_from_cache</code> trả về số review của mẫu chưa có trong cache. Docstring nói mục đích thật: phân biệt "cache của thành phố khác còn sót" với "cache đúng của nhóm". <a href="#run_pipeline-L96">run_pipeline dòng 96</a> dùng nó để quyết định có bỏ qua bước LLM hay không.</p>

=== 137-139
<p>Đọc cache không truyền <code>aspects</code> (xem <a href="#llm-L158">load_cache</a>), nên bước kiểm schema bị bỏ qua. Điểm lệch đã kiểm chứng: cache schema cũ vẫn được tính là "đã có", hàm trả 0, rồi <code>run</code> mới ném <code>ValueError</code> "schema/aspect cũ", nên pipeline dừng thay vì bỏ qua bước LLM. Xem mục review.</p>

=== 142-146
<p>Docstring nêu hai luật: đúng kiểu list, chỉ chứa tên hợp lệ, không lặp; và một aspect được phép nằm ở cả hai phía. Luật cuối là chủ ý: "phòng đẹp nhưng bếp bẩn" vừa khen vừa chê amenities.</p>

=== 147-155
<p>Duyệt hai khoá <code>"positive_aspects"</code> và <code>"negative_aspects"</code> (đúng tên trong cache, khác tên trường pydantic <code>aspects_positive</code>/<code>aspects_negative</code>). Điều kiện <code>not isinstance(values, list)</code> bắt cả trường hợp model trả chuỗi thay vì list. <code>len(values) != len(set(values))</code> phát hiện trùng. Test tham số hoá <code>test_call_gemini_batch_rejects_bad_aspect_lists</code> phủ 4 kiểu sai: trùng tên, tên lạ, chuỗi thay list, và cùng aspect ở hai phía nhưng sentiment positive.</p>

=== 158-163
<p><code>load_cache</code> là cửa đọc cache duy nhất, trả <code>(dict, set)</code>. Docstring nêu hai điểm: khi truyền <code>aspects</code> thì kiểm schema và bộ khía cạnh; dòng trùng <code>review_id</code> thì dòng sau thắng (khác <a href="#llm_segments-L95">llm_segments.read_cache</a> coi trùng là lỗi).</p>

=== 164-166
<p>Chưa có file thì trả cache rỗng, chuyện bình thường ở lần chạy đầu chứ không phải lỗi.</p>

=== 167-172
<p>Đọc từng dòng, bỏ dòng trắng, <code>json.loads</code>. Cache JSONL chọn vì ghi nối thêm một dòng là xong, không phải đọc/ghi lại cả file như CSV.</p>

=== 173-174
<p>Lấy ID theo thứ tự ưu tiên <code>review_id</code> rồi <code>id</code> (cache cũ dùng <code>id</code>). Dòng không có ID nào bị bỏ im lặng; test <code>test_cache_operations</code> ghi một dòng <code>{"invalid":123}</code> và mong nó không xuất hiện.</p>

=== 175-181
<p>Chỉ khi <code>aspects</code> được truyền: so <code>schema_version</code> và <code>aspect_vocabulary</code> với hiện tại. Lệch một trong hai là <code>ValueError</code> kèm gợi ý chạy <code>--force</code>, để không trộn nhãn sinh theo định nghĩa khía cạnh cũ vào KPI mới.</p>
<p>Gọi <code>validate_aspect_lists(item, aspects)</code> ở đây là kiểm lại cả cache đã qua ghi, phòng file bị sửa tay.</p>

=== 182-183
<p>Gán vào dict (dòng sau đè dòng trước) rồi trả cả dict lẫn tập ID. Trả hai dạng vì nơi gọi cần hai kiểu tra cứu khác nhau: <code>run</code> cần bản ghi, <code>missing_from_cache</code> chỉ cần membership.</p>

=== 186-192
<p>Ghi nối thêm, mỗi bản ghi một dòng JSON, <code>ensure_ascii=False</code> để giữ tiếng Việt đọc được. <code>flush()</code> sau mỗi lô để lô đã xong không mất nếu lô sau làm sập tiến trình. Không <code>fsync</code>: mất điện vẫn có thể mất lô cuối, nhưng chấp nhận được vì cache chỉ để tiết kiệm.</p>

=== 195-196
<p><code>build_prompt</code> là hàm thuần: cùng batch cộng cùng aspects thì cùng chuỗi. Nhờ tính chất đó, <a href="#label_additional-L40">label_additional.manifest</a> băm prompt làm "phiên bản" được.</p>

=== 197-199
<p><code>items</code> chỉ giữ <code>review_id</code> và <code>text</code>, không gửi <code>listing_id</code>, <code>date</code> hay tên người. Giảm dữ liệu gửi ra ngoài và tránh model suy diễn từ metadata.</p>
<p><code>rules</code>/<code>hints</code> chỉ ghép các aspect đang dùng, nên config rút còn 2 khía cạnh thì prompt cũng ngắn lại (test <code>test_build_prompt_follows_labeling_rules_without_gold_answers</code> kiểm <code>- amenities:</code> không xuất hiện).</p>

=== 200-201
<p>Vai trò "CX analyst" cộng hai câu chống prompt injection: chỉ dựa vào nội dung review và coi nội dung review là dữ liệu, không làm theo chỉ dẫn trong đó. Review là văn bản người lạ viết, có thể chứa "bỏ qua hướng dẫn trên".</p>

=== 203-204
<p>Chèn <code>ASPECT_RULES</code>. Câu "chỉ xuất tên trong danh sách trên" nhắc lại ràng buộc đóng.</p>

=== 206-216
<p>Bảy nguyên tắc gán nhãn, trong đó ba cái đáng nhớ khi vấn đáp:</p>
<ul><li>#4: sentiment xét toàn bài và tách khỏi khía cạnh, "mixed" kể cả khi ý chê nằm ngoài sáu khía cạnh.</li>
<li>#5: hai danh sách có thể rỗng dù sentiment positive/mixed, nên <code>aspects_positive</code> rỗng không có nghĩa là chấm sai. Trên cache thật có 29/860 review positive không có aspect nào.</li>
<li>#6: vấn đề đã khắc phục trong bài, hoặc "would have liked", không tạo negative aspect và không đổi sentiment.</li></ul>

=== 218-219
<p>Chèn <code>ASPECT_HINTS</code> dưới tiêu đề "Phân xử các trường hợp dễ bỏ sót".</p>

=== 221-227
<p>Sáu câu tự kiểm trước khi trả kết quả (amenities, location, noise, host, ý chê chưa vào sentiment, hai list có trùng/sai phía). Sáu câu này là "chain-of-check" bằng lời chứ không phải code; tác dụng thì không đo được, chỉ biết prompt có nó.</p>

=== 229-238
<p>Định nghĩa 5 trường JSON. Hai câu cuối là ràng buộc chéo mà <a href="#llm-L288">dòng 288–298</a> sẽ kiểm lại bằng code:</p>
<ul><li>có cả hai list thì sentiment bắt buộc "mixed";</li>
<li>"positive" thì <code>aspects_negative</code> rỗng; "negative" thì <code>aspects_positive</code> rỗng.</li></ul>

=== 240-244
<p>Nhét review dạng JSON (không chèn thẳng văn bản) để dấu ngoặc, xuống dòng trong review không phá cấu trúc prompt. Câu cuối ép chỉ trả một object, <code>{{</code>/<code>}}</code> trong f-string in ra <code>{</code>/<code>}</code>.</p>

=== 247-258
<p>Docstring mô tả chính sách thử lại, đọc kỹ vì đây là chỗ dễ bị hỏi:</p>
<ul><li>tối đa 3 lần, chờ 15s rồi 30s;</li>
<li>lỗi dữ liệu (schema, ID, nhãn mâu thuẫn) và lỗi mạng/quota đều thử lại;</li>
<li>4xx (trừ 429) là lỗi request, dừng ngay không chờ;</li>
<li>thất bại cả 3 lần thì trả <code>[]</code>, lô đó chưa vào cache nên lần sau chạy lại.</li></ul>

=== 259-260
<p>Dựng prompt một lần cho cả lô. <code>lookup</code> ánh xạ ID đã <code>strip()</code> về bản ghi gốc, để lấy <code>listing_id</code>/<code>date</code> khi ghi cache; LLM không trả hai trường đó.</p>

=== 262-263
<p><code>for attempt in range(3)</code> là vòng thử lại. Mọi thứ trong <code>try</code> phải thành công toàn bộ lô mới <code>return</code>: một review sai là cả lô bị thử lại, vì ghi nửa lô sẽ làm mẫu số KPI lệch.</p>

=== 264-273
<p>Gọi Gemini qua <code>client.interactions.create</code> với <code>response_format</code> kiểu JSON và <code>schema=ReviewBatch.model_json_schema()</code>, model bị ép trả đúng cấu trúc. <code>store=False</code> để không lưu hội thoại phía Google.</p>

=== 274-275
<p><code>strict=True</code> là chi tiết đáng nhớ: pydantic không tự ép kiểu, nên <code>review_id: 123</code> (số) bị từ chối thay vì thành <code>"123"</code>. Tránh âm thầm đổi ID.</p>

=== 277-280
<p>Ba kiểm tra gói trong một dòng: không trùng, không thiếu, không thừa ID so với batch. Comment nói lý do: mẫu số KPI phải đúng tập review đã gửi. Test <code>test_call_gemini_batch_never_invents_positive_or_accepts_wrong_ids</code> phủ ID ngoài batch, list rỗng, ID trùng.</p>

=== 281-287
<p>Với từng review: lấy bản ghi gốc, rồi kiểm hai list aspect. Ở đây phải đổi tên <code>aspects_positive</code> thành <code>positive_aspects</code> vì <a href="#llm-L142">validate_aspect_lists</a> đọc tên của cache, không phải tên trường pydantic.</p>

=== 288-298
<p>Ba ràng buộc sentiment và aspect, đúng như prompt dặn:</p>
<ol><li>có cả khen và chê thì phải "mixed";</li>
<li>có chê thì không được "positive";</li>
<li>có khen thì không được "negative".</li></ol>
<p>Cuối cùng đòi <code>language</code> không rỗng. Mọi vi phạm ném <code>ValueError</code> và cả lô thử lại. Ba ràng buộc này thay cho việc tin model.</p>

=== 300-315
<p>Bản ghi cache có 11 trường. Hai trường không đến từ LLM: <code>listing_id</code> và <code>date</code> lấy từ <code>lookup</code> (chuỗi rỗng nếu thiếu).</p>
<p><code>complaint_aspects</code> là chuỗi nối bằng <code>"; "</code>, dạng KPI đọc được (<a href="#kpi-L753">kpi.py dòng 753</a> tách lại).</p>
<p><code>has_complaint</code> bằng sentiment negative/mixed hoặc có ít nhất một aspect bị chê. Vì sentiment đã bắt buộc "mixed" khi có chê, vế <code>bool(neg_asp)</code> gần như dư, nhưng giữ để phòng cache cũ/thiếu.</p>

=== 316-317
<p><code>if results: return results</code>. <code>results</code> luôn đầy khi items không rỗng, nên nhánh <code>if</code> chỉ để an toàn kiểu.</p>

=== 318-324
<p>Nhánh lỗi dữ liệu: chờ <code>15 * (attempt + 1)</code> giây (15, 30, rồi không chờ), in cảnh báo. Hết 3 lần thì in rồi rơi xuống <code>return []</code> ở <a href="#llm-L335">dòng 335</a>.</p>

=== 325-328
<p>Nhánh lỗi khác: đọc thuộc tính <code>code</code> của exception. Nếu là 4xx và không phải 429 thì <code>RuntimeError</code> ngay, vì request sai thì thử lại cũng sai, chỉ tốn tiền. Test <code>test_call_gemini_batch_does_not_retry_bad_request</code> khẳng định chỉ gọi API 1 lần và không <code>sleep</code>.</p>

=== 329-335
<p>Lỗi tạm thời (429, 5xx, timeout, mất mạng) thì chờ 15/30s và thử lại; hết lượt thì trả <code>[]</code>. Lô đó không vào cache nên <a href="#llm-L408">kiểm tra cuối</a> sẽ chặn KPI.</p>

=== 338-351
<p><code>run</code> là hàm <code>run_pipeline.py</code> gọi (<a href="#run_pipeline-L101">dòng 101</a>). Docstring chốt nguyên tắc: trả DataFrame nhãn của đúng các review trong mẫu; cache đủ thì không gọi API; thiếu key mà cache chưa đủ thì báo lỗi chứ không sinh nhãn giả; <code>dry_run</code> chỉ in prompt; <code>force</code> xoá cache để chạy lại.</p>

=== 352-358
<p>Năm giá trị đọc từ config, đều có mặc định: cache, aspects, model, <code>request_interval_seconds</code> = 4,2s. <code>load_dotenv()</code> nạp <code>.env</code>; <code>api_key</code> có thể <code>None</code>.</p>

=== 360-364
<p>Lấy mẫu trước khi xoá cache, để nếu lấy mẫu lỗi thì cache cũ còn nguyên.</p>
<p><code>--force</code> đi kèm <code>skip_llm</code>/<code>dry_run</code>/thiếu key thì <code>ValueError</code> ngay: xoá cache mà không gọi được API là tự phá dữ liệu. Test <code>test_force_without_api_key_preserves_cache</code> kiểm file vẫn nguyên.</p>

=== 366-371
<p>Đọc cache (có kiểm schema), tính phần thiếu, in 3 số: tổng mẫu, đã có, cần phân tích. Trên repo này: 1.000 / 1.000 / 0.</p>

=== 373-375
<p>Cache đủ thì trả luôn DataFrame theo thứ tự mẫu (<code>df_samples["id"]</code>), không theo thứ tự file cache. Nhờ vậy kết quả ổn định giữa các lần chạy.</p>

=== 377-380
<p><code>dry_run</code> in 600 ký tự đầu của prompt lô đầu rồi trả DataFrame rỗng. Dùng để kiểm prompt mà không tốn request. Test <code>test_run_dry_run</code>.</p>

=== 382-388
<p>Chốt an toàn cuối file: không có key hoặc dùng <code>--skip-llm</code> mà vẫn thiếu nhãn thì <code>RuntimeError</code>. Comment nói thẳng "không sinh dữ liệu giả"; nếu ở đây điền nhãn positive cho đủ thì mọi KPI phàn nàn thành 0 và bài mất nghĩa. Test <code>test_run_skip_llm</code>, <code>test_run_missing_key_never_creates_mock</code>.</p>

=== 390-391
<p>Import trễ <code>google.genai</code>: chỉ cần thư viện khi thật sự gọi API. Nhờ vậy chạy cache/test/CI không phải cài SDK Google.</p>

=== 393-395
<p><code>total_batches</code> chia làm tròn lên: <code>(n + b - 1) // b</code>. <code>with genai.Client(...) as client</code> để đóng kết nối kể cả khi lỗi giữa chừng.</p>

=== 396-399
<p>Duyệt theo lô 10 review (mặc định). Chỉ số lô <code>idx // batch_size + 1</code> để in "Lô k/n".</p>

=== 400-402
<p>Gọi <a href="#llm-L247">call_gemini_batch</a>; chỉ ghi cache khi có kết quả. Lô trả <code>[]</code> bị bỏ qua, cuối hàm sẽ báo thiếu.</p>

=== 403-405
<p>Nghỉ 4,2s giữa các lô để không vượt hạn mức request/phút. Điều kiện <code>idx + batch_size &lt; len(items)</code> để không nghỉ sau lô cuối.</p>

=== 407-414
<p>Đọc lại cache từ đĩa (nguồn sự thật, không tin biến trong RAM), tính phần còn thiếu. Còn thiếu là <code>RuntimeError</code> kèm số lượng; các lô đã xong vẫn nằm trong cache nên chạy lại là tiếp tục, không làm lại từ đầu. Test <code>test_run_refuses_partial_llm_results</code>.</p>

=== 417-418
<p><code>main</code> cho phép chạy riêng bước này: <code>python -m src.llm --config configs/sydney.yaml</code>.</p>

=== 419-426
<p>Sáu tham số CLI, trùng tên với tham số <code>run</code>: <code>--config</code>, <code>--sample-size</code>, <code>--batch-size</code>, <code>--skip-llm</code>, <code>--force</code>, <code>--dry-run</code>. Mặc định config là <code>configs/sydney.yaml</code>.</p>

=== 428-436
<p>Đọc config qua <code>load_config</code> (đã kiểm khoá và chuẩn hoá ngày) rồi gọi <code>run</code>. Không tự mở yaml, giữ nguyên tắc một cửa vào cấu hình của <a href="#f-config">config.py</a>.</p>

=== 439-440
<p>Chỉ chạy <code>main</code> khi gọi trực tiếp; import từ module khác thì không kích hoạt CLI.</p>

--- flow
## Đọc mẫu
fn 0 92 | load_sample_reviews | Lấy đúng 1.000 review mau_llm, thiếu thì lấy ngẫu nhiên theo seed
st 1 99 | Tham số | sample_size, seed, city, mốc cuối
st 1 108 | Lọc review dùng được | dtype=str, bỏ rỗng và &lt; 15 ký tự
st 1 120 | Gộp các mốc trước | Mốc cuối đứng đầu, trùng thì mốc cuối thắng
fn 0 83 | _read_usable_reviews | Đọc reviews.csv, đổi id/review_id về id
## Cache
fn 0 158 | load_cache | Đọc JSONL, kiểm schema/aspect, dòng sau thắng
fn 0 186 | append_to_cache | Ghi nối thêm, flush từng lô
fn 0 131 | missing_from_cache | Đếm review của mẫu chưa có nhãn
## Gọi Gemini
fn 0 195 | build_prompt | Ghép prompt: vai trò, luật, 7 nguyên tắc, mẫu JSON
fn 0 247 | call_gemini_batch | Gọi 1 lô, kiểm schema/ID/nhãn, thử 3 lần
st 1 264 | Gọi API | response_format JSON + schema pydantic
st 1 277 | Kiểm ID | Thiếu/trùng/thừa là bỏ cả lô
st 1 288 | Kiểm sentiment | Ba ràng buộc chéo với hai list
st 1 318 | Lỗi và thử lại | 15s, 30s; 4xx (trừ 429) dừng ngay
fn 0 142 | validate_aspect_lists | Đúng list, tên hợp lệ, không lặp
## Điều phối
fn 0 338 | run | Mẫu → cache → gọi thiếu → kiểm đủ
st 1 360 | Lấy mẫu, xử lý --force | Không xoá cache khi không gọi được API
st 1 373 | Cache đủ | Trả DataFrame theo thứ tự mẫu, không gọi API
st 1 382 | Thiếu key/cache | Báo lỗi, không sinh nhãn giả
st 1 396 | Chạy theo lô | 10 review/lô, nghỉ 4,2s
st 1 407 | Kiểm đủ cuối | Còn thiếu thì RuntimeError, cache giữ phần xong
fn 0 417 | main | CLI: --config, --force, --dry-run
chips 1 | run_pipeline:91 run_llm_stage ; kpi:747 complaint_bearing_review_rate ; llm_segments:31 summarize ; download:325 load_sample_ids

--- review
mid | missing_from_cache bỏ qua kiểm schema | Gọi <code>load_cache(cache_path)</code> không truyền <code>aspects</code> nên cache schema cũ vẫn được tính "đã có": <code>missing_from_cache</code> trả 0, <a href="#run_pipeline-L96">run_llm_stage</a> thấy thiếu 0 nên gọi <code>llm.run</code>, và <code>run</code> ném <code>ValueError</code> "schema/aspect cũ". Đã tái hiện bằng cache 1 dòng <code>{"review_id":"1001","aspects":{...}}</code>: missing = 0 rồi run raise. Hệ quả: pipeline dừng thay vì bỏ qua bước LLM.
mid | <code>language</code> chưa được kiểm thật | Cả 1.000 bản ghi cache đều <code>language="en"</code> (dữ liệu Sydney toàn review tiếng Anh), nên trường này và bước đòi <code>language</code> không rỗng chưa từng chạy trên ngôn ngữ khác. <code>language_accuracy = 1,0</code> trong <code>reports/eval_summary.csv</code> không chứng minh model nhận ngôn ngữ tốt.
low | <code>head(target_n)</code> phụ thuộc thứ tự file | Nếu <code>review_ids.csv</code> có hơn 1.000 dòng <code>mau_llm="x"</code>, mẫu là 1.000 dòng đầu theo thứ tự file, không theo seed và không ngẫu nhiên. Hiện dữ liệu có đúng 1.000 nên không ảnh hưởng.
low | <code>_read_usable_reviews</code> giả định có cột ID | Nếu <code>reviews.csv</code> không có cả <code>id</code> lẫn <code>review_id</code>, <code>rename</code> ném <code>KeyError</code> khó đọc thay vì thông báo rõ. File do <code>download.py</code> ghi luôn có <code>id</code>.
ok | Không sinh nhãn giả | Thiếu key/cache là <code>RuntimeError</code>; 4xx không thử lại; cache chỉ được ghi sau khi qua kiểm ID, schema và ba ràng buộc sentiment. Đúng tinh thần "không bịa số".

--- qa
? Vì sao phải có cache thay vì gọi API mỗi lần chạy?
<p>Vì API tốn tiền, chậm và không tất định. Cache JSONL cho phép chạy lại pipeline, CI và máy khác mà không gọi mạng; nhãn đã commit là nguồn sự thật cho KPI. <a href="#llm-L366">run</a> chỉ gọi phần thiếu, và <a href="#llm-L407">kiểm tra cuối</a> chặn KPI nếu mẫu chưa đủ.</p>
? Nếu không có GEMINI_API_KEY thì sao?
<p>Nếu cache đã đủ 1.000 review: <a href="#llm-L373">dòng 373</a> trả kết quả từ cache, không cần key. Nếu cache chưa đủ: <a href="#llm-L382">dòng 382–388</a> ném <code>RuntimeError</code>, tuyệt đối không điền nhãn giả.</p>
? Vì sao một aspect được nằm ở cả hai danh sách?
<p>Vì hai danh sách độc lập: khách có thể khen bếp nhưng chê điều hoà, cả hai đều là <code>amenities</code>. Khi đó sentiment bắt buộc "mixed" (<a href="#llm-L288">dòng 288–298</a>). Trên cache thật có 118/1.000 review có cả hai phía và 40 review có cùng aspect ở cả hai.</p>
? Sentiment và khía cạnh khác nhau thế nào?
<p>Sentiment xét toàn bài (positive/negative/mixed); khía cạnh là chỗ cụ thể được khen/chê. Một bài "great place" là positive nhưng không sinh khía cạnh nào: 29/860 review positive trong cache không có aspect. Vì vậy <code>has_complaint</code> tính cả sentiment negative/mixed hoặc có aspect bị chê.</p>
? Con số 14,0% phàn nàn ở đâu ra?
<p>Từ cache <code>data/processed/llm_cache_pydantic.jsonl</code>: 140/1.000 bản ghi có <code>has_complaint=true</code>. Khía cạnh bị chê nhiều nhất là <code>amenities</code> 88/176 lượt = 50,0%; sau đó <code>noise</code> 33, <code>cleanliness</code> 27. Khớp <code>data/processed/kpi_metrics.csv</code> scope <code>llm</code>.</p>
? Vì sao 4xx thì không thử lại?
<p>4xx là request sai (schema sai, model không tồn tại), thử lại chỉ tốn tiền và thời gian. 429 là ngoại lệ vì là giới hạn tạm thời. Xem <a href="#llm-L325">dòng 325–328</a>; test <code>test_call_gemini_batch_does_not_retry_bad_request</code> kiểm chỉ gọi 1 lần.</p>
? Cache cũ khác schema thì chuyện gì xảy ra?
<p>Nếu đọc qua <a href="#llm-L158">load_cache</a> có truyền <code>aspects</code>: <code>ValueError</code> "schema/aspect cũ" và cache không bị sửa. Muốn chạy lại phải <code>--force</code> với key thật. Chú ý <code>missing_from_cache</code> không truyền <code>aspects</code> nên có thể báo "đủ" trước khi <code>run</code> báo lỗi (xem mục review).</p>
