--- meta
title: qa_rules.py
lead: Bộ luật QA theo từng dòng. <code>apply_rules</code> nhận ba bảng của một mốc, trả bản sao có thêm cột cờ <code>qa_&lt;luật&gt;</code> và nhật ký cho báo cáo. Có <b>7 tên cờ</b> (<code>price_unusable</code>, <code>price_outlier</code>, <code>duplicate_key</code>, <code>cross_snapshot_duplicate</code>, <code>orphan_fk</code>, <code>contract_violation</code>, <code>review_empty</code>) chia thành <b>13 luật</b> theo bảng, gồm 21 mục con ghi vào cột <code>detail</code>. Ba cờ tổng: <code>qa_has_error</code>, <code>qa_has_error_excl_price</code>, <code>qa_has_warning</code>. QA chỉ gắn cờ, không xoá dòng nào.

--- blocks
=== 1-21
<p>Docstring là bản đồ của cả file, đọc kỹ trước khi vấn đáp:</p>
<ul><li>Mỗi luật là <b>một</b> dòng <code>Rule(...)</code> trong <code>RULES</code>. Thêm luật = viết một hàm <code>_check_...</code> và thêm một dòng, không sửa chỗ khác.</li>
<li>Hàm kiểm tra trả Series bool, <code>True</code> = dòng vi phạm.</li>
<li>Một cờ "tổng hợp" là phép OR của nhiều hàm con; tên các hàm con được ghi vào cột <code>detail</code> của báo cáo để biết cụ thể cái gì bật.</li></ul>
<p>Lịch sử: bản cũ báo cáo từng hàm con như một luật riêng (báo cáo PDF nhắc "19 luật"). Hiện có 21 mục con: 19 cũ + 2 mục trùng giữa mốc (<code>listing_stale_copy</code>, <code>review_conflict_across_snapshots</code>). Code là sự thật: 7 tên cờ, 13 luật (test <code>test_rule_metadata_complete_and_unique</code> khoá đúng hai số này).</p>

=== 23-29
<p>Import: <code>dataclass</code> cho <code>Context</code> và <code>Rule</code>, <code>Literal</code> giới hạn tên bảng/mức độ, kiểu <code>Callable</code>/<code>Mapping</code> cho chú thích.</p>

=== 31-32
<p>Hai kiểu "chỉ được là các chuỗi này": bảng là listings/reviews/calendar; mức độ là error/warning. mypy bắt lỗi gõ nhầm như <code>"listing"</code>.</p>

=== 34-35
<p>Thứ tự gắn cờ trong một mốc. Listings đi đầu vì reviews/calendar cần tập id listing để bắt "mồ côi".</p>

=== 37-40
<p>Tập giá trị hợp lệ cho cột boolean kiểu Inside Airbnb (<code>t</code>/<code>f</code>), so sau khi <code>lower()</code>. Giá trị khác (ví dụ <code>"Yes"</code>) là "trôi phân loại", dùng ở <a href="#qa_rules-L212">_check_bool_category_drift</a>.</p>

=== 42-49
<p>Ba cờ tổng:</p>
<ul><li><code>qa_has_error</code>: vi phạm ít nhất một luật mức error (kể cả lỗi giá).</li>
<li><code>qa_has_error_excl_price</code>: như trên nhưng <b>bỏ luật giá</b>. KPI phi giá (tỉ lệ kín lịch, điểm đánh giá, số đêm tối thiểu, phân nhóm căn ảo) lọc theo cờ này (<a href="#kpi-L849">kpi.py</a>).</li>
<li><code>qa_has_warning</code>: luật mức warning, hiện chỉ có <code>price_outlier</code>.</li></ul>
<p>Vì sao tách cờ trừ giá: mốc cuối có 20 căn thiếu giá. Thiếu giá không làm sai lịch hay review của căn đó. Nếu lọc bằng <code>qa_has_error</code>, 22 căn bị loại oan khỏi mọi KPI phi giá; với hai mốc đầu (giá trống 100%) còn tệ hơn nếu luật giá chạy. Tách cờ thì mỗi KPI chỉ bỏ dòng có lỗi liên quan đến nó.</p>

=== 52-66
<p><code>Context</code>: gói thông tin chung cho mọi luật của một mốc, để chữ ký hàm kiểm tra luôn là <code>(df, ctx)</code>.</p>
<ul><li><code>cfg</code>: mục <code>qa</code> của config.</li>
<li><code>snapshot</code>: ngày mốc, để bắt review có ngày sau mốc.</li>
<li><code>listing_ids</code>: id listing của mốc, để bắt review/lịch mồ côi.</li>
<li><code>previous</code>: listings/reviews đã gộp của các mốc trước.</li></ul>
<p>Trường nào <code>None</code> thì luật dùng nó tự tắt (trả toàn False). <code>frozen=True</code>: không luật nào sửa được ngữ cảnh của luật khác.</p>

=== 69
<p>Kiểu chung của hàm kiểm tra: nhận (bảng, Context), trả Series bool cùng index.</p>

=== 72-92
<p><code>Rule</code> mô tả một luật bằng dữ liệu, không bằng code rẽ nhánh:</p>
<ul><li><code>name</code>, <code>table</code>: khoá duy nhất là cặp (bảng, tên); <code>duplicate_key</code> có ở cả ba bảng.</li>
<li><code>severity</code>: error hay warning, quyết định cờ tổng nào bật.</li>
<li><code>needs</code>: cột bắt buộc; thiếu thì cả cột cờ False.</li>
<li><code>is_price</code>: không tính vào <code>qa_has_error_excl_price</code> và bị bỏ khi mốc không có giá.</li>
<li><code>condition</code>, <code>reason</code>: chữ ghi thẳng vào CSV.</li>
<li><code>subchecks</code>: các hàm con, cho cột <code>detail</code>. <code>info</code>: phép đếm chỉ để ghi <code>detail</code>, không gắn cờ.</li></ul>

=== 94-97
<p>Tên cột cờ: <code>qa_</code> + tên luật, ví dụ <code>qa_price_unusable</code>.</p>

=== 100-107
<p><code>parse_price</code>: Inside Airbnb ghi giá dạng chữ <code>"$1,234.00"</code>. Bỏ <code>$</code> và dấu phẩy nghìn rồi <code>to_numeric(errors="coerce")</code>: không đọc được thì NaN, không ném lỗi. Chạy thử: <code>""</code>, <code>" "</code>, <code>None</code> → NaN; <code>"$1,234.00"</code> → 1234.0; <code>"-5"</code> → -5.0. Hàm này cũng được <code>qa.py</code> và <code>kpi.py</code> (dòng 301) dùng lại, nên mọi nơi đọc giá cùng một cách.</p>

=== 110-113
<p><code>has_price_data</code>: mốc có ít nhất một giá đọc được không. Đây là công tắc của hai luật giá.</p>
<p>Vì sao cần: hai mốc đầu (2025-09-12, 2025-12-12) cột <code>price</code> trống 100% (<code>download.py</code> cũng ghi "mốc trước giá trống là bình thường"). Nếu vẫn chạy, <code>price_missing</code> bật cho cả 1.000 căn, <code>qa_has_error</code> = True mọi dòng, và báo cáo QA nói "100% lỗi" trong khi dữ liệu chỉ đơn giản là không có giá. Bằng chứng trong <code>reports/qa_report.csv</code>: hai mốc đầu chỉ có 11 dòng luật (thiếu <code>price_unusable</code>, <code>price_outlier</code>), <code>mean_price</code> = NaN.</p>

=== 116-118
<p>Series toàn False cùng index: kết quả "luật không áp dụng". Dùng khắp nơi để mọi nhánh bỏ qua đều trả cùng dạng.</p>

=== 121-123
<p>Đọc cột thành số, ô rác thành NaN. So sánh với NaN luôn ra False, nên ô rác <b>không</b> bị gắn cờ bởi các luật so ngưỡng (ví dụ <code>minimum_nights</code>).</p>

=== 126-130
<p><code>_orphan</code>: dòng có <code>listing_id</code> không nằm trong tập id listing của <b>cùng mốc</b>. Dùng chung cho reviews và calendar. <code>listing_id</code> và <code>id</code> đều đọc dạng chuỗi (<code>ID_DTYPES</code> trong download.py) nên <code>isin</code> không lệch kiểu int/str.</p>

=== 133-141
<p><code>_requires</code> bọc hàm con: bảng thiếu cột cần thì trả toàn False thay vì <code>KeyError</code>. Nhờ vậy mỗi mục con tự an toàn, kể cả khi gọi riêng trong <code>_detail</code>.</p>

=== 144-154
<p><code>_or_checks</code> hợp nhiều hàm con thành một cờ bằng phép OR (<code>|=</code>). Một dòng vi phạm hai mục con vẫn chỉ tính <b>một</b> dòng bị gắn cờ; còn <code>detail</code> đếm theo từng mục con, nên tổng trong <code>detail</code> có thể lớn hơn <code>n_flagged</code>.</p>

=== 157-162
<p>Mục con <code>price_missing</code>: ô giá NaN. Mốc cuối: 20 (khớp đề), mốc 2026-03-21: 1.</p>

=== 165-167
<p><code>price_bad_type</code>: ô có giá trị nhưng không đọc được thành số (ví dụ <code>"abc"</code>, hoặc chuỗi rỗng chưa thành NaN). Dữ liệu thật: 0.</p>

=== 170-172
<p><code>price_non_positive</code>: giá ≤ 0. Giá 0 hay âm không thể là giá thuê thật. Dữ liệu thật: 0.</p>

=== 175-177
<p><code>price_above_cap</code>: giá &gt; <code>qa.price_max</code> = 10.000 AUD/đêm (config chép từ <code>price_max_aud</code>). Dữ liệu thật: 2 căn ở cả hai mốc có giá.</p>

=== 180-184
<p>Luật ngoại lệ theo <b>IQR</b> (khoảng tứ phân vị):</p>
<ul><li>Q1 = phân vị 25%, Q3 = phân vị 75%. IQR = Q3 − Q1 là độ rộng của 50% giá ở giữa.</li>
<li>Rào dưới = Q1 − k·IQR, rào trên = Q3 + k·IQR. Ngoài rào là ngoại lệ.</li>
<li>k = 1,5 là "ngoại lệ" theo Tukey (biểu đồ hộp); k = 3 là "ngoại lệ xa". Nhóm chọn k = 3 để chỉ bắt giá rất lạ.</li></ul>
<p>Để hình dung: nếu dữ liệu chuẩn, Q3 ≈ μ + 0,674σ và IQR ≈ 1,349σ, nên k = 1,5 tương ứng ±2,7σ (bắt khoảng 0,7% dòng) còn k = 3 tương ứng ±4,7σ (gần như 0). Giá Airbnb lệch phải mạnh, nên dù k = 3 vẫn bắt 51–52 căn (5,1–5,2%).</p>

=== 185-186
<p>Tính Q1, Q3 trên giá đọc được của <b>chính mốc đó</b> (bỏ NaN). Vì sao dùng IQR thay vì trung bình ± 3 độ lệch chuẩn: phân vị gần như không bị kéo bởi chính các giá cực đoan cần bắt, còn trung bình và độ lệch chuẩn thì bị kéo mạnh (hai căn &gt; 10.000 AUD đủ đẩy trung bình lên khoảng 26 AUD, xem <a href="#qa-L55">qa.py</a>). Lưu ý: phân vị tính cả giá ≤ 0 và giá &gt; cap, nhưng vài giá như vậy hầu như không dịch Q1/Q3.</p>

=== 187
<p>k đọc từ <code>qa.outlier_iqr_k</code> (configs/sydney.yaml đặt 3.0), mặc định 3.</p>

=== 188
<p>Gắn cờ hai phía. Thực tế rào dưới thường âm: Q1 − 3(Q3 − Q1) &lt; 0 khi Q3 &gt; 4/3·Q1, điều gần như luôn đúng với giá thuê. Khi đó chỉ rào trên có tác dụng; giá quá thấp (≤ 0) đã do <code>price_non_positive</code> lo. Ví dụ chạy thử 10 giá 80…500 và 20.000: Q1 = 162,5, Q3 = 387,5, rào = [−512,5; 1.062,5], chỉ 20.000 bị gắn cờ.</p>
<p>Giá &gt; cap cũng ngoài rào trên, nên nằm trong cả hai cờ. Kiểm bằng số thật: mốc cuối 52 cảnh báo, nhưng bỏ cảnh báo chỉ làm 978 → 928 (bớt 50); 2 căn còn lại chính là 2 căn &gt; 10.000 AUD đã bị bỏ ở mức lỗi. Mốc 2026-03-21: 51 cảnh báo, 997 → 948 (bớt 49), cũng chồng 2.</p>

=== 191-193
<p><code>min_nights_above_cap</code>: <code>minimum_nights</code> &gt; <code>qa.min_nights_cap</code> = 365 (khoá đề bắt buộc). Bắt căn thực chất không cho thuê ngắn hạn hoặc nhập sai.</p>

=== 196-201
<p><code>listing_duplicate</code>: trùng bộ khoá <code>qa.dedupe_keys</code> = (<code>id</code>, <code>last_scraped</code>) trong cùng mốc. <code>keep=False</code> gắn cờ <b>tất cả</b> bản trùng, không chừa bản đầu: QA không đoán bản nào đúng. Thiếu khoá trong config hoặc trong bảng thì bỏ qua.</p>

=== 204-209
<p><code>room_type_unknown</code>: loại phòng không có trong <code>qa.expected.room_type_counts</code>. Phụ thuộc mục <code>expected</code>: khi run_pipeline bỏ <code>expected</code> (đổi mốc, mẫu theo seed) thì mục con này tự tắt (test <code>test_room_type_unknown_without_expected_flags_nothing</code>). Ô trống không bị gắn cờ.</p>

=== 212-219
<p><code>bool_category_drift</code>: một trong các cột <code>qa.bool_columns</code> (<code>instant_bookable</code>, <code>host_is_superhost</code>, <code>has_availability</code>) có giá trị ngoài t/f/true/false/1/0. Ô trống không tính. Bắt trường hợp nguồn đổi cách mã hoá (ví dụ "Yes"/"No") làm các phép <code>== "t"</code> ở bước sau âm thầm sai.</p>

=== 222-224
<p><code>min_gt_max_nights</code>: số đêm tối thiểu lớn hơn tối đa, mâu thuẫn ngay trong một dòng.</p>

=== 227-234
<p><code>review_score_out_of_range</code>: quét mọi cột bắt đầu bằng <code>review_scores_</code>, điểm ngoài [0, 5] (<code>qa.review_score_range</code>). NaN (căn chưa có điểm) không bị gắn cờ.</p>

=== 237-245
<p><code>coord_out_of_bbox</code>: toạ độ ngoài khung Sydney (<code>qa.bbox</code>: vĩ độ −34,5…−33,0; kinh độ 150,0…151,6). Không có bbox thì tắt. Dòng cuối yêu cầu cả hai toạ độ đọc được, để toạ độ trống không bị coi là "ngoài khung".</p>

=== 248-253
<p><code>review_text_missing</code>: <code>comments</code> trống hoặc chỉ khoảng trắng. Chạy thử: comment <code>"  "</code> bật <code>qa_review_empty</code>. Review rỗng vô dụng cho bước LLM.</p>

=== 256-263
<p><code>review_date_after_snapshot</code>: ngày review sau ngày mốc, điều không thể có trong dữ liệu chụp tại mốc. So <b>nghiêm ngặt</b> (&gt;), review đúng ngày mốc là hợp lệ (đã chạy thử). Ngày không đọc được thành NaT, so sánh ra False.</p>

=== 266-268
<p><code>review_id_duplicate</code>: <code>id</code> review lặp trong cùng mốc. Bỏ qua id trống để nhiều ô trống không bị coi là "trùng nhau".</p>

=== 271-273
<p><code>calendar_duplicate</code>: cặp (<code>listing_id</code>, <code>date</code>) lặp, tức một ngày khai hai lần.</p>

=== 276-279
<p><code>calendar_incomplete</code>: đếm số dòng lịch của từng listing (<code>transform("size")</code> trả số đếm về từng dòng), khác 365 thì gắn cờ <b>mọi dòng</b> của listing đó. Chạy thử với <code>calendar_days=3</code>: listing có 2 dòng trùng ngày bị gắn cờ, listing đủ 3 ngày thì không. Lưu ý: listing không có dòng lịch nào thì không có dòng để gắn cờ, luật này không thấy. Dữ liệu thật: 365.000 dòng = 1.000 × 365, 0 vi phạm.</p>

=== 282-290
<p>Lấy bảng của các mốc trước từ <code>ctx.previous</code>; chưa có (mốc đầu) hoặc rỗng thì <code>None</code>, luật trùng giữa mốc tự tắt.</p>

=== 293-297
<p>So bộ khoá của từng dòng với tập khoá đã thấy, bằng <code>MultiIndex.isin</code> (so cả bộ, không so từng cột rời). Ép <code>str</code> hai phía để không lệch kiểu giữa các mốc. Dòng thiếu khoá luôn False.</p>

=== 300-310
<p><code>listing_stale_copy</code> (cờ <code>cross_snapshot_duplicate</code> của listings). Cùng <code>id</code> ở nhiều mốc là bình thường: đó chính là theo dõi một căn qua thời gian, nền của cả bài "căn ảo". Nhưng cùng <code>id</code> <b>và</b> cùng <code>last_scraped</code> nghĩa là bản ghi mốc cũ bị chép nguyên sang mốc sau, KPI mốc sau dùng dữ liệu cũ. Dữ liệu thật: 0 ở mọi mốc.</p>

=== 313-318
<p>Phép đếm <code>info</code>, không gắn cờ: bao nhiêu listing đã có id ở mốc trước. Báo cáo ghi <code>id_seen_in_earlier_snapshot:1000</code> ở ba mốc sau, tức 1.000/1.000 căn được theo dõi xuyên suốt (mẫu cố định).</p>

=== 321-330
<p><code>review_conflict_across_snapshots</code>: <code>reviews.csv</code> của Inside Airbnb <b>cộng dồn</b>, review cũ lặp lại ở mọi mốc sau là bình thường. Chỉ lỗi khi cùng <code>id</code> review mà khác <code>listing_id</code> hoặc <code>date</code>: không biết bản nào đúng.</p>

=== 331-333
<p>Dựng bảng tra từ các mốc trước: bỏ id trống, ép chuỗi, giữ bản <b>mới nhất</b> của mỗi id (<code>keep="last"</code>, vì <code>previous</code> ghép theo thứ tự thời gian), đặt <code>id</code> làm index.</p>

=== 334-338
<p>Với dòng có id đã biết, tra <code>listing_id</code>/<code>date</code> cũ và so. Chạy thử: review có <code>listing_id</code> trống bị coi là "khác" (chuỗi <code>"nan"</code> ≠ id cũ) nên bật cờ này, đồng thời bật <code>orphan_fk</code>. Dữ liệu thật: 0.</p>

=== 341-346
<p>Phép đếm <code>info</code>: review đã có ở mốc trước. Báo cáo ghi <code>review_seen_in_earlier_snapshot:5000</code> ở ba mốc sau: cả 5.000 review của nhóm lặp lại ở mọi mốc, đúng với README ("5.000/5.000 review lặp lại hợp lệ"). Khi gộp nhiều mốc, bước sau khử trùng theo id.</p>

=== 349-358
<p>Từ đây là phần "lắp ráp": mỗi tuple gồm (tên mục con, hàm đã bọc <code>_requires</code>). Thứ tự trong tuple là thứ tự ghi <code>detail</code>. <code>price_unusable</code> gồm 4 mục: thiếu, sai kiểu, ≤ 0, &gt; cap.</p>

=== 359
<p><code>price_outlier</code>: một mục con IQR.</p>

=== 360-364
<p>Trùng khoá (listings, reviews, calendar) và mồ côi (reviews, calendar), mỗi cái một mục con. <code>_LISTING_DUPLICATE</code> không bọc <code>_requires</code> vì hàm đã tự kiểm cột khoá.</p>

=== 365-372
<p>Hợp đồng cột listings: 6 mục con. Ba mục <code>bool_category_drift</code>, <code>review_score_out_of_range</code> không bọc vì tự lặp qua cột có thật.</p>

=== 373-375
<p>Hợp đồng reviews (ngày sau mốc), hợp đồng calendar (đủ 365 ngày), review rỗng.</p>

=== 376-379
<p>Hai mục trùng giữa mốc và hai phép đếm <code>info</code> đi kèm. Lưu ý: <code>_REVIEW_CROSS</code> <b>không</b> bọc <code>_requires</code> theo cột của bảng hiện tại, chỉ kiểm cột của bảng mốc trước (xem nhận xét lỗi).</p>

=== 381-383
<p><code>RULES</code>: 13 luật. Thứ tự ở đây là thứ tự cột <code>qa_*</code> và thứ tự dòng trong <code>reports/qa_report.csv</code>.</p>

=== 384-393
<p>Luật 1, listings, <b>error</b>, <code>is_price=True</code>: giá không dùng được. Số thật: mốc 2026-03-21 gắn cờ 3 (<code>price_missing:1; price_above_cap:2</code>); mốc 2026-06-16 gắn cờ 22 (<code>price_missing:20; price_above_cap:2</code>), 2,2%.</p>

=== 394-403
<p>Luật 2, listings, <b>warning</b>, <code>is_price=True</code>: ngoại lệ IQR. Mức warning vì giá cao bất thường có thể là thật (biệt thự, căn sự kiện), không chắc là lỗi. Số thật: 51 (5,1%) và 52 (5,2%).</p>

=== 404-412
<p>Luật 3, listings: trùng (<code>id</code>, <code>last_scraped</code>) trong mốc. 0 ở mọi mốc.</p>

=== 413-425
<p>Luật 4, listings: bản sao cũ từ mốc trước. Có <code>info</code> đếm id lặp hợp lệ. 0 vi phạm.</p>

=== 426-434
<p>Luật 5, listings: hợp đồng cột (6 mục con). 0 vi phạm.</p>

=== 435-444
<p>Luật 6, reviews: trùng id review. <code>needs=("id",)</code>.</p>

=== 445-458
<p>Luật 7, reviews: xung đột id review giữa các mốc. <code>needs</code> đủ ba cột, nên khi gắn cờ thì an toàn; nhưng <code>_detail</code> không xét <code>needs</code> (xem nhận xét lỗi).</p>

=== 459-468
<p>Luật 8, reviews: review mồ côi (listing không có trong mốc).</p>

=== 469-478
<p>Luật 9, reviews: ngày review sau ngày mốc.</p>

=== 479-488
<p>Luật 10, reviews: review không có nội dung. Lý do ghi rõ: ảnh hưởng chất lượng phân tích LLM.</p>

=== 489-498
<p>Luật 11, calendar: trùng (listing, ngày).</p>

=== 499-508
<p>Luật 12, calendar: lịch của listing không còn trong mốc.</p>

=== 509-519
<p>Luật 13, calendar: số ngày lịch khác 365. Cả ba luật calendar chạy trên 365.000 dòng mỗi mốc, đều 0 vi phạm.</p>

=== 522-529
<p><code>_evaluate</code>: hai cổng trước khi chạy luật: thiếu cột <code>needs</code>, hoặc luật giá mà mốc không có giá, thì trả toàn False. <code>fillna(False).astype(bool)</code> đảm bảo cột cờ luôn là bool thật (NaN = không vi phạm).</p>

=== 532-537
<p><code>flag_table</code>: làm trên <b>bản sao</b> (<code>df.copy()</code>), thêm một cột <code>qa_*</code> cho mỗi luật của bảng. Bảng gốc giữ nguyên, số dòng giữ nguyên (test <code>test_apply_rules_preserves_rows_and_adds_qa_has_error</code>).</p>

=== 539-540
<p><code>any_of</code>: OR theo hàng của các cột cờ được chọn; danh sách rỗng (ví dụ calendar không có luật warning) thì toàn False.</p>

=== 542-546
<p>Tính ba cờ tổng từ <b>các cột luật</b>, không từ cột cũ nào có sẵn: nếu bảng vào đã có cột <code>qa_has_error</code> thì bị ghi đè (test <code>test_add_any_flag_ignores_existing_qa_has_error</code>). Ví dụ chạy thử một dòng giá 15.000: <code>qa_price_unusable</code> và <code>qa_price_outlier</code> bật, nên <code>qa_has_error</code> = True, <code>qa_has_warning</code> = True, còn <code>qa_has_error_excl_price</code> = False: KPI phi giá vẫn giữ căn này.</p>

=== 549-557
<p><code>_detail</code>: chạy lại từng mục con và <code>info</code>, ghi những cái có đếm &gt; 0 dạng <code>tên:số; tên:số</code>. Không bật gì thì chuỗi rỗng (trong CSV đọc ra NaN). Hàm gọi thẳng <code>check</code> của mục con, <b>không qua cổng <code>needs</code></b> như <code>_evaluate</code>.</p>

=== 560-575
<p>Một dòng báo cáo: <code>n_flagged</code> là số dòng có cột cờ True (sau OR), <code>pct_flagged</code> làm tròn 2 chữ số. <code>action</code> luôn là <code>"flag"</code>: QA không có hành động xoá.</p>

=== 578-591
<p><code>apply_rules</code>: cửa vào từ <a href="#qa-L148">qa.py dòng 148</a>. Docstring giải thích vì sao mốc không có giá thì <b>không ghi dòng báo cáo</b> cho luật giá: ghi "0 lỗi giá" sẽ hiểu nhầm là đã kiểm và giá sạch, trong khi thực ra không có giá để kiểm.</p>

=== 592-595
<p>Lấy tập id listing của mốc cho luật mồ côi. Không có listings thì tập rỗng, mọi review/lịch bị coi là mồ côi (test <code>test_apply_rules_skips_missing_tables</code>). Dựng <code>Context</code> một lần cho cả mốc.</p>

=== 597-599
<p>Gắn cờ theo thứ tự listings → reviews → calendar, chỉ các bảng có mặt.</p>

=== 600-605
<p>Mỗi luật của bảng có mặt sinh một dòng báo cáo, trừ luật giá ở mốc không có giá. Kết quả ở bản commit: hai mốc đầu 11 dòng, hai mốc sau 13 dòng.</p>

--- flow
## Gọi từ qa.run, mỗi mốc
fn 0 578 | apply_rules | Một mốc, mọi bảng
st 1 594 | Tập id listing | Cho luật mồ côi
st 1 595 | Context | cfg, mốc, id, mốc trước
## Gắn cờ từng bảng
fn 1 532 | flag_table | Bản sao + cột qa_*
fn 2 525 | _evaluate | Cổng needs và cổng giá
fn 2 110 | has_price_data | Hai mốc đầu: không có giá
st 2 542 | Ba cờ tổng | error, excl_price, warning
## Các luật (RULES)
fn 1 384 | price_unusable | Thiếu, sai kiểu, ≤ 0, &gt; 10.000
fn 1 394 | price_outlier | IQR k = 3, warning
fn 1 404 | duplicate_key | Trùng khoá trong mốc
fn 1 413 | cross_snapshot_duplicate | Bản cũ chép sang; review xung đột
fn 1 426 | contract_violation | Hợp đồng cột của bảng
fn 1 459 | orphan_fk | Review/lịch không có listing
fn 1 479 | review_empty | comments rỗng
## Báo cáo
fn 1 560 | _report_row | n_flagged, pct, detail
fn 2 549 | _detail | Mục con đã bật
chips 1 | qa:148 run ; qa:25 compute_kpis ; kpi:849 _filter_passed_qa

--- review
bug | _detail bỏ qua needs, có thể KeyError | <code>flag_table</code> an toàn khi reviews thiếu cột <code>date</code>, nhưng <code>apply_rules</code> sau đó gọi <code>_detail</code>, chạy thẳng <a href="#qa_rules-L321">_check_review_cross_snapshot_conflict</a> và ném <code>KeyError: 'date'</code> (dòng 337) nếu có reviews mốc trước. Tái hiện: <code>apply_rules({"reviews": DataFrame({"id": ["r1"], "listing_id": ["1"]})}, {}, "2025-12-12", {"reviews": DataFrame({"id": ["r1"], "listing_id": ["1"], "date": ["2025-01-01"]})})</code>. Dữ liệu thật đủ cột nên không xảy ra; sửa bằng cách kiểm <code>rule.needs</code> trong <code>_detail</code> hoặc bọc <code>_requires</code>.
mid | Báo cáo PDF nói "19 luật" | Code có 7 tên cờ, 13 luật theo bảng, 21 mục con (19 cũ + 2 mục trùng giữa mốc). Bảng II.2 của báo cáo dùng tên mục con (<code>price_missing</code>, <code>price_outlier_iqr</code>), khớp cột <code>detail</code>, không phải tên cờ.
low | Cờ giá chồng nhau | Giá &gt; 10.000 bật cả <code>price_unusable</code> và <code>price_outlier</code>; 52 cảnh báo ở mốc cuối có 2 căn đã là lỗi. Đọc "52 ngoại lệ" cần biết chỉ 50 là ngoại lệ thuần.
low | Lịch thiếu hẳn không bị bắt | <code>calendar_incomplete</code> đếm theo dòng có sẵn; listing không có dòng lịch nào thì không có dòng để gắn cờ. Ràng buộc tổng 365.000 dòng ở download.py che chỗ này.
ok | Tách cờ trừ giá | <code>qa_has_error_excl_price</code> giữ 20 căn thiếu giá và 2 căn giá vượt cap trong KPI phi giá; test <code>test_core_flag_ignores_price_rules</code>.
ok | Không chạy luật giá khi không có giá | <code>has_price_data</code> chặn cả gắn cờ lẫn ghi báo cáo, tránh 1.000 lỗi giả ở hai mốc đầu.
ok | Thêm luật bằng dữ liệu | Luật là một dòng <code>Rule</code>, phần chạy và báo cáo dùng chung; test khoá 13 luật, 7 tên, warning duy nhất là <code>price_outlier</code>.

--- qa
? Vì sao QA chỉ gắn cờ mà không xoá dòng?
<p>Mỗi KPI cần lọc khác nhau: KPI giá phải bỏ căn thiếu giá, KPI lịch thì không. Xoá sớm là ép mọi bước dùng một cách lọc, và mất khả năng kiểm lại. Gắn cờ giữ đủ 1.000 căn mỗi mốc; báo cáo cho thấy tác động: mốc cuối 1.000 → 978 → 928.</p>
? IQR là gì, vì sao k = 3?
<p>IQR = Q3 − Q1, độ rộng 50% giá ở giữa. Ngoại lệ là giá ngoài [Q1 − k·IQR, Q3 + k·IQR]. k = 1,5 là ngưỡng biểu đồ hộp, bắt nhiều giá cao hợp lệ vì giá lệch phải; k = 3 chỉ bắt giá rất lạ. Vẫn ra 51–52 căn (khoảng 5%), nên để mức warning, không phải error.</p>
? Vì sao dùng IQR thay vì trung bình ± 3 độ lệch chuẩn?
<p>Phân vị bền với ngoại lệ; trung bình và độ lệch chuẩn bị chính các giá cực đoan kéo lên, làm rào rộng ra và bỏ sót. Ví dụ: chỉ 2 căn &gt; 10.000 AUD đã làm giá TB mốc cuối tăng khoảng 26 AUD.</p>
? Vì sao hai mốc đầu không có dòng price_unusable trong báo cáo?
<p>Cột price trống 100% ở 2025-09-12 và 2025-12-12. <code>has_price_data</code> = False nên luật giá không chạy và không ghi dòng báo cáo. Nếu chạy, 1.000/1.000 căn bị "thiếu giá", <code>qa_has_error</code> bật toàn bộ.</p>
? price_missing ở mốc cuối là bao nhiêu, có khớp đề không?
<p>20 (<code>detail</code> = <code>price_missing:20; price_above_cap:2</code>, tổng 22 căn bị cờ). Khớp <code>missing_price_last_snapshot: 20</code> mà <code>qa_constraints</code> đã kiểm trước đó.</p>
? cross_snapshot_duplicate khác duplicate_key thế nào?
<p><code>duplicate_key</code> bắt trùng trong một mốc. <code>cross_snapshot_duplicate</code> so với mốc trước: listing trùng cả id lẫn <code>last_scraped</code> (bản cũ chép sang), review cùng id nhưng khác listing/ngày. Cùng id ở mốc sau là bình thường, chỉ đếm vào <code>detail</code>: 1.000 listing và 5.000 review ở mỗi mốc sau, 0 vi phạm.</p>
? Vì sao cần qa_has_error_excl_price?
<p>Căn chỉ có lỗi giá vẫn có lịch và review đúng. KPI phi giá (kín lịch, điểm, phân nhóm căn ảo) lọc theo cờ này nên không loại oan 22 căn lỗi giá ở mốc cuối.</p>
