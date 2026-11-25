--- meta
title: segments/transitions.py
lead: Theo dõi listing đổi nhóm giữa các mốc và kiểm tra mốc bị lọc (gap). Ba việc: <code>track</code> dựng bảng rộng id × mốc (vắng = <code>VANG</code>), <code>transition_matrix</code> dựng ma trận 7×8 (thêm cột <code>BIEN_MAT</code>) chuẩn hoá theo hàng, và <code>gap_audit</code> đếm căn vắng ở mốc 2026-03-21 rồi tách "do bộ lọc" với "biến mất thật". <code>VANG</code> và <code>BIEN_MAT</code> là hai tên cho cùng một hiện tượng: không có mặt ở mốc.

--- blocks
=== 1-8
<p>Docstring nêu bối cảnh quan trọng: mốc gap (2026-03-21) bị lọc nên thiếu căn, vì vậy module tách riêng căn "vắng" do bộ lọc khỏi căn chủ nhà thật sự rời sàn. Chạy sau khi <code>rules.py</code> đã gán cột <code>segment</code>. Vào/ra đều trong RAM; ghi file do <code>report.py</code>.</p>

=== 10
<p><code>from __future__ import annotations</code> cho cú pháp kiểu hiện đại.</p>

=== 12
<p><code>Any</code> cho giá trị trong dict kết quả audit.</p>

=== 14
<p><code>pandas</code> để ghép theo id, <code>crosstab</code> và xử lý cột số.</p>

=== 16
<p><code>SEGMENTS</code> để reindex ma trận đủ 7 hàng; <code>cfg_get</code> để đọc các ngưỡng gap.</p>

=== 18-19
<p><code>GONE = "BIEN_MAT"</code> là nhãn "không có mặt ở mốc đích" trong ma trận. Khác <code>VANG</code> ở <code>track</code> chỉ là tên gọi: cả hai đều nghĩa là vắng mặt. Đặt thành hằng để test và chỗ khác tham chiếu không gõ sai chuỗi.</p>

=== 22-23
<p>Docstring: bảng rộng mỗi id một dòng, mỗi mốc một cột ghi nhóm hoặc <code>VANG</code>. Đây là bảng để nhìn một căn đi qua 4 mốc.</p>

=== 24-30
<p><code>track</code> đặt index theo <code>id</code> dạng chuỗi cho từng mốc, rồi ghép cột. Khi ghép, pandas tự căn theo index nên id vắng ở mốc nào thành <code>NaN</code>; <code>fillna("VANG")</code> đổi <code>NaN</code> thành nhãn vắng. Kết quả: id có ở bất kỳ mốc nào đều xuất hiện một dòng, ô thiếu ghi <code>VANG</code>. Test <code>test_track_marks_missing_listings_as_absent</code> kiểm id 1 và 2 chéo nhau cho <code>VANG</code>.</p>

=== 33-39
<p>Docstring <code>transition_matrix</code> nói rõ hợp đồng: cohort là id có mặt ở mốc nguồn; id không còn ở mốc đích rơi vào <code>BIEN_MAT</code>; <code>share</code> chuẩn hoá <b>theo hàng</b> để so được các nhóm quy mô khác nhau.</p>

=== 40-42
<p>Chuẩn bị DataFrame rỗng đúng cột để chỗ gọi không phải kiểm kiểu, rồi nếu thiếu một trong hai mốc thì trả luôn bảng rỗng. Test <code>test_transition_matrix_is_empty_when_a_snapshot_is_missing</code> kiểm cả <code>empty</code> lẫn tên cột.</p>

=== 44-45
<p>Lấy Series nhóm của mốc nguồn và mốc đích, index theo <code>id</code> dạng chuỗi. Nhờ <code>load.py</code> đã bỏ id trùng, index ở đây là duy nhất nên <code>reindex</code> bên dưới an toàn.</p>

=== 46-47
<p><code>dst_seg.reindex(from_seg.index)</code> căn mốc đích theo đúng danh sách id của mốc nguồn; id không có ở đích thành <code>NaN</code> rồi <code>fillna(GONE)</code> thành <code>BIEN_MAT</code>. Đây là chỗ biến "vắng mặt" thành một nhãn đếm được.</p>

=== 49-50
<p><code>pd.crosstab</code> đếm số cặp (from, to), rồi <code>reindex(index=SEGMENTS, columns=[*SEGMENTS, GONE])</code> ép đủ 7 hàng × 8 cột. Nhờ reindex, ô bằng 0 vẫn có mặt nên ma trận luôn đầy đủ, không phụ thuộc dữ liệu. Với Sydney, cột <code>D_never</code> ở mốc nguồn 2025 toàn 0 vì hai mốc đó không có <code>D_never</code>.</p>

=== 51-54
<p>Đặt tên hai trục, rồi <code>stack()</code> chuyển sang dạng dài (mỗi cặp một dòng) và đặt lại tên cột <code>["from_segment", "to_segment", "n"]</code>. Dạng dài này là thứ <code>report.py</code> ghi ra CSV và cũng tiện lọc.</p>

=== 55-58
<p>Tính tổng theo <code>from_segment</code>, rồi <code>share = n / total</code>. Mẹo <code>total.where(total &gt; 0, 1)</code>: nhóm nguồn rỗng chia cho 1 thay vì 0 để tránh chia cho 0. Kết quả làm tròn 4 chữ số và sắp theo (from, to). Số thật: <code>D_dormant → D_dormant</code> = <b>0,6544</b> (09/2025→06/2026) và <b>0,6712</b> (12/2025→06/2026); <code>H_healthy</code> giữ <b>0,6941</b> / <b>0,7281</b> (file <code>segments_transitions_full.csv</code>).</p>

=== 61-67
<p>Docstring <code>gap_audit</code> định nghĩa <code>n_explained</code>: ở mốc cuối, căn đó đòi <b>&gt; 7 đêm</b> (<code>gap_explain_min_nights</code>) hoặc đã kín lịch (<code>availability &lt;= blocked_max</code>), tức bị bộ lọc của mốc gap loại chứ không phải chủ nhà rời sàn. Lưu ý ngưỡng là <b>7</b>, không phải 90 của <code>stay_type</code>.</p>

=== 68-70
<p>Vòng đầu tính thống kê từng mốc. <code>availability_365</code> ép số, NaN → 0.</p>

=== 71-79
<p>Mỗi mốc một dòng gồm: <code>n_listings</code>, <code>max_minimum_nights</code> (đòi đêm tối thiểu cao nhất), và <code>share_blocked</code> = tỉ lệ avail <code>&lt;= blocked_max</code>. Comment dòng 76 nhắc <code>availability_365 &lt;= 0</code> nghĩa là cả năm tới không ngày nào đặt được. Số thật ở scope full: n = 17.730 / 20.436 / 13.563 / 20.573; <code>max_minimum_nights</code> = 999 / 500 / <b>7</b> / 500; <code>share_blocked</code> = 9,98% / 7,73% / 0,18% / 10,10%. Con số <b>7</b> ở mốc 2026-03-21 chính là bằng chứng mốc này bị lọc theo <code>minimum_nights &lt;= 7</code>.</p>

=== 80-87
<p>Gom thống kê thành DataFrame (luôn có, kể cả khi không có gap) và khởi tạo dict <code>audit</code> với các bộ đếm bằng 0. <code>per_snapshot</code> luôn được ghi ra <code>segments_gap_audit_*.csv</code>.</p>

=== 88-89
<p>Không có mốc gap hoặc mốc gap không được nạp → trả audit với bộ đếm 0. Test <code>test_gap_audit_without_a_usable_gap_snapshot</code> kiểm cả <code>None</code> lẫn mốc không tồn tại.</p>

=== 91-93
<p><code>others</code> là các mốc bình thường (bỏ mốc gap). Nếu không còn mốc nào khác thì không so được, trả audit 0.</p>

=== 95-99
<p>Comment dòng 95 nói nguyên tắc: chỉ xét căn <b>có mặt ở mọi mốc bình thường</b>, để "vắng" chắc chắn là do mốc gap. <code>common</code> là giao id của 09/2025, 12/2025 và 06/2026; <code>missing</code> = <code>common</code> trừ id có ở mốc gap. Vì đòi có mặt ở <b>tất cả</b> mốc thường, một căn chỉ xuất hiện ở 09 và 06 mà thiếu 12 sẽ không được tính — <code>n_missing</code> vì thế là con số thận trọng (xem review).</p>

=== 101-104
<p><code>last</code> là mốc cuối cùng trong <code>others</code> (ở đây 2026-06-16), index theo id. <code>reindex(sorted(missing))</code> lấy đúng các căn vắng; vì <code>missing ⊆ common</code> nên chắc chắn chúng có mặt ở <code>last</code>. Lấy <code>minimum_nights</code> và <code>availability_365</code> của các căn đó.</p>

=== 105-107
<p><code>explained</code> = (đòi &gt; <code>gap_explain_min_nights</code> đêm) HOẶC (kín lịch, avail <code>&lt;= blocked_max</code>). Đây là heuristic "căn này sẽ bị bộ lọc của mốc gap loại". Số thật: <code>n_missing = 4.645</code>, <code>n_explained = 3.569</code> (76,84%), <code>n_unexplained = 1.076</code>. Tách ra: 2.918 căn chỉ do &gt; 7 đêm, 1.242 căn chỉ do kín lịch, 591 căn thoả cả hai (mình tự tính lại từ <code>data/raw</code>).</p>

=== 109-112
<p>Ghi ba bộ đếm vào audit rồi trả. <code>n_unexplained = n_missing − n_explained</code> là phần chưa giải thích được — với Sydney là 1.076 căn, con số đáng nêu khi bị hỏi "vì sao tháng 3 thiếu căn".</p>

--- flow
## Bảng rộng
fn 0 22 | track | id × mốc, vắng = VANG
## Ma trận đổi nhóm
fn 0 33 | transition_matrix | from/to/n/share, chuẩn hoá hàng
st 1 40 | Guard | thiếu mốc → bảng rỗng
st 1 44 | Ghép theo id | đích reindex theo nguồn, thiếu = BIEN_MAT
st 1 50 | Crosstab 7×8 | luôn đủ hàng/cột
st 1 56 | Chia theo hàng | share = n / tổng from_segment
## Audit mốc gap
fn 0 61 | gap_audit | đếm căn vắng + giải thích
st 1 68 | Thống kê mỗi mốc | n, max minimum_nights, share_blocked
st 1 96 | Căn chung | có mặt ở mọi mốc thường
st 1 105 | Giải thích | &gt;7 đêm hoặc kín lịch
chips 1 | seg_rules:18 SEGMENTS ; seg_report:120 track

--- review
ok | Số liệu tái lập được | Chạy lại <code>gap_audit</code> trên 4 mốc scope full ra đúng 4.645 / 3.569 / 1.076 và <code>per_snapshot</code> khớp CSV đã commit.
ok | BIEN_MAT + chuẩn hoá hàng | Tách hẳn cột <code>BIEN_MAT</code> và chia theo tổng hàng nên so được nhóm lớn/nhỏ; nhóm nguồn rỗng được chặn chia cho 0.
mid | Giả định mốc cuối là mốc thường | <code>others[-1]</code> lấy mốc cuối sau khi bỏ gap. Nếu <code>gap_snapshot</code> lại là mốc cuối cùng thì "mốc cuối" thành mốc trước nó; hiện gap ở giữa nên đúng, nhưng đổi cấu hình dễ sai âm thầm.
mid | n_missing là con số thận trọng | Chỉ đếm căn có mặt ở <b>mọi</b> mốc thường, nên căn thiếu ở một mốc thường trung gian bị loại khỏi tử số. Đúng ý đồ (comment dòng 95) nhưng cần nói rõ khi giải thích 4.645.
low | share làm tròn rời rạc | <code>round(4)</code> từng ô nên tổng share mỗi hàng có thể lệch 1 đơn vị ở chữ số cuối, không còn đúng bằng 1.
low | Hai tên cho một hiện tượng | <code>track</code> dùng <code>VANG</code>, ma trận dùng <code>BIEN_MAT</code>. Cùng nghĩa "vắng mặt" nhưng khác chuỗi; dễ gây nhầm khi đối chiếu hai bảng.

--- qa
? VANG và BIEN_MAT khác nhau không?
<p>Không, cùng nghĩa "không có mặt ở mốc". <code>track</code> dùng nhãn <code>VANG</code> trong bảng rộng; <code>transition_matrix</code> dùng hằng <code>GONE = "BIEN_MAT"</code> cho cột đích. Chỉ là hai tên cho cùng hiện tượng.</p>
? Vì sao share phải chuẩn hoá theo hàng?
<p>Để so sánh giữa các nhóm có quy mô khác nhau. <code>D_dormant</code> nhỏ hơn <code>H_healthy</code> rất nhiều, nên đếm tuyệt đối không so được. Chia theo tổng hàng cho ra tỉ lệ ở lại / rời đi trong cùng nhóm nguồn. Ví dụ <code>D_dormant</code> ở lại 0,6544 (09/2025→06/2026).</p>
? n_explained tính bằng ngưỡng nào và vì sao?
<p>Là căn ở mốc cuối đòi <b>&gt; 7 đêm</b> (<code>gap_explain_min_nights</code>) hoặc kín lịch. Mốc gap 2026-03-21 có <code>max_minimum_nights = 7</code>, tức bị lọc theo <code>minimum_nights &lt;= 7</code>, nên căn đòi &gt; 7 đêm hẳn bị loại. Kết quả: 3.569/4.645 giải thích được.</p>
? Vì sao tháng 3 thiếu 4.645 căn mà còn 1.076 chưa giải thích được?
<p>4.645 là số căn có mặt ở mọi mốc thường nhưng vắng ở mốc gap. Trong đó 3.569 thoả "&gt; 7 đêm hoặc kín lịch" nên quy được cho bộ lọc; 1.076 còn lại không thoả điều kiện nào, tức chưa rõ nguyên nhân — đúng phần <code>n_unexplained</code>.</p>
