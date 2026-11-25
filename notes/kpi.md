--- meta
title: kpi.py
lead: Bước 5 của pipeline, và 5b cho căn ảo. Có hai cửa vào. <code>run()</code> tính 5 KPI chung, thương mại theo <code>analysis_area</code> và availability theo khu, ghi <code>data/processed/kpi_metrics.csv</code> (158 dòng). <code>run_phantom()</code> tính KPI căn ảo, ghi <code>kpi_phantom.csv</code> (216 dòng). Mọi KPI trả <code>(giá trị, n_obs)</code>: giá trị là tỷ lệ 0–100 chứ không phải 0–1, còn <code>n_obs</code> là mẫu số thật của tỷ lệ đó. Giảng viên hay hỏi ba chỗ: lọc <code>qa_has_error_excl_price</code>, tách chế độ lưu trú khi so giá, và vì sao <code>n_obs</code> không phải lúc nào cũng là mẫu số.

--- blocks
=== 1-21
<p>Docstring nói file đứng ở đâu trong pipeline và mọi hàm KPI theo một hợp đồng chung.</p>
<p>Về vị trí: chạy sau QA, LLM và đánh giá, trước viz. Trong <code>run_pipeline.py</code>, <a href="#run_pipeline-L180">dòng 180</a> gọi <code>kpi.run(config, flagged)</code>; <a href="#run_pipeline-L184">dòng 184</a> gọi <code>kpi.run_phantom(config)</code> nhưng chỉ khi <code>seg["scope"] == "full"</code>.</p>
<p>Hợp đồng: mỗi KPI là một hàm nhỏ trả <code>(value, n_obs)</code>. <code>value</code> là phần trăm (nhân 100), <code>n_obs</code> là số dòng thực sự vào mẫu số. <code>add_kpi</code> ghi một dòng; <code>compute_regular_kpis</code>/<code>compute_phantom_kpis</code> chỉ gọi các hàm rồi ghi.</p>
<p>Đầu vào là bảng listings/calendar đã qua QA (hoặc đọc <code>data/processed/&lt;city&gt;/&lt;mốc&gt;/</code> khi gọi trực tiếp), cache LLM, và <code>config["kpi"]</code> (<code>area_col</code>, <code>min_area_listings</code>). Đầu ra là <code>kpi_metrics.csv</code> dạng dài, cột <code>OUTPUT_COLUMNS</code>.</p>
<p>Dòng 19–20 nói mẫu số chỉ gồm dòng có dữ liệu hợp lệ (không NaN), và <code>n_obs</code> cho người đọc biết tỷ lệ dựa trên bao nhiêu quan sát. Vì thế mỗi KPI trả hai giá trị chứ không trả một con số trần.</p>

=== 23-26
<p>Bốn import chuẩn: <code>json</code> để đọc chuỗi dạng JSON list trong <code>split_aspects</code>; <code>re</code> để tách aspect theo dấu phân cách; <code>Path</code> để ghép đường dẫn; <code>Any</code> cho dict config tự do. Ngoài pandas ở dòng 28 không có import nặng nào.</p>

=== 28
<p><code>pandas</code> là công cụ chính: đọc CSV/JSONL, <code>groupby</code>, <code>to_numeric</code>, <code>merge</code>, <code>drop_duplicates</code>.</p>

=== 30-32
<p>Ba import nội bộ:</p>
<ul><li><code>load_sample_ids</code> (từ <code>download.py</code>) đọc danh sách ID review của nhóm, dùng để lọc cache LLM (<code>_keep_group_reviews</code>).</li>
<li><code>parse_price</code> (từ <code>qa_rules.py</code>, <a href="#qa_rules-L103">dòng 103</a>) đổi chuỗi kiểu <code>"$1,200.00"</code> sang số. Thử nhanh: <code>"$1,200.00" → 1200.0</code>, chuỗi rỗng/None → <code>NaN</code>.</li>
<li><code>PHANTOM</code> (từ <code>segments/rules.py</code>, <a href="#seg_rules-L32">dòng 32</a>) là tuple <code>("B_ghost", "D_dormant", "D_never")</code>, ba nhóm bị coi là căn ảo.</li></ul>

=== 34-36
<p><code>OUTPUT_COLUMNS</code> cố định 6 cột của file dài. <code>scope</code> nhận một trong: <code>overall</code>, <code>analysis_area</code>, tên cột khu vực (<code>neighbourhood_cleansed</code>), <code>llm</code>, <code>llm_additional_4000</code>, <code>llm_combined_5000</code>; <code>group_name</code> là giá trị trong scope (<code>all</code>, tên khu, tên nhóm, tên aspect).</p>

=== 38-49
<p>Hai danh sách cột bắt buộc, kiểm sớm ở <code>compute_regular_kpis</code>:</p>
<ul><li><code>LISTING_COLUMNS</code>: 7 cột cho 5 KPI chung. Trong đó <code>neighbourhood_cleansed</code> luôn bắt buộc, kể cả khi <code>config["kpi"]["area_col"]</code> là cột khác, vì các hàm mặc định vẫn dùng nó.</li>
<li><code>CALENDAR_COLUMNS</code>: chỉ <code>listing_id</code> và <code>available</code> cho KPI availability.</li></ul>

=== 52-71
<p><code>add_kpi</code> là nơi duy nhất dựng một dòng kết quả. Nó xử lý ba chỗ về định dạng. NaN đổi thành <code>None</code> (dòng 68) để CSV ghi ô trống, phân biệt với 0 thật: nhóm không có quan sát thì <code>value</code> trống chứ không phải 0%. Số được <code>round(..., 4)</code> nên chỉ giữ 4 chữ số thập phân, vì thế CSV có <code>21.188</code>, <code>6.1683</code>. Còn <code>int(n_obs)</code> giữ mẫu số là số nguyên, không để pandas đổi thành float khi có NaN.</p>
<p>Test <code>test_add_kpi_rounds_to_four_decimals_and_keeps_n_obs_int</code> kiểm đúng <code>2/3*100 = 66.6667</code> và kiểu <code>int</code>.</p>

=== 74-78
<p><code>require_columns</code> gom <em>tất cả</em> cột thiếu vào một <code>ValueError</code> thay vì chết ở cột đầu. Nhờ vậy sửa dữ liệu một lần là biết đủ danh sách. Được gọi ở hầu hết hàm KPI trước khi tính.</p>

=== 81-83
<p><code>load_phantom_kpi_data</code> đọc bảng phân nhóm <b>toàn thành phố</b> (<code>segments_full.csv</code>) rồi nối thêm <code>price</code>/<code>license</code> từ listings thô. Docstring ghi "full Sydney"; <code>city</code> lấy từ config nên đổi thành phố vẫn chạy, miễn có file cùng tên.</p>

=== 85
<p>Đường dẫn cứng <code>data/processed/&lt;city&gt;/segments_full.csv</code>. Bước 5b chỉ chạy với scope <code>full</code> vì scope <code>sample</code> không sinh file này.</p>

=== 87-88
<p>Thiếu file thì <code>FileNotFoundError</code> kèm đường dẫn. Không âm thầm trả bảng rỗng, vì KPI căn ảo mà tính trên bảng rỗng sẽ ra toàn NaN khó hiểu.</p>

=== 90-94
<p>Đọc CSV với <code>dtype={"id": "string"}</code>. ID Airbnb dài 18 chữ số; đọc thành số sẽ bị làm tròn và <code>merge</code> sai. <code>low_memory=False</code> để pandas đọc một lượt, tránh đoán kiểu từng khối.</p>

=== 96-107
<p>Kiểm 6 cột tối thiểu: <code>id</code>, <code>snapshot</code>, <code>segment</code>, <code>neighbourhood_cleansed</code>, <code>room_type</code>, <code>minimum_nights</code>. Đủ cho mọi KPI căn ảo trừ giá/license (nối thêm ở dưới).</p>

=== 109
<p>Danh sách tạm gom listings thô của từng mốc trước khi <code>concat</code>.</p>

=== 111-112
<p>Lặp qua các mốc trong config; <code>str(snapshot)</code> để chắc chắn là chuỗi, vì PyYAML có thể đã đổi ngày thành <code>date</code> (xem <a href="#config-L31">config._as_text</a>).</p>

=== 114
<p>Đường dẫn listings thô: <code>data/raw/&lt;city&gt;/&lt;mốc&gt;/listings.csv.gz</code>. Thiếu <code>data/raw</code> (bị gitignore) thì <code>run_phantom</code> không chạy được trên bản clone sạch.</p>

=== 116-117
<p>Thiếu file thô của bất kỳ mốc nào thì dừng cả hàm. Cố ý: KPI căn ảo cần đủ mọi mốc để so sánh, thiếu một mốc thì bảng sẽ lệch.</p>

=== 119-124
<p>Chỉ đọc 3 cột <code>id</code>, <code>license</code>, <code>price</code> để nhẹ bộ nhớ (file thô rất rộng). <code>id</code> giữ kiểu chuỗi như trên.</p>

=== 126-128
<p>Khử trùng theo <code>id</code> trong từng mốc, gắn cột <code>snapshot</code>, gom vào danh sách. Khử trùng ở đây là để <code>merge</code> với <code>validate="one_to_one"</code> không nổ nếu file thô có dòng lặp.</p>

=== 130
<p>Nối các mốc thành một bảng thô dài.</p>

=== 132-137
<p><code>merge</code> trái theo <code>(id, snapshot)</code>, <code>validate="one_to_one"</code>. <code>validate</code> là lưới an toàn: nếu một bên có khoá lặp, pandas ném lỗi thay vì nhân đôi dòng và thổi phồng mẫu số. <code>how="left"</code> giữ mọi dòng phân nhóm, kể cả khi thiếu giá/license (khi đó hai cột này NaN).</p>

=== 140-144
<p><code>phantom_listing_rate</code>: tỷ lệ căn ảo trên toàn bộ. <code>require_columns</code> kiểm cột <code>segment</code> trước.</p>

=== 146-147
<p><code>valid</code> = dòng có <code>segment</code> không NaN; <code>value</code> = trung bình của <code>isin(PHANTOM)</code> trên đúng các dòng đó, nhân 100. Với mốc 2026-06-16: 918 + 1.913 + 1.528 = 4.359 căn ảo / 20.573 = <b>21,188%</b> (khớp <code>kpi_phantom.csv</code>).</p>

=== 149
<p>Trả <code>(value, valid.sum())</code> = <code>(21.188, 20573)</code>. Docstring nói "trên tổng số listing" nhưng mẫu số thực tế là số listing có <code>segment</code> hợp lệ; với dữ liệu hiện tại hai số bằng nhau vì mọi dòng đều được phân nhóm.</p>

=== 152-160
<p><code>phantom_listing_rate_by_area</code>: cùng phép tính nhưng chia theo <code>neighbourhood_cleansed</code>. Kiểm 2 cột trước khi làm.</p>

=== 162
<p>Bỏ dòng thiếu <code>segment</code> hoặc thiếu khu, để không sinh nhóm <code>nan</code>.</p>

=== 164
<p>Danh sách kết quả dạng <code>(tên khu, tỷ lệ, số listing)</code>.</p>

=== 166-168
<p><code>groupby</code> từng khu, tính tỷ lệ căn ảo trong khu, thêm <code>len(group)</code> làm <code>n_obs</code>. Hàm này <b>không lọc khu nhỏ</b>: <code>kpi_phantom.csv</code> có đủ 38 khu mỗi mốc, kể cả Hunters Hill chỉ 22 căn, Lane Cove 128 căn. Muốn lọc mẫu nhỏ thì phải làm ở nơi khác (xem review).</p>

=== 170
<p>Trả danh sách cho <code>compute_phantom_kpis</code> ghi từng dòng.</p>

=== 173-182
<p><code>long_stay_90_rate_by_segment</code>: tỷ lệ listing yêu cầu ở tối thiểu <code>threshold</code> đêm, theo từng nhóm. <code>threshold</code> được truyền từ <code>config["segments"]["long_stay_min_nights"]</code> = 90.</p>

=== 184-189
<p>Chỉ lấy 2 cột cần, đổi <code>minimum_nights</code> sang số (<code>errors="coerce"</code> biến chữ thành NaN), rồi bỏ dòng thiếu nhóm hoặc thiếu số đêm.</p>

=== 191
<p>Danh sách kết quả <code>(segment, tỷ lệ, n_obs)</code>.</p>

=== 193-195
<p>Với mỗi nhóm, đếm tỷ lệ <code>minimum_nights &gt;= threshold</code>, nhân 100. <code>n_obs</code> là số listing của nhóm có <code>minimum_nights</code> hợp lệ. Vì vậy <code>B_booked</code> có <code>n_obs = 1.151</code> chứ không phải 1.159: 8 căn thiếu <code>minimum_nights</code> bị loại khỏi mẫu số của chính KPI này.</p>

=== 197
<p>Trả danh sách; mốc 2026-06-16 cho <code>D_never 60,6021%</code>, <code>D_dormant 55,4104%</code>, <code>B_ghost 47,0588%</code>, <code>H_healthy 1,1422%</code>.</p>

=== 200-204
<p><code>missing_registration_rate</code>: tỷ lệ listing thiếu license (số đăng ký). Kiểm cột <code>license</code> trước.</p>

=== 206
<p><code>license_text</code> đổi sang kiểu chuỗi rồi <code>strip</code>, để chuỗi toàn khoảng trắng bị coi là rỗng.</p>

=== 208
<p><code>missing</code> = NaN <b>hoặc</b> chuỗi rỗng sau khi strip. Vì thế <code>"Exempt"</code> (được miễn) <b>không</b> tính là thiếu, đúng như cách báo cáo dùng. Kiểm trên raw 2026-06-16: 1.269 thiếu, 4.067 <code>Exempt</code>.</p>

=== 210
<p>Tỷ lệ trên <b>toàn bộ</b> listings: 1.269 / 20.573 = <b>6,1683%</b>.</p>

=== 212
<p>Trả <code>(float(value), len(listings))</code>. Mẫu số ở đây là mọi dòng, gồm cả <code>Exempt</code>; khác với KPI bucket bên dưới chỉ tính các căn thiếu license.</p>

=== 215-224
<p><code>missing_registration_min_nights_buckets</code>: phân bố <code>minimum_nights</code> của các căn <b>thiếu license</b> theo 4 rổ. <code>long_stay_threshold</code> = 90 từ config.</p>

=== 226-227
<p>Lặp lại phép xác định "thiếu license" y như <code>missing_registration_rate</code>: NaN hoặc rỗng sau strip.</p>

=== 229-232
<p>Chỉ lấy các dòng thiếu license, giữ cột <code>minimum_nights</code>.</p>

=== 234-237
<p>Đổi sang số, chữ/None thành NaN.</p>

=== 239
<p>Bỏ NaN và giá trị &lt; 1. Với dữ liệu hiện tại không mất dòng nào: 1.269 căn thiếu license đều có <code>minimum_nights &gt;= 1</code>, nên tổng 4 rổ = 1.269.</p>

=== 241-249
<p>Bốn mặt nạ, nhãn viết cứng theo ngưỡng 90: <code>1-7</code>, <code>8-20</code>, <code>21-89</code> (<code>between(21, threshold-1)</code>), <code>90+</code> (<code>&gt;= threshold</code>). Nếu config đổi <code>long_stay_min_nights</code> khác 90 thì nhãn <code>21-89</code>/<code>90+</code> sẽ sai, xem review.</p>

=== 251-252
<p><code>total</code> = số căn thiếu license có số đêm hợp lệ; <code>results</code> gom kết quả.</p>

=== 254-257
<p>Mỗi rổ: <code>count</code> = số căn trong rổ; <code>value</code> = <code>count / total * 100</code> (nếu <code>total = 0</code> thì NaN). Trả <code>(nhãn, value, count)</code>. Ở đây <code>n_obs</code> là <em>số đếm của rổ</em>, không phải mẫu số <code>total</code>. Trong <code>kpi_phantom.csv</code> mốc cuối: <code>1-7</code> 21, <code>8-20</code> 4, <code>21-89</code> 0, <code>90+</code> 1.244, và tỷ lệ 98,0299% của rổ <code>90+</code> là 1.244/1.269.</p>

=== 259
<p>Trả 4 dòng cho <code>compute_phantom_kpis</code>.</p>

=== 262-274
<p>KPI khó nhất của file là so giá mỗi căn với trung vị giá của "hàng xóm" <b>cùng khu, cùng loại phòng và cùng chế độ lưu trú</b>. Docstring nêu lý do (<code>WHY</code>): căn thuê dài có giá/đêm thấp hơn hẳn căn ngắn ngày; nếu gộp hai chế độ vào một trung vị, trung vị bị kéo xuống và tỷ số của căn ngắn ngày bị thổi lên. Đây là bẫy gộp nhóm (Simpson): nhìn chung tưởng căn ảo rẻ, tách ra thì căn ngắn ngày lại đắt hơn hàng xóm.</p>

=== 275-285
<p>Kiểm 5 cột trước khi tính: <code>segment</code>, <code>neighbourhood_cleansed</code>, <code>room_type</code>, <code>minimum_nights</code>, <code>price</code>.</p>

=== 287-295
<p>Chỉ giữ 5 cột cần, sao chép để không sửa bảng gốc.</p>

=== 297-301
<p><code>minimum_nights</code> sang số; <code>price</code> qua <code>parse_price</code> thành <code>price_numeric</code> (bỏ <code>$</code> và dấu phẩy nghìn).</p>

=== 303-311
<p>Bỏ dòng thiếu bất kỳ trường nào trong 5 trường. Nhờ vậy tử số và mẫu số của tỷ số luôn có đủ ngữ cảnh so sánh.</p>

=== 313
<p>Chỉ giữ giá dương. <code>parse_price</code> đã biến ô không đọc được thành NaN, nhưng giá 0 hoặc âm vẫn lọt qua, nên cần <code>gt(0)</code>.</p>

=== 315
<p>Tạo cột <code>stay_regime</code> rỗng (<code>pd.NA</code>); căn không thuộc chế độ nào sẽ ở lại NA và bị bỏ ở dòng 327.</p>

=== 317-320
<p>Gán <code>"short_stay"</code> cho căn có <code>minimum_nights &lt;= short_stay_max</code> (= 20).</p>

=== 322-325
<p>Gán <code>"90_plus"</code> cho căn có <code>minimum_nights &gt;= long_stay_min</code> (= 90). Nhãn <code>90_plus</code> viết cứng; nếu config đổi ngưỡng thì nhãn trong <code>kpi_name</code> sẽ lệch (xem review). Với 20/90, khoảng 21–89 không thuộc chế độ nào và bị loại.</p>

=== 327
<p>Bỏ các căn ở khoảng giữa (21–89 đêm). Chúng không vào tử số lẫn mẫu số, đúng như docstring nói.</p>

=== 329-333
<p>Khoá nhóm hàng xóm: khu × loại phòng × chế độ. Trung vị được tính <b>trong từng nhóm này</b>, không phải toàn thành phố.</p>

=== 335-338
<p><code>transform("median")</code> gắn trung vị của nhóm trở lại từng dòng, nên mỗi căn có <code>peer_median_price</code> riêng. Trung vị <b>tính cả chính căn đó</b>; nhóm chỉ có 1 căn thì trung vị = giá căn đó và tỷ số = 1,0 (test <code>test_price_relative_to_local_median</code> chứng minh).</p>

=== 340
<p>Bỏ nhóm có trung vị 0 (không thể chia). Thực tế hiếm vì đã lọc giá dương.</p>

=== 342
<p><code>price_ratio</code> = giá căn / trung vị hàng xóm. Tỷ số 1,0 = ngang hàng xóm; 1,32 = đắt hơn 32%.</p>

=== 344
<p>Danh sách kết quả <code>(regime, segment, tỷ lệ, n_obs)</code>.</p>

=== 346-347
<p>Gom theo <code>(stay_regime, segment)</code>, lấy <b>trung vị của các tỷ số</b> (không phải tỷ số của các trung vị). Chọn vậy có chủ ý: trung vị tỷ số chịu được vài căn giá lệch.</p>

=== 349-356
<p>Thêm một dòng kết quả, <code>n_obs</code> = số căn trong nhóm. Mốc 2026-06-16 (khớp <code>kpi_phantom.csv</code>): ngắn ngày <code>D_dormant 1,3203×</code> (791 căn), <code>D_never 1,8549×</code> (529), <code>H_healthy 0,9639×</code> (11.584); 90+ <code>D_dormant 0,9583×</code> (836), <code>D_never 1,0706×</code> (740), <code>H_healthy 0,9761×</code> (66).</p>

=== 358
<p>Trả danh sách. Khi đọc CSV, hai mốc 2025 <b>không có dòng giá nào</b> vì cột <code>price</code> trong listings thô của hai mốc đó rỗng; mốc 2026-03-21 chỉ có <code>short_stay</code> vì <code>minimum_nights</code> lớn nhất của mốc này là 7 (không có căn 90+).</p>

=== 361-362
<p><code>availability_rate</code>: tỷ lệ ngày còn trống trên toàn bộ lịch. Docstring nói rõ mẫu số chỉ đếm ngày có <code>available</code> là <code>t</code> hoặc <code>f</code>.</p>

=== 364-368
<p><code>valid</code> = ngày có cờ <code>t</code>/<code>f</code>; giá trị = tỷ lệ <code>t</code> trong đúng các ngày đó, nhân 100; <code>n_obs</code> = số ngày hợp lệ. Với 1.000 listing × 365 ngày, <code>n_obs = 365.000</code>; mốc cuối có 185.272 ngày <code>t</code> / 365.000 = <b>50,7595%</b>.</p>

=== 371-375
<p><code>long_stay_restriction_rate</code>: tỷ lệ listing yêu cầu ở tối thiểu <code>threshold</code> đêm, mặc định 7. Đừng nhầm với <code>long_stay_90_rate</code> (ngưỡng 90) ở phần căn ảo: đây là ngưỡng "thuê dài ngày" 7 đêm, dùng cho 5 KPI chung.</p>

=== 377-380
<p><code>minimum_nights</code> sang số; <code>valid</code> = dòng có số đêm hợp lệ. Không cần kiểm cột vì <code>compute_regular_kpis</code> đã kiểm <code>LISTING_COLUMNS</code>.</p>

=== 382-383
<p>Tỷ lệ <code>&gt;= 7</code> trên số dòng hợp lệ. Bốn mốc: <b>7,2 / 8,0 / 3,5 / 4,4%</b>, <code>n_obs = 1.000</code>.</p>

=== 386-390
<p><code>high_utilization_listing_rate</code>: tỷ lệ listing có occupancy ước tính <code>&gt;= threshold</code> ngày/năm, mặc định 180 (khoảng nửa năm có khách).</p>

=== 392-398
<p>Đổi <code>estimated_occupancy_l365d</code> sang số, giữ dòng hợp lệ. Cột này do Inside Airbnb ước tính, không phải số đo trực tiếp.</p>

=== 400-401
<p>Tỷ lệ <code>&gt;= 180</code>: <b>23,2 / 25,6 / 24,3 / 22,8%</b>, <code>n_obs = 1.000</code>.</p>

=== 404-407
<p><code>professional_host_presence</code>: tỷ lệ <b>host</b> sở hữu hơn một listing. Docstring nhấn: tính trên host, mỗi host đếm một lần.</p>

=== 409-411
<p>Lấy <code>host_id</code> và <code>calculated_host_listings_count</code>, bỏ dòng thiếu <code>host_id</code>.</p>

=== 413-416
<p>Đổi số listing của host sang số.</p>

=== 418-422
<p>Gộp về một dòng mỗi host, lấy <code>max</code>. Vì cột này lặp cùng giá trị ở mọi listing của host, <code>max</code> chỉ để chắc chắn lấy được giá trị (không phải cộng dồn).</p>

=== 424
<p><code>valid</code> = host có số listing hợp lệ.</p>

=== 426
<p>Tỷ lệ host có <code>calculated_host_listings_count &gt; 1</code>. Mốc cuối: 384/738 = <b>52,0325%</b>. Cột này là <b>tổng số listing của host trên Airbnb</b>, không phải số listing xuất hiện trong mẫu 1.000; đã kiểm 283/738 host có trường này &gt; 1 nhưng chỉ có đúng 1 listing trong mẫu, nên vẫn bị tính là "chuyên nghiệp".</p>

=== 428
<p>Trả <code>(value, số host)</code>. <code>n_obs</code> là số host (738–740), không phải 1.000 listing.</p>

=== 431-435
<p><code>high_rated_listing_share</code>: tỷ lệ listing có điểm đánh giá <code>&gt;= threshold</code>, mặc định 4,9/5.</p>

=== 437-443
<p>Đổi <code>review_scores_rating</code> sang số; <code>valid</code> = listing đã có điểm. Listing chưa có review (điểm NaN) bị loại khỏi mẫu số, nên <code>n_obs</code> nhỏ hơn 1.000.</p>

=== 445-446
<p>Tỷ lệ <code>&gt;= 4,9</code>: <b>36,5263 / 35,4639 / 34,4615 / 32,8205%</b>, <code>n_obs</code> 950 / 970 / 975 / 975. Xu hướng giảm qua bốn mốc.</p>

=== 449-452
<p><code>commercialized_listing_rate_by_area</code>: tỷ lệ listing có dấu hiệu vận hành thương mại theo <code>analysis_area</code>. Định nghĩa trong docstring: <b>cả căn (Entire home/apt) VÀ host có hơn 1 listing</b>.</p>

=== 454-466
<p>Kiểm 4 cột: <code>id</code>, <code>analysis_area</code>, <code>room_type</code>, <code>calculated_host_listings_count</code>. Hàm dùng thẳng <code>analysis_area</code>, <b>không</b> theo <code>config["kpi"]["area_col"]</code>; đổi <code>area_col</code> chỉ đổi bảng availability theo khu, không đổi KPI thương mại.</p>

=== 468-479
<p>Lấy 4 cột và <code>drop_duplicates(subset=["id"])</code>. Trong <code>run</code> hàm được gọi cho từng mốc nên mỗi id chỉ có một dòng; bước khử trùng là lưới an toàn.</p>

=== 481-484
<p>Đổi số listing của host sang số.</p>

=== 486-487
<p>Chỉ giữ dòng đủ khu, đủ loại phòng và đủ số listing của host.</p>

=== 489
<p><code>commercialized</code> = <code>room_type == "Entire home/apt"</code> <b>và</b> host có &gt; 1 listing. So sánh chuỗi chính xác; dữ liệu mẫu chỉ có hai loại <code>Entire home/apt</code> (875) và <code>Private room</code> (125).</p>

=== 491
<p>Danh sách kết quả <code>(khu, tỷ lệ, n_obs)</code>.</p>

=== 493-495
<p>Mỗi khu: tỷ lệ dòng <code>commercialized</code>, <code>n_obs</code> = số listing của khu. Mốc cuối: <b>A05 70,6349%</b>, <b>A02 69,0476%</b>, … <b>A08 38,0952%</b> (mỗi khu ~120–130 căn).</p>

=== 497
<p>Trả danh sách cho <code>compute_regular_kpis</code> ghi dưới scope <code>analysis_area</code>.</p>

=== 500-510
<p><code>availability_rate_by_area</code>: cùng KPI availability nhưng chia theo khu vực. Docstring nêu hai quy tắc: bỏ nhóm thiếu khu (<code>dropna=True</code>) để không sinh nhóm <code>'nan'</code>, và chỉ giữ khu có ít nhất <code>min_area_listings</code> listing để tỷ lệ không dựa trên mẫu quá nhỏ.</p>

=== 511-512
<p>Lấy bảng ánh xạ <code>id → khu</code> (mỗi listing một dòng), đổi tên <code>id</code> thành <code>listing_id</code> để merge với lịch. <code>validate="many_to_one"</code>: nhiều ngày lịch ứng với một listing.</p>

=== 514-522
<p>Gom lịch theo khu. Khu nào có <code>group["listing_id"].nunique() &lt; min_area_listings</code> thì <code>continue</code>. Với <code>min_area_listings = 10</code>, <code>kpi_metrics.csv</code> có 25 khu (so với 38 khu thô), khác với KPI căn ảo theo khu không lọc. Phần tính chỉ lấy ngày hợp lệ <code>t</code>/<code>f</code>; <code>n_obs</code> là số ngày hợp lệ của khu, không phải số listing.</p>
<p>Đếm <code>nunique</code> listing (không đếm số dòng lịch) để một listing có 365 ngày không bị tính thành 365 "căn".</p>

=== 525-534
<p><code>compute_phantom_kpis</code> điều phối bước 5b: đọc hai ngưỡng từ <code>config["segments"]</code> (<code>long_stay_min_nights = 90</code>, <code>short_stay_max_nights = 20</code>) rồi gọi từng hàm KPI và ghi qua <code>add_kpi</code>.</p>

=== 536-545
<p>KPI đầu tiên: <code>phantom_listing_rate</code> cho toàn thành phố, scope <code>overall</code>, group <code>all</code>. Bốn mốc: <b>13,1472 / 12,0180 / 6,4882 / 21,1880%</b>; <code>n_obs</code> theo mốc là 17.730 / 20.436 / 13.563 / 20.573 (đúng số dòng listings thô của từng mốc).</p>

=== 547-556
<p>Cùng KPI nhưng theo khu: scope <code>neighbourhood_cleansed</code>, mỗi khu một dòng. Vì hàm theo khu không lọc mẫu nhỏ, mỗi mốc có đủ <b>38 dòng</b> khu; mốc cuối cao nhất là Pittwater 36,4924% (918 căn), Mosman 36,1624% (271), Woollahra 32,1951% (615).</p>

=== 558-570
<p><code>long_stay_90_rate</code> theo từng nhóm, scope <code>segment</code>. Mốc cuối: <code>D_never 60,6021%</code>, <code>D_dormant 55,4104%</code>, <code>B_ghost 47,0588%</code>, <code>B_booked 10,6864%</code>, <code>L_low 5,9766%</code>, <code>N_new 1,6393%</code>, <code>H_healthy 1,1422%</code>. Hai mốc 2025 chỉ có 6 nhóm vì <code>D_never</code> có 0 căn (không có mốc cũ ≥ 150 ngày).</p>

=== 572-581
<p><code>missing_registration_rate</code> cho toàn thành phố: <b>7,6368 / 6,7968 / 0,1770 / 6,1683%</b>. Mốc 2026-03-21 thấp bất thường (0,177%) vì lần cào đó phần lớn listing đã có license; đây là khác biệt dữ liệu giữa các mốc, không phải lỗi code.</p>

=== 583-595
<p>Bốn rổ <code>minimum_nights</code> của căn thiếu license, scope <code>missing_registration_min_nights</code>, group là nhãn rổ. Mốc cuối: 21 / 4 / 0 / 1.244 căn; tỷ lệ 1,6548 / 0,3152 / 0 / 98,0299%. Ở đây <code>n_obs</code> là số đếm của rổ, còn mẫu số của tỷ lệ là tổng 1.269.</p>

=== 597-610
<p>Giá so hàng xóm, scope <code>segment</code>, tên KPI ghép động <code>price_relative_local_median_{regime}</code> → <code>..._short_stay</code> và <code>..._90_plus</code>. Kết quả của <code>price_relative_to_local_median</code> được nối vào bảng dài ở đây.</p>

=== 613-620
<p><code>compute_regular_kpis</code> điều phối bước 5: tính 5 KPI chung, rồi thương mại theo <code>analysis_area</code>, rồi availability theo khu. Docstring nói rõ hàm chỉ ghi vào <code>rows</code>, không trả về gì.</p>

=== 622-625
<p>Kiểm cột bắt buộc của cả hai bảng trước khi tính. Thiếu cột thì <code>ValueError</code> ngay, không để lỗi lan sang từng KPI.</p>

=== 627-636
<p>KPI 1: <code>availability_rate</code> toàn thành phố, scope <code>overall</code>. Bốn mốc: <b>49,6477 / 50,0811 / 52,1800 / 50,7595%</b>, <code>n_obs = 365.000</code>.</p>

=== 638-647
<p>KPI 2: <code>long_stay_restriction_rate</code> (ngưỡng 7 đêm): <b>7,2 / 8,0 / 3,5 / 4,4%</b>, <code>n_obs = 1.000</code>.</p>

=== 649-658
<p>KPI 3: <code>high_utilization_listing_rate</code> (occupancy ≥ 180 ngày): <b>23,2 / 25,6 / 24,3 / 22,8%</b>, <code>n_obs = 1.000</code>.</p>

=== 660-669
<p>KPI 4: <code>professional_host_presence</code>: <b>50,9485 / 51,6915 / 47,9730 / 52,0325%</b>, <code>n_obs</code> là số host 738 / 739 / 740 / 738.</p>

=== 671-680
<p>KPI 5: <code>high_rated_listing_share</code> (rating ≥ 4,9): <b>36,5263 / 35,4639 / 34,4615 / 32,8205%</b>, <code>n_obs</code> 950 / 970 / 975 / 975.</p>

=== 682-694
<p>Thương mại theo <code>analysis_area</code> (8 khu, mỗi khu ~120–130 căn). Sau vòng lặp, hai dòng 692–693 đọc cấu hình khu vực cho KPI availability: <code>area_col</code> mặc định <code>neighbourhood_cleansed</code>, <code>min_area_listings</code> mặc định 10. Dòng 694 kiểm lại cột <code>id</code> + cột khu đã chọn, cần thiết vì <code>area_col</code> có thể khác cột mặc định.</p>

=== 696-697
<p>Availability theo từng khu, scope là chính tên <code>area_col</code>. Với config hiện tại: 25 khu × 4 mốc = 100 dòng trong <code>kpi_metrics.csv</code>.</p>

=== 700-703
<p><code>to_bool</code> chuẩn hoá cờ LLM về bool. Nhánh đầu: nếu cột đã là kiểu bool (kể cả <code>boolean</code> có NA) thì điền NA thành <code>False</code>. Nhờ vậy không phải đoán chuỗi cho cột chuẩn.</p>

=== 705-717
<p>Nhánh còn lại: đổi sang chuỗi, <code>strip</code>, <code>lower</code>, rồi so với đúng bốn token <code>true/1/yes/y</code>:</p>
<ul><li><code>True</code> (Python bool trong cột object) → <code>"true"</code> → True; <code>False</code> → False.</li>
<li>Số <code>1</code> → <code>"1"</code> → True; <code>0</code> → False.</li>
<li>Chuỗi <code>"t"</code> <b>không</b> được coi là true; <code>"maybe"</code> cũng False. Test <code>test_to_bool_string_columns_understand_truthy_tokens_only</code> kiểm đủ danh sách.</li></ul>

=== 720-724
<p><code>split_aspects</code> tách danh sách khía cạnh bị phàn nàn. Nhánh đầu: nếu đã là Python list thì strip từng phần tử, bỏ rỗng, khử trùng <b>giữ thứ tự</b> bằng <code>dict.fromkeys</code>.</p>

=== 726-727
<p>Giá trị thiếu (NaN/None/<code>pd.NA</code>) → danh sách rỗng. Test kiểm cả ba kiểu thiếu.</p>

=== 729-731
<p>Đổi sang chuỗi và strip; chuỗi rỗng → danh sách rỗng.</p>

=== 733-741
<p>Nếu chuỗi trông như JSON list (<code>[...]</code>) thì thử <code>json.loads</code>. Thành công và là list thì strip/khử trùng như nhánh list. Thất bại (<code>JSONDecodeError</code>) thì rơi xuống nhánh tách thường, ví dụ <code>"[not,json]"</code> thành <code>["[not", "json]"]</code> (có test).</p>

=== 743-744
<p>Nhánh cuối: tách theo bất kỳ dấu <code>;</code>, <code>,</code>, <code>|</code>, bỏ phần rỗng, khử trùng giữ thứ tự. Hàm không tách theo xuống dòng.</p>

=== 747-750
<p><code>complaint_bearing_review_rate</code>: tỷ lệ review có phàn nàn. Mẫu số là <b>toàn bộ review trong bảng</b> (sau khử trùng ở nơi gọi), không phải chỉ review có phàn nàn. Mốc chính thức: 14,0% trên 1.000 review.</p>

=== 753-764
<p><code>top_complaint_aspect_share</code> trả <code>(aspect, tỷ trọng %, tổng lượt nhắc)</code> hoặc <code>None</code>. Cách làm: lọc review có phàn nàn, <code>apply(split_aspects)</code> để mỗi review thành một list, rồi <code>explode()</code> trải thành mỗi khía cạnh một dòng. Sau đó bỏ ô NaN/rỗng.</p>

=== 766-767
<p>Không có khía cạnh nào → <code>None</code>, và nơi gọi sẽ <b>không</b> ghi dòng KPI khía cạnh (chỉ còn dòng tỷ lệ phàn nàn).</p>

=== 769-773
<p><code>value_counts</code> đếm từng aspect; aspect đầu tiên là nhiều nhất. <code>total_aspects</code> = tổng lượt nhắc (một review có thể nhắc nhiều aspect); <code>share</code> = lượt của top / tổng lượt × 100. Vì vậy <code>n_obs</code> của KPI này (176) <b>khác</b> mẫu số của tỷ lệ phàn nàn (1.000).</p>

=== 776-778
<p><code>compute_llm_kpis</code> ghi 2 KPI LLM chính thức. Kiểm hai cột <code>has_complaint</code>, <code>complaint_aspects</code> trước.</p>

=== 780-782
<p>Cache LLM là file JSONL nối thêm, nên một review có thể xuất hiện nhiều lần; giữ bản ghi <b>sau cùng</b> (<code>keep="last"</code>) để nhãn mới nhất thắng. Chỉ làm khi có cột <code>review_id</code>.</p>

=== 784-785
<p>Ghi dòng tỷ lệ phàn nàn dưới scope <code>llm</code>, <code>snapshot = "ALL"</code> (KPI LLM không gắn mốc). Mốc chính thức: 14,0% / 1.000.</p>

=== 787-790
<p>Ghi dòng top aspect nếu có. Với cache chính thức: <code>amenities</code> 50,0%, <code>n_obs = 176</code> lượt nhắc.</p>

=== 793-797
<p><code>_dedupe_reviews</code> gói lại đúng phép khử trùng "giữ bản sau" để phần KPI mở rộng dùng lại. Không có <code>review_id</code> thì trả nguyên bảng.</p>

=== 800-803
<p><code>_add_llm_kpi_rows</code> ghi 2 KPI của một bảng dưới một <code>scope</code> cho trước, dùng chung cho cohort bổ sung và bảng gộp.</p>

=== 805-808
<p>Phần top aspect lặp lại y hệt <code>compute_llm_kpis</code> nhưng scope khác. Viết vậy để khỏi lặp cùng logic ba lần.</p>

=== 811-816
<p><code>compute_extended_llm_kpis</code> tính 2 KPI mở rộng: một cho cache bổ sung (scope <code>llm_additional_4000</code>) và một cho bảng gộp với cache chính thức (scope <code>llm_combined_5000</code>). Docstring nhấn: đây là số <b>tham khảo</b>, không thay KPI chính thức.</p>

=== 818-822
<p>Khử trùng từng bảng riêng (giữ bản sau) trước khi tính. Tên scope viết cứng "4000"/"5000" theo cỡ cohort hiện tại; nếu config đổi số cohort thì tên vẫn vậy, còn <code>n_obs</code> phản ánh số thật.</p>

=== 824-827
<p>Chặn trùng giữa hai cache: nếu một <code>review_id</code> có ở cả chính thức lẫn bổ sung thì <code>ValueError</code> (kèm 5 id đầu). Cố ý <b>không</b> tự khử trùng giữa hai cache: trùng nghĩa là cấu hình cohort sai, phải sửa nguồn.</p>

=== 829
<p>Bảng gộp = nối chính thức + bổ sung rồi khử trùng lần nữa. Với dữ liệu hiện tại: 1.000 + 4.000 = 5.000 review.</p>

=== 831-832
<p>Ghi 2 KPI cho bổ sung (14,175% / 4.000 review; <code>amenities</code> 48,0503% / 795 lượt) và 2 KPI cho bảng gộp (14,14% / 5.000; 48,4037% / 971 lượt).</p>

=== 835-836
<p><code>_keep_group_reviews</code> lọc cache LLM về đúng review của nhóm. Docstring: mục đích là để cache của thành phố/nhóm khác không lọt vào KPI; nếu không đọc được danh sách ID thì giữ nguyên cache như trước.</p>

=== 838-846
<p>Không có cột <code>review_id</code> → trả nguyên. Gọi <code>load_sample_ids(config)</code> lấy <code>review_ids</code>; <b>chỉ bắt <code>FileNotFoundError</code></b> (thiếu file ID) để lùi về hành vi cũ. Có file thì giữ các dòng có <code>review_id</code> nằm trong tập ID của nhóm. Hàm này chỉ áp cho cache chính thức, không áp cho cohort bổ sung.</p>

=== 849-850
<p><code>_filter_passed_qa</code> quyết định dùng cờ QA nào. Docstring nêu <code>WHY</code>: lỗi giá không làm listing sai cho các KPI phi giá (occupancy/rating/min-nights), nên dùng <code>qa_has_error_excl_price</code> để không loại oan dòng chỉ vướng cờ giá.</p>

=== 852-860
<p>Thứ tự lùi ba mức: có <code>qa_has_error_excl_price</code> thì lọc theo nó; không có thì lùi về <code>qa_has_error</code>; không có cột cờ nào thì giữ nguyên. Test <code>test_filter_passed_qa_prefers_core_flag_then_falls_back_to_any</code> kiểm cả ba.</p>

=== 863-864
<p><code>filter_calendar_to_listings</code> cắt lịch về đúng tập listing còn lại. Docstring nêu <code>WHY</code>: nếu lịch còn ngày của listing đã bị loại, tử số và mẫu số của <code>availability_rate</code> lệch nhau.</p>

=== 866-871
<p>Thiếu một trong hai cột khoá thì trả nguyên lịch (không lỗi). Có đủ thì giữ các dòng có <code>listing_id</code> nằm trong tập <code>id</code> của listings. Test <code>test_filter_calendar_to_listings_keeps_only_remaining_listing_ids</code> kiểm.</p>

=== 874-878
<p><code>_read_snapshot</code> đọc listings và calendar của một mốc từ <code>data/processed</code>. Docstring nhấn ID dạng chuỗi. Đường này dùng khi gọi <code>run</code> trực tiếp, không qua pipeline.</p>

=== 880-883
<p>Thiếu <code>listings.csv</code> hoặc <code>calendar.csv</code> → <code>FileNotFoundError</code> kèm đường dẫn. Có test riêng cho từng file.</p>

=== 885-895
<p>Đọc CSV với <code>id</code>/<code>host_id</code>/<code>listing_id</code> kiểu chuỗi, <code>low_memory=False</code>. Trả hai bảng.</p>

=== 898-902
<p><code>run</code> là cửa vào chính. Tham số <code>tables</code> tuỳ chọn: pipeline truyền bảng đã gắn cờ QA; gọi trực tiếp thì bỏ trống và hàm đọc CSV đã xử lý.</p>

=== 904-909
<p>Docstring nhắc lại hợp đồng lọc QA. <code>processed_root</code> = <code>data/processed/&lt;city&gt;</code>; <code>rows</code> là danh sách dòng kết quả dùng chung cho mọi mốc.</p>

=== 911-912
<p>Lặp từng mốc; <code>str(snapshot)</code> như các hàm khác.</p>

=== 914-921
<p>Hai nhánh:</p>
<ul><li><b>Không có <code>tables</code>:</b> đọc CSV processed. Kiểm rồi: <code>listings.csv</code> trong processed <b>không</b> có cột <code>qa_has_error*</code>, nên <code>_filter_passed_qa</code> không lọc gì. Với dữ liệu hiện tại không khác biệt vì mọi lỗi error đều là lỗi giá (<code>excl_price</code> = 0 ở cả 4 mốc).</li>
<li><b>Có <code>tables</code>:</b> lọc listings theo cờ QA lõi; lọc calendar theo <b>cờ của chính lịch</b> (bỏ ngày trùng/orphan) rồi cắt về tập listing còn lại. Test <code>test_run_excludes_calendar_own_qa_flags</code> kiểm nhánh này.</li></ul>

=== 923
<p>Tính KPI chung cho mốc: 5 KPI, phần thương mại và availability theo khu ghi vào <code>rows</code>.</p>

=== 925-927
<p>Đường dẫn cache LLM lấy từ <code>config["llm"]["cache"]</code>, mặc định <code>data/processed/llm_cache.jsonl</code>. <code>official_llm_df</code> giữ cache chính thức để phần mở rộng dùng lại; <code>None</code> nghĩa là chưa có.</p>

=== 929-941
<p>Nếu file cache tồn tại: đọc JSONL với <code>review_id</code> kiểu chuỗi, lọc về review của nhóm. Ba nhánh:</p>
<ul><li>Rỗng sau lọc → in cảnh báo "cache thành phố/nhóm khác", bỏ 2 KPI LLM.</li>
<li>Đủ hai cột <code>has_complaint</code>, <code>complaint_aspects</code> → gán <code>official_llm_df</code> và tính 2 KPI.</li>
<li>Thiếu cột → in cảnh báo, bỏ 2 KPI.</li></ul>
<p>Không có file → in "Chưa có LLM output" và bỏ. Test <code>test_run_ignores_llm_cache_of_another_group</code> và <code>test_run_with_incomplete_llm_cache_skips_llm_kpis</code> kiểm hai nhánh.</p>

=== 943-956
<p>Phần mở rộng chỉ chạy khi config có <code>llm.comparison_cohorts.additional</code> <b>và</b> đã có cache chính thức. Với mỗi cohort: thiếu file thì in cảnh báo, xoá danh sách tạm và <code>break</code>, nghĩa là <b>một</b> cohort thiếu làm bỏ <b>toàn bộ</b> KPI mở rộng, không tính thiếu. Đọc từng cache bằng <code>read_json</code>.</p>

=== 958-967
<p>Nối các cohort, kiểm đủ hai cột rồi gọi <code>compute_extended_llm_kpis</code>. Thiếu cột thì in cảnh báo và bỏ, không ghi dòng nào cho hai scope mở rộng.</p>

=== 969-970
<p>Dựng DataFrame đúng thứ tự <code>OUTPUT_COLUMNS</code> rồi sắp xếp ổn định theo <code>(snapshot, scope, group_name, kpi_name)</code>, thứ tự này là thứ tự test kiểm. Cạnh biên: nếu <code>rows</code> rỗng (config không có mốc nào) thì <code>pd.DataFrame(rows)[OUTPUT_COLUMNS]</code> ném <code>KeyError</code>; chưa có test cho nhánh này.</p>

=== 972-974
<p>Ghi <code>data/processed/kpi_metrics.csv</code>. Đường dẫn <b>không</b> có <code>&lt;city&gt;</code>, nên chạy thành phố khác sẽ ghi đè file cũ (xem review). <code>mkdir(parents=True, exist_ok=True)</code> để chạy được cả khi thư mục chưa có.</p>

=== 976-977
<p>In số dòng đã ghi rồi trả DataFrame, tiện cho test và cho bước sau dùng lại mà không phải đọc lại CSV.</p>

=== 980-983
<p><code>run_phantom</code> là cửa vào bước 5b. Đọc bảng phân nhóm full + giá/license, chuẩn bị <code>rows</code>. Chỉ được gọi khi scope <code>full</code> (xem <a href="#run_pipeline-L184">run_pipeline dòng 184</a>).</p>

=== 985-987
<p>Lặp từng mốc, cắt bảng full theo <code>snapshot</code> bằng <code>.eq(snapshot)</code>. Mỗi lần là một bản sao nên <code>compute_phantom_kpis</code> không sửa dữ liệu của mốc khác.</p>

=== 989-994
<p>Tính toàn bộ KPI căn ảo cho mốc: overall, theo khu, theo nhóm, theo rổ license, và giá so hàng xóm.</p>

=== 996-1000
<p>Dựng DataFrame đúng cột và sắp xếp cùng khoá với <code>run</code>. Test <code>test_run_phantom_writes_kpi_phantom_csv</code> kiểm thứ tự và số dòng.</p>

=== 1002-1004
<p>Ghi <code>data/processed/kpi_phantom.csv</code>. Cũng là đường dẫn phẳng, không theo thành phố.</p>

=== 1006-1007
<p>In số dòng và trả DataFrame. Với dữ liệu đã commit: 216 dòng (4 mốc; mốc cuối 61 dòng).</p>

--- flow
## Cửa vào pipeline
fn 0 898 | run | Bước 5: 5 KPI + thương mại + availability theo khu
st 1 911 | Lặp từng mốc | lọc QA rồi tính KPI chung
st 2 914 | Chọn nguồn bảng | tables của pipeline, hoặc đọc CSV processed
st 2 923 | compute_regular_kpis | ghi 5 KPI + 2 bảng theo khu
st 1 929 | Cache LLM chính thức | 2 KPI phàn nàn (scope llm)
st 1 943 | Cohort bổ sung | 2 KPI mở rộng (4000 + gộp 5000)
fn 0 980 | run_phantom | Bước 5b: KPI căn ảo
st 1 982 | load_phantom_kpi_data | segments_full + raw price/license
st 1 985 | Lặp từng mốc | compute_phantom_kpis

## KPI chung (giá trị, n_obs)
fn 0 361 | availability_rate | ngày t / (t+f)
fn 0 371 | long_stay_restriction_rate | minimum_nights >= 7
fn 0 386 | high_utilization_listing_rate | occupancy >= 180
fn 0 404 | professional_host_presence | host có > 1 listing
fn 0 431 | high_rated_listing_share | rating >= 4,9
fn 0 449 | commercialized_listing_rate_by_area | Entire + host > 1
fn 0 500 | availability_rate_by_area | khu có >= 10 listing

## KPI căn ảo
fn 0 140 | phantom_listing_rate | B_ghost + D_dormant + D_never
fn 0 173 | long_stay_90_rate_by_segment | minimum_nights >= 90
fn 0 200 | missing_registration_rate | license NaN hoặc rỗng
fn 0 215 | missing_registration_min_nights_buckets | 4 rổ số đêm
fn 0 262 | price_relative_to_local_median | tách <= 20 và >= 90 đêm

## LLM
fn 0 776 | compute_llm_kpis | 2 KPI chính thức
fn 0 811 | compute_extended_llm_kpis | 2 scope mở rộng
fn 0 747 | complaint_bearing_review_rate | % review có phàn nàn
fn 0 753 | top_complaint_aspect_share | aspect top / tổng lượt nhắc
fn 0 720 | split_aspects | list / JSON / chuỗi phân tách
fn 0 700 | to_bool | cờ LLM về bool
chips 1 | 923 compute_regular_kpis ; 989 compute_phantom_kpis ; run_pipeline:180 run ; run_pipeline:184 run_phantom

--- review
mid | Hai mốc 2025 không có KPI giá | Listings thô 2025-09-12 và 2025-12-12 có cột <code>price</code> rỗng (0/17.730 và 0/20.436 ô parse được), nên <code>price_relative_to_local_median</code> không sinh dòng nào; <code>kpi_phantom.csv</code> chỉ có dòng giá từ 2026-03-21. Mốc 2026-03-21 chỉ có <code>short_stay</code> vì <code>minimum_nights</code> lớn nhất là 7.
mid | Nhãn 90 viết cứng | <code>stay_regime = "90_plus"</code> và nhãn rổ <code>"21-89"</code>/<code>"90+"</code> viết cứng trong khi ngưỡng lấy từ <code>config["segments"]["long_stay_min_nights"]</code>; đổi ngưỡng khác 90 sẽ làm nhãn trong <code>kpi_name</code>/<code>group_name</code> sai.
mid | n_obs của rổ không phải mẫu số | Bốn dòng <code>missing_registration_bucket_share</code> có <code>n_obs</code> là số đếm từng rổ (21 / 4 / 0 / 1.244) nhưng <code>value</code> chia cho tổng 1.269; đọc CSV dễ tưởng <code>n_obs</code> là mẫu số.
mid | KPI căn ảo theo khu không lọc mẫu nhỏ | <code>phantom_listing_rate_by_area</code> giữ đủ 38 khu (Hunters Hill 22 căn, Lane Cove 128), trong khi <code>availability_rate_by_area</code> lọc <code>min_area_listings = 10</code> nên chỉ còn 25 khu; xếp hạng khu căn ảo vì thế có khu rất nhỏ.
mid | "Professional host" dùng số listing toàn tài khoản | <code>professional_host_presence</code> dựa trên <code>calculated_host_listings_count</code>, không phải số listing trong mẫu; đã kiểm 283/738 host có trường &gt; 1 nhưng chỉ 1 listing trong mẫu vẫn bị tính là chuyên nghiệp.
low | Gọi trực tiếp không lọc QA | <code>data/processed/&lt;city&gt;/&lt;mốc&gt;/listings.csv</code> không có cột <code>qa_has_error*</code> nên <code>_filter_passed_qa</code> trả nguyên bảng; với dữ liệu hiện tại không khác biệt vì mọi lỗi error đều là lỗi giá (<code>excl_price</code> = 0 ở cả 4 mốc), nhưng nếu có lỗi lõi thì chạy trực tiếp sẽ khác pipeline.
mid | KPI thương mại buộc cột analysis_area | <code>commercialized_listing_rate_by_area</code> dùng thẳng <code>analysis_area</code> thay vì <code>config["kpi"]["area_col"]</code>; đổi sang thành phố không có cột này sẽ <code>ValueError</code> ở <code>require_columns</code>, còn đổi <code>area_col</code> thì KPI thương mại vẫn chia theo <code>analysis_area</code>. Đường dẫn đầu ra cũng phẳng (không có <code>&lt;city&gt;</code>) nên chạy thành phố khác sẽ ghi đè <code>kpi_metrics.csv</code>/<code>kpi_phantom.csv</code>.
ok | Tách chế độ khi so giá | <code>price_relative_to_local_median</code> tách &lt;= 20 đêm và &gt;= 90 đêm, bỏ khoảng giữa, tránh bẫy gộp nhóm; test chứng minh trung vị hàng xóm đổi từ 125 (gộp) sang 150 (tách), và căn 90+ đơn độc có tỷ số 1,0.

--- qa
? Vì sao KPI dùng <code>qa_has_error_excl_price</code> chứ không dùng <code>qa_has_error</code>?
<p>Vì lỗi giá không làm listing sai cho các KPI phi giá (occupancy, rating, minimum_nights). Mốc 2026-06-16 có 22 listing bị <code>price_unusable</code> nên <code>qa_has_error</code> bỏ còn 978 dòng, nhưng <code>qa_has_error_excl_price</code> không gắn cờ dòng nào, nên KPI vẫn dùng đủ 1.000 và <code>n_obs = 1.000</code>.</p>
? Vì sao <code>availability_rate</code> có <code>n_obs = 365.000</code>?
<p>Vì mẫu có 1.000 listing × 365 ngày lịch, và mọi ngày đều có cờ <code>t</code>/<code>f</code> hợp lệ. Tử số là số ngày <code>t</code> (185.272 ở mốc cuối), tỷ lệ 50,7595%.</p>
? Vì sao KPI giá chỉ có ở hai mốc 2026?
<p>Cột <code>price</code> trong listings thô của 2025-09-12 và 2025-12-12 rỗng hoàn toàn (0 ô parse được), nên hàm giá bị loại hết. Mốc 2026-03-21 có giá nhưng <code>minimum_nights</code> lớn nhất là 7 nên chỉ sinh nhóm <code>short_stay</code>; mốc 2026-06-16 mới có cả <code>90_plus</code>.</p>
? Giá căn ảo "1,32×" nghĩa là gì?
<p>Đó là trung vị của tỷ số (giá căn / trung vị giá hàng xóm cùng khu, cùng loại phòng, cùng chế độ lưu trú). Mốc cuối, ngắn ngày: D_dormant 1,3203× (791 căn), D_never 1,8549× (529), H_healthy 0,9639× (11.584). Căn ảo ngắn ngày đắt hơn hàng xóm, còn căn khoẻ thì không.</p>
? Hai KPI LLM có cùng mẫu số không?
<p>Không. <code>complaint_bearing_review_rate</code> chia cho toàn bộ review (1.000), ra 14,0%. <code>top_complaint_aspect_share</code> chia cho tổng lượt nhắc khía cạnh (176), ra <code>amenities</code> 50,0%; một review có thể nhắc nhiều aspect nên hai mẫu số khác nhau.</p>
? Vì sao <code>professional_host_presence</code> có <code>n_obs = 738</code> chứ không phải 1.000?
<p>Vì KPI tính trên host, mỗi host một dòng. 738 host sở hữu 1.000 listing; 384 host có <code>calculated_host_listings_count &gt; 1</code>, tức 52,0325%. Cột này là tổng số listing của host trên Airbnb, không phải số listing trong mẫu.</p>
? Vì sao KPI căn ảo theo khu có 38 khu còn availability theo khu chỉ 25?
<p><code>phantom_listing_rate_by_area</code> không lọc mẫu nhỏ nên giữ đủ 38 khu; <code>availability_rate_by_area</code> bỏ khu có ít hơn <code>min_area_listings = 10</code> listing nên còn 25 khu. Vì thế Hunters Hill (22 căn) có mặt trong bảng căn ảo nhưng không có trong bảng availability.</p>
? License ghi "Exempt" có bị tính là thiếu không?
<p>Không. <code>missing</code> chỉ đúng khi license là NaN hoặc chuỗi rỗng sau <code>strip</code>; "Exempt" là chuỗi khác rỗng nên vẫn tính là có license. Trên raw 2026-06-16: 1.269 căn thiếu (6,1683%), 4.067 căn ghi "Exempt".</p>
