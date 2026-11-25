--- meta
title: segments/rules.py
lead: Trái tim của bước 3: định nghĩa 7 nhóm và luật gán nhóm. Luật là một <em>decision list</em> — xét theo thứ tự, khớp điều kiện đầu tiên thì thắng, nên thứ tự điều kiện chính là thứ tự ưu tiên bằng chứng: kín lịch mạnh nhất, rồi tới lịch sử review, cuối cùng là mức độ mở lịch. File cũng có <code>seen_before_ids</code> để tách <code>D_never</code> khỏi <code>N_new</code>.

--- blocks
=== 1-8
<p>Docstring nêu lý do tách file: luật nằm một chỗ, sửa ngưỡng hay thứ tự xét chỉ phải sửa ở đây. Vào là DataFrame đã nạp (<code>load.py</code>) và ngưỡng trong <code>config["segments"]</code>; ra là cột <code>segment</code> trong RAM, không ghi file.</p>

=== 10
<p><code>from __future__ import annotations</code> cho cú pháp kiểu hiện đại chạy trên Python 3.10.</p>

=== 12
<p><code>Any</code> cho config và giá trị trả về của <code>cfg_get</code>.</p>

=== 14-15
<p><code>numpy</code> để dựng Series mặc định và <code>np.select</code>; <code>pandas</code> cho xử lý cột.</p>

=== 17-18
<p><code>SEGMENTS</code> là thứ tự cố định 7 nhóm, dùng cho báo cáo và để <code>np.select</code> lấy 6 nhãn đầu (nhóm 7 là mặc định). Thứ tự này cũng là thứ tự dòng trong file <code>segments_counts_*.csv</code> và ma trận chuyển nhóm.</p>

=== 20-29
<p>Nhãn tiếng Việt của 7 nhóm để bảng kết quả dễ đọc. Khoá phải khớp đúng tên trong <code>SEGMENTS</code>; <code>report._counts</code> tra thẳng <code>SEGMENT_LABELS_VI[seg]</code> nên thiếu khoá sẽ <code>KeyError</code>.</p>

=== 31-32
<p><code>PHANTOM</code> gom 3 nhóm "ảo": <code>B_ghost</code>, <code>D_dormant</code>, <code>D_never</code> — listing còn trên sàn nhưng thực tế không phục vụ khách. Đây là định nghĩa dùng cho cột <code>is_phantom</code> và dòng tóm tắt. Số thật ở mốc 2026-06-16: (918 + 1.913 + 1.528) / 20.573 = 4.359 / 20.573 = <b>21,2%</b> (file <code>segments_counts_full.csv</code>).</p>

=== 35-40
<p><code>cfg_get</code> đọc <code>config["segments"][key]</code>. Bắt <code>KeyError</code> rồi ném lại thông báo rõ "Config thiếu khoá <code>segments.&lt;key&gt;</code>", kèm <code>from None</code> để không lộ chuỗi lỗi gốc. Nhờ đây mọi chỗ gọi đều báo lỗi dễ hiểu thay vì <code>KeyError: 'scope'</code> trần. Test <code>test_cfg_get_reads_yaml_and_names_missing_key</code> kiểm cả trường hợp <code>config</code> không có mục <code>segments</code>.</p>

=== 43-47
<p><code>_col</code> lấy một cột dạng số, xử lý hai tình huống: cột không tồn tại → trả Series toàn <code>0.0</code> cùng index (để luật không lỗi); cột có nhưng có NaN/hỏng → <code>to_numeric(errors="coerce").fillna(0)</code>. Hệ quả cần nhớ: <b>NaN bị coi là 0</b>, nên <code>availability_365</code> thiếu thành 0 (kín lịch) và <code>number_of_reviews</code> thiếu thành 0. Với dữ liệu thật các cột này luôn có, nhưng đây là mặc định âm thầm. (Docstring ghi "trả chuỗi 0" — thực ra trả Series số; xem review.)</p>

=== 50-65
<p>Docstring của <code>classify</code> chính là bảng luật cần thuộc, xét theo thứ tự:</p>
<ol><li><code>B_ghost</code>: kín lịch (avail <code>&lt;= 0</code>) và không review gần đây.</li>
<li><code>B_booked</code>: kín lịch và có review gần đây.</li>
<li><code>D_dormant</code>: có review nhưng lần cuối cũ hơn 365 ngày.</li>
<li><code>D_never</code>: 0 review và id đã xuất hiện ở mốc ≥ 150 ngày trước.</li>
<li><code>N_new</code>: 0 review, chưa đủ cũ để kết luận.</li>
<li><code>L_low</code>: mở nhiều (avail <code>&gt;= 180</code>) và có 1–3 review 12 tháng.</li>
<li><code>H_healthy</code>: phần còn lại.</li></ol>
<p>Câu chốt cuối docstring: "có review trong cửa sổ" = <code>days_since_review &lt;= recent_review_days</code>, với NaN → False.</p>

=== 66-69
<p>Đọc 4 ngưỡng từ config (yaml hiện tại): <code>recent_review_days = 365</code>, <code>blocked_max_availability = 0</code>, <code>low_open_days = 180</code>, <code>low_reviews_ltm_max = 3</code>. Không có giá trị mặc định trong code — thiếu khoá là <code>KeyError</code> qua <code>cfg_get</code>.</p>

=== 71-74
<p>Lấy các cột số qua <code>_col</code>. Riêng <code>days</code> dùng <code>df.get("days_since_review", pd.Series(np.nan, ...))</code>: nếu bảng không có cột này (file cũ), dùng Series toàn NaN để mọi căn thành "không review gần đây" mà không lỗi — test <code>test_classify_without_days_since_review_column...</code> kiểm đúng vậy.</p>

=== 76-81
<p>Ba tín hiệu, kèm comment quan trọng:</p>
<ul><li><code>has_recent = days &lt;= recent</code>. Với NaN, so sánh là False → căn chưa có review tự rơi vào nhánh "không có review".</li>
<li><code>blocked = avail &lt;= blocked_max</code> (kín lịch khi <code>availability_365 = 0</code>).</li>
<li><code>seen = df["id"].isin(seen_before)</code> nếu có tập, ngược lại Series False → không căn nào đủ điều kiện <code>D_never</code>.</li></ul>
<p>Comment dòng 77–78 khẳng định với <code>recent_review_days = 365</code> thì <code>has_recent</code> trùng khít <code>number_of_reviews_ltm &gt; 0</code>. Mình đã kiểm lại trên dữ liệu thật cả 4 mốc, cả scope full và sample: <b>0 chỗ lệch</b> (lần lượt 17.730 / 20.436 / 13.563 / 20.573 dòng).</p>

=== 83-91
<p>Sáu điều kiện, đúng thứ tự ưu tiên của 6 nhóm đầu trong <code>SEGMENTS</code>. <code>np.select</code> lấy điều kiện <b>đúng đầu tiên</b>, nên:</p>
<ul><li>Kín lịch thắng mọi thứ: căn avail = 0 và 0 review là <code>B_ghost</code>, không phải <code>D_never</code> (test <code>test_blocked_wins_over_zero_reviews_and_history</code>).</li>
<li>Điều kiện 3 dùng <code>~has_recent</code> chứ không phải <code>n_ltm == 0</code>; đó là lý do cần cửa sổ 365 ngày.</li>
<li>Điều kiện 4 (<code>D_never</code>) chỉ đúng khi <code>seen</code> True; nếu <code>seen_before</code> là None thì không bao giờ chạm.</li>
<li>Điều kiện 6 dùng <code>between(1, low_max)</code> — bao gồm cả hai đầu: 1 và 3 đều là <code>L_low</code>, 4 thì không (test <code>test_low_reviews_ltm_upper_bound</code>).</li></ul>

=== 92-93
<p><code>np.select(conditions, SEGMENTS[:-1], default="H_healthy")</code>: <code>SEGMENTS[:-1]</code> là 6 nhãn đầu, khớp 6 điều kiện; <code>H_healthy</code> là mặc định cho phần còn lại. Kết quả bọc lại thành <code>Series</code> cùng index, đặt tên <code>segment</code> để gán thẳng vào DataFrame. Ngưỡng biên đều bao gồm: <code>days = 365</code> là còn khách, <code>avail = 180</code> là mở nhiều (test <code>test_recent_review_window_boundary_is_inclusive</code>, <code>test_low_open_threshold_is_inclusive</code>).</p>

=== 96-101
<p><code>seen_before_ids</code> trả tập id đã thấy ở mốc cách <code>snapshot</code> <b>ít nhất</b> <code>never_seen_days</code> ngày. Docstring nói rõ: trả <code>None</code> khi không có mốc nào đủ cũ, vì lúc đó không phân biệt được <code>D_never</code> với <code>N_new</code> — mọi căn 0 review thành <code>N_new</code>.</p>

=== 102-104
<p><code>cutoff = snapshot − never_seen_days</code> (với 2026-06-16 và 150 ngày là 2026-01-17). <code>ids</code> gom id, <code>found</code> đánh dấu đã gặp mốc đủ cũ chưa.</p>

=== 105-108
<p>Duyệt mọi mốc; mốc có ngày <code>&lt;= cutoff</code> (tức cách ≥ 150 ngày) thì bật <code>found</code> và gom id. Vì <code>cutoff</code> luôn nhỏ hơn chính <code>snapshot</code>, mốc hiện tại không bao giờ tự tính vào. Test <code>test_seen_before_ids_uses_the_150_day_cutoff</code>: mốc đúng 150 ngày trước được tính, 149 ngày thì không.</p>

=== 109
<p>Trả tập id nếu có ít nhất một mốc đủ cũ, ngược lại <code>None</code>. Đây là lý do hai mốc 2025 có <code>D_never = 0</code>: cutoff 2025-04-15 và 2025-07-15 sớm hơn mọi mốc đã có, nên <code>found = False</code> → <code>None</code>.</p>

--- flow
## Hằng số và hàm phụ
fn 0 35 | cfg_get | segments.&lt;key&gt; hoặc KeyError
fn 0 43 | _col | Cột số, cột thiếu/NaN → 0
## Chia nhóm
fn 0 50 | classify | 6 điều kiện, khớp trước thắng
st 1 66 | Đọc ngưỡng | 365 / 0 / 180 / 3
st 1 71 | Lấy cột số | reviews, ltm, avail, days
st 1 79 | Ba tín hiệu | has_recent, blocked, seen
st 1 84 | Sáu luật | np.select → 7 nhóm
## Mốc cũ
fn 0 96 | seen_before_ids | id ở mốc ≥150 ngày trước
st 1 102 | Cutoff | snapshot − never_seen_days
chips 1 | seg_load:45 load_listings ; seg_init:43 run

--- review
mid | _col coi NaN là 0 | Cột <code>availability_365</code> thiếu bị điền 0 nên thành "kín lịch" (B_ghost), cột review thiếu thành 0. Dữ liệu thật luôn có các cột này, nhưng mặc định âm thầm dễ gây hiểu nhầm khi gặp file thiếu cột.
low | Docstring _col ghi sai kiểu | Docstring nói "trả chuỗi 0" nhưng hàm trả <code>pd.Series(0.0, ...)</code> — Series số, không phải chuỗi.
ok | Thứ tự ưu tiên hiện rõ | Sáu điều kiện viết theo đúng thứ tự ưu tiên và có comment giải thích; <code>np.select</code> lấy khớp đầu tiên nên "kín lịch thắng" là hệ quả trực tiếp, có test chứng minh.
ok | Đã kiểm has_recent ↔ ltm>0 | Kiểm trên 4 mốc, cả scope full và sample: 0 chỗ lệch, đúng như comment dòng 77–78.

--- qa
? Vì sao căn kín lịch mà 0 review lại là B_ghost chứ không phải D_never?
<p>Vì kín lịch là điều kiện số 1–2, đứng trước <code>D_never</code> (điều kiện 4). <code>np.select</code> lấy điều kiện đúng đầu tiên, nên bằng chứng mạnh nhất (kín lịch) thắng. Test <code>test_blocked_wins_over_zero_reviews_and_history</code> kiểm đúng ca này.</p>
? Vì sao hai mốc 2025 có D_never = 0?
<p><code>seen_before_ids</code> cần một mốc cách ≥ 150 ngày. Với mốc 2025-09-12, cutoff là 2025-04-15; với 2025-12-12, cutoff là 2025-07-15 — đều sớm hơn mọi mốc đã có nên trả <code>None</code>, mọi căn 0 review thành <code>N_new</code>. Mốc 2026-06-16 có cutoff 2026-01-17 nên mới có <code>D_never = 1.528</code>.</p>
? NaN ở days_since_review rơi vào nhánh nào?
<p><code>has_recent = days &lt;= 365</code>, mà <code>NaN &lt;= 365</code> là False, nên căn đó bị coi là "không review gần đây". Nếu đang kín lịch thì thành <code>B_ghost</code>; nếu có review cũ thì <code>D_dormant</code>; nếu 0 review thì <code>D_never</code> hoặc <code>N_new</code> tuỳ <code>seen</code>.</p>
? L_low khác H_healthy ở đâu?
<p><code>L_low</code> cần <code>availability_365 &gt;= 180</code> và <code>number_of_reviews_ltm</code> trong khoảng 1..3. Có 4 review 12 tháng hoặc avail &lt; 180 thì rơi xuống <code>H_healthy</code>. Test <code>test_low_reviews_ltm_upper_bound</code> và <code>test_low_open_threshold_is_inclusive</code> chốt hai biên.</p>
