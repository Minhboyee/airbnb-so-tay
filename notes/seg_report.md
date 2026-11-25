--- meta
title: segments/report.py
lead: Bước cuối của package: ghi kết quả phân nhóm ra CSV và in tóm tắt. Năm bảng: đếm theo nhóm (<code>segments_counts</code>), ma trận đổi nhóm (<code>segments_transitions</code>), audit mốc gap (<code>segments_gap_audit</code> + <code>segments_gap_summary</code>), bảng từng listing (<code>segments_&lt;scope&gt;.csv</code>) và bảng rộng theo căn (<code>segments_track</code>). Ghi bằng <code>utf-8-sig</code> để Excel đọc đúng tiếng Việt.

--- blocks
=== 1-10
<p>Docstring liệt kê đúng các file đầu ra, kèm quy ước vị trí: bốn bảng tổng hợp để ngay <code>output_dir</code> (mặc định <code>data/processed</code>), còn bảng theo listing và bảng rộng để trong <code>&lt;output_dir&gt;/&lt;city&gt;/</code> (đã gitignore vì rất lớn). Đây là bảng đối chiếu khi bị hỏi "bước 3 sinh ra file nào".</p>

=== 12
<p><code>from __future__ import annotations</code> cho cú pháp kiểu hiện đại trên Python 3.10.</p>

=== 14-15
<p><code>Path</code> để ghép đường dẫn, <code>Any</code> cho config và audit dict.</p>

=== 17
<p><code>pandas</code> để dựng bảng và ghi CSV.</p>

=== 19-20
<p>Import hằng số/nhãn từ <code>rules</code> (<code>PHANTOM</code>, <code>SEGMENT_LABELS_VI</code>, <code>SEGMENTS</code>, <code>cfg_get</code>) và <code>track</code> từ <code>transitions</code> để ghi bảng rộng.</p>

=== 23-25
<p><code>_out_dir</code> lấy <code>segments.output_dir</code> qua <code>cfg_get</code> (yaml đặt <code>data/processed</code>), bọc <code>Path</code>. Thiếu khoá thì <code>cfg_get</code> đã báo lỗi rõ; không có giá trị mặc định trong code.</p>

=== 28-33
<p><code>_write</code> tạo thư mục cha (<code>mkdir(parents=True, exist_ok=True)</code>) rồi ghi CSV với <code>index=False</code>. Comment dòng 30 nói lý do <code>encoding="utf-8-sig"</code>: thêm BOM để Excel mở đúng tiếng Việt (nếu không, chữ có dấu bị lỗi font). Trả lại đường dẫn đã ghi để <code>write_outputs</code> gom vào danh sách <code>paths</code>.</p>

=== 36-37
<p><code>_counts</code> dựng bảng dài: mỗi cặp (mốc, nhóm) một dòng. Docstring nói rõ có <code>n</code>, <code>share</code> và cờ <code>is_phantom</code>.</p>

=== 38-41
<p><code>rows</code> gom dòng; với mỗi mốc, <code>value_counts()</code> đếm số căn mỗi nhóm rồi <code>reindex(SEGMENTS, fill_value=0)</code> để nhóm vắng mặt vẫn có dòng 0. <code>total = int(vc.sum()) or 1</code>: <code>or 1</code> chặn chia cho 0 khi mốc rỗng (comment dòng 41).</p>

=== 42-52
<p>Với từng nhóm, thêm một dòng gồm <code>snapshot</code>, <code>segment</code>, nhãn tiếng Việt, <code>n</code>, <code>share = n / total</code> (làm tròn 4 chữ số) và <code>is_phantom</code> (nhóm có trong <code>PHANTOM</code>). Mỗi mốc đúng 7 dòng, nên 4 mốc cho 28 dòng — khớp file <code>segments_counts_full.csv</code>. Tổng share mỗi mốc bằng 1 (test <code>test_write_outputs_writes_every_table</code> kiểm <code>round(4)</code>).</p>

=== 53
<p>Trả DataFrame. Nếu không có mốc nào, <code>rows=[]</code> nên DataFrame rỗng không cột — file CSV ghi ra sẽ trắng (chỉ là ca biên, test chỉ kiểm file tồn tại).</p>

=== 56-57
<p><code>_listings</code> gộp các mốc thành một bảng dài theo listing, để tra một căn cụ thể.</p>

=== 58-70
<p>Danh sách cột giữ lại: khoá <code>id</code>, <code>segment</code>, vài cột mô tả (<code>neighbourhood_cleansed</code>, <code>room_type</code>, <code>minimum_nights</code>, <code>stay_type</code>) cùng các cột số dùng cho luật. Đây là khối dữ liệu thuần nên dài là bình thường.</p>

=== 71-75
<p>Với mỗi mốc, chỉ lấy các cột <code>keep</code> thực có (phòng khi thiếu cột), rồi <code>insert(1, "snapshot", snap)</code> chèn cột mốc ngay sau <code>id</code>. Cuối cùng <code>concat</code> tất cả; nếu không có mốc nào thì trả DataFrame rỗng đúng cột để chỗ đọc không lỗi.</p>

=== 78-85
<p>Hàm xuất chính. Nhận <code>segmented</code>, <code>transitions</code>, <code>audit</code>, <code>config</code>, <code>scope</code>; trả danh sách <code>Path</code> đã ghi. Docstring ghi "4 loại output" nhưng thực tế ghi <b>6 file</b> (vì audit tách audit + summary, listing tách segments + track); xem <a href="#seg_report-L86">các dòng dưới</a>.</p>

=== 86-87
<p><code>out</code> là thư mục gốc. Ghi bảng đếm nhóm đầu tiên: <code>segments_counts_&lt;scope&gt;.csv</code>. Đây là file dùng cho bảng 7 nhóm trong báo cáo (mốc 2026-06-16: B_ghost 918, B_booked 1.159, D_dormant 1.913, D_never 1.528, N_new 1.525, L_low 1.623, H_healthy 11.907).</p>

=== 89-92
<p>Gom các ma trận chuyển thành một bảng dài: mỗi cặp mốc thêm hai cột <code>src</code>/<code>dst</code> rồi chọn sáu cột cố định. Danh sách rỗng nếu config không khai cặp transitions nào.</p>

=== 93-100
<p>Ghi <code>segments_transitions_&lt;scope&gt;.csv</code>. Nếu không có cặp nào, ghi DataFrame rỗng <b>đúng tên cột</b> thay vì lỗi — test <code>test_write_outputs_handles_no_transitions</code> kiểm file rỗng đọc lại được. Khi có dữ liệu, file chứa cả hai cặp (09/2025→06/2026 và 12/2025→06/2026) với 56 dòng mỗi cặp (7×8).</p>

=== 102
<p>Ghi thống kê từng mốc ra <code>segments_gap_audit_&lt;scope&gt;.csv</code> (<code>audit["per_snapshot"]</code> luôn có, kể cả khi không có gap).</p>

=== 103-112
<p>Dựng bảng tóm tắt một dòng từ các bộ đếm gap: <code>gap_snapshot</code>, <code>n_missing</code>, <code>n_explained</code>, <code>n_unexplained</code>. Dùng <code>audit.get("gap_snapshot")</code> để chịu được <code>None</code>.</p>

=== 113
<p>Ghi bảng tóm tắt ra <code>segments_gap_summary_&lt;scope&gt;.csv</code>. Với Sydney: <code>2026-03-21, 4645, 3569, 1076</code>.</p>

=== 115-117
<p>Bảng theo listing rất lớn nên để trong <code>&lt;output_dir&gt;/&lt;city&gt;/segments_&lt;scope&gt;.csv</code> (comment dòng 115 nhắc thư mục này đã gitignore). Đường dẫn lấy <code>config["city"]</code> trực tiếp vì đây là tên thư mục, không phải tham số <code>segments</code>.</p>

=== 119-121
<p>Bảng rộng theo căn: gọi <code>track(segmented)</code> rồi <code>reset_index()</code> để <code>id</code> thành cột, ghi ra <code>segments_track_&lt;scope&gt;.csv</code>. Đây là bảng để nhìn một căn đổi nhóm qua 4 mốc.</p>

=== 122
<p>Trả toàn bộ đường dẫn đã ghi. <code>run_pipeline</code> dùng độ dài danh sách này để in "đã ghi N bảng" (<a href="#run_pipeline-L154">dòng 154</a>).</p>

=== 125-130
<p><code>summary_lines</code> trả vài dòng in ra console: tỉ lệ nhóm ảo, tỉ lệ <code>D_dormant</code> ở lại, và số căn vắng ở mốc gap.</p>

=== 131
<p>Dòng tiêu đề cố định. Test <code>test_summary_lines_reports_phantom_share_stay_rate_and_gap</code> kiểm đúng chuỗi này và số dòng khi không có transition (4 dòng: tiêu đề + 2 mốc + gap).</p>

=== 132-134
<p>Với mỗi mốc, tính <code>share = df["segment"].isin(PHANTOM).mean()</code> — tỉ lệ căn thuộc 3 nhóm ảo — rồi in kèm số căn. Mốc 2026-06-16: 4.359/20.573 = <b>21,2%</b>, khớp cột <code>is_phantom</code> trong CSV.</p>

=== 136-139
<p>Với mỗi cặp mốc, lọc ô <code>D_dormant → D_dormant</code> trong ma trận và in <code>share</code>; nếu không có dòng (ma trận rỗng) thì <code>pct = 0.0</code> nhờ <code>if len(stay) else 0.0</code>. Số thật: 65,44% (09/2025→06/2026), 67,12% (12/2025→06/2026).</p>

=== 141-144
<p>Dòng cuối về mốc gap: vắng bao nhiêu, giải thích được bao nhiêu, còn bao nhiêu chưa rõ. Dùng <code>audit.get("gap_snapshot")</code> để in <code>None</code> gọn khi không có gap.</p>

=== 145
<p>Trả danh sách dòng để <a href="#seg_init-L57">seg_init dòng 57</a> in từng dòng.</p>

--- flow
## Hàm ghi
fn 0 23 | _out_dir | segments.output_dir
fn 0 28 | _write | CSV utf-8-sig, tạo thư mục
fn 0 36 | _counts | n + share + is_phantom mỗi (mốc, nhóm)
fn 0 56 | _listings | gộp mốc, chèn cột snapshot
## Xuất 6 file
fn 0 78 | write_outputs | ghi CSV, trả list Path
st 1 86 | Đếm nhóm | segments_counts_&lt;scope&gt;
st 1 89 | Ma trận chuyển | segments_transitions_&lt;scope&gt;
st 1 102 | Audit gap | gap_audit + gap_summary
st 1 115 | Theo listing | segments_&lt;scope&gt; + segments_track
## In tóm tắt
fn 0 125 | summary_lines | phantom, D_dormant ở lại, gap
chips 1 | seg_rules:18 SEGMENTS ; seg_transitions:22 track ; seg_init:56 write_outputs

--- review
ok | Đủ bảng + chống rỗng | Ghi đủ 6 file, mỗi bảng có guard cho trường hợp rỗng (transitions rỗng vẫn đúng cột; audit luôn có per_snapshot). <code>utf-8-sig</code> xử lý tiếng Việt cho Excel.
low | track dựng hai lần | <code>write_outputs</code> gọi <code>track(segmented)</code> ở dòng 121, rồi <code>segments.run</code> gọi lại để trả về. Cùng một bảng bị tính hai lần.
low | _counts rỗng mất header | Khi <code>segmented</code> rỗng, <code>pd.DataFrame([])</code> không có cột nên CSV ghi ra trắng, không có dòng tiêu đề. Chỉ là ca biên; test chỉ kiểm file tồn tại.
mid | insert vị trí cố định | <code>part.insert(1, "snapshot", snap)</code> giả định <code>id</code> luôn ở cột 0. Đúng với thứ tự <code>keep</code> và <code>load.py</code>, nhưng nếu <code>id</code> thiếu thì cột mốc chèn sai chỗ.

--- qa
? Bước 3 ghi ra những file nào, ở đâu?
<p>Bốn bảng tổng hợp ở <code>output_dir</code> (mặc định <code>data/processed</code>): <code>segments_counts_&lt;scope&gt;</code>, <code>segments_transitions_&lt;scope&gt;</code>, <code>segments_gap_audit_&lt;scope&gt;</code>, <code>segments_gap_summary_&lt;scope&gt;</code>. Hai bảng lớn ở <code>output_dir/&lt;city&gt;/</code>: <code>segments_&lt;scope&gt;</code> và <code>segments_track_&lt;scope&gt;</code>.</p>
? Vì sao ghi CSV bằng utf-8-sig?
<p>Vì <code>utf-8-sig</code> thêm BOM ở đầu file, giúp Excel nhận đúng bảng mã và hiện tiếng Việt có dấu thay vì lỗi font. Ghi <code>utf-8</code> thường thì mở bằng Excel hay bị méo chữ.</p>
? total = int(vc.sum()) or 1 để làm gì?
<p>Chặn chia cho 0 khi một mốc rỗng: nếu tổng số căn bằng 0, <code>or 1</code> đổi mẫu số thành 1 để <code>share = 0/1 = 0</code> thay vì lỗi. Mốc bình thường thì tổng dương nên dùng tổng thật.</p>
? Dòng tóm tắt in ra những gì?
<p>Tiêu đề, mỗi mốc một dòng kèm tỉ lệ nhóm ảo (mốc cuối 21,2%), mỗi cặp mốc một dòng tỉ lệ <code>D_dormant</code> ở lại (65,44% và 67,12%), và một dòng mốc gap: vắng 4.645, giải thích được 3.569, không giải thích được 1.076.</p>
