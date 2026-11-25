--- meta
title: __init__.py
lead: Cửa vào của bước 3. Hàm <code>run</code> nạp listing của cả 4 mốc, gán nhóm cho từng mốc, dựng ma trận đổi nhóm, kiểm mốc gap, rồi giao <code>report</code> ghi CSV. Package gồm 4 module: <code>load</code> (đọc), <code>rules</code> (luật 7 nhóm), <code>transitions</code> (đổi nhóm + gap), <code>report</code> (xuất). File này chỉ nối chúng lại, không chứa luật.

--- blocks
=== 1-17
<p>Docstring nói rõ vai trò và hợp đồng của package, đọc là đủ để trả lời "bước 3 làm gì":</p>
<ul><li><b>Vị trí:</b> sau QA, trước LLM. <a href="#run_pipeline-L153">run_pipeline dòng 153</a> gọi <code>segments.run(config, scope=args.segments_scope)</code>; kết quả được bước 4b và 5b dùng lại.</li>
<li><b>Bốn module một việc:</b> <code>load.py</code> đọc + cột dẫn xuất; <code>rules.py</code> giữ luật và hằng số (chỉ file này biết luật); <code>transitions.py</code> bảng theo dõi, ma trận, gap; <code>report.py</code> ghi CSV và in tóm tắt.</li>
<li><b>Đầu vào:</b> <code>config["snapshots"]</code>, <code>config["segments"]</code>, và listing từng mốc. Scope <code>full</code> đọc <code>data/raw/&lt;city&gt;/&lt;mốc&gt;/listings.csv.gz</code>, scope <code>sample</code> đọc <code>data/processed/&lt;city&gt;/&lt;mốc&gt;/listings.csv</code> (xem <a href="#seg_load-L37">seg_load._path</a>).</li>
<li><b>Đầu ra:</b> các file <code>segments_*.csv</code> trong <code>config["segments"]["output_dir"]</code>, cộng một dict kết quả trong RAM cho bước sau.</li></ul>

=== 19
<p><code>from __future__ import annotations</code> để các chú thích kiểu như <code>dict[str, Any]</code>, <code>str | None</code> được lưu dạng chuỗi, chạy được cả trên Python 3.10 mà CI kiểm.</p>

=== 21
<p><code>Any</code> chỉ dùng trong chú thích: config là dict lồng nhau tự do, không có schema cố định nên không thể gõ kiểu chặt hơn.</p>

=== 23-26
<p>Bốn import nối bốn module con. Chú ý dòng 25 import cả <code>cfg_get</code> và <code>seen_before_ids</code>: hai hàm này không nằm trong <code>__all__</code> nhưng vẫn trở thành thuộc tính của package, nên chỗ khác gọi được <code>segments.cfg_get(...)</code> — đúng như <a href="#run_pipeline-L169">run_pipeline dòng 169</a> làm để lấy <code>output_dir</code>.</p>

=== 28
<p><code>__all__</code> khai báo API công khai: <code>PHANTOM</code>, <code>SEGMENTS</code>, <code>classify</code>, <code>run</code>. Đây là những thứ module ngoài nên dùng; <code>cfg_get</code>/<code>seen_before_ids</code> vẫn gọi được nhưng coi là nội bộ.</p>

=== 31-38
<p>Hàm điều phối duy nhất. Nhận <code>config</code> đã chuẩn hoá và <code>scope</code> tuỳ chọn (CLI <code>--segments-scope</code> truyền vào). Trả dict gồm <code>scope</code>, <code>track</code> (bảng rộng), <code>transitions</code>, <code>audit</code>, <code>paths</code> (danh sách file đã ghi).</p>
<p>Docstring nói "scope mặc định ... không có thì <code>sample</code>". Thực tế dòng 39 chỉ lùi về <code>sample</code> khi giá trị <em>rỗng</em>; nếu thiếu hẳn khoá <code>segments.scope</code> thì <code>cfg_get</code> ném <code>KeyError</code> (đã chạy thử). Xem mục <a href="#seg_init-L39">dòng 39</a> và phần review.</p>

=== 39-40
<p><code>scope = scope or str(cfg_get(config, "scope") or "sample")</code>: ưu tiên tham số CLI, không có thì đọc <code>segments.scope</code> trong yaml (hiện là <code>full</code>), và chỉ khi giá trị đó rỗng mới thành <code>"sample"</code>. <code>snapshots</code> lấy từ <code>config["snapshots"]</code>, <code>or []</code> phòng khi thiếu.</p>

=== 42
<p>Dict comprehension nạp <b>tất cả</b> mốc trước, khoá là tên mốc. Scope full nạp khoảng 20.573 dòng mỗi mốc ở mốc cuối; scope sample là 1.000. Giữ cả 4 DataFrame trong RAM vì bước sau cần so chéo giữa các mốc.</p>

=== 43-46
<p>Vòng lặp gán nhóm cho từng mốc. Điểm cốt lõi nằm ở comment dòng 44: <code>seen_before</code> phải tính trên các mốc <b>cũ hơn</b>, nên phải nạp hết (dòng 42) rồi mới chia nhóm. <code>seen_before_ids</code> trả tập id đã thấy ở mốc cách ít nhất <code>never_seen_days</code> (150) ngày, hoặc <code>None</code> nếu chưa có mốc đủ cũ. <code>classify</code> dùng tập đó để tách <code>D_never</code> khỏi <code>N_new</code>.</p>
<p>Hệ quả số thật: hai mốc 2025 (<a href="#seg_rules-L102">cutoff</a> 2025-04-15 và 2025-07-15) không có mốc nào đủ cũ nên <code>seen_before=None</code>, mọi căn 0 review thành <code>N_new</code>, <code>D_never = 0</code>. Mốc 2026-06-16 có <code>D_never = 1.528</code>.</p>

=== 48-52
<p>Dựng ma trận đổi nhóm cho mỗi cặp <code>[từ, đến]</code> trong <code>config["segments"]["transitions"]</code> (hiện có hai cặp: 09/2025→06/2026 và 12/2025→06/2026). Điều kiện <code>if src in segmented and dst in segmented</code> khiến cặp trỏ tới mốc không được nạp bị <b>bỏ im lặng</b> — test <code>test_run_end_to_end</code> cố tình thêm cặp <code>[2025-09-12, 2020-01-01]</code> và kiểm nó biến mất.</p>

=== 54-58
<p><code>gap_snapshot</code> là tuỳ chọn (yaml đặt <code>2026-03-21</code>); không có thì <code>gap_audit</code> trả các bộ đếm bằng 0. <code>write_outputs</code> ghi toàn bộ CSV, rồi <code>summary_lines</code> in vài dòng ra console. Đọc trực tiếp <code>config["segments"].get(...)</code> ở đây an toàn vì dòng 39 đã chứng minh mục <code>segments</code> tồn tại (nếu thiếu, <code>cfg_get</code> đã ném lỗi trước).</p>

=== 60-66
<p>Trả kết quả trong RAM cho các bước sau. <code>track(segmented)</code> ở dòng 62 tính lại bảng rộng — <code>write_outputs</code> cũng đã tính nó để ghi <code>segments_track_*.csv</code>, nên bảng rộng bị dựng hai lần. Không sai, chỉ tốn công; xem review.</p>

--- flow
## Nạp và chia nhóm
fn 0 31 | run | Chạy cả bước 3, trả dict kết quả
st 1 42 | Nạp mọi mốc | load_listings cho từng snapshot
st 1 43 | Gán nhóm | seen_before_ids + classify từng mốc
## Đổi nhóm và audit
st 1 50 | Ma trận đổi nhóm | mỗi cặp mốc trong yaml
st 1 55 | Kiểm mốc gap | gap_audit (tuỳ chọn)
## Ghi và trả kết quả
st 1 56 | Ghi CSV + in tóm tắt | write_outputs rồi summary_lines
st 1 62 | Bảng rộng theo căn | track(segmented)
chips 1 | seg_load:45 load_listings ; seg_rules:50 classify ; seg_transitions:33 transition_matrix ; seg_transitions:61 gap_audit ; seg_report:79 write_outputs

--- review
mid | Docstring scope lệch code | Docstring <code>run</code> nói thiếu scope thì mặc định <code>sample</code>, nhưng thiếu khoá <code>segments.scope</code> thì <code>cfg_get</code> ném <code>KeyError</code>; chỉ giá trị rỗng mới lùi về <code>sample</code> (đã chạy thử).
low | track dựng hai lần | <code>write_outputs</code> tính <code>track(segmented)</code> để ghi CSV, rồi <code>run</code> tính lại ở dòng 62 để trả về. Có thể truyền bảng đã tính.
ok | Chia nhóm sau khi nạp đủ | <code>seen_before_ids</code> được tính trên toàn bộ mốc trước khi <code>classify</code>, đúng yêu cầu tách <code>D_never</code>/<code>N_new</code>; comment dòng 44 ghi rõ lý do.

--- qa
? Vì sao phải nạp hết 4 mốc rồi mới chia nhóm?
<p>Vì <code>D_never</code> cần biết id đã xuất hiện ở mốc cũ hơn ít nhất 150 ngày chưa (<code>seen_before_ids</code>). Nếu chia ngay khi nạp từng mốc thì chưa có mốc cũ để so. Vòng lặp ở dòng 43 làm đúng thứ tự: nạp hết (dòng 42) rồi mới <code>classify</code>.</p>
? Mốc 2025-09-12 có bao nhiêu căn D_never và vì sao?
<p>Bằng 0. Cutoff = 2025-09-12 − 150 ngày = 2025-04-15; không có mốc nào ≤ ngày đó nên <code>seen_before_ids</code> trả <code>None</code>, mọi căn 0 review thành <code>N_new</code>. Mốc 2025-12-12 cũng vậy. Mốc 2026-06-16 mới có <code>D_never = 1.528</code>.</p>
? Nếu yaml khai một cặp transitions tới mốc không tồn tại thì sao?
<p>Bị bỏ qua im lặng: dòng 51 kiểm <code>src in segmented and dst in segmented</code>, không khớp thì không tạo ma trận. Test <code>test_run_end_to_end</code> thêm cặp <code>[2025-09-12, 2020-01-01]</code> và kiểm kết quả chỉ còn cặp hợp lệ.</p>
? scope mặc định là gì khi chạy pipeline?
<p>Lấy <code>config["segments"]["scope"]</code> trong yaml, hiện là <code>full</code> (toàn bộ ~20.573 căn). Muốn chạy nhanh trên 1.000 căn thì truyền <code>--segments-scope sample</code>; khi đó bước 5b/6b bị bỏ vì cần scope full.</p>
