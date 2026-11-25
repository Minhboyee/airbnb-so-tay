--- meta
title: eval_report.py
lead: Phần "ra giấy" của bước đánh giá: ghi <code>eval_errors.md</code>, ghi báo cáo chẩn đoán khi chưa đủ điều kiện chấm, in log console và vẽ hình ma trận nhầm lẫn. Không tính toán (việc đó ở <code>metrics.py</code>), không đọc gold/cache (việc đó ở <code>evaluate.py</code>). Hai điểm dễ bị hỏi: báo cáo chẩn đoán không tự xoá metric cũ (do <code>evaluate.run</code> trả sớm mới không ghi), và câu caveat <code>PROMPT_REUSE_NOTE</code> nói nhãn tay đã dùng rà prompt nên kết quả chỉ là tham khảo nội bộ.

--- blocks
=== 1-12
<p>Docstring nói rõ vị trí và ranh giới:</p>
<ul><li>Vị trí: <code>evaluate.py</code> tính số rồi gọi module này để ghi file, in console và vẽ hình.</li>
<li>Vào: DataFrame đã tính, danh sách lý do chưa chấm được, thư mục ra.</li>
<li>Ra: <code>eval_diagnostics.csv/.md</code> (chế độ chẩn đoán), <code>eval_errors.md</code> (chế độ đầy đủ), <code>eval_confusion_matrices.png</code>, và các dòng <code>[EVAL] ...</code>.</li>
<li>Không import <code>evaluate</code> nên không có vòng phụ thuộc; chỉ import <code>LABELS</code> từ <code>metrics</code>.</li></ul>

=== 14-17
<p><code>Counter</code> để đếm số lần một cặp khía cạnh bị bỏ sót/gán thừa; <code>Path</code> cho đường dẫn; <code>from __future__ import annotations</code> cho cú pháp kiểu mới trên Python 3.10.</p>

=== 19-22
<p>numpy cho mảng ma trận và toạ độ chữ; pandas cho bảng; matplotlib dùng <code>Figure</code> + <code>FigureCanvasAgg</code> trực tiếp, <b>không</b> dùng <code>pyplot</code>. Nhờ vậy chạy được trên CI không có màn hình và không rò trạng thái toàn cục giữa các lần vẽ.</p>

=== 24
<p><code>LABELS</code> quyết định thứ tự hàng/cột của hình và thứ tự dòng trong bảng support. Phải khớp <code>metrics.py</code> và <code>evaluate.py</code>.</p>

=== 26-33
<p>Năm file số liệu của lần chấm đầy đủ. Hằng này dùng để phát hiện "artifact cũ còn sót" khi lần chạy này chỉ là chẩn đoán. Không có <code>eval_diagnostics.*</code> trong danh sách vì đó là file của chế độ ngược lại.</p>

=== 34-38
<p>Câu caveat in vào mọi báo cáo: bộ nhãn tay đã được dùng để rà lại prompt của LLM, nên nhãn tay và nhãn máy không độc lập; kết quả chỉ là tham khảo nội bộ. Đây là tự khai của nhóm, code không kiểm chứng được. Khi vấn đáp nên chủ động nói: accuracy 0,970 là "đồng thuận với nhãn tay", không phải bằng chứng chất lượng độc lập.</p>

=== 41-45
<p>Liệt kê những file metric/hình <b>đang tồn tại</b>: 5 file trong <code>output_dir</code> cộng hình trong <code>figure_dir</code>, lọc bằng <code>path.exists()</code>. Hàm chỉ đọc, không xoá. <code>print_diagnostics</code> gọi hàm này để cảnh báo; việc không ghi đè là nhờ <code>evaluate.run</code> trả sớm trước khi gọi các hàm ghi metric.</p>

=== 48-53
<p>Chữ ký ghi chẩn đoán: bảng coverage, support theo lớp, danh sách lý do, thư mục ra. Không có tham số <code>figure_dir</code> vì chế độ chẩn đoán không vẽ hình.</p>

=== 54-58
<p>Docstring nói đầu vào/đầu ra. "Thay cho metric" nghĩa là khi chưa đủ điều kiện, báo cáo này là thứ duy nhất được ghi; không có accuracy/F1.</p>

=== 59-60
<p>Tạo thư mục nếu chưa có rồi ghi <code>eval_diagnostics.csv</code>, bảng coverage thô, mở bằng Excel/pandas được. Luôn ghi CSV trước để người đọc máy có dữ liệu, kể cả khi bước ghi Markdown phía dưới lỗi.</p>

=== 62-66
<p>Bắt đầu dựng Markdown. Dòng đầu là tiêu đề; dòng thứ ba in đậm câu "Không công bố accuracy/F1" để người mở file thấy ngay, tránh đọc nhầm bảng coverage thành điểm số.</p>

=== 67-71
<p>Mục "Lý do": mỗi lý do từ <code>diagnostic_reasons</code> thành một gạch đầu dòng, cộng thêm câu caveat prompt. Với gold 3 dòng, lý do đầu là "Có 3/100 review nhãn tay tối thiểu...".</p>

=== 72-74
<p>Câu tuyên bố không ghi/cập nhật 5 file metric và hình trong lần chạy này. Đây là <b>mô tả hành vi của người gọi</b>, không phải code cưỡng chế: bản thân <code>write_diagnostics</code> không xoá file cũ. Nếu ai gọi thẳng hàm này sau một lần chấm đầy đủ, metric cũ vẫn nằm đó.</p>

=== 75-85
<p>Hai bảng Markdown: support nhãn tay (3 dòng theo <code>LABELS</code>, kể cả lớp 0) và phần đầu bảng coverage 8 cột. Cột coverage in 3 chữ số thập phân; các cột nhãn là số đếm dự đoán, không phải tỷ lệ. Dòng cuối đóng list <code>lines</code>.</p>

=== 86-99
<p>Mỗi phương pháp một dòng bảng, định dạng bằng <code>.format</code> (không phải f-string) để dễ đọc khi có nhiều cột. Các khoá <code>predicted_positive/mixed/negative/unlabeled</code> lấy từ <code>coverage_table</code>. Số coverage in <code>{:.3f}</code>, không dùng <code>format_rate</code>.</p>

=== 100
<p>Ghi file UTF-8. Dùng <code>write_text</code> một lần thay vì mở file và ghi từng dòng, nên hoặc có cả file hoặc không có gì (trong phạm vi một lần ghi).</p>

=== 103-105
<p>In chẩn đoán ra console, bắt đầu bằng câu nhắc "không công bố accuracy/F1". Console là nơi người chạy pipeline nhìn trước, nên phải nói rõ ngay.</p>

=== 106-107
<p>In từng lý do với tiền tố <code>[EVAL] Lý do:</code>. Không in bảng metric vì không có.</p>

=== 108-113
<p>Mỗi phương pháp một dòng: coverage dạng phần trăm, số đã chấm / tổng, và phân bố nhãn dự đoán. Với cache thiếu hoàn toàn: baseline 100%, LLM 0% (0/100).</p>

=== 114
<p>In câu caveat prompt. Câu này lặp lại trong file Markdown; in ở console để người chạy không bỏ qua.</p>

=== 115-119
<p>Gọi <code>stale_metric_paths</code>. Nếu có file metric cũ, in cảnh báo kèm tên file; đây là cơ chế duy nhất phát hiện "báo cáo cũ không phản ánh lần chạy này". Cuối cùng in nơi đã ghi chẩn đoán.</p>

=== 122-124
<p>Định dạng tỷ lệ cho báo cáo: NaN thành <code>"n/a"</code>, còn lại 3 chữ số thập phân. Cách nhận NaN là <code>value != value</code> (NaN khác chính nó). Cách này chỉ đúng với NaN kiểu float; <code>None</code> sẽ ném <code>TypeError</code> khi format (đã chạy thử), trong pipeline không xảy ra.</p>

=== 127-132
<p>Lấy một khoá số từ dòng summary, chịu được dòng thiếu khoá hoặc <code>None</code>: trả NaN để <code>format_rate</code> in "n/a". Mục đích theo docstring là không vỡ fixture/báo cáo cũ thiếu cột; hiện chỉ ba cột CI macro-F1 đi qua hàm này. Các cột khác vẫn đọc trực tiếp, nên tương thích chỉ là một phần.</p>

=== 135-140
<p>Chữ ký ghi báo cáo đầy đủ: bảng summary (mỗi phương pháp một dòng), bảng per-review, đường dẫn file, và danh sách cảnh báo tuỳ chọn (ví dụ gold thiếu lớp âm).</p>

=== 141-145
<p>Docstring mô tả ba phần của file: bảng tổng hợp metric, khía cạnh hay bị bỏ sót/gán thừa, và các ca sai sentiment.</p>

=== 146-153
<p>Phần đầu file Markdown: tiêu đề; số review nhãn tay lấy từ dòng đầu của summary; hai câu nhắc "số liệu là đồng thuận, không phải chân lý" và "CI 95% vì n nhỏ"; câu caveat prompt. Bốn dòng này là những gì giảng viên hay hỏi khi mở báo cáo.</p>

=== 154-155
<p>Nếu có cảnh báo (gold thiếu lớp), chèn mục "## Cảnh báo" với từng gạch đầu dòng. Với gold thật: "Bộ nhãn tay không có mẫu lớp negative...".</p>

=== 157-163
<p>Tiêu đề bảng tổng hợp 8 cột: phương pháp, coverage, accuracy [CI], macro-F1 [CI], kappa [CI], aspect micro-F1 [CI], aspect khớp hệt, language accuracy. Cột "Phủ" là coverage; các cột CI in dạng <code>[thấp; cao]</code>. Dòng cuối mở vòng lặp qua từng phương pháp.</p>

=== 164-185
<p>Mỗi phương pháp một dòng. Dùng <code>format_rate</code> cho mọi số, riêng ba cột macro-F1 đi qua <code>_row_value</code> để chịu được summary cũ thiếu cột. Số thật: baseline <code>1.000 | 0.870 [0.790; 0.922] | 0.622 [0.462; 0.763] | 0.270 [-0.019; 0.534] | 0.602 [0.533; 0.667] | 0.240 | 1.000</code>.</p>

=== 187-197
<p>Mục khía cạnh: mỗi phương pháp một tiểu mục. Với mỗi dòng review, tách chuỗi <code>missing_aspects</code>/<code>extra_aspects</code> theo <code>;</code>, đếm bằng <code>Counter</code>, in theo thứ tự nhiều đến ít bằng <code>most_common()</code>. Baseline bỏ sót <code>positive:host</code> 43 lần, <code>positive:amenities</code> 39; LLM bỏ sót <code>positive:amenities</code> 16. Không có lỗi thì in "không có".</p>

=== 199-213
<p>Mục "Ca sai sentiment": lọc các dòng có <code>error_types</code> chứa <code>"sentiment:"</code>, tức chỉ ca sai nhãn, không gồm <code>unlabeled</code>. Mỗi ca in tiêu đề <code>method · review_id: gold → máy</code>, hai dòng khía cạnh gold/máy, dòng thiếu/thừa, và trích review. Ký tự <code>∅</code> thay cho danh sách rỗng. Có 16 ca: 13 của baseline, 3 của LLM.</p>

=== 214
<p>Ghi toàn bộ Markdown một lần, UTF-8. Tên file do <code>evaluate.run</code> truyền vào: <code>eval_errors.md</code>.</p>

=== 217-218
<p>Vẽ ma trận nhầm lẫn cho từng phương pháp cạnh nhau và lưu PNG. Vào là dict <code>method → ma trận 3×3</code>; ra là file ảnh.</p>

=== 219-220
<p>Tạo <code>Figure</code> kích thước 10,4×4,4 inch, nền trắng, và gắn <code>FigureCanvasAgg</code>, backend không cần màn hình. Không gọi <code>plt.show()</code> hay <code>plt.savefig()</code>.</p>

=== 221-222
<p>Mỗi phương pháp một ô: <code>add_subplot(1, len(matrices), position)</code>, vị trí bắt đầu từ 1. Với hai phương pháp: baseline trái, LLM phải, đúng thứ tự dict do <code>run</code> dựng.</p>

=== 223-228
<p><code>imshow</code> với bảng màu <code>Blues</code>, <code>vmin=0</code> để mọi ô cùng thang màu. Trục x là "Dự đoán", trục y là "Nhãn tay", nhãn tick theo <code>LABELS</code>, tiêu đề là tên phương pháp.</p>

=== 229
<p>Ngưỡng tô màu chữ: nửa giá trị lớn nhất của ma trận. Ô lớn hơn ngưỡng nền xanh đậm nên chữ trắng; ô nhỏ hơn nền nhạt nên chữ đen. Với ma trận LLM max 85, ngưỡng 42,5: ô 85 chữ trắng, ô 3 và 12 chữ đen.</p>

=== 230-240
<p>Ghi số vào từng ô: duyệt 3×3, lấy <code>int(matrix[row, column])</code>, đặt tại toạ độ (cột, hàng), chú ý thứ tự này vì <code>text(x, y)</code> nhận hoành trước tung. Màu chữ theo ngưỡng ở trên.</p>

=== 241
<p>Thêm thanh màu cho từng ô, <code>fraction=0.046, pad=0.04</code> để không chiếm chỗ của ma trận bên cạnh.</p>

=== 242
<p>Tiêu đề chung của cả hình: "Ma trận nhầm lẫn sentiment trên nhãn tay".</p>

=== 243
<p><code>tight_layout</code> để nhãn trục và tiêu đề không bị cắt khi lưu.</p>

=== 244
<p>Tạo thư mục cha của file ảnh nếu chưa có (ví dụ <code>figures/evaluation/</code> khi chạy trong thư mục tạm của test).</p>

=== 245
<p>Lưu PNG ở 165 dpi, nền trắng. File thật: <code>figures/evaluation/eval_confusion_matrices.png</code>, nhúng vào trang Lý thuyết/Đánh giá.</p>

--- flow
## Chẩn đoán
fn 0 48 | write_diagnostics | CSV + MD khi chưa chấm được
fn 0 41 | stale_metric_paths | Liệt kê file metric cũ còn sót
fn 0 103 | print_diagnostics | In lý do, coverage, cảnh báo
## Báo cáo đầy đủ
fn 0 135 | write_markdown | eval_errors.md
st 1 146 | Phần đầu | n_gold, caveat, cảnh báo
st 1 157 | Bảng tổng hợp | 8 cột kèm CI
st 1 187 | Khía cạnh thiếu/thừa | Counter, most_common
st 1 199 | Ca sai sentiment | trích review, 16 ca
fn 0 217 | plot_confusion | PNG hai ma trận
st 1 219 | Figure + Agg | không dùng pyplot
st 1 229 | Tô màu số | ngưỡng max/2
chips 1 | evaluate:368 run ; evaluate:419 gọi báo cáo ; metrics:58 confusion_matrix

--- review
mid | Chẩn đoán không tự bảo vệ metric cũ | Câu "Không ghi/cập nhật eval_summary.csv..." trong file .md là mô tả hành vi của <code>evaluate.run</code> (trả sớm), không phải code cưỡng chế. Gọi thẳng <code>write_diagnostics</code> sau một lần chấm đầy đủ sẽ để lại metric cũ mà không cảnh báo; cảnh báo chỉ có nếu gọi thêm <code>print_diagnostics</code>.
low | Tương thích ngược chỉ một phần | <code>_row_value</code> chỉ che ba cột CI macro-F1; các cột khác đọc trực tiếp. Thiếu <code>sentiment_accuracy_ci_low</code> vẫn <code>KeyError</code> (đã chạy thử); <code>format_rate(None)</code> ném <code>TypeError</code> vì chỉ nhận diện NaN kiểu float. Trong pipeline các cột luôn đủ và là float.
low | Không có test trực tiếp | Không có <code>tests/test_eval_report.py</code>; các hàm chỉ được kiểm gián tiếp qua <code>evaluate.run</code> (file tồn tại, Markdown chứa chuỗi cảnh báo, hình &gt; 0 byte).
ok | Không dùng pyplot | <code>Figure</code> + <code>FigureCanvasAgg</code> chạy headless, không rò trạng thái toàn cục, phù hợp CI.
mid | Câu caveat tự khai | <code>PROMPT_REUSE_NOTE</code> khẳng định gold đã dùng rà prompt; code không kiểm chứng được. Nếu đúng, accuracy/F1 không phải bằng chứng độc lập; báo cáo in câu này ở mọi lần chạy, nên trích dẫn kèm caveat.
low | Bộ lọc ca sai bỏ qua unlabeled | <code>str.contains("sentiment:")</code> không bắt dòng <code>unlabeled</code>. Trong pipeline không có dòng nào như vậy khi tới bước ghi báo cáo (cổng coverage đã chặn), nên số công bố không đổi.

--- qa
? Vì sao có hai chế độ ghi báo cáo?
<p>Vì chưa đủ điều kiện thì không được công bố accuracy/F1. <code>evaluate.run</code> gọi <code>write_diagnostics</code> + <code>print_diagnostics</code> khi gold &lt; 100 hoặc cache thiếu (<a href="#evaluate-L368">evaluate dòng 368</a>), và chỉ gọi <code>write_markdown</code> + <code>plot_confusion</code> khi đã qua cổng. Hai chế độ ghi vào hai bộ file khác nhau.</p>
? Báo cáo chẩn đoán có xoá metric cũ không?
<p>Không. <code>write_diagnostics</code> chỉ ghi <code>eval_diagnostics.csv/.md</code>. Metric cũ còn nguyên; <code>print_diagnostics</code> liệt kê chúng qua <code>stale_metric_paths</code> và in cảnh báo "giữ nguyên artifact cũ". Test <code>test_diagnostic_does_not_overwrite_old_metric_artifacts</code> kiểm đúng hành vi này.</p>
? Vì sao eval_errors.md ghi "nhãn tay và nhãn máy không độc lập"?
<p>Vì <code>PROMPT_REUSE_NOTE</code>: bộ 100 nhãn tay đã được dùng để rà prompt LLM, nên LLM có thể đã "học" cách gán của người. Accuracy 0,970 đo đồng thuận với nhãn tay, không đo chất lượng trên dữ liệu mới. Câu này được in ở cả file lẫn console.</p>
? Vì sao dùng Figure thay vì pyplot?
<p>Để chạy trên máy không có màn hình (CI, server) mà không cần backend GUI, và không để lại trạng thái toàn cục giữa các lần vẽ. <code>FigureCanvasAgg</code> gắn backend vẽ ảnh trực tiếp (<a href="#eval_report-L219">dòng 219</a>).</p>
? Ngưỡng tô màu trắng/đen trong hình là gì?
<p><code>threshold = matrix.max() / 2</code>; ô có số lớn hơn ngưỡng dùng chữ trắng, còn lại chữ đen (<a href="#eval_report-L229">dòng 229</a>). Với ma trận LLM max 85, ngưỡng 42,5.</p>
? Cột nào trong bảng tổng hợp đi qua _row_value, vì sao?
<p>Ba cột CI macro-F1 (cận dưới, cận trên; điểm cũng đi qua hàm). Chúng dùng <code>_row_value</code> để summary cũ thiếu cột in "n/a" thay vì <code>KeyError</code>; các cột còn lại đọc trực tiếp.</p>
? Gold thiếu lớp negative thì báo cáo thể hiện thế nào?
<p><code>evaluate.scoring_warnings</code> tạo cảnh báo, <code>write_markdown</code> chèn mục "## Cảnh báo", và bảng per-class vẫn có dòng negative với support 0, F1 0. Macro-F1 chỉ tính 2 lớp, thể hiện ở cột <code>sentiment_macro_f1_labels</code> = 2 trong summary.</p>
