--- meta
title: evaluate.py
lead: Bước đánh giá của pipeline: đọc 100 nhãn tay và cache LLM, dựng dự đoán baseline + LLM, rồi chấm bằng <code>metrics.py</code>. Hai cổng an toàn: gold dưới <code>min_gold_size</code> hoặc cache LLM chưa phủ hết thì chỉ ghi báo cáo chẩn đoán, không công bố accuracy/F1; gold thiếu lớp chỉ là cảnh báo. Kết quả thật (<code>reports/evaluation/eval_summary.csv</code>): LLM accuracy 0,970, macro-F1 0,936, kappa 0,872, aspect micro-F1 0,904; baseline 0,870 / 0,622 / 0,270 / 0,602.

--- blocks
=== 1-14
<p>Docstring ghi rõ:</p>
<ul><li>Vị trí: <code>run_pipeline.py</code> gọi <code>evaluate.run(config)</code> trong <code>run_evaluation_stage</code>, sau khi baseline và cache LLM đã có. Chạy riêng được bằng <code>python -m src.evaluate</code>.</li>
<li>Vào: file nhãn tay (mặc định <code>data/samples/hand_labels.csv</code>), cache LLM, mục <code>eval</code> trong config.</li>
<li>Ra: DataFrame tóm tắt + 4 CSV + <code>eval_errors.md</code> trong <code>reports/evaluation/</code>, và hình ma trận nhầm lẫn trong <code>figures/evaluation/</code>.</li>
<li>Hai cổng: gold quá ít hoặc cache LLM chưa phủ hết thì chỉ ghi chẩn đoán, không công bố accuracy/F1. Gold thiếu lớp sentiment thì vẫn chấm, chỉ cảnh báo. Đây là trạng thái ở tag <code>final</code>; tài liệu cũ nói "không công bố F1 vì thiếu lớp negative" đã lỗi thời.</li>
<li>Phân công: file này đọc dữ liệu và điều phối; công thức ở <code>metrics.py</code>; ghi báo cáo và vẽ hình ở <code>eval_report.py</code>. Không có vòng import.</li></ul>

=== 16-20
<p>Ba import chuẩn: <code>argparse</code> cho <code>main()</code>, <code>Path</code> cho đường dẫn, <code>Any</code> cho dict kết quả nhiều kiểu. <code>from __future__ import annotations</code> cho phép viết <code>Path | None</code>, <code>list[dict[str, Any]]</code> trên Python 3.10.</p>

=== 22-23
<p>numpy để tính ma trận, trace, mảng boolean; pandas để đọc CSV, ghép bảng, groupby. Không dùng scikit-learn: mọi công thức nằm ở <code>metrics.py</code> và có test số tính tay.</p>

=== 25-28
<p>Bốn nhóm phụ thuộc nội bộ:</p>
<ul><li><code>predict_reviews</code>: baseline luật từ khoá.</li>
<li><code>load_config</code>: chỉ dùng trong <code>main()</code> khi chạy dòng lệnh.</li>
<li>Bốn hàm của <code>eval_report</code>: ghi chẩn đoán, in chẩn đoán, ghi Markdown, vẽ hình.</li>
<li><code>load_cache</code>: đọc cache JSONL của LLM, có kiểm schema và bộ khía cạnh.</li></ul>

=== 29-40
<p>Mười công thức/hằng từ <code>metrics.py</code>. Chia ba nhóm: sentiment (<code>confusion_matrix</code>, <code>cohen_kappa</code>, <code>per_class_scores</code>, <code>macro_f1</code>), khía cạnh (<code>aspect_pairs</code>, <code>aspect_counts</code>, <code>micro_scores</code>), khoảng tin cậy (<code>wilson_interval</code>, <code>bootstrap_interval</code>). <code>LABELS</code> giữ thứ tự ba nhãn cho ma trận và bảng.</p>

=== 42-43
<p>Sáu cột bắt buộc của file nhãn tay. Thiếu cột nào thì <code>load_gold</code> báo lỗi kèm tên cột. Cột <code>ghi_chu</code> có trong file thật nhưng không bắt buộc, nên không nằm trong danh sách.</p>

=== 46-48
<p>Tách một ô khía cạnh như <code>"location; host ;location;"</code> thành danh sách. Ba bước trong một dòng: cắt theo <code>;</code>, <code>strip</code> từng mẩu và bỏ mẩu rỗng, gom vào <code>set</code> để bỏ trùng, rồi <code>sorted</code> để thứ tự ổn định. Test <code>test_parse_aspects_drops_duplicates_and_blanks</code> kiểm đúng ví dụ này ra <code>["host", "location"]</code>. Sắp xếp cũng làm chuỗi trong báo cáo dễ so.</p>

=== 51-55
<p>Đọc nhãn tay và chặn dữ liệu hỏng trước khi chấm. <code>dtype=str, keep_default_na=False</code> để mọi cột đọc thành chuỗi, ô trống thành <code>""</code> chứ không phải <code>NaN</code>, và ID review dài 18–19 chữ số không bị đổi sang số thực. Nhờ vậy <code>aspects_positive</code> rỗng so sánh được bằng chuỗi, còn <code>review_id</code> khớp cache LLM.</p>

=== 56-59
<p><code>read_csv</code> trong <code>try</code>. File rỗng hoàn toàn làm pandas ném <code>EmptyDataError</code>; code đổi thành <code>ValueError</code> có thông báo tiếng Việt, thống nhất với các lỗi kiểm tra bên dưới.</p>

=== 60-62
<p>Thiếu cột bắt buộc: liệt kê <b>tất cả</b> cột thiếu trong một lần, không bắt sửa từng cái.</p>

=== 63-64
<p>File có header nhưng 0 dòng dữ liệu cũng bị chặn, vì <code>read_csv</code> không ném lỗi trong trường hợp này.</p>

=== 65-66
<p>ID trùng làm mọi phép ghép theo <code>review_id</code> nhân dòng, nên dừng sớm. Đây là lỗi dữ liệu, không phải lỗi code.</p>

=== 67-69
<p>Sentiment ngoài <code>LABELS</code> bị chặn. Nếu để lọt, <code>confusion_matrix</code> bỏ qua dòng đó (không vào ô nào) và mẫu số accuracy lệch mà không báo. Gold thật chỉ có <code>positive</code> (85) và <code>mixed</code> (15), không có <code>negative</code>.</p>

=== 70-75
<p>Gom mọi tên khía cạnh xuất hiện trong hai cột, kể cả ô có nhiều tên ngăn bởi <code>;</code>. Dùng set comprehension ba tầng: duyệt hai cột, duyệt từng ô, duyệt từng tên đã tách.</p>

=== 76-78
<p>So với danh sách khía cạnh của config (<code>llm.aspects</code>, 6 tên). Tên lạ như <code>safety</code> bị chặn thay vì lặng lẽ tính vào micro-F1 với support 0. Test <code>test_load_gold_rejects_bad_input</code> kiểm ca này.</p>

=== 79
<p>Trả DataFrame gốc, chưa đổi gì. Các bước sau tự tách cột cần dùng.</p>

=== 82-85
<p>Đếm support từng lớp bằng <code>value_counts</code>, rồi ép đủ ba khoá theo <code>LABELS</code> với <code>counts.get(label, 0)</code>. Nhờ vậy lớp vắng mặt vẫn có mặt với số 0, không bị thiếu khoá. Gold thật: <code>{"positive": 85, "mixed": 15, "negative": 0}</code>.</p>

=== 88-91
<p>Danh sách lớp không có mẫu nào. Với gold thật là <code>["negative"]</code>; hàm này được dùng cho cảnh báo và cho cột <code>missing_gold_labels</code> của bảng chẩn đoán.</p>

=== 94-98
<p>Bảng chẩn đoán: mỗi phương pháp một dòng, chỉ có support, coverage và phân bố nhãn dự đoán, <b>không</b> có accuracy/F1. Dùng khi pipeline chưa đủ điều kiện công bố số.</p>

=== 99-100
<p>Lấy support và danh sách lớp thiếu một lần, dùng lại cho mọi dòng.</p>

=== 101-102
<p><code>rows</code> gom dict từng phương pháp; <code>groupby("method", sort=False)</code> giữ thứ tự xuất hiện (baseline trước, LLM sau) thay vì sắp alphabet.</p>

=== 103-104
<p><code>scored</code> = dòng có sentiment không rỗng. Chỉ đếm nhãn dự đoán trên các dòng đã chấm; <code>predicted</code> là <code>value_counts</code> của nhãn máy. Dòng chưa có nhãn được đếm riêng ở <code>predicted_unlabeled</code>.</p>

=== 105-116
<p>Mỗi dòng chẩn đoán gồm: tên phương pháp, <code>n_gold</code> (100), <code>n_scored</code>, <code>coverage</code> (tỷ lệ đã có dự đoán), support gold từng lớp, số máy đoán từng lớp, số chưa có nhãn, và chuỗi lớp gold bị thiếu. Tên cột dùng tiền tố <code>gold_</code>/<code>predicted_</code> để không lẫn hai phía.</p>

=== 117
<p>Trả DataFrame. Với cache đầy đủ, bảng có 2 dòng, coverage 1,0 cả hai, <code>predicted_positive</code> 96/88, <code>predicted_mixed</code> 4/12.</p>

=== 120-124
<p>Hàm trả danh sách lý do chưa được công bố metric; rỗng nghĩa là đủ điều kiện. Kiểm tham số trước: <code>min_gold_size</code> nhỏ hơn 1 là cấu hình vô nghĩa, ném <code>ValueError</code> (test <code>test_minimum_gold_size_must_be_positive</code>).</p>

=== 125-126
<p>Cổng thứ nhất: ít hơn 100 nhãn tay thì không đủ mẫu, thêm lý do kèm số thực tế dạng <code>"Có 3/100 review..."</code>. Chạy test với 3 dòng gold sẽ thấy đúng chuỗi này trong <code>eval_diagnostics.md</code>.</p>

=== 127-129
<p>Cổng thứ hai, phần đầu: không có dòng LLM nào hoặc toàn bộ sentiment rỗng (cache thiếu hẳn, file rỗng). Không có dự đoán LLM thì không có gì để so, chỉ chẩn đoán.</p>

=== 130-131
<p>Cổng thứ hai, phần sau: có dự đoán nhưng thiếu ít nhất một review, hoặc số dòng LLM khác số gold. Trong pipeline, <code>llm_predictions</code> luôn phát đúng một dòng cho mỗi gold id, nên vế <code>len(llm) != len(gold)</code> không bao giờ đúng; vế thực sự bắt lỗi là <code>llm["sentiment"].isna().any()</code>, nên <code>eval_summary.csv</code> đã công bố luôn có coverage 1,000.</p>

=== 132
<p>Trả danh sách lý do. Rỗng nghĩa là đủ điều kiện chấm. <code>run</code> chỉ cần kiểm <code>if reasons:</code>.</p>

=== 135-139
<p>Cảnh báo (không chặn) khi gold thiếu lớp. Ở tag <code>final</code> đây là lớp <code>negative</code>: vẫn chấm bình thường, nhưng macro-F1 chỉ lấy trung bình các lớp có support &gt; 0 (<a href="#metrics-L112">metrics dòng 112</a>), nên báo trước để người đọc không hiểu nhầm.</p>

=== 140-143
<p>Trả danh sách một phần tử (nối tên các lớp thiếu bằng dấu phẩy) hoặc rỗng. Câu chữ được in ra console và chép vào mục "Cảnh báo" của <code>eval_errors.md</code>.</p>

=== 146-147
<p>Dự đoán baseline. Để so sánh công bằng, hàm chỉ truyền <code>review_id</code> và <code>comments</code>, không truyền nhãn tay. Baseline không thể "nhìn đáp án".</p>

=== 148
<p>Gọi <code>predict_reviews</code> của <code>baseline.py</code>: regex cố định, không seed, không mạng, nên chạy lại cho cùng kết quả.</p>

=== 149-158
<p>Đóng gói lại đúng schema của nhãn LLM: thêm cột <code>method = "baseline"</code>, ID về chuỗi, giữ hai danh sách khía cạnh và <code>language</code>. Nhờ cùng tên cột, <code>run</code> ghép hai bảng bằng <code>pd.concat</code> và <code>score_method</code> dùng chung một đoạn code.</p>

=== 161-163
<p>Ghép nhãn LLM từ cache. <code>load_cache</code> trả <code>(dict review_id → bản ghi, tập id)</code>; tập id không dùng, nên gán vào <code>_</code>. Truyền <code>aspects</code> để cache kiểm schema và bộ khía cạnh, tránh dùng nhãn của định nghĩa cũ.</p>

=== 164-165
<p>Duyệt theo đúng thứ tự <code>gold["review_id"]</code>, không theo thứ tự cache. Nhờ vậy bảng LLM thẳng hàng với gold và với baseline.</p>

=== 166-168
<p>Nếu cache có bản ghi nhưng sentiment lạ (file bị sửa tay, phiên bản cũ), ném <code>ValueError</code> nêu review id. Không âm thầm coi là thiếu nhãn, vì như vậy sẽ hạ coverage mà không rõ nguyên nhân.</p>

=== 169-170
<p>Tương tự cho <code>language</code> rỗng: cache thiếu ngôn ngữ là lỗi dữ liệu, không phải "chưa có nhãn". Test <code>test_evaluation_rejects_invalid_cached_fields</code> kiểm cả hai trường.</p>

=== 171-180
<p>Mỗi review một dòng. Có bản ghi: lấy sentiment, hai danh sách khía cạnh, language. Không có: sentiment <code>pd.NA</code>, hai danh sách rỗng, language <code>pd.NA</code>, dòng vẫn tồn tại để đếm coverage thay vì biến mất khỏi bảng.</p>

=== 181-184
<p>Dựng DataFrame rồi đổi <code>pd.NA</code> thành <code>None</code> và ép <code>dtype=object</code>. Lý do: <code>pd.NA</code> trong cột object gây nhập nhằng khi so sánh; <code>None</code> thì <code>notna()</code> và <code>isna()</code> xử lý ổn định, còn <code>astype(str)</code> chỉ chạy trên dòng đã chấm.</p>

=== 185-187
<p>Làm y hệt cho cột <code>language</code>. Nếu để lẫn kiểu, phép so chuỗi ở <code>score_method</code> có thể so <code>"&lt;NA&gt;"</code> với <code>"en"</code> và làm sai <code>language_accuracy</code>.</p>

=== 188
<p>Trả bảng LLM đủ 100 dòng (khi gold 100), kể cả dòng thiếu nhãn. Nhờ vậy cổng <code>diagnostic_reasons</code> phát hiện được cache chưa phủ hết.</p>

=== 191-197
<p>Chấm <b>một</b> phương pháp, dùng chung cho baseline và LLM. Hàm nhận tham số <code>aspects</code> nhưng không dùng trong thân hàm; <code>per_aspect_scores</code> mới là chỗ cần. Đây là tham số thừa, không ảnh hưởng kết quả.</p>

=== 198-202
<p>Docstring nói rõ hai việc: chỉ chấm trên dòng đã có dự đoán (coverage), và trả kèm <code>per_class</code>/<code>matrix</code> để <code>run</code> tách ra ghi file riêng. Nhờ vậy bảng tóm tắt không phình bởi hai cột kiểu DataFrame/ndarray.</p>

=== 203-206
<p>Cắt ba mảng song song: nhãn gold, nhãn máy (ép chuỗi), và <code>n_scored</code>. Cả ba dùng cùng mặt nạ <code>scored</code> của <code>predicted</code>. Hệ quả kỹ thuật: index của <code>predicted</code> phải trùng index của <code>gold</code>, vì <code>gold.loc[scored]</code> áp mặt nạ boolean theo nhãn index. <code>run</code> gọi <code>reset_index(drop=True)</code> trước nên hai bên đều 0..n-1.</p>

=== 208-210
<p>Dựng ma trận 3×3, bảng từng lớp, và macro-F1 kèm số lớp dùng. Với gold thật: ma trận LLM [[85,0,0],[3,12,0],[0,0,0]], macro 0,936 trên 2 lớp.</p>

=== 211-216
<p>Bootstrap cho macro-F1: mỗi lần bốc lại chỉ số, tính lại ma trận rồi <code>per_class_scores</code> rồi macro, lấy phần tử <code>[0]</code> (bỏ số lớp). Dùng đúng 2.000 lần, seed 42, nên khoảng LLM [0,851; 1,000]. Code tính lại từ mảng nhãn chứ không bốc lại bảng per-class, đúng cách bootstrap theo review.</p>

=== 217-219
<p>Accuracy = trace / n. Trace là tổng đường chéo = số dự đoán đúng: LLM 97/100 = 0,970, baseline 87/100 = 0,870. Khoảng tin cậy dùng Wilson (<a href="#metrics-L118">metrics dòng 118</a>) vì là tỷ lệ nhị thức và tỷ lệ sát 1.</p>

=== 220-225
<p>Bootstrap cho kappa, cùng bộ chỉ số và seed với macro-F1. Kappa baseline [−0,019; 0,534] chứa 0; kappa LLM [0,706; 1,000] không chứa 0, bằng chứng mạnh hơn việc so hai accuracy, vì hai khoảng accuracy [0,790; 0,922] và [0,915; 0,990] chồng nhau một chút.</p>

=== 227-232
<p>Dựng tập cặp (phía, khía cạnh) cho gold, chỉ trên dòng đã chấm. Gold lưu khía cạnh dạng chuỗi <code>"location;host"</code>, nên phải <code>parse_aspects</code> trước khi ghép phía.</p>

=== 233-238
<p>Tương tự cho máy, nhưng khía cạnh đã là list trong cache/baseline nên chỉ cần <code>list(...)</code>. <code>strict=True</code> buộc số dòng hai bên bằng nhau, lệch là lỗi thay vì cắt im lặng.</p>

=== 239-240
<p>Cộng dồn TP/FP/FN trên toàn bộ cặp, rồi tính micro precision/recall/F1. Số thật: LLM TP 222, FP 12, FN 35 cho F1 0,904; baseline 114/8/143 cho 0,602.</p>

=== 241-248
<p>Bootstrap cho micro-F1: mỗi lần bốc lại chỉ số review, lấy lại tập cặp gold/máy theo chỉ số đó, đếm lại rồi tính F1. Vì bốc theo review, một review có nhiều cặp vẫn đi cùng nhau, đúng đơn vị lấy mẫu.</p>

=== 250-252
<p>So ngôn ngữ gold với ngôn ngữ máy. Gold đọc bằng <code>keep_default_na=False</code> nên ô trống là <code>""</code>; <code>fillna("")</code> chỉ để phòng DataFrame dựng tay. Với dữ liệu thật, cả hai bên đều <code>"en"</code> nên <code>language_accuracy</code> = 1,000.</p>

=== 254-255
<p><code>exact</code> = tập cặp khía cạnh hai bên bằng hệt nhau cho từng review (không cần đúng thứ tự, vì là set). <code>sentiment_correct</code> = nhãn sentiment đúng. Hai mảng này dùng cho hai chỉ số "khớp hệt".</p>

=== 256-260
<p>Bắt đầu dict kết quả. <code>method</code> lấy từ dòng đầu; <code>n_gold</code> là 100; <code>n_scored</code> số dòng có nhãn; <code>coverage</code> = n_scored/n_gold. Trong pipeline, cổng chẩn đoán đã chặn trường hợp coverage &lt; 1, nên số công bố luôn 1,000.</p>

=== 261-263
<p>Accuracy và hai cận Wilson. Với baseline: 0,870 [0,790; 0,922]; LLM: 0,970 [0,915; 0,990].</p>

=== 264-267
<p>Macro-F1, hai cận bootstrap, và <code>sentiment_macro_f1_labels</code> = 2, số lớp đã đưa vào trung bình. Cột này để người đọc biết lớp <code>negative</code> (support 0) không được tính.</p>

=== 268-270
<p>Kappa điểm và hai cận bootstrap. Kappa không dùng Wilson vì là hàm của cả ma trận, không phải tỷ lệ đơn.</p>

=== 271-275
<p>Micro precision/recall/F1 của khía cạnh và khoảng bootstrap cho F1. Precision baseline 0,934 cao nhưng recall 0,444 thấp: luật hẹp, khớp thì đúng, bỏ sót nhiều.</p>

=== 276-278
<p>Ba số đếm thô TP/FP/FN, để người đọc tự kiểm lại F1 hoặc tính lại theo cách khác. LLM: 222/12/35; baseline: 114/8/143.</p>

=== 279-281
<p>Ba chỉ số phụ: tỷ lệ review có tập khía cạnh khớp hệt (0,630 LLM; 0,240 baseline), <code>language_accuracy</code> (1,000), và tỷ lệ vừa đúng sentiment vừa khớp hệt khía cạnh (0,620 / 0,230).</p>

=== 282-284
<p>Hai khoá không phải số, để <code>run</code> <code>pop</code> ra và ghi file riêng: bảng per-class (3 dòng/phương pháp) và ma trận 3×3. Nếu để trong dict, <code>pd.DataFrame(summaries)</code> sẽ tạo cột chứa object, khó ghi CSV.</p>

=== 287-292
<p>Tách micro-F1 theo từng khía cạnh, trả lời "khía cạnh nào bị bỏ sót nhiều". Vào là hai danh sách tập cặp đã lọc theo dòng có nhãn, và danh sách 6 tên khía cạnh.</p>

=== 293-295
<p>Với mỗi khía cạnh, dựng tập <code>names</code> gồm hai cặp (khen, khía cạnh) và (chê, khía cạnh). Đây là bộ lọc: giao tập gold/máy với <code>names</code> để chỉ giữ cặp của khía cạnh đang xét.</p>

=== 296-299
<p>Đếm TP/FP/FN sau khi lọc, bằng chính <code>aspect_counts</code> của metrics. Nhờ tách phía, "khen host" và "chê host" là hai cặp khác nhau, không bị lẫn.</p>

=== 300
<p>Một dòng: tên khía cạnh, P/R/F1, ba số đếm, và <code>support = tp + fn</code> = số cặp gold của khía cạnh. Số thật: location support 81 (baseline F1 0,677), amenities 60 (0,373), value 6 (0,444).</p>

=== 301
<p>Trả DataFrame 6 dòng/phương pháp. <code>run</code> gán thêm cột <code>method</code> và nối hai phương pháp thành <code>eval_aspects.csv</code> 12 dòng.</p>

=== 304-308
<p>Bảng từng review cho từng phương pháp, phục vụ phân tích lỗi. Năm loại lỗi trong docstring: <code>unlabeled</code>, <code>sentiment:gold-&gt;máy</code>, <code>aspect_missing</code>, <code>aspect_extra</code> (một dòng có thể mang nhiều loại, ngăn bởi <code>;</code>).</p>

=== 309-312
<p>Tính tập cặp gold cho <b>toàn bộ</b> gold, không lọc theo dòng có nhãn, khác <code>score_method</code>. Lý do: bảng lỗi cần cả dòng <code>unlabeled</code> để hiển thị.</p>

=== 313-314
<p><code>rows</code> gom kết quả; lặp từng phương pháp theo thứ tự xuất hiện.</p>

=== 315
<p>Căn bảng dự đoán theo thứ tự <code>gold["review_id"]</code>: đặt <code>review_id</code> làm index rồi <code>reindex</code>. Review thiếu trong bảng dự đoán sẽ thành dòng toàn NaN. Trong pipeline không xảy ra vì <code>llm_predictions</code> phát đủ dòng; nếu gọi hàm với bảng thiếu dòng, <code>list(NaN)</code> ở dưới sẽ ném <code>TypeError</code> (đã chạy thử).</p>

=== 316-317
<p><code>zip(..., strict=True)</code> buộc ba dãy cùng độ dài: gold, tập cặp gold, bảng đã căn. Mỗi vòng có nhãn gold, tập gold, và dòng dự đoán. <code>predicted_set</code> dựng từ hai cột list của máy.</p>

=== 318-320
<p>Tính phần thiếu (gold có, máy không), phần thừa (máy có, gold không), và nhãn sentiment máy. Dùng set nên không phụ thuộc thứ tự.</p>

=== 321-325
<p>Xếp loại lỗi theo thứ tự cố định: chưa có nhãn thì <code>unlabeled</code>; sai sentiment thì <code>sentiment:gold-&gt;máy</code> (ví dụ <code>sentiment:mixed-&gt;positive</code>); rồi cờ thiếu/thừa khía cạnh. Dòng chưa có nhãn vẫn được tính lỗi khía cạnh: cache thiếu bản ghi nên hai danh sách rỗng, gold có khía cạnh thì sinh thêm <code>aspect_missing</code>. Test <code>test_per_review_frame_marks_error_types</code> kỳ vọng đúng chuỗi <code>unlabeled;aspect_missing</code>.</p>

=== 326-329
<p>Thêm <code>aspect_missing</code>/<code>aspect_extra</code> nếu có. Một review vừa thiếu vừa thừa sẽ có cả hai, đúng như ca LLM ở test: <code>sentiment:positive-&gt;mixed;aspect_missing;aspect_extra</code>.</p>

=== 330-335
<p>Dòng kết quả phần đầu: phương pháp, review id, sentiment gold, sentiment máy (dòng chưa có nhãn ghi chữ <code>"unlabeled"</code> thay vì NaN để CSV dễ đọc).</p>

=== 336-339
<p>Bốn cột khía cạnh dạng chuỗi ngăn <code>;</code>: gold khen/chê (đã sắp xếp) và máy khen/chê. Giữ cả hai phía để đọc báo cáo thấy ngay máy bỏ gì.</p>

=== 340-345
<p>Ba cột chẩn đoán cuối: danh sách cặp thiếu/thừa (có tiền tố phía), chuỗi loại lỗi, và trích review 300 ký tự đầu sau khi gộp khoảng trắng/xuống dòng. Giới hạn 300 để báo cáo không phình. Hai dòng cuối đóng dict và lời gọi <code>rows.append</code>.</p>

=== 346
<p>Trả DataFrame 200 dòng khi có 2 phương pháp × 100 review. <code>eval_report.write_markdown</code> đếm lỗi trên bảng này để viết mục "Khía cạnh hay bị bỏ sót / gán thừa" và "Ca sai sentiment".</p>

=== 349-354
<p>Hàm điều phối chính. <code>output_dir</code>/<code>figure_dir</code> là tham số tuỳ chọn để ghi đè đường dẫn trong config, dùng cho test và cho chạy thử vào thư mục tạm. Trả bảng tóm tắt, hoặc bảng coverage nếu chỉ chẩn đoán.</p>

=== 355
<p>Đường dẫn nhãn tay: <code>labels.path</code>, mặc định <code>data/samples/hand_labels.csv</code>. Dùng <code>Path</code> để ghép đường dẫn an toàn trên Windows.</p>

=== 356
<p>Sáu khía cạnh lấy từ <code>llm.aspects</code>, mặc định viết cứng đúng 6 tên. Danh sách này vừa dùng để kiểm gold, vừa dùng cho bảng per-aspect.</p>

=== 357
<p>Cache LLM: <code>llm.cache</code>, mặc định <code>llm_cache_pydantic.jsonl</code>. Đây là cache đã commit trong <code>data/processed/</code>; không gọi API ở bước đánh giá.</p>

=== 358
<p>Mục <code>eval</code> trong config, có thể rỗng. Các khoá con đọc ngay dưới với giá trị mặc định.</p>

=== 359-360
<p>Thư mục ra: ưu tiên tham số truyền vào, rồi <code>eval.output_dir</code> / <code>eval.figure_dir</code>, cuối cùng là <code>reports/evaluation</code> và <code>figures/evaluation</code>. Test <code>test_run_uses_defaults_from_config</code> kiểm đúng hai mặc định này.</p>

=== 361-363
<p>Ba tham số số: 2.000 lần bootstrap, tối thiểu 100 nhãn tay, seed 42. Seed lấy ở cấp config (không phải <code>eval.seed</code>) để mọi bước dùng chung một hạt giống.</p>

=== 365
<p>Đọc và kiểm gold. Mọi lỗi dữ liệu dừng ở đây trước khi tốn công chấm.</p>

=== 366
<p>Ghép baseline và LLM thành một bảng dài, thêm cột <code>method</code>. <code>ignore_index=True</code> để index 0..199, tránh trùng index giữa hai bảng.</p>

=== 368-373
<p>Cổng an toàn. Nếu có lý do: dựng bảng coverage, ghi <code>eval_diagnostics.csv/.md</code>, in ra console, rồi <b>trả về sớm</b>. Không ghi metric, không vẽ hình, không đụng file cũ. Test kiểm thư mục chỉ có đúng hai file chẩn đoán.</p>

=== 375-377
<p>Gold thiếu lớp chỉ cảnh báo, không dừng. In tiền tố <code>[EVAL] Cảnh báo:</code> để người chạy thấy ngay; cùng câu đó được chép vào <code>eval_errors.md</code>.</p>

=== 379-382
<p>Bốn túi gom kết quả: danh sách dict tóm tắt, các dòng per-class, các dòng per-aspect, và dict ma trận theo phương pháp. Tách ra để cuối hàm ghi từng file một lần.</p>

=== 383-385
<p>Lặp đúng hai phương pháp theo thứ tự cố định <code>("baseline", "llm")</code>, không theo thứ tự xuất hiện trong bảng. <code>reset_index(drop=True)</code> là bắt buộc để mặt nạ boolean trong <code>score_method</code> thẳng hàng với gold.</p>

=== 386-389
<p><code>score_method</code> trả dict gồm cả hai khoá không phải số. <code>pop</code> chúng ra trước khi thêm vào <code>summaries</code>, nhờ vậy bảng tóm tắt chỉ còn số và chuỗi. Bảng per-class được gán thêm cột <code>method</code>.</p>

=== 390-407
<p>Dựng lại tập cặp gold/máy trên các dòng đã chấm (cùng logic với <code>score_method</code>), rồi gọi <code>per_aspect_scores</code> với 6 khía cạnh. Đoạn này lặp lại việc tách cặp hai lần, có thể gom vào một hàm phụ, nhưng hiện tại vẫn đúng và dễ đọc theo từng bước.</p>

=== 409-412
<p>Ghép thành bốn bảng: <code>summary</code> (2 dòng), <code>per_class</code> (6 dòng), <code>per_aspect</code> (12 dòng), <code>per_review</code> (200 dòng).</p>

=== 414-418
<p>Tạo thư mục rồi ghi bốn CSV, đều <code>index=False, encoding="utf-8"</code>. Đây là các file đã commit trong <code>reports/evaluation/</code>; chạy lại cho cùng số vì seed cố định.</p>

=== 419-420
<p>Ghi <code>eval_errors.md</code> (bảng tổng hợp + lỗi khía cạnh + ca sai sentiment) và vẽ <code>eval_confusion_matrices.png</code> (hai ma trận cạnh nhau). Hai việc này nằm ở <code>eval_report.py</code>.</p>

=== 422-423
<p>Nếu lần chạy trước là chẩn đoán, hai file <code>eval_diagnostics.*</code> vẫn còn; code không xoá mà cảnh báo chúng không phản ánh lần chạy này. Ngược lại, khi chạy chẩn đoán, <code>eval_report.print_diagnostics</code> cảnh báo artifact metric cũ còn sót.</p>

=== 425-426
<p>In phân bố nhãn tay: <code>{'positive': 85, 'mixed': 15}</code> với gold thật. Dòng này giúp phát hiện ngay nếu file nhãn bị đổi.</p>

=== 427-435
<p>Mỗi phương pháp một dòng log: coverage, accuracy kèm CI, kappa, macro-F1 kèm CI, aspect micro-F1. Số in ra khớp <code>eval_summary.csv</code>; đây là thứ hay được trích khi vấn đáp.</p>

=== 436-437
<p>In nơi đã ghi và trả bảng tóm tắt cho người gọi (pipeline dùng để biết bước đã xong).</p>

=== 440-447
<p><code>main()</code> cho chạy độc lập. Bốn tham số: <code>--config</code> (mặc định <code>configs/sydney.yaml</code>), <code>--gold</code>, <code>--output-dir</code>, <code>--figure-dir</code>. Chỉ <code>--gold</code> ghi đè config, ba cái còn lại truyền thẳng vào <code>run</code>.</p>

=== 449-452
<p>Đọc config qua <code>load_config</code> (đã kiểm khoá và chuẩn hoá ngày). Nếu có <code>--gold</code>, ghi vào <code>config["labels"]["path"]</code> bằng <code>setdefault</code> để không lỗi khi mục <code>labels</code> chưa có. Rồi gọi <code>run</code>.</p>

=== 455-456
<p>Chỉ chạy <code>main()</code> khi gọi trực tiếp. Import từ <code>run_pipeline</code> hay test không kích hoạt argparse.</p>

--- flow
## Đọc và ghép dữ liệu
fn 0 349 | run | Điều phối bước đánh giá
st 1 355 | Đường dẫn và tham số | labels, cache, eval, seed
st 1 365 | load_gold | 100 nhãn tay, chặn dữ liệu hỏng
st 1 366 | Dựng dự đoán | baseline + LLM, cùng schema
## Cổng an toàn
fn 0 120 | diagnostic_reasons | Gold &lt; 100 hoặc cache thiếu
fn 0 135 | scoring_warnings | Gold thiếu lớp, chỉ cảnh báo
## Chấm điểm
fn 0 191 | score_method | Một phương pháp, 27 khoá
st 1 203 | Cắt dòng có nhãn | coverage
st 1 208 | Ma trận + macro | confusion_matrix, macro_f1
st 1 211 | Bootstrap | macro-F1, kappa, aspect F1
st 1 217 | Accuracy | Wilson cho tỷ lệ đúng
st 1 227 | Cặp khía cạnh | tách khen/chê, micro-F1
st 1 256 | Trả dict | tách per_class và matrix
fn 0 287 | per_aspect_scores | Tách theo 6 khía cạnh
fn 0 304 | per_review_frame | Bảng lỗi từng review
## Ghi báo cáo
st 1 414 | Bốn CSV | summary, perclass, aspects, per_review
st 1 419 | Markdown + hình | eval_report.py
chips 1 | metrics:58 confusion_matrix ; metrics:118 wilson_interval ; metrics:133 bootstrap_interval ; eval_report:135 write_markdown ; eval_report:217 plot_confusion

--- review
mid | per_review_frame vỡ nếu thiếu dòng dự đoán | Nếu bảng <code>predictions</code> không có đủ <code>review_id</code> của gold, <code>reindex</code> tạo NaN ở cột khía cạnh và <code>list(NaN)</code> ném <code>TypeError: 'float' object is not iterable</code> (đã chạy thử với baseline bỏ dòng cuối). Trong pipeline không xảy ra vì <code>llm_predictions</code> luôn phát đủ 100 dòng.
mid | score_method phụ thuộc index ngầm | <code>gold.loc[scored]</code> dùng mặt nạ boolean của <code>predicted</code>; nếu index hai bên lệch, pandas ném <code>AssertionError</code> (đã chạy thử bằng <code>set_index(range(1, 101))</code>). <code>run</code> gọi <code>reset_index</code> nên an toàn; chỗ gọi ngoài phải giữ index 0..n−1.
mid | Nhánh chấm một phần gần như không chạy | Chỉ cần một nhãn LLM thiếu là <code>diagnostic_reasons</code> chặn và <code>run</code> trả sớm, nên <code>eval_summary.csv</code> luôn có coverage 1,000 cho cả hai. Logic coverage trong <code>score_method</code> chỉ dùng khi gọi trực tiếp (test). Vế <code>len(llm) != len(gold)</code> cũng không bao giờ đúng trong pipeline.
low | Tham số aspects không dùng | <code>score_method</code> nhận <code>aspects</code> nhưng không đọc; chỉ <code>per_aspect_scores</code> dùng. Tham số thừa, không sai kết quả.
ok | Cổng an toàn và không ghi đè | Gold &lt; 100 hoặc cache thiếu thì chỉ ghi chẩn đoán; gold thiếu lớp chỉ cảnh báo; file metric cũ không bị xoá âm thầm mà có cảnh báo artifact cũ.
mid | Báo cáo tự nhận nhãn tay không độc lập | <code>PROMPT_REUSE_NOTE</code> ở <code>eval_report.py</code> nói gold đã dùng để rà prompt, nên accuracy/F1 chỉ là tham khảo nội bộ. Code không kiểm chứng được điều này; khi vấn đáp nên chủ động nói rõ.
low | load_gold không kiểm language | Cột <code>language</code> chỉ cần tồn tại; giá trị rỗng hay lạ vẫn qua và có thể kéo <code>language_accuracy</code> xuống. Dữ liệu hiện tại toàn <code>"en"</code> nên chỉ số bằng 1,000.

--- qa
? Vì sao phải có cổng min_gold_size và cổng cache?
<p>Vì 100 review là mẫu nhỏ; chấm trên 3 dòng rồi công bố accuracy sẽ gây hiểu nhầm. <code>diagnostic_reasons</code> (<a href="#evaluate-L120">dòng 120</a>) chặn khi gold &lt; 100 hoặc cache LLM thiếu bất kỳ nhãn nào; khi đó <code>run</code> chỉ ghi <code>eval_diagnostics.*</code> và trả sớm, không đụng file metric cũ.</p>
? Gold không có lớp negative mà vẫn công bố F1, có gian không?
<p>Không giấu: <code>scoring_warnings</code> in cảnh báo và chép vào <code>eval_errors.md</code>; <code>sentiment_macro_f1_labels</code> = 2 cho biết trung bình chỉ trên positive và mixed. Lớp negative vẫn có dòng trong <code>eval_perclass.csv</code> với support 0 và F1 0.</p>
? Accuracy 0,970 so với baseline 0,870, chênh có ý nghĩa không?
<p>Hai khoảng Wilson chồng nhau một chút ([0,915; 0,990] và [0,790; 0,922]), nên chỉ nhìn accuracy thì chưa dứt khoát. Kappa mạnh hơn: LLM [0,706; 1,000] không chứa 0, baseline [−0,019; 0,534] thì chứa 0. Kết luận an toàn: LLM hơn rõ về đồng thuận vượt mức ngẫu nhiên.</p>
? Vì sao baseline và LLM dùng chung seed bootstrap?
<p>Để hai phương pháp được bốc trên cùng các bộ chỉ số, so sánh công bằng và tái lập được từng chữ số (<a href="#metrics-L142">metrics dòng 142</a>). Hạn chế: code không tính khoảng cho hiệu số LLM − baseline, nên không kết luận được ý nghĩa thống kê của chênh lệch chỉ từ hai khoảng riêng.</p>
? baseline_predictions chỉ nhận hai cột, vì sao?
<p>Để baseline không nhìn thấy nhãn tay (<a href="#evaluate-L146">dòng 146</a>). Nếu truyền cả bảng gold, một sửa đổi vô tình trong baseline có thể dùng <code>sentiment</code> và làm mất tính đối chứng.</p>
? Nếu cache thiếu đúng một review thì chuyện gì xảy ra?
<p><code>llm_predictions</code> vẫn phát đủ 100 dòng, dòng thiếu có sentiment <code>None</code>. <code>diagnostic_reasons</code> thấy <code>isna().any()</code> nên trả lý do; <code>run</code> ghi bảng coverage (LLM 99/100) và dừng, không cập nhật <code>eval_summary.csv</code>. Test <code>test_run_partial_llm_cache_only_reports_coverage</code> kiểm đúng nhánh này.</p>
? Vì sao phải reset_index trước khi gọi score_method?
<p>Vì <code>score_method</code> dùng <code>gold.loc[scored]</code> với <code>scored</code> lấy từ <code>predicted</code>; hai index phải trùng. <code>run</code> gọi <code>reset_index(drop=True)</code> để cả hai về 0..n−1 (<a href="#evaluate-L384">dòng 384</a>). Gọi trực tiếp mà lệch index sẽ lỗi, không tự căn.</p>
