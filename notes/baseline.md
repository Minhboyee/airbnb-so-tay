--- meta
title: baseline.py
lead: Phương pháp đối chứng của bước 4c: đoán sentiment và khía cạnh khen/chê của review chỉ bằng regex từ khoá tiếng Anh, không gọi LLM, không nhìn nhãn tay. Vào DataFrame <code>review_id</code> + <code>comments</code>, ra cùng định dạng với nhãn LLM để <code>evaluate.py</code> chấm hai bên trên cùng 100 nhãn tay. Kết quả thật (<code>reports/evaluation/eval_summary.csv</code>): accuracy 0,870, macro-F1 0,622, kappa 0,270, aspect micro-F1 0,602; precision khía cạnh cao (0,934) nhưng recall thấp (0,444).

--- blocks
=== 1-9
<p>Docstring nói ba điều cần nhớ:</p>
<ul><li><b>Vai trò:</b> mốc so sánh. Nếu LLM không hơn rõ một bộ luật vài chục từ khoá thì không đáng tiền gọi API. Người gọi duy nhất là <a href="#evaluate-L146">evaluate.baseline_predictions</a>.</li>
<li><b>Không dùng nhãn tay để thiết kế luật</b> (docstring của <code>tests/test_baseline.py</code> ghi rõ: test dùng ví dụ tự tạo). Nếu chỉnh regex theo 100 review gold thì so sánh với LLM sẽ không công bằng.</li>
<li><b>Tất định:</b> cùng đầu vào luôn cho cùng kết quả, không có seed hay mạng. <code>language</code> luôn là <code>"en"</code>.</li></ul>

=== 11
<p>Tắt luật E501 (dòng quá dài) của Ruff cho cả file, vì các regex ở dưới dài hơn giới hạn dòng và cắt ra thì khó đọc hơn.</p>

=== 13
<p>Chỉ cần pandas: toàn bộ xử lý là các phép chuỗi vector hoá <code>.str.contains</code>, <code>.str.replace</code> trên cả cột.</p>

=== 15-41
<p>Bảng luật: mỗi khía cạnh (đúng 6 khía cạnh của <code>llm.aspects</code> trong yaml) có một cặp regex <code>(khen, chê)</code>. Vài điểm hay bị hỏi:</p>
<ul><li><code>\b</code> là ranh giới từ: <code>\bclean\b</code> không khớp trong <code>unclean</code>, nên "unclean" chỉ rơi vào vế chê.</li>
<li><code>location</code> khen phải có tính từ đứng ngay trước (<code>great location</code>) hoặc cụm vị trí (<code>close to</code>, <code>walking distance</code>). "The location was fantastic" (tính từ đứng sau) không khớp vế đầu; review 6778680 vẫn được tính nhờ cụm <code>walking distance</code>.</li>
<li><code>host</code> dùng <code>.{0,35}</code>: từ "host/owner" và một tính từ khen cách nhau tối đa 35 ký tự, theo cả hai chiều. Review gọi chủ nhà bằng tên ("Di was very quick to respond") thì không có chữ host, nên bị bỏ sót. Vì vậy baseline bỏ sót <code>positive:host</code> 43 lần (<code>eval_errors.md</code>).</li>
<li><code>amenities</code> chỉ có vài cụm cứng (<code>fully equipped</code>, <code>comfy bed</code>, <code>no wifi</code>…), nên recall chỉ 0,233 (14/60, <code>eval_aspects.csv</code>).</li></ul>
<p>Hệ quả chung: luật hẹp nên khi đã khớp thì thường đúng (precision từng khía cạnh 0,67–1,0) nhưng bỏ sót nhiều.</p>

=== 43-44
<p>Từ khen chung không gắn khía cạnh. Chỉ dùng để quyết định có "ý khen" hay không, không sinh ra khía cạnh nào. Lưu ý <code>great</code>, <code>good</code> khớp cả trong "not great": baseline không xử lý phủ định cho các từ này.</p>

=== 45-48
<p>Từ chê chung. Chỉ cần một từ như <code>bad</code> là review có "ý chê". Ví dụ thật: review 1210501524180141784 gold là positive, có câu "got rid of my bad mood", baseline đọc thấy <code>bad</code> nên đoán mixed. Đây là ca positive→mixed duy nhất của baseline.</p>

=== 51-56
<p>Hàm công khai duy nhất. Luật sentiment tóm trong docstring: có khen và chê thì <code>mixed</code>; chỉ chê thì <code>negative</code>; còn lại (chỉ khen, hoặc không khớp từ nào) là <code>positive</code>. Như vậy review trung tính hay review chê bằng từ không có trong danh sách đều mặc định thành positive.</p>

=== 57-59
<p>Chấp nhận cả tên cột <code>review_id</code> (file nhãn tay, cache LLM) lẫn <code>id</code> (file <code>reviews.csv</code> gốc của Inside Airbnb). <code>id_column not in reviews</code> kiểm tên cột (toán tử <code>in</code> trên DataFrame xét cột). Thiếu thì <code>ValueError</code>.</p>

=== 61-63
<p>Đổi ID sang chuỗi (ID review Airbnb dài 18–19 chữ số, giữ dạng chuỗi để không mất chữ số và khớp với cache) rồi chặn ID trùng. Trùng ID thì khi ghép với gold theo <code>review_id</code> sẽ nhân dòng, nên dừng sớm.</p>

=== 65-69
<p>Chuẩn hoá văn bản: <code>fillna("")</code> để review rỗng không lỗi, rồi chữ thường. Sau đó ba phép thay xử lý phủ định, <b>chỉ cho hai khía cạnh</b>:</p>
<ul><li>"not/wasn't/isn't clean" → <code>dirty</code> (rơi vào vế chê cleanliness và từ chê chung).</li>
<li>"not noisy" → <code>quiet</code> (thành khen noise).</li>
<li>"no noise", "without real noise" → xoá hẳn. Tức là "no noise" không được tính là khen noise; test <code>"No noise and no real issues"</code> ra positive, không khía cạnh nào.</li></ul>
<p>Mọi phủ định khác không được xử lý. Chạy thử: <code>"Host was not helpful"</code> → khen <code>host</code>; <code>"The place was not quiet"</code> → khen <code>noise</code>.</p>

=== 71-75
<p>Hai bảng cờ True/False: mỗi dòng một review, mỗi cột một khía cạnh. Giữ <code>index</code> của đầu vào để các phép <code>|</code>, <code>&amp;</code> sau đó căn đúng dòng, kể cả khi index không phải 0..n-1 (test dùng index 10, 20).</p>
<p>Một review có thể vừa khen vừa chê cùng một khía cạnh: test <code>"A helpful host but rude owner"</code> cho <code>host</code> ở cả hai phía.</p>

=== 77-81
<p>Quyết định sentiment:</p>
<ul><li><code>has_positive</code> = khớp ít nhất một khía cạnh khen hoặc một từ khen chung.</li>
<li><code>has_negative</code> tương tự cho chê.</li>
<li>Mặc định <code>positive</code>, rồi ghi đè: chỉ chê → <code>negative</code>; cả hai → <code>mixed</code>.</li></ul>
<p>Vì review Airbnb gần như luôn có một từ khen ("great", "nice"), chỉ cần một từ chê là thành mixed; thiếu từ chê trong danh sách thì thành positive. Trên gold: baseline đoán 96 positive, 4 mixed, 0 negative; đúng 3/15 mixed (ma trận chạy lại từ <code>evaluate.run</code>). Ví dụ 600307857792014827: "sound isolation is not great and had cockroach problem" không có từ chê nào trong danh sách, nên ra positive.</p>

=== 83-97
<p>Dựng kết quả theo đúng thứ tự dòng đầu vào. <code>.to_numpy()</code> bỏ index cũ để DataFrame mới có index 0..n-1. Danh sách khía cạnh lấy theo thứ tự khoá của <code>ASPECT_PATTERNS</code> (location, cleanliness, host…), không theo thứ tự xuất hiện trong review. <code>strict=True</code> trong <code>zip</code> bảo đảm số cờ bằng số khía cạnh. Đầu ra cùng tên cột với nhãn LLM nên <a href="#evaluate-L146">evaluate.py</a> ghép thẳng.</p>

--- flow
## Lúc import
st 0 16 | ASPECT_PATTERNS | 6 khía cạnh × (regex khen, regex chê)
st 0 44 | GENERAL_POSITIVE / NEGATIVE | Từ khen/chê chung
## Dự đoán
fn 0 51 | predict_reviews | Luật cố định, không nhìn gold
st 1 57 | Kiểm cột, ID trùng | Sai thì ValueError
st 1 66 | Chuẩn hoá chữ | Chữ thường, đảo "not clean", "not noisy"
st 1 73 | Cờ khía cạnh | str.contains từng regex
st 1 77 | Sentiment | Khen+chê → mixed; chỉ chê → negative
st 1 83 | Dựng kết quả | Cùng cột với nhãn LLM
chips 1 | evaluate:146 baseline_predictions ; evaluate:191 score_method

--- review
bug | Dấu nháy cong không khớp | Regex viết <code>didn't</code>, <code>doesn't</code> bằng nháy thẳng. Chạy thử: <code>"The host didn’t respond"</code> (nháy cong ’, kiểu iPhone hay gõ) ra positive, không chê host; bản nháy thẳng ra negative. Gold có 23/100 review chứa ’ nhưng không câu nào rơi đúng hai cụm này, nên số trên gold không đổi.
mid | Phủ định chỉ cho clean/noisy | "not helpful", "not quiet", "not great" vẫn được tính là khen (đã chạy thử). Một phần các ca mixed→positive đến từ đây, ví dụ 600307857792014827 ("not great").
mid | Mặc định positive | Review không khớp từ nào được gán positive. Đoán toàn positive trên gold đã được accuracy 0,85, nên accuracy 0,870 của baseline chỉ hơn mốc này 2 điểm.
ok | Không dùng gold để chỉnh luật | Test chỉ dùng câu tự tạo; luật tất định, không seed, không mạng.

--- qa
? Baseline hoạt động thế nào, vì sao cần nó?
<p>Regex từ khoá: mỗi khía cạnh một mẫu khen và một mẫu chê, cộng hai danh sách từ khen/chê chung. Có cả khen và chê thì mixed, chỉ chê thì negative, còn lại positive (<a href="#baseline-L77">dòng 77–81</a>). Nó là mốc: LLM phải hơn rõ cách rẻ nhất này thì mới đáng dùng.</p>
? Vì sao baseline accuracy 0,87 mà kappa chỉ 0,27?
<p>Gold có 85/100 positive. Đoán toàn positive đã được 0,85 và kappa 0. Baseline gần như đoán toàn positive (96/100), chỉ nhận đúng 3/15 mixed, nên phần đồng thuận vượt mức ngẫu nhiên rất ít. Kappa phạt đúng điều này.</p>
? Vì sao precision khía cạnh cao mà recall thấp?
<p>Luật hẹp: khi khớp "very clean" thì gần như chắc đúng (precision 0,934), nhưng mọi cách nói khác ("Di was very quick to respond", "everything worked") đều bị bỏ qua. Recall 0,444: 114 cặp đúng, bỏ sót 143 (<code>eval_summary.csv</code>).</p>
? Baseline có xử lý phủ định không?
<p>Chỉ ba mẫu: "not clean" → dirty, "not noisy" → quiet, "no noise" bị xoá (<a href="#baseline-L67">dòng 67–69</a>). "Host was not helpful" vẫn bị tính là khen host.</p>
? Có khi nào baseline đoán negative không?
<p>Có, khi chỉ khớp từ chê mà không có từ khen nào, ví dụ test "The room was not clean". Trên 100 gold nó không đoán negative lần nào, và gold cũng không có review negative.</p>
