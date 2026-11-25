--- meta
title: qa.py
lead: <code>qa.py</code> điều phối bước 2. <code>run_pipeline.py</code> gọi <code>qa.run</code> với dict <code>{mốc: {listings, reviews, calendar}}</code> đọc từ <code>data/processed/</code>. Mỗi mốc có ba việc: kiểm ràng buộc mẫu của đề (sai thì dừng, <code>qa_constraints.py</code>), gắn cờ từng dòng (<code>qa_rules.py</code>), tính KPI trước và sau lọc. Cuối cùng ghi <code>reports/qa_report.csv</code> (48 dòng luật + 12 dòng KPI) và trả lại các bảng đã gắn cờ. Không dòng nào bị xoá.

--- blocks
=== 1-12
<p>Docstring nói rõ phân công: file này không tự kiểm tra gì, chỉ điều phối hai module.</p>
<ul><li><code>qa_constraints.py</code> giữ "hợp đồng" số lượng với đề (1000 căn, 875/125…). Lệch là <b>dừng</b>.</li>
<li><code>qa_rules.py</code> kiểm luật theo từng dòng. Vi phạm thì gắn cờ, pipeline chạy tiếp.</li></ul>
<p>Đầu ra gồm hai thứ: bảng đã gắn cờ trả về cho bước sau, và file CSV báo cáo. Docstring khớp code.</p>

=== 14
<p>Chú thích kiểu lưu dạng chuỗi, để cú pháp <code>str | Path</code> chạy được trên Python 3.10.</p>

=== 16-19
<p>Import <code>Path</code> để tạo thư mục báo cáo, <code>Any</code> cho dict config tự do và <code>pandas</code> cho mọi bảng.</p>

=== 21-22
<p>Lấy ba thứ từ hai module con: hàm kiểm ràng buộc, hàm chạy luật và <code>parse_price</code>. <code>parse_price</code> dùng lại để KPI đọc giá giống hệt luật giá, khỏi phải viết hai bộ parse.</p>

=== 25-29
<p><code>compute_kpis</code> tính ba KPI cơ bản của bảng listings: số căn, giá trung bình, giá trung vị. Chỉ dùng cho báo cáo QA; KPI chính của bài nằm ở <a href="#f-kpi">kpi.py</a>.</p>

=== 30
<p>Số căn để kiểu <code>float</code> cho đồng bộ với hai KPI giá (cùng nằm trong cột <code>before</code>/<code>after</code> của CSV).</p>

=== 31-37
<p>Giá đọc qua <code>parse_price</code> ("$1,234.00" thành 1234.0, chữ rác thành NaN) rồi <code>dropna()</code>. Trung bình và trung vị chỉ tính trên các ô đọc được, <b>không nội suy</b> ô thiếu. Bảng không có cột <code>price</code> thì dùng Series rỗng.</p>

=== 38-43
<p>Series rỗng thì trả <code>NaN</code> để pandas khỏi cảnh báo. Vì vậy trong <code>reports/qa_report.csv</code> hai mốc đầu (2025-09-12, 2025-12-12) có <code>mean_price</code>, <code>median_price</code> = NaN: cột giá của hai mốc này trống 100%, không ô nào đọc được. Test: <code>test_compute_kpis_empty_and_no_price_return_nan</code>.</p>

=== 46-50
<p><code>kpi_before_after</code> đo "QA làm KPI thay đổi bao nhiêu" ở ba mức:</p>
<ol><li><code>before</code>: mọi dòng.</li>
<li><code>after</code>: bỏ dòng <code>qa_has_error</code> (lỗi, tính cả lỗi giá).</li>
<li><code>after_excl_warnings</code>: bỏ thêm dòng <code>qa_has_warning</code> (ngoại lệ IQR).</li></ol>

=== 51-54
<p>Lọc bằng <code>~cờ</code> trên bản đã gắn cờ. Thiếu cột cờ thì coi như không lọc (ba mức bằng nhau), không báo lỗi. Test: <code>test_kpi_before_after_without_qa_has_error_is_identity</code>.</p>
<p>Ở đây dùng <code>qa_has_error</code>, tức tính cả lỗi giá. KPI chính trong <a href="#kpi-L849">kpi.py</a> lại lọc bằng <code>qa_has_error_excl_price</code>. Hai chỗ khác cờ là có chủ ý: báo cáo QA nói về giá, còn KPI chính phần lớn là KPI phi giá.</p>

=== 55-57
<p>Tính ba bộ KPI. Số thật mốc cuối 2026-06-16 (<code>reports/qa_report.csv</code>):</p>
<table><tr><th></th><th>trước</th><th>bỏ lỗi</th><th>bỏ lỗi + cảnh báo</th></tr>
<tr><td>số căn</td><td>1.000</td><td>978</td><td>928</td></tr>
<tr><td>giá TB</td><td>490,01</td><td>464,16</td><td>370,56</td></tr>
<tr><td>trung vị</td><td>343,00</td><td>342,84</td><td>333,33</td></tr></table>
<p>Trung bình tụt mạnh, trung vị gần như đứng yên: đúng tính chất trung vị bền với ngoại lệ. Thử tính: 490,006929 × 980 − 464,163384 × 978 ≈ 26.255, tức hai căn giá &gt; 10.000 AUD bị bỏ có tổng khoảng 26.255 AUD/đêm.</p>

=== 58-72
<p>Trả ba dòng (mỗi KPI một dòng) với <code>section="kpi"</code>, kèm số dòng ở ba mức. 4 mốc × 3 KPI = 12 dòng KPI trong CSV.</p>

=== 75-96
<p>Các cột của CSV xếp theo thứ tự sau. Dòng luật và dòng KPI dùng chung bộ cột: dòng luật để trống các cột KPI và ngược lại. Ý nghĩa từng cột có trong <code>reports/data_dictionary.md</code>.</p>

=== 99-100
<p>Năm cột đếm cần ép về số nguyên, xem dòng 112.</p>

=== 103-107
<p><code>build_report</code> gộp nhật ký luật (từ <code>apply_rules</code>) và dòng KPI thành một bảng.</p>

=== 108
<p>Dòng luật được gắn thêm <code>section="rule"</code> ở đây, không ở <code>qa_rules.py</code>.</p>

=== 109-110
<p>Không có dòng nào thì vẫn trả bảng rỗng đúng cột, để file CSV luôn có tiêu đề. Test: <code>test_build_report_with_no_rows_has_report_columns</code>.</p>

=== 111
<p><code>reindex(columns=...)</code> vừa sắp cột đúng thứ tự, vừa thêm cột thiếu (điền NaN).</p>

=== 112-116
<p>Khi gộp dòng luật với dòng KPI, cột đếm có NaN nên pandas đổi sang float (1000.0). Ép về <code>Int64</code> (chữ I hoa, kiểu nguyên cho phép thiếu) để CSV ghi <code>1000</code> và ô trống vẫn trống.</p>

=== 119-124
<p>Ghi CSV, tự tạo thư mục cha. <code>index=False</code> để không có cột số thứ tự thừa.</p>

=== 127-134
<p><code>run</code> là hàm duy nhất <code>run_pipeline.py</code> gọi (<a href="#run_pipeline-L144">run_pipeline dòng 144</a>). Đầu vào là config đã chuẩn hoá và bảng của mọi mốc; đầu ra là dict cùng dạng nhưng bảng đã có cột <code>qa_*</code>.</p>

=== 135-140
<p>Chuẩn bị bốn thứ: mục <code>qa</code> của config, danh sách mốc dạng chuỗi, đường dẫn báo cáo (mặc định <code>reports/qa_report.csv</code>), và ba nơi gom kết quả.</p>

=== 141-143
<p><code>seen</code> giữ bảng listings và reviews của các mốc đã duyệt, để luật <code>cross_snapshot_duplicate</code> so mốc hiện tại với mốc trước. Calendar không đưa vào: lịch 365 ngày của các mốc chụp cách nhau 3 tháng chồng ngày lên nhau là chuyện bình thường.</p>

=== 144-145
<p>Duyệt mốc theo đúng thứ tự trong config (thứ tự thời gian). <code>idx</code> cần cho ràng buộc "số căn 0 review của mốc thứ idx" và "mốc cuối thiếu 20 giá".</p>

=== 146
<p>Kiểm ràng buộc mẫu trước khi gắn cờ. Sai là ném <code>QAConstraintError</code> ngay. Vì <code>write_report</code> chỉ chạy ở dòng 155 sau vòng lặp, khi dừng thì không ghi báo cáo mới nào (file cũ nếu có vẫn nằm đó). Nếu <code>qa.expected</code> đã bị bỏ (đổi mốc, mẫu theo seed) thì <code>expected</code> là <code>None</code> và hàm không làm gì.</p>

=== 147
<p>Ghép bảng của mọi mốc trước thành một bảng mỗi loại. Mốc đầu <code>seen</code> rỗng nên <code>previous = {}</code>, luật trùng giữa mốc tự bỏ qua. Ở mốc 4, reviews trước là 3 × 5.000 = 15.000 dòng.</p>

=== 148
<p>Gắn cờ mọi bảng của mốc, nhận lại bảng đã gắn cờ và nhật ký luật. Xem <a href="#qa_rules-L578">apply_rules</a>.</p>

=== 149-151
<p>Thêm bảng gốc (chưa có cột <code>qa_*</code>) của mốc này vào <code>seen</code> cho mốc sau.</p>

=== 152-154
<p>Lưu bảng đã gắn cờ, gom nhật ký luật và 3 dòng KPI của mốc.</p>

=== 155-156
<p>Ghi một file CSV cho cả 4 mốc rồi trả các bảng đã gắn cờ. Ở bản commit: 11 + 11 + 13 + 13 = 48 dòng luật (hai mốc đầu thiếu 2 luật giá) và 12 dòng KPI.</p>

--- flow
## Hàm phụ
fn 0 25 | compute_kpis | Số căn, giá TB, trung vị
fn 0 46 | kpi_before_after | KPI ở 3 mức lọc
fn 0 103 | build_report | Gộp luật + KPI, ép Int64
fn 0 119 | write_report | Ghi CSV
## Chạy QA (run_pipeline gọi)
fn 0 127 | run | Duyệt 4 mốc theo thứ tự
st 1 146 | Ràng buộc mẫu | Lệch số lượng đề thì dừng
chips 2 | qa_constraints:113 check_sample_constraints
st 1 147 | Bảng mốc trước | Cho luật trùng giữa mốc
st 1 148 | Gắn cờ | 7 cờ + 3 cờ tổng
chips 2 | qa_rules:578 apply_rules
st 1 149 | Lưu mốc vào seen | Bảng gốc, chưa có cờ
st 1 154 | KPI trước/sau | 3 dòng mỗi mốc
st 1 155 | Ghi báo cáo | reports/qa_report.csv
chips 1 | run_pipeline:144 main ; kpi:849 _filter_passed_qa

--- review
mid | Dừng giữa chừng thì không ghi báo cáo | <code>write_report</code> ở <a href="#qa-L155">dòng 155</a> chạy sau vòng lặp. Nếu mốc 3 vỡ ràng buộc thì kết quả mốc 1–2 cũng mất, còn file <code>qa_report.csv</code> cũ (nếu có) vẫn nằm đó, dễ bị đọc nhầm là kết quả mới.
low | KPI báo cáo QA khác cờ KPI chính | Báo cáo QA lọc <code>qa_has_error</code> (tính cả giá), KPI chính trong kpi.py lọc <code>qa_has_error_excl_price</code>. Đúng thiết kế nhưng cần nói rõ khi đọc số 978/928.
ok | Một cách đọc giá | KPI dùng lại <code>parse_price</code> của qa_rules nên "giá hợp lệ" ở luật và ở KPI là cùng một định nghĩa.
ok | Bảng gốc không bị sửa | <code>flag_table</code> làm việc trên bản sao; test end-to-end kiểm bảng đầu vào không có cột <code>qa_*</code> sau khi chạy.

--- qa
? QA có xoá dòng lỗi không?
<p>Không. <code>run</code> trả bảng đủ 1.000 listing mỗi mốc, chỉ thêm cột <code>qa_*</code>. Việc bỏ dòng do bước KPI tự quyết, theo cờ phù hợp với KPI đó. Báo cáo chỉ mô phỏng ảnh hưởng lọc: mốc cuối 1.000 → 978 (bỏ lỗi) → 928 (bỏ thêm cảnh báo).</p>
? Vì sao hai mốc đầu mean_price là NaN?
<p>Cột price của 2025-09-12 và 2025-12-12 trống toàn bộ. <code>compute_kpis</code> bỏ NaN rồi thấy Series rỗng nên trả NaN, không đoán giá.</p>
? Vì sao giá TB giảm 490 → 464 khi bỏ lỗi mà trung vị gần như không đổi?
<p>Hai căn giá &gt; 10.000 AUD (tổng khoảng 26.255 AUD) kéo trung bình lên; bỏ chúng thì trung bình giảm khoảng 26. Trung vị chỉ phụ thuộc thứ tự nên chỉ dịch từ 343 xuống 342,84.</p>
? Thứ tự trong vòng lặp mỗi mốc là gì, vì sao?
<p>Ràng buộc mẫu, gắn cờ, lưu vào <code>seen</code>, rồi KPI. Ràng buộc đi trước để dữ liệu sai mẫu không kịp sinh báo cáo. Lưu <code>seen</code> sau khi gắn cờ để mốc hiện tại không tự so với chính nó.</p>
? Đổi sang mốc khác thì bước này có dừng oan không?
<p>Không. <code>run_pipeline</code> bỏ <code>qa.expected</code> khi mốc khác mốc được giao; khi đó <code>check_sample_constraints</code> nhận <code>None</code> và bỏ qua, luật theo dòng vẫn chạy.</p>
