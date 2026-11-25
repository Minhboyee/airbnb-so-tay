--- meta
title: config.py
lead: Cửa vào duy nhất của cấu hình. <code>run_pipeline.py</code> gọi <code>load_config</code> đúng một lần, nhận lại một dict đã kiểm khoá và chuẩn hoá; mọi bước sau chỉ đọc dict đó, không module nào tự mở file yaml. Hai việc chuẩn hoá quan trọng: đổi ngày về chuỗi <code>"YYYY-MM-DD"</code>, và chép ngưỡng giá <code>price_max_aud</code> sang tên chung <code>qa.price_max</code>.

--- blocks
=== 1-17
<p>Docstring đầu file nói ba điều cần nhớ khi vấn đáp:</p>
<ul><li><b>Vị trí:</b> được gọi trước bước 1, và cả khi chạy riêng một module (<code>python -m src.llm</code>…). Nhờ vậy mọi đường chạy đều thấy cùng một config đã chuẩn hoá.</li>
<li><b>Khoá bắt buộc</b> theo mẫu đề, và <b>khoá tuỳ chọn</b> của nhóm (<code>segments</code>, <code>qa.expected</code>, <code>labels</code>, <code>eval</code>): thiếu khoá tuỳ chọn thì bước tương ứng tự bỏ qua, xem <a href="#run_pipeline-L151">run_pipeline dòng 151</a>.</li>
<li><b>Hai phép chuẩn hoá</b> giải thích ở <a href="#config-L56">dòng 56–66</a>.</li></ul>

=== 19
<p><code>from __future__ import annotations</code> làm mọi chú thích kiểu (<code>dict[str, Any]</code>, <code>str | Path</code>) được lưu dưới dạng chuỗi, không bị Python tính lúc định nghĩa hàm. Nhờ vậy cú pháp <code>X | Y</code> chạy được cả trên Python 3.10, phiên bản CI kiểm (<a href="#ci-L1">ci.yml</a>).</p>

=== 21-25
<p>Bốn import, đều nhẹ:</p>
<ul><li><code>date</code>: để nhận ra giá trị YAML đã tự đổi thành ngày (dòng 33).</li>
<li><code>Path</code>: chỉ dùng trong chú thích kiểu của <code>load_config</code>.</li>
<li><code>Any</code>: config là dict lồng nhau tự do, không có schema cố định.</li>
<li><code>yaml</code> (thư viện PyYAML): đọc file cấu hình.</li></ul>

=== 27-28
<p>Tám khoá mức trên cùng mà đề bắt buộc trong <code>configs/&lt;city&gt;.yaml</code>. Dùng tuple (không sửa được) vì đây là hằng số. Kiểm ở <a href="#config-L48">dòng 48</a>.</p>

=== 31-33
<p>PyYAML đọc <code>2025-09-12</code> (không có ngoặc kép) thành đối tượng <code>datetime.date</code>, không phải chuỗi. Nếu để nguyên, chỗ khác ghép đường dẫn <code>data/processed/sydney/2025-09-12</code> hay so sánh với cột <code>snapshot</code> (kiểu chuỗi) sẽ lệch kiểu.</p>
<p>Hàm này đổi <code>date</code> sang <code>isoformat()</code> = <code>"2025-09-12"</code>; giá trị khác thì <code>str()</code>. Gọi được nhiều lần mà không đổi kết quả (chuỗi vào thì chuỗi ra).</p>

=== 36-41
<p>Mẫu của đề đặt tên ngưỡng giá theo tiền tệ: <code>price_max_aud</code> cho Sydney, <code>price_max_clp</code> cho Santiago… Hàm thử lần lượt <code>price_max_aud</code> rồi tên chung <code>price_max</code>, trả về <code>float</code>.</p>
<p>Thiếu cả hai thì <code>KeyError</code> với thông báo nói rõ cần thêm khoá nào. Với config hiện tại: <code>10000.0</code> AUD, dùng ở luật <code>price_unusable</code> của QA (<a href="#qa_rules-L176">qa_rules.py dòng 176</a>).</p>

=== 44-54
<p><code>normalize</code> nhận dict thô từ YAML. Trước khi chuẩn hoá, nó kiểm theo thứ tự và dừng ở lỗi đầu tiên:</p>
<ol><li>File rỗng (<code>safe_load</code> trả <code>None</code>) hoặc không phải bảng khoá → <code>TypeError</code>.</li>
<li>Thiếu khoá nào trong <code>REQUIRED_KEYS</code> → <code>KeyError</code> liệt kê <b>tất cả</b> khoá thiếu một lần, không bắt sửa từng cái.</li>
<li><code>city</code> không phải chuỗi (ví dụ YAML đọc nhầm thành số) → <code>TypeError</code>. <code>city</code> được dùng làm tên thư mục nên phải là chuỗi.</li>
<li>Thiếu <code>qa.min_nights_cap</code> → <code>KeyError</code>; đề yêu cầu khoá này trong mục <code>qa</code>.</li></ol>
<p>Nguyên tắc: config sai thì dừng ngay ở đây với thông báo rõ, thay vì để một bước giữa pipeline hỏng khó hiểu.</p>

=== 56-57
<p>Bắt đầu dựng dict <b>mới</b> (<code>{**raw, ...}</code> là sao chép nông), nên dict đọc từ YAML không bị sửa. Hai việc:</p>
<ul><li><code>snapshots</code> đổi hết về chuỗi bằng <code>_as_text</code>.</li>
<li><code>qa</code> được chép lại và thêm khoá <code>price_max</code> từ <code>_price_cap</code>. Từ đây code chỉ đọc <code>config["qa"]["price_max"]</code>, không cần biết tiền tệ.</li></ul>

=== 58-60
<p><code>qa.expected</code> (số lượng đề cam kết cho mẫu của nhóm: 1000 căn, 875/125, 50/30/25/25 căn 0 review…) có danh sách mốc riêng. Danh sách đó cũng phải đổi về chuỗi, vì <a href="#config-L70">expected_applies</a> so nó với <code>config["snapshots"]</code> bằng chuỗi.</p>
<p><code>isinstance(expected, dict)</code> phòng trường hợp mục này viết sai kiểu: khi đó giữ nguyên, không lỗi ở đây.</p>

=== 61-66
<p>Mục <code>segments</code> là tuỳ chọn. Nếu có, chép thành dict mới rồi chuẩn hoá hai chỗ có ngày:</p>
<ul><li><code>gap_snapshot</code> (mốc 2026-03-21 bị lọc thiếu căn) đổi về chuỗi, nếu có.</li>
<li><code>transitions</code>: mỗi cặp <code>[từ, đến]</code> đổi về hai chuỗi. <code>or []</code> xử lý cả khi khoá có mà giá trị rỗng (<code>None</code>).</li></ul>
<p>Vì sao cần: <code>segments/transitions.py</code> so mốc của cặp với tên mốc trong dữ liệu (chuỗi). Để <code>date</code> thì không cặp nào khớp và ma trận đổi nhóm rỗng mà không báo lỗi.</p>

=== 67
<p>Trả về dict đã chuẩn hoá. Các khoá khác (<code>kpi</code>, <code>llm</code>, <code>seed</code>, <code>labels</code>, <code>eval</code>…) đi qua nguyên vẹn.</p>

=== 70-77
<p>Docstring giải thích vấn đề: các số trong <code>qa.expected</code> chỉ đúng cho đúng 4 mốc được giao. Nếu giảng viên đổi mốc (yêu cầu “đổi thành phố hoặc mốc chỉ sửa yaml” của đề), so số căn 0 review theo <b>vị trí</b> (mốc thứ nhất 50, thứ hai 30…) sẽ sai và dừng pipeline oan ở bước QA.</p>

=== 78-82
<p>Logic:</p>
<ul><li>Không có <code>qa.expected</code> → <code>False</code> (không có gì để đối chiếu).</li>
<li>Có nhưng không ghi <code>snapshots</code> → <code>True</code>, giữ hành vi cũ.</li>
<li>Có ghi → <code>True</code> chỉ khi danh sách mốc giống hệt <code>config["snapshots"]</code>, cả thứ tự.</li></ul>
<p><code>str(s)</code> ở cả hai vế để so chắc chắn bằng chuỗi. Được gọi ở <a href="#run_pipeline-L125">run_pipeline dòng 125</a>.</p>

=== 85-87
<p>Trả bản sao config với mục <code>qa</code> bỏ khoá <code>expected</code>. Dùng ở hai chỗ trong <code>run_pipeline.py</code>: khi mốc khác mốc được giao (<a href="#run_pipeline-L125">dòng 125</a>) và khi mẫu được chọn theo seed thay vì danh sách ID của nhóm (<a href="#run_pipeline-L140">dòng 140</a>). Không sửa dict gốc, nên test có thể so trước/sau.</p>

=== 90-93
<p>Hàm công khai duy nhất các module khác gọi. Mở file với <code>encoding="utf-8-sig"</code>: giống utf-8 nhưng tự bỏ BOM ở đầu file. Notepad trên Windows hay lưu kèm BOM; không bỏ thì khoá đầu tiên đọc ra thành <code>"﻿city"</code> và báo thiếu <code>city</code>.</p>
<p><code>yaml.safe_load</code> (không phải <code>yaml.load</code>) chỉ dựng kiểu dữ liệu cơ bản, không chạy được code lạ trong file YAML.</p>

--- flow
## Hàm phụ
fn 0 31 | _as_text | Ngày → "YYYY-MM-DD"
fn 0 36 | _price_cap | price_max_aud → float
## Đọc config
fn 0 90 | load_config | Mở yaml (bỏ BOM), safe_load
fn 1 44 | normalize | Kiểm khoá rồi chuẩn hoá
st 2 46 | Kiểm khoá bắt buộc | Sai thì dừng ngay, báo rõ khoá nào
st 2 56 | Mốc và giá | snapshots → chuỗi; thêm qa.price_max
st 2 61 | segments | gap_snapshot, transitions → chuỗi
## Khi đổi mốc
fn 0 70 | expected_applies | Số của đề có còn đúng không
fn 0 85 | without_expected | Bỏ qa.expected, giữ phần còn lại
chips 1 | run_pipeline:125 main

--- review
ok | Kiểm config sớm | Thiếu khoá bắt buộc thì dừng trước bước 1 với thông báo liệt kê đủ các khoá thiếu; tốt hơn để bước giữa pipeline hỏng.

--- qa
? Vì sao phải đổi ngày trong yaml về chuỗi?
<p>PyYAML đọc <code>2025-09-12</code> thành <code>datetime.date</code>. Tên mốc được ghép vào đường dẫn và so với cột <code>snapshot</code> kiểu chuỗi, nên để kiểu <code>date</code> thì so sánh không khớp. <code>_as_text</code> đổi tất cả về <code>"YYYY-MM-DD"</code> một lần ở đây.</p>
? Đổi sang thành phố khác thì phải sửa gì?
<p>Chỉ sửa yaml: <code>city</code>, <code>data_root</code>, <code>currency</code>, <code>snapshots</code>, <code>qa.price_max_&lt;tiền tệ&gt;</code>, <code>qa.bbox</code>. Nếu mốc khác mốc được giao, <code>expected_applies</code> trả <code>False</code> và pipeline bỏ đối chiếu số lượng của đề thay vì dừng oan.</p>
