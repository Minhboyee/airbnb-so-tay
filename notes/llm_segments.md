--- meta
title: llm_segments.py
lead: Bước 4b: nối nhãn LLM với nhóm căn. Review → <code>listing_id</code> → nhóm của listing ở mốc cuối, rồi đếm mỗi nhóm bị chê khía cạnh nào. Kết quả chính là <code>llm_segment_aspects.csv</code> (7 nhóm × 6 khía cạnh = 42 dòng); hai bảng cohort/gộp thêm là phân tích mở rộng, có cột cảnh báo vì trộn model và prompt.

--- blocks
=== 1-18
<p>Docstring chốt vị trí: chạy <b>sau</b> LLM và chia nhóm, <b>trước</b> đánh giá và KPI. Nó là cầu nối: cache nhãn chỉ có <code>review_id</code>/<code>listing_id</code>; bảng phân nhóm chỉ có <code>listing_id</code>/<code>segment</code>. Module này ghép hai bên.</p>
<p>Ba đầu ra, phân cấp rõ:</p>
<ul><li><code>llm_segment_aspects.csv</code>: bảng <b>chính thức</b>, mẫu LLM 1.000 review.</li>
<li><code>llm_segment_aspects_cohorts.csv</code>: 5 cohort tách riêng (1 chính thức + 4 bổ sung).</li>
<li><code>llm_segment_aspects_combined.csv</code>: gộp 5.000 review, <b>chỉ thăm dò</b> vì các cohort dùng model/prompt khác nhau.</li></ul>
<p>Câu cuối docstring là nguyên tắc của cả file: kiểm dữ liệu chặt, sai thì báo lỗi chứ không ghi bảng sai.</p>

=== 20-22
<p><code>hashlib</code> để băm danh sách ID (kiểm cohort), <code>json</code> đọc metadata và cache, <code>Path</code> cho đường dẫn.</p>

=== 24
<p><code>pandas</code> cho merge và groupby thủ công.</p>

=== 26-28
<p>Ba import nội bộ: <code>llm</code> (dùng lại <code>load_sample_reviews</code>, <code>load_cache</code>, <code>CACHE_SCHEMA_VERSION</code>, <code>ASPECTS</code>), <code>load_sample_ids</code>, và từ <code>src.segments</code>: <code>SEGMENTS</code> (danh sách 7 nhóm) và <code>cfg_get</code> (đọc <code>segments.output_dir</code> có mặc định).</p>

=== 31-37
<p><code>summarize</code> là lõi tính toán. Docstring nêu định nghĩa mẫu số — chỗ giảng viên hay hỏi: <b>share tính theo review, không theo listing</b>. Một căn có 10 review thì đóng góp 10 vào mẫu số. Vì thế bảng không trả lời "bao nhiêu % căn bị chê", chỉ trả lời "trong các review đã gán nhãn của nhóm, bao nhiêu % nhắc khía cạnh này bị chê".</p>
<p>Duyệt đủ 7 nhóm nên nhóm không có review vẫn có dòng với <code>share = None</code> (CSV ghi ô trống).</p>

=== 38-39
<p>Ba kiểm tra trùng ID trước khi merge: listing, review, nhãn. Cần vì <code>validate="one_to_one"</code> ở dưới sẽ ném lỗi khó đọc; kiểm sớm cho thông báo rõ. Test <code>test_summary_rejects_invalid_joins</code> phủ cả ba.</p>

=== 40-41
<p>Nhóm căn phải thuộc đúng 7 tên trong <code>SEGMENTS</code> và không được thiếu. Bảng phân nhóm thiếu nhóm nghĩa là bước 3 lỗi, không phải để tự đoán.</p>

=== 42-43
<p>Giữ <code>date</code> nếu có, để tính ngày review đầu/cuối. Không có <code>date</code> vẫn chạy, chỉ là các cột ngày trống.</p>

=== 44-52
<p>Ghép review với nhãn theo <code>review_id</code>. <code>validate="one_to_one"</code> bắt cả hai phía đều duy nhất; <code>indicator=True</code> thêm cột <code>_merge</code> để biết dòng nào không khớp. <code>suffixes=("", "_cache")</code> vì hai bảng đều có cột <code>listing_id</code>.</p>

=== 53-54
<p><code>(labeled["_merge"] != "both").any()</code> nghĩa là có review <b>không có nhãn</b> trong cache. Ném lỗi thay vì tính trên mẫu thiếu — cùng tinh thần với <a href="#llm-L382">llm.py dòng 382</a>.</p>

=== 55-56
<p><code>listing_id</code> của review và của nhãn phải khớp. Cache ghi <code>listing_id</code> lấy từ lúc gửi; nếu khác thì cache đang lẫn dữ liệu hai lần chạy.</p>

=== 57-60
<p>Ghép tiếp với bảng phân nhóm để lấy <code>segment</code>. <code>validate="many_to_one"</code> đúng bản chất: nhiều review thuộc một listing, mỗi listing một nhóm.</p>

=== 61-62
<p>Review không ghép được nhóm là lỗi dữ liệu (listing lạ). Ở <a href="#llm_segments-L151">run</a> đã lọc orphan trước, nên tới đây còn NaN là bất thường thật.</p>

=== 64-65
<p><code>rows</code> gom theo kiểu "bảng dài": mỗi (nhóm, khía cạnh) một dòng. Duyệt theo <code>SEGMENTS</code> cố định nên thứ tự dòng ổn định và đủ 7 nhóm.</p>

=== 66-69
<p>Bốn số mức nhóm: tổng số căn, số review có nhãn, số căn có ít nhất một review được gán, và phần bù. <code>nunique()</code> trên <code>listing_id</code> — một căn nhiều review chỉ đếm một.</p>

=== 70-71
<p><code>number_of_reviews</code> ép số, lỗi thành NaN (căn thiếu số review). <code>dates</code> chỉ tính nếu có cột <code>date</code>; nếu không thì Series datetime rỗng.</p>

=== 72-74
<p>Với mỗi khía cạnh, đếm số review có khía cạnh đó trong <code>negative_aspects</code>. <code>sum(aspect in values for values in ...)</code> là cách đếm "list chứa phần tử" — chậm hơn vector hoá nhưng chỉ 42 vòng nên không đáng tối ưu. Một review chê 3 khía cạnh được đếm ở cả 3 dòng, nên tổng tỷ lệ có thể vượt 100%.</p>

=== 75-91
<p>Mười ba cột của một dòng. Vài cột đáng chú ý:</p>
<ul><li><code>n_listings_never_reviewed</code>: đếm <code>number_of_reviews == 0</code>. NaN <b>không</b> được tính là 0 — test <code>test_missing_review_count_is_not_never_reviewed</code> kiểm đúng: NaN vào <code>n_listings_review_count_missing</code>.</li>
<li><code>n_listings_without_labeled_review</code> = tổng căn − số căn có review được gán. Cột này gộp cả "căn không có review" và "căn có review nhưng không nằm trong mẫu".</li>
<li><code>first_review_date</code>/<code>last_review_date</code>: ngày cũ nhất/mới nhất trong các review của nhóm, định dạng <code>YYYY-MM-DD</code>; không có ngày nào thì <code>None</code>.</li>
<li><code>share_reviews_negative_aspect</code> = <code>count / total</code>, <code>None</code> khi nhóm 0 review.</li></ul>

=== 92
<p>Trả bảng dài 42 dòng khi có đủ 6 khía cạnh (7 nhóm × 6). Đã chạy thử với 6 aspect: <code>(42, 13)</code>.</p>

=== 95-100
<p><code>read_cache</code> khác <a href="#llm-L158">llm.load_cache</a> ở chỗ: <b>trùng hoặc thiếu ID là lỗi</b>. Lý do nêu trong docstring: bảng so sánh không được đếm một review hai lần. <code>llm.load_cache</code> cho dòng sau thắng vì nó phục vụ chạy lại/ghi nối; ở đây thì không.</p>

=== 101-107
<p>Đọc cả file một lượt, lấy ID theo thứ tự ưu tiên <code>review_id</code> rồi <code>id</code> (cache cũ). List comprehension hai tầng: dòng trắng bị <code>if line.strip()</code> bỏ, mỗi dòng còn lại <code>json.loads</code> đúng một lần.</p>

=== 108-109
<p>Một dòng: trùng hoặc có ID rỗng là <code>ValueError</code>. Test <code>test_run_rejects_duplicate_cache</code> ghi cache hai lần và mong lỗi.</p>

=== 110-111
<p>Gọi lại <code>llm.load_cache</code> để lấy bản ghi đầy đủ <b>và</b> được kiểm schema/aspect miễn phí. Hệ quả: file bị parse hai lượt — với 5.000 dòng vẫn nhỏ, đổi lấy việc không phải viết lại logic kiểm schema.</p>

=== 114-118
<p><code>_sample_listings</code> trả đúng các listing của mẫu ở mốc cuối, kèm <code>segment</code>. Docstring nêu hai lỗi phải chặn: ID mẫu trùng, và bảng phân nhóm thiếu listing của mẫu.</p>

=== 119-122
<p>Đọc <code>&lt;output_dir&gt;/&lt;city&gt;/segments_&lt;scope&gt;.csv</code> với <code>id</code>/<code>snapshot</code> dạng chuỗi (giữ số 0 đầu và so mốc bằng chuỗi). <code>load_sample_ids(config)[0]</code> là bảng listing của nhóm.</p>

=== 123-125
<p>Đoạn WHY giải thích ngoại lệ: listing của mẫu có thể đã <b>rời Airbnb</b> ở mốc cuối, nên vắng khỏi bảng phân nhóm là hợp lý. Comment nêu ví dụ mốc 2026-09-16 còn 942/1.000 — mốc này không có trong config hiện tại, là phòng cho lần chạy sau.</p>

=== 126-130
<p><code>present</code> = phần mẫu còn thật sự trong <code>listings.csv</code> đã lọc của mốc cuối. Chưa có file đã lọc thì đòi đủ cả mẫu như cũ. <code>listings</code> lấy đúng mốc cuối và đúng ID mẫu.</p>

=== 131-132
<p>Hai điều kiện lỗi: ID mẫu trùng, hoặc tập listing đọc được <b>khác</b> tập còn hiện diện. Cái sau bắt trường hợp listing vẫn còn trong dữ liệu mốc cuối mà bảng phân nhóm thiếu — lỗi thật của bước 3. Test <code>test_run_still_rejects_listing_present_in_snapshot_but_missing_from_segments</code>.</p>

=== 133-136
<p>Còn lại là trường hợp hợp lệ: in số listing đã rời mốc cuối rồi chạy tiếp trên phần còn lại. Test <code>test_run_tolerates_sample_listings_that_left_the_last_snapshot</code> kiểm cả thông báo.</p>

=== 139-143
<p><code>run</code> ghi bảng chính thức, trả đường dẫn hoặc <code>None</code>. <code>scope</code> chỉ dùng để chọn file phân nhóm; nội dung vẫn chỉ là 1.000 căn của mẫu, nên cột <code>listing_population</code> luôn là <code>provided_listing_ids</code> — không phải toàn Sydney.</p>

=== 144-146
<p>Chưa có cache thì <b>bỏ qua</b>, trả <code>None</code>. Đây là đường chạy khi <code>--skip-llm</code> và chưa có nhãn; <a href="#run_pipeline-L162">run_pipeline dòng 162</a> dùng <code>None</code> để không vẽ hình từ bảng cũ.</p>

=== 147-149
<p>Đọc bảng phân nhóm của mẫu, đọc 1.000 review của mẫu qua đúng hàm của <a href="#llm-L92">llm.py</a> — không tự lấy mẫu lần hai, tránh hai định nghĩa mẫu lệch nhau.</p>

=== 150-154
<p>Review của listing đã rời mốc cuối không có nhóm để ghép. Bỏ ra <b>và in số lượng</b>, thay vì lặng lẽ làm mẫu số nhỏ đi. Đây là ngoại lệ duy nhất được phép làm mẫu hụt.</p>

=== 155-157
<p>Đọc cache (có kiểm schema/aspect), rồi dựng DataFrame nhãn theo <b>thứ tự review của mẫu</b>. <code>if review_id in records</code> là để không <code>KeyError</code>; phần thiếu được kiểm ngay dưới.</p>

=== 158-161
<p>Cache không phủ đủ mẫu thì in cảnh báo và trả <code>None</code>, <b>không</b> ghi bảng trên mẫu thiếu. Cùng quyết định với bước 4 khi chưa có key: thà không có bảng còn hơn bảng sai mẫu số.</p>

=== 162-168
<p>Tính bảng rồi chèn ba cột mô tả nguồn: <code>snapshot</code> (mốc cuối), <code>segments_scope</code> (full/sample), <code>listing_population</code>. Ghi CSV UTF-8, <code>index=False</code>. Kết quả: 42 dòng × 16 cột.</p>

=== 171-178
<p><code>run_cohorts</code> là phần mở rộng: so sánh 5 lần chạy LLM. Docstring nêu rõ giới hạn — model/prompt có thể khác, metadata chỉ <b>xác nhận</b> chứ không chứng minh nhãn do model nào tạo; kết quả không thay bảng chính thức.</p>

=== 179-181
<p>Không cấu hình <code>llm.comparison_cohorts</code> thì trả <code>None</code>. Test <code>test_cohorts_can_be_unconfigured</code>.</p>

=== 182-184
<p>Ba giá trị dùng suốt hàm: mốc cuối, thành phố, bộ khía cạnh. Lưu ý <code>config["llm"]["aspects"]</code> truy cập thẳng (không <code>.get</code> mặc định) — thiếu khoá là <code>KeyError</code>, khác các chỗ khác trong file dùng mặc định <code>llm.ASPECTS</code>.</p>

=== 185-194
<p>Kiểm metadata <b>trước</b> khi làm bất cứ việc gì. Hai trường hợp bỏ qua, không dừng pipeline:</p>
<ul><li>metadata thuộc thành phố khác (cache còn sót từ config Sydney);</li>
<li>metadata ghi mốc khác mốc cuối hiện tại → bảng cũ không được cập nhật, tránh trộn mốc.</li></ul>
<p>Test <code>test_cohorts_skip_other_city</code> và <code>test_cohorts_skip_changed_snapshot_without_overwriting</code> kiểm cả việc file cũ không bị ghi đè.</p>

=== 195-197
<p>Ba nguồn: thư mục ra, bảng phân nhóm của mẫu, và bảng review của nhóm (<code>load_sample_ids(config)[1]</code>).</p>

=== 199-201
<p>Đọc <code>reviews.csv</code> của mốc cuối và danh sách review chính thức. <code>fillna("")</code> để so tập ID không bị NaN làm nhiễu.</p>

=== 202-205
<p>Hai kiểm tra toàn cục: không trùng ID ở cả hai phía, và <b>tập ID phải bằng nhau</b>. Trên dữ liệu thật: 5.000 = 5.000 (đã chạy thử). Nếu file review bị lọc khác đi, hàm dừng thay vì ghép thiếu.</p>

=== 206-214
<p>Ghép review với danh sách chính thức để lấy <code>listing_id</code> đối chiếu, <code>validate="one_to_one"</code>. Khác <code>listing_id</code> giữa hai nguồn là lỗi dữ liệu.</p>

=== 215
<p><code>expected_official</code> = tập 1.000 review có <code>mau_llm == "x"</code>. Đây là "chân lý" để kiểm cache chính thức ở <a href="#llm_segments-L230">dòng 230</a>.</p>

=== 217-220
<p>Danh sách cặp (cache, metadata): chính thức trước (metadata <code>None</code>), rồi 4 bổ sung. Thứ tự này quyết định thứ tự dòng trong bảng cohort.</p>

=== 221-222
<p><code>all_records</code> tích luỹ ID đã thấy để phát hiện trùng giữa các cohort; <code>cohort_rows</code> gom bảng từng cohort.</p>

=== 223-228
<p>Với mỗi cache: đọc bằng <code>read_cache</code> (trùng/thiếu ID là lỗi), rồi chặn hai trường hợp — ID đã xuất hiện ở cohort trước (<code>ids &amp; set(all_records)</code>) hoặc ID ngoài danh sách review của nhóm. <code>selected</code> là review của cohort theo thứ tự file.</p>

=== 229-233
<p>Nhánh cache chính thức: bắt buộc <b>đúng</b> tập <code>mau_llm</code>; model và prompt lấy từ config. Prompt chính thức ghi <code>original_fingerprint_not_recorded</code> — nghĩa là không có mã băm của prompt gốc, chỉ có tên phiên bản.</p>

=== 234-248
<p>Nhánh cohort bổ sung: đọc metadata và kiểm <b>sáu</b> điều kiện. Đáng chú ý là <code>cohort_sha256</code>:</p>
<p><code>digest = sha256(json.dumps(selected["id"].tolist(), ensure_ascii=False))</code> — băm danh sách ID <b>theo thứ tự file reviews.csv</b>. <a href="#label_additional-L40">label_additional.manifest</a> băm đúng như vậy, nên hai bên khớp. Đổi thứ tự file là đổi hash và metadata bị từ chối.</p>
<p>Metadata chỉ xác nhận "danh sách ID và cấu hình khớp", không chứng minh nhãn do model ghi trong metadata tạo ra — chính <code>reports/llm_segment_notes.md</code> cũng nói vậy.</p>

=== 249-254
<p>Tính bảng cho cohort, chèn <code>cohort</code> (tên file cache), <code>model</code>, <code>prompt_version_or_sha256</code>, rồi gom lại và cộng ID vào <code>all_records</code>. Chèn từ vị trí 0,1,2 nên ba cột này đứng đầu, trước 13 cột thống kê.</p>

=== 255-256
<p>Cuối vòng: các cache phải phủ <b>đủ</b> 5.000 review. Thiếu là lỗi, không ghi bảng gộp trên mẫu hụt. Test <code>test_cohorts_require_coverage_of_all_review_ids</code>.</p>

=== 257-258
<p>Bảng gộp tính trên toàn bộ review (đủ 5.000) và mang cột cảnh báo <code>method_warning = "exploratory_mixed_model_prompt_not_citywide"</code>. Tên cột này là lời nhắc đọc số: trộn model/prompt và không đại diện toàn thành phố.</p>

=== 259-263
<p><code>pd.concat</code> các bảng cohort; rồi chèn cùng ba cột mô tả nguồn cho cả hai bảng. Sau bước này: bảng cohort 19 cột (3 nguồn + cohort/model/prompt + 13), bảng gộp 17 cột (3 nguồn + method_warning + 13).</p>

=== 264-267
<p>Ghi hai file cạnh bảng chính thức. Cả hai đều nằm trong <code>data/processed/&lt;city&gt;/</code> — thư mục bị gitignore, chỉ có sau khi chạy pipeline; vì vậy sổ tay không dẫn số theo nhóm từ các bảng này.</p>

=== 268
<p>Trả cặp đường dẫn để <a href="#run_pipeline-L165">run_pipeline dòng 165</a> in ra; <code>None</code> ở các nhánh bỏ qua.</p>

--- flow
## Ghép và đếm
fn 0 31 | summarize | 42 dòng: 7 nhóm × 6 khía cạnh
st 1 38 | Kiểm trùng ID | listing, review, nhãn
st 1 44 | Ghép nhãn | one_to_one + indicator, thiếu nhãn là lỗi
st 1 58 | Ghép nhóm căn | many_to_one, review phải có nhóm
st 1 72 | Đếm theo khía cạnh | review chứa aspect trong negative_aspects
## Đọc cache
fn 0 95 | read_cache | Trùng/thiếu ID là lỗi, khác llm.load_cache
## Bảng chính thức
fn 0 139 | run | Cache → mẫu listing → summarize → CSV
st 1 144 | Chưa có cache | Trả None, bỏ qua bước
st 1 151 | Bỏ review orphan | Listing đã rời mốc cuối, in số lượng
st 1 158 | Cache thiếu | Trả None, không ghi bảng sai mẫu số
fn 0 114 | _sample_listings | Listing của mẫu ở mốc cuối + segment
## Cohort mở rộng
fn 0 171 | run_cohorts | 1 chính thức + 4 bổ sung + bảng gộp
st 1 185 | Kiểm metadata sớm | Khác thành phố/mốc thì bỏ qua, không ghi đè
st 1 204 | Đối chiếu review | reviews.csv phải bằng danh sách của nhóm
st 1 223 | Từng cohort | Không trùng ID giữa các cache
st 1 237 | Băm danh sách ID | sha256 theo thứ tự file, khớp manifest
st 1 255 | Phủ đủ 5.000 | Thiếu thì lỗi, không ghi bảng gộp
chips 1 | llm:92 load_sample_reviews ; llm:158 load_cache ; run_pipeline:162 run ; kpi:811 compute_extended_llm_kpis ; label_additional:40 manifest

--- review
mid | Metadata cohort không chứng minh nhãn | Code chỉ so <code>city</code>, <code>snapshot</code>, <code>schema_version</code>, <code>aspects</code>, <code>cohort_size</code>, <code>cohort_sha256</code> — tức xác nhận <b>danh sách ID</b> và cấu hình, không xác nhận model nào đã sinh từng nhãn. Bốn cohort bổ sung dùng hai model khác nhau (<code>v4</code>/<code>v4_2</code>: gemini-3.1-flash-lite; <code>v4_3</code>/<code>v4_4</code>: gemini-3.5-flash-lite) theo metadata, nhưng điều đó do người chạy khai, không do file cache chứng minh.
mid | <code>run_cohorts</code> đòi tập review bằng đúng danh sách nhóm | <a href="#llm_segments-L204">Dòng 204</a> so <code>set(reviews["id"]) == set(official_ids["review_id"])</code> trên dữ liệu thật đúng 5.000 = 5.000, nhưng chỉ cần một review bị gỡ khỏi <code>reviews.csv</code> mà danh sách ID chưa cập nhật là cả bước 4b dừng, trong khi <code>run</code> (bảng chính thức) lại chịu được listing/review đã rời mốc cuối. Hai mức khắt khe khác nhau.
low | <code>aspects</code> truy cập thẳng | <a href="#llm_segments-L184">Dòng 184</a> dùng <code>config["llm"]["aspects"]</code>, còn <code>run</code> dùng <code>.get(..., llm.ASPECTS)</code>. Config thiếu khoá thì <code>run_cohorts</code> ném <code>KeyError</code> thay vì dùng mặc định.
low | Đọc cache hai lượt | <code>read_cache</code> parse JSON một lần để kiểm ID rồi gọi <code>llm.load_cache</code> parse lại. Với 5.000 dòng không đáng kể, nhưng là hai nguồn logic đọc cùng một file.
ok | Kiểm join rất chặt | <code>one_to_one</code>, <code>many_to_one</code>, <code>indicator</code> và so <code>listing_id</code> hai phía; sáu kiểu dữ liệu sai đều có test (<code>test_summary_rejects_invalid_joins</code>).

--- qa
? Mẫu số của "share" là gì?
<p>Là số <b>review được gán nhãn</b> của nhóm, không phải số căn. Một căn 10 review đóng góp 10. Vì thế bảng trả lời "trong review của nhóm, bao nhiêu % chê khía cạnh này", không phải "% căn bị chê". Một review chê nhiều khía cạnh được đếm nhiều lần nên tổng các dòng có thể vượt 100%.</p>
? Vì sao nhóm không có review vẫn có dòng?
<p>Vì <a href="#llm_segments-L65">vòng lặp</a> duyệt cố định <code>SEGMENTS</code> (7 nhóm), không duyệt các nhóm có trong dữ liệu. Nhóm rỗng có <code>n_reviews=0</code> và <code>share=None</code> — "không có dữ liệu" khác "không có lời chê". Test <code>test_summary_counts_reviews_and_preserves_missing_groups</code>.</p>
? Bảng này có đại diện toàn Sydney không?
<p>Không. Cả ba bảng chỉ xét 1.000 căn của nhóm và review của chúng; cột <code>listing_population</code> ghi <code>provided_listing_ids</code>. <code>reports/llm_segment_notes.md</code> nhắc lại: không suy rộng tỷ lệ than phiền ra toàn thành phố.</p>
? Vì sao bảng gộp chỉ để thăm dò?
<p>Vì trộn 5 lần chạy: cache chính thức và 4 cohort bổ sung dùng model/prompt khác nhau, chọn review theo đoạn tuần tự khác nhau. Cột <code>method_warning</code> ghi đúng điều đó. Số KPI mở rộng tương ứng là scope <code>llm_additional_4000</code> và <code>llm_combined_5000</code> trong <code>kpi_metrics.csv</code>.</p>
? Băm danh sách ID để làm gì?
<p>Để chắc cache bổ sung đúng là cohort mà metadata mô tả. Hash tính trên <code>json.dumps(selected["id"].tolist())</code> — danh sách ID theo thứ tự file. <a href="#label_additional-L44">label_additional</a> băm y hệt lúc tạo cohort, nên nếu file review đổi thứ tự hoặc đổi nội dung, hash lệch và bước này từ chối.</p>
? Nếu listing của mẫu đã biến mất khỏi Airbnb thì sao?
<p>Hai chỗ xử lý: <a href="#llm_segments-L133">_sample_listings</a> in số listing đã rời mốc cuối và chạy trên phần còn lại; <a href="#llm_segments-L151">run</a> bỏ review của listing đó và in số review bị bỏ. Mẫu số nhỏ đi nhưng có thông báo, không im lặng.</p>
? Bảng chính thức có bao nhiêu dòng?
<p>42 dòng khi dùng đủ 6 khía cạnh: 7 nhóm × 6 aspect. Đã chạy thử <code>summarize</code> với 6 aspect và được <code>(42, 13)</code>; sau khi <code>run</code> chèn thêm 3 cột nguồn là 16 cột.</p>
