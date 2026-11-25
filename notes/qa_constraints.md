--- meta
title: qa_constraints.py
lead: <code>qa_constraints.py</code> giữ "hợp đồng" số lượng giữa mẫu dữ liệu của nhóm và đề bài: mỗi mốc 1.000 căn (875 Entire home/apt, 125 Private room), số căn 0 review 50/30/25/25, mốc cuối thiếu đúng 20 giá, 8 khu <code>analysis_area</code> mỗi khu 120–130 căn. Lệch số nào thì ném <code>QAConstraintError</code> và pipeline dừng. <code>qa_rules.py</code> thì chỉ gắn cờ. Không có <code>qa.expected</code> thì file này không làm gì.

--- blocks
=== 1-9
<p>Docstring nêu vị trí: bước 2, <code>qa.py</code> gọi cho từng mốc <b>trước</b> khi gắn cờ. Chỗ khác với <code>qa_rules</code>: vi phạm ở đây là dừng, còn ở đó chỉ gắn cờ.</p>
<p>Vì sao dừng: các số này là đề cam kết cho mẫu của nhóm. Lệch nghĩa là đã lọc sai tập ID, đọc nhầm mốc hoặc tải nhầm file. Khi đó mọi KPI sau đều tính trên dữ liệu sai, gắn cờ từng dòng không cứu được.</p>
<p>Docstring ghi đầu vào có <code>reviews</code>, nhưng không hàm nào dùng bảng reviews (xem <a href="#qa_constraints-L41">dòng 41</a>).</p>

=== 11-15
<p>Import tối thiểu: <code>Any</code> cho dict <code>expected</code>, <code>pandas</code> cho bảng.</p>

=== 18-19
<p>Ngoại lệ riêng, kế thừa <code>RuntimeError</code>. Có tên riêng để test bắt đúng loại lỗi (<code>pytest.raises(QAConstraintError, match="room_types")</code>) và người chạy nhìn tên lỗi là biết do ràng buộc mẫu, không phải lỗi code.</p>

=== 22-23
<p>Ràng buộc 1: tổng số căn và số căn theo <code>room_type</code>. Mỗi hàm <code>_check_*</code> trả về danh sách thông báo, không tự ném lỗi; hàm tổng ở cuối gom lại.</p>

=== 24-26
<p>Thiếu <code>expected</code> hoặc thiếu một trong hai khoá cần thì bỏ qua ràng buộc này (trả list rỗng). Mẫu chung cho mọi hàm: config thiếu mục nào thì không kiểm mục đó.</p>

=== 27-29
<p>So số dòng listings với <code>n_listings</code> (1.000).</p>

=== 30-32
<p>Thiếu cột <code>room_type</code> thì báo lỗi và dừng hàm luôn (không thể đếm). Test: <code>test_missing_room_type_column_errors</code>.</p>

=== 33-38
<p>Đếm từng loại và so với 875/125. <code>counts.get(..., 0)</code> để loại phòng không xuất hiện đếm là 0 thay vì lỗi. Chỉ kiểm các loại có trong config: một căn đổi thành "Shared room" làm "Entire home/apt" còn 874 nên vẫn bị bắt (test <code>test_room_types_constraint_broken_by_room_type_value</code>).</p>

=== 41-47
<p>Ràng buộc 2: số căn có <code>number_of_reviews = 0</code> ở mốc thứ <code>idx</code>. Tham số <code>reviews</code> có trong chữ ký nhưng không dùng: đếm từ cột của listings, vì bảng reviews của nhóm chỉ là mẫu 5.000 review, không phản ánh căn nào có 0 review. Test <code>test_no_reviews_constraint_does_not_depend_on_review_sample</code> khoá hành vi này.</p>

=== 48-51
<p>Không có khoá <code>no_reviews_per_snapshot</code> thì bỏ qua.</p>

=== 53-55
<p>Thiếu cột thì báo lỗi rõ ràng.</p>

=== 57
<p>Lấy số kỳ vọng <b>theo vị trí</b>: <code>[50, 30, 25, 25][idx]</code>. Vì so theo vị trí nên số chỉ đúng khi mốc trong config đúng 4 mốc được giao; <code>config.expected_applies</code> lo điều đó, nếu không thì <code>expected</code> bị bỏ trước khi tới đây (<a href="#config-L70">config.py</a>). Thiếu cơ chế đó, thêm mốc thứ 5 sẽ gây <code>IndexError</code>.</p>

=== 59-63
<p>Ép về số với <code>errors="coerce"</code>: ô rác thành NaN và không được đếm là 0. Chỉ ô bằng đúng 0 mới tính.</p>

=== 65-68
<p>Lệch thì thêm thông báo dạng "expected 50 ..., got 49".</p>

=== 71-74
<p>Ràng buộc 3: thiếu giá, chỉ ở mốc cuối. Đề cho biết mốc cuối có đúng 20 căn thiếu giá. Hai mốc đầu thì cả cột giá trống, nên kiểm số giá thiếu ở các mốc trước là vô nghĩa.</p>

=== 75-77
<p>Không phải mốc cuối (<code>idx != n_snapshots - 1</code>) hoặc không có khoá thì bỏ qua. Test: <code>test_missing_price_constraint_skipped_before_last_snapshot</code>.</p>

=== 78-80
<p>Mốc cuối mà mất cả cột <code>price</code> là lỗi (test <code>test_missing_price_column_errors_on_last_snapshot</code>).</p>

=== 81
<p>Đếm ô giá "thiếu": NaN hoặc chuỗi rỗng/toàn khoảng trắng. Rộng hơn mục con <code>price_missing</code> ở <a href="#qa_rules-L160">qa_rules</a> (chỉ NaN); ô <code>" "</code> ở đây tính là thiếu, còn bên luật rơi vào <code>price_bad_type</code>. Với CSV đọc bằng <code>read_csv</code> ô trống đã thành NaN nên hai cách đếm trùng nhau: mốc 2026-06-16 ràng buộc qua (20) và luật ghi <code>price_missing:20</code> trong <code>reports/qa_report.csv</code>.</p>

=== 82-85
<p>So với <code>missing_price_last_snapshot</code> = 20.</p>

=== 88-92
<p>Ràng buộc 4: cột <code>analysis_area</code> (khu phân tích do <code>download.py</code> gán). Kiểm bốn điều: có cột, không ô trống, đúng 8 khu, mỗi khu 120–130 căn.</p>

=== 93-95
<p>Bỏ qua khi config không có <code>n_areas</code> hoặc <code>area_size_range</code>.</p>

=== 96-98
<p>Thiếu cột thì báo và dừng hàm. Test: <code>test_analysis_area_constraint_broken_by_missing_column</code>.</p>

=== 99-101
<p>Đếm ô trống riêng, vì <code>value_counts()</code> ở dòng sau bỏ NaN: không có bước này thì căn thiếu khu bị "biến mất" khỏi phép đếm mà không báo.</p>

=== 102-105
<p>Đúng 8 khu. Thêm khu lạ thì số khu thành 9 (test <code>test_analysis_area_constraint_broken_by_extra_area</code>).</p>

=== 106-110
<p>Mỗi khu phải có 120 ≤ số căn ≤ 130. 1.000 căn / 8 khu = 125 trung bình, nên đề cho dung sai ±5. Chuyển vài căn từ khu này sang khu khác là bị bắt (test <code>test_analysis_area_constraint_broken_by_moving_rows</code>).</p>

=== 113-124
<p>Hàm công khai duy nhất, gọi ở <a href="#qa-L146">qa.py dòng 146</a>. Docstring nói rõ: gom hết lỗi rồi ném một lần.</p>

=== 125-128
<p><code>if not expected</code> bắt cả <code>None</code> lẫn dict rỗng. Đường chạy này xảy ra khi <code>run_pipeline</code> đã bỏ <code>qa.expected</code> (mốc khác mốc được giao, hoặc mẫu chọn theo seed): không đối chiếu gì cả.</p>

=== 129-133
<p>Chạy đủ bốn hàm và nối danh sách lỗi. Không dừng ở lỗi đầu tiên.</p>

=== 134-135
<p>Có lỗi thì ném một <code>QAConstraintError</code> duy nhất, thông báo dạng <code>snapshot 3: room_types: ...; analysis_area: ...</code> (số mốc đếm từ 1). Sửa dữ liệu một lần là thấy hết vấn đề. Test: <code>test_multiple_violations_reported_in_one_message</code>.</p>

--- flow
## Gọi từ qa.run cho mỗi mốc
fn 0 113 | check_sample_constraints | Không có expected thì bỏ qua
st 1 130 | Loại phòng | 1.000 căn; 875 / 125
fn 1 22 | _check_room_types | Đếm theo room_type
st 1 131 | Căn 0 review | 50 / 30 / 25 / 25 theo vị trí mốc
fn 1 41 | _check_no_reviews | Đếm từ listings, không từ reviews
st 1 132 | Thiếu giá mốc cuối | Đúng 20 căn
fn 1 71 | _check_missing_price | NaN hoặc chuỗi rỗng
st 1 133 | Khu phân tích | 8 khu, mỗi khu 120–130
fn 1 88 | _check_areas | Có cột, không trống, đủ khu, cỡ khu
st 1 134 | Gom lỗi | Ném QAConstraintError một lần
chips 1 | qa:146 run ; config:70 expected_applies

--- review
low | Tham số reviews không dùng | <code>_check_no_reviews</code> và <code>check_sample_constraints</code> nhận <code>reviews</code> nhưng không đọc; docstring đầu file vẫn ghi đầu vào gồm reviews. Có chủ ý (đếm từ listings) nhưng chữ ký gây hiểu nhầm.
low | Số review của đề không kiểm ở đây | <code>qa.expected.n_reviews</code> (5.000) không được file này dùng; nó được kiểm ở bước tải (<a href="#download-L438">download.py dòng 438</a>). Khi bị hỏi "QA có kiểm đủ 5.000 review không" thì trả lời: có, nhưng ở bước 1.
low | Hai định nghĩa "thiếu giá" | Ràng buộc tính cả chuỗi rỗng, mục con <code>price_missing</code> chỉ tính NaN. Trên dữ liệu thật trùng nhau (20 = 20) vì <code>read_csv</code> đã đổi ô trống thành NaN.
ok | Gom mọi lỗi một lần | Không dừng ở lỗi đầu tiên; thông báo nêu mốc và từng ràng buộc lệch, kèm số kỳ vọng và số thật.
ok | Có lối thoát khi đổi mốc | Số đếm theo vị trí mốc chỉ chạy khi <code>expected_applies</code> đúng; đổi mốc hay đổi seed thì không dừng oan.

--- qa
? Vì sao ràng buộc mẫu thì dừng còn luật QA thì chỉ gắn cờ?
<p>Ràng buộc mẫu kiểm cả tập có đúng là tập đề giao không (1.000 căn, 875/125, 8 khu…). Sai là mọi kết quả sau vô nghĩa, nên dừng. Luật QA kiểm từng dòng; một vài dòng xấu không làm hỏng cả tập, chỉ cần đánh dấu để KPI tự bỏ.</p>
? Vì sao đếm căn 0 review bằng cột number_of_reviews mà không đếm từ bảng reviews?
<p>Bảng reviews của nhóm chỉ là mẫu 5.000 review, nhiều căn có review thật nhưng không có dòng nào trong mẫu. Đếm từ đó sẽ ra số căn "0 review" quá lớn. Cột <code>number_of_reviews</code> của listings là số Inside Airbnb ghi cho từng căn.</p>
? Vì sao chỉ kiểm thiếu giá ở mốc cuối?
<p>Đề chỉ cam kết số thiếu giá (20) cho mốc cuối. Hai mốc đầu cột giá trống toàn bộ, nếu đếm thì ra 1.000 và dừng oan.</p>
? Nếu dữ liệu lệch hai chỗ cùng lúc thì báo thế nào?
<p>Cả hai cùng nằm trong một thông báo, nối bằng dấu chấm phẩy, ví dụ <code>snapshot 1: room_types: ...; analysis_area: ...</code>.</p>
? Đổi sang thành phố khác thì file này có làm hỏng pipeline không?
<p>Không, nếu bỏ hoặc sửa <code>qa.expected</code>. Không có mục đó thì <code>check_sample_constraints</code> trả về ngay ở dòng 128.</p>
