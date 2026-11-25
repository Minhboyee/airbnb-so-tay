--- meta
title: metrics.py
lead: Các công thức chấm điểm của bước 4c, viết tay bằng numpy, không đọc ghi file. <code>evaluate.py</code> đưa vào nhãn tay và nhãn máy, nhận lại ma trận nhầm lẫn, precision/recall/F1 từng lớp, macro-F1, Cohen's kappa, micro-F1 trên cặp (khen/chê, khía cạnh), và hai loại khoảng tin cậy 95%: Wilson cho accuracy, bootstrap cho kappa và F1. Mọi số ví dụ dưới đây tính lại từ 100 nhãn tay và khớp <code>reports/evaluation/eval_summary.csv</code>.

--- blocks
=== 1-10
<p>Docstring nói rõ phân công: file này <b>chỉ có công thức</b> (hàm thuần: cùng đầu vào cho cùng đầu ra, không I/O). Nhờ vậy test có thể kiểm từng công thức bằng số tính tay (<code>tests/test_evaluate.py</code>: kappa 0,6364, Wilson 80/100 = [0,711; 0,867]). Không import <code>evaluate</code>/<code>eval_report</code> nên không có vòng import.</p>

=== 12
<p>Cho phép viết <code>tuple[float, float]</code>, <code>set[tuple[str, str]]</code> trong chú thích kiểu trên Python 3.10.</p>

=== 14
<p><code>Callable</code> chỉ dùng để chú thích tham số <code>metric</code> của <a href="#metrics-L133">bootstrap_interval</a>: một hàm nhận mảng chỉ số, trả một số.</p>

=== 16-17
<p>numpy cho ma trận và lấy mẫu ngẫu nhiên; pandas cho bảng từng lớp. Không dùng scikit-learn: các công thức đủ ngắn để viết tay và giải thích được từng dòng.</p>

=== 19-20
<p>Thứ tự ba nhãn cố định. Hàng/cột của ma trận nhầm lẫn, bảng từng lớp và hình đều theo thứ tự này. <code>evaluate.load_gold</code> cũng dùng hằng này để chặn sentiment lạ.</p>

=== 21-22
<p><code>1.96</code> là phân vị 97,5% của phân phối chuẩn tắc: khoảng ±1,96 độ lệch chuẩn chứa 95% xác suất. Chỉ Wilson dùng hệ số này; bootstrap lấy phân vị trực tiếp.</p>

=== 25-30
<p>Biến hai danh sách khía cạnh thành <b>một tập cặp</b> (phía, khía cạnh). Vì sao cần: nếu chỉ so tên khía cạnh, máy nói "khen host" trong khi người gán "chê host" sẽ bị tính là đúng. Ghép phía vào cặp thì hai cái này khác nhau: một FP (<code>positive:host</code>) và một FN (<code>negative:host</code>).</p>
<p>Dùng <code>set</code> nên trùng lặp tự bỏ và thứ tự không quan trọng.</p>

=== 33-41
<p>Đếm trên từng review rồi cộng dồn:</p>
<ul><li>TP = <code>|gold ∩ máy|</code>: cặp máy đoán và người cũng gán.</li>
<li>FP = <code>|máy − gold|</code>: máy đoán thừa.</li>
<li>FN = <code>|gold − máy|</code>: máy bỏ sót.</li></ul>
<p>Ví dụ: gold <code>{(+,location), (+,value), (−,cleanliness), (−,noise)}</code>, baseline <code>{(+,location), (+,value)}</code> (review 600307857792014827) → TP 2, FP 0, FN 2. Không có "TN": số cặp có thể có là 12 (6 khía cạnh × 2 phía) nhưng đếm cặp vắng mặt không có nghĩa, nên không dùng accuracy cho khía cạnh.</p>
<p><code>strict=True</code>: hai danh sách phải dài bằng nhau, lệch là lỗi thay vì cắt im lặng.</p>

=== 44-50
<p>Docstring giải thích micro: cộng TP/FP/FN của mọi review (và mọi khía cạnh) trước, rồi tính một lần. Khía cạnh hay gặp (location 81 cặp gold) nặng hơn khía cạnh hiếm (value 6 cặp).</p>

=== 51-55
<p>Ba công thức:</p>
<ul><li>Precision P = TP / (TP + FP)</li>
<li>Recall R = TP / (TP + FN)</li>
<li>F1 = 2PR / (P + R) = 2TP / (2TP + FP + FN). Code dùng dạng thứ hai: cùng giá trị, chỉ một phép chia, và chỉ bằng 0 khi không có cặp nào.</li></ul>
<p>Số thật của LLM: TP 222, FP 12, FN 35 → P = 222/234 = 0,949; R = 222/257 = 0,864; F1 = 444/491 = 0,904. Baseline: TP 114, FP 8, FN 143 → P 0,934; R 0,444; F1 = 228/379 = 0,602.</p>
<p>Mẫu số bằng 0 trả 0.0 thay vì NaN (test: <code>{"tp":0,"fp":0,"fn":0}</code> → F1 0).</p>

=== 58-63
<p>Ma trận 3×3, hàng = nhãn tay, cột = máy. Mỗi ô đếm bằng phép so sánh mảng boolean. Nhãn ngoài <code>LABELS</code> sẽ không vào ô nào (tổng ma trận nhỏ hơn n), nhưng <code>evaluate.py</code> đã chặn nhãn lạ ở cả gold và cache nên không xảy ra. Docstring nói "chỉ trên dòng đã có dự đoán": việc lọc đó do người gọi làm (<a href="#evaluate-L203">evaluate dòng 203</a>), hàm này không lọc.</p>
<p>Ma trận thật (chạy lại <code>evaluate.run</code>):</p>
<table><tr><th></th><th>LLM: pos</th><th>mixed</th><th>neg</th><th>Baseline: pos</th><th>mixed</th><th>neg</th></tr>
<tr><td>gold positive</td><td>85</td><td>0</td><td>0</td><td>84</td><td>1</td><td>0</td></tr>
<tr><td>gold mixed</td><td>3</td><td>12</td><td>0</td><td>12</td><td>3</td><td>0</td></tr>
<tr><td>gold negative</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td><td>0</td></tr></table>

=== 66-71
<p>Cohen's kappa trả lời: hai bên đồng ý nhiều hơn mức "trùng do may" bao nhiêu? Công thức κ = (p<sub>o</sub> − p<sub>e</sub>) / (1 − p<sub>e</sub>):</p>
<ul><li>p<sub>o</sub>: tỷ lệ khớp thật = accuracy.</li>
<li>p<sub>e</sub>: tỷ lệ khớp nếu hai bên gán độc lập, mỗi bên giữ tần suất nhãn của mình.</li></ul>
<p>κ = 1 là khớp hoàn toàn, 0 là không hơn ngẫu nhiên, âm là tệ hơn ngẫu nhiên.</p>

=== 72-74
<p>Ma trận rỗng (n = 0) thì trả 0, tránh chia cho 0.</p>

=== 75
<p>p<sub>o</sub> = tổng đường chéo / n.</p>

=== 76
<p>p<sub>e</sub> = Σ<sub>k</sub> (tổng cột k × tổng hàng k) / n². Tổng hàng là số gold của lớp k, tổng cột là số máy đoán lớp k.</p>
<p>Ví dụ LLM: hàng (85, 15, 0), cột (88, 12, 0). p<sub>e</sub> = (85·88 + 15·12)/10.000 = 0,766; p<sub>o</sub> = 0,97 → κ = (0,97 − 0,766)/0,234 = <b>0,872</b>.</p>
<p>Baseline: hàng (85, 15, 0), cột (96, 4, 0). p<sub>e</sub> = (85·96 + 15·4)/10.000 = 0,822; p<sub>o</sub> = 0,87 → κ = 0,048/0,178 = <b>0,270</b>. Accuracy cao nhưng p<sub>e</sub> cũng cao vì cả hai bên gần như toàn positive.</p>

=== 77
<p>p<sub>e</sub> = 1 xảy ra khi cả gold và máy chỉ dùng đúng một nhãn (ví dụ toàn positive): mẫu số 1 − p<sub>e</sub> = 0, kappa không xác định. Code quy ước trả 0. Với gold thật (15 mixed) trường hợp này không xảy ra; trong bootstrap thì chỉ xảy ra nếu một mẫu bốc lại không có review mixed nào, xác suất cỡ 0,85<sup>100</sup>, bỏ qua được.</p>

=== 81-84
<p>Precision/recall/F1 của <b>từng lớp</b> sentiment, đọc từ ma trận. <code>support</code> = tổng hàng (gold có bao nhiêu), <code>predicted</code> = tổng cột (máy đoán bao nhiêu).</p>

=== 85-90
<p>Với lớp ở vị trí <code>index</code>: TP = ô đường chéo; precision = TP / tổng cột; recall = TP / tổng hàng. Ví dụ baseline lớp mixed: TP 3, đoán 4, gold 15 → P 0,75, R 0,20.</p>

=== 91-92
<p>Mẫu số 0 trả 0. Hệ quả: lớp negative (support 0, predicted 0) có P = R = 0, nên F1 = 0 trong <code>eval_perclass.csv</code>. Số 0 này không có nghĩa "máy sai hết lớp negative", mà là không có dữ liệu.</p>

=== 93
<p>F1 = 2PR/(P+R), trung bình điều hoà. Baseline mixed: 2·0,75·0,2/0,95 = 0,316. Trung bình điều hoà kéo về số nhỏ hơn: precision cao không bù được recall thấp.</p>

=== 94-104
<p>Mỗi lớp một dòng; luôn đủ 3 dòng kể cả lớp vắng mặt, để bảng có hình dạng cố định.</p>

=== 107-111
<p>Macro-F1 = trung bình cộng F1 các lớp, mỗi lớp nặng như nhau. Khác accuracy: lớp mixed chỉ 15 review nhưng chiếm nửa điểm, nên đoán dồn về positive bị phạt nặng.</p>

=== 112-115
<p><b>Chỉ lấy lớp có support &gt; 0.</b> Gold không có negative; nếu tính cả lớp đó (F1 = 0 theo quy ước trên) thì mọi phương pháp bị trừ oan. Chạy thử: macro-F1 baseline tính 3 lớp là 0,415, tính 2 lớp là 0,622. Hàm trả kèm số lớp đã dùng (<code>sentiment_macro_f1_labels = 2</code> trong <code>eval_summary.csv</code>) để người đọc biết trung bình trên mấy lớp.</p>
<p>Số thật: LLM (0,983 + 0,889)/2 = 0,936; baseline (0,928 + 0,316)/2 = 0,622. Lưu ý: lớp negative mà máy đoán sai (gold không có) vẫn làm giảm precision chỗ khác, nhưng không có dòng negative nào trong trung bình.</p>

=== 118-122
<p>Khoảng tin cậy cho một tỷ lệ (accuracy = số đúng / n). n = 0 thì trả NaN, báo cáo hiện "n/a".</p>

=== 123-127
<p>Công thức Wilson, với p̂ = đúng/n, z = 1,96:</p>
<ul><li>tâm = (p̂ + z²/2n) / (1 + z²/n)</li>
<li>nửa độ rộng = z·√(p̂(1−p̂)/n + z²/4n²) / (1 + z²/n)</li></ul>
<p>Tính tay LLM 97/100: tâm = (0,97 + 0,0192)/1,0384 = 0,9526; nửa độ rộng = 1,96·√(0,000291 + 0,000096)/1,0384 = 0,0371 → <b>[0,915; 0,990]</b>. Baseline 87/100 → [0,790; 0,922].</p>
<p>Vì sao không dùng khoảng chuẩn (Wald) p̂ ± 1,96√(p̂(1−p̂)/n)? Với 97/100 Wald cho [0,937; 1,003], vượt 1, vô nghĩa. Wilson luôn nằm trong [0; 1] và tâm bị kéo về 0,5 một chút, hợp với n nhỏ và tỷ lệ sát 1. (Chạy thử <code>wilson_interval(0, 10)</code> ra cận dưới −2,8·10<sup>−17</sup>: sai số dấu phẩy động, thực chất là 0.)</p>

=== 130-138
<p>Kappa và F1 không có công thức khoảng gọn như Wilson, nên dùng bootstrap: coi 100 review là "tổng thể thu nhỏ", bốc lại có hoàn lại 100 review, tính lại số đo, lặp nhiều lần, xem số đo dao động thế nào. Tắt bằng <code>n_boot = 0</code> (test dùng điều này).</p>

=== 139
<p>Sinh một lần ma trận chỉ số <code>(n_boot, n)</code>, mỗi hàng là một mẫu bốc lại. Với config thật <code>n_boot = 2000</code> (<code>eval.bootstrap_samples</code>), n = 100, seed 42. Cùng seed và cùng n thì ra đúng cùng 2000 mẫu: baseline và LLM, kappa, macro-F1 và micro-F1 đều được bốc trên cùng các bộ chỉ số. Kết quả lặp lại được từng chữ số.</p>

=== 140
<p>Gọi <code>metric</code> trên từng hàng chỉ số. <code>metric</code> là hàm đóng (lambda) do <code>evaluate.score_method</code> truyền vào, tự lấy dòng gold/máy theo chỉ số và tính lại ma trận (<a href="#evaluate-L211">evaluate dòng 211</a>).</p>

=== 141-142
<p>Phương pháp <b>phân vị</b>: khoảng 95% là phân vị 2,5% và 97,5% của 2000 giá trị. Ví dụ kappa baseline [−0,019; 0,534]: cận dưới âm nghĩa là với 100 review này chưa loại được khả năng baseline không hơn ngẫu nhiên. Kappa LLM [0,706; 1,000] và macro-F1 LLM [0,851; 1,000] chạm 1 vì có những mẫu bốc lại không chứa 3 ca LLM sai.</p>

--- flow
## Hằng số
st 0 20 | LABELS | positive, mixed, negative
st 0 22 | Z_SCORE | 1,96 cho 95%
## Sentiment
fn 0 58 | confusion_matrix | Hàng gold, cột máy
fn 0 63 | cohen_kappa | (po − pe)/(1 − pe)
fn 0 78 | per_class_scores | P/R/F1 từng lớp
fn 0 104 | macro_f1 | Trung bình lớp có support &gt; 0
## Khía cạnh
fn 0 25 | aspect_pairs | (phía, khía cạnh)
fn 0 33 | aspect_counts | TP/FP/FN cộng dồn
fn 0 44 | micro_scores | P, R, F1 = 2TP/(2TP+FP+FN)
## Khoảng tin cậy
fn 0 118 | wilson_interval | Accuracy, công thức đóng
fn 0 133 | bootstrap_interval | Kappa, F1: bốc lại 2000 lần
chips 1 | evaluate:191 score_method ; evaluate:287 per_aspect_scores

--- review
ok | Công thức viết tay, có test số | Kappa, Wilson, micro-F1 được kiểm bằng giá trị tính tay trong <code>tests/test_evaluate.py</code>; chạy lại trên gold khớp <code>eval_summary.csv</code> tới chữ số cuối.
ok | Macro-F1 ghi rõ số lớp | Bỏ lớp support 0 khỏi trung bình và trả kèm <code>sentiment_macro_f1_labels</code>, tránh trừ oan 0,622 xuống 0,415 mà vẫn minh bạch.
mid | F1 = 0 cho lớp không có dữ liệu | Lớp negative hiện P = R = F1 = 0 trong <code>eval_perclass.csv</code>. Đọc bảng mà không xem <code>support</code> dễ hiểu nhầm là máy sai hết lớp này.
low | Docstring confusion_matrix | Ghi "chỉ trên dòng đã có dự đoán" nhưng hàm không lọc; người gọi lọc trước.
low | Bootstrap dùng chung seed | Mọi khoảng bootstrap dùng cùng bộ 2000 mẫu (cùng seed, cùng n). Lặp lại được, nhưng code không tính khoảng cho <b>hiệu số</b> LLM − baseline, nên không kết luận được độ chênh có ý nghĩa thống kê chỉ từ hai khoảng riêng.

--- qa
? Tính tay kappa của LLM.
<p>Ma trận hàng gold (85, 15, 0), cột máy (88, 12, 0), đường chéo 97. p<sub>o</sub> = 0,97; p<sub>e</sub> = (85·88 + 15·12)/100² = 0,766; κ = (0,97 − 0,766)/(1 − 0,766) = 0,872 (<a href="#metrics-L63">cohen_kappa</a>).</p>
? Macro-F1 và micro-F1 khác nhau thế nào? Ở đây dùng cái nào cho gì?
<p>Macro: tính F1 từng lớp rồi lấy trung bình, lớp hiếm nặng ngang lớp phổ biến; dùng cho sentiment để lớp mixed (15 review) không bị lớp positive (85) che. Micro: cộng TP/FP/FN của mọi cặp rồi tính một lần; dùng cho khía cạnh vì mỗi review có nhiều nhãn và ta quan tâm tổng số cặp đúng.</p>
? Vì sao macro-F1 chỉ lấy lớp có support &gt; 0?
<p>Gold không có review negative. Lớp đó có F1 = 0 theo quy ước, đưa vào trung bình sẽ kéo baseline từ 0,622 xuống 0,415 dù không có dữ liệu để chấm. Code bỏ lớp đó và báo số lớp đã dùng (2).</p>
? Vì sao accuracy dùng Wilson còn kappa, F1 dùng bootstrap?
<p>Accuracy là tỷ lệ nhị thức (đúng/sai), có công thức đóng; Wilson không vượt [0; 1] khi tỷ lệ sát 1 (Wald cho 97/100 ra cận trên 1,003). Kappa và F1 là hàm phức tạp của cả ma trận, không có công thức khoảng đơn giản, nên bốc lại 2000 lần rồi lấy phân vị 2,5% và 97,5%.</p>
? Khoảng tin cậy của kappa baseline chứa số âm nghĩa là gì?
<p>[−0,019; 0,534]: với 100 review, chưa loại được khả năng baseline chỉ đồng thuận với người ở mức ngẫu nhiên. Đoán toàn positive đã có accuracy 0,85 và kappa 0.</p>
? Vì sao F1 khía cạnh phải tách khen/chê?
<p><a href="#metrics-L25">aspect_pairs</a> ghép phía vào tên. Nếu không, đoán "khen host" cho review "chê host" vẫn được tính đúng. Tách ra thì ca đó thành 1 FP và 1 FN.</p>
