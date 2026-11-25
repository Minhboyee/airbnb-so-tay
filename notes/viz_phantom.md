--- meta
title: viz_phantom.py
lead: Bộ 8 hình kể câu chuyện “căn ảo”, chạy ở bước 6b sau khi đã chia nhóm, tính KPI và ghép nhãn LLM. File chỉ đọc các bảng tổng hợp, tính tỉ lệ để trình bày và ghi PNG; không tự phân nhóm lại listing. Cần nhớ ba mẫu số khác nhau: toàn bộ căn, căn của một nhóm ở mốc đầu và review có nhãn trong mẫu.

--- blocks
=== 1-18
<p>Docstring đặt hợp đồng dữ liệu cho 8 hình trong <code>figures/phantom/</code>: hình 01 dùng số đếm nhóm; 02 và 05 dùng ma trận chuyển; 03, 04, 06 dùng KPI; 07 dùng audit và summary; 08 dùng bảng khía cạnh LLM. “Căn ảo” là tên vận hành của ba nhóm theo luật, không phải bằng chứng listing giả hay không từng có khách.</p>
<p>Thiếu file được bỏ qua; file có nhưng thiếu cột thì lỗi. Câu “sai số thì dừng hẳn” mạnh hơn mức kiểm tra thực tế: ví dụ <code>kpi_rows</code> ép kiểu nhưng chưa kiểm tỉ lệ trong khoảng 0–100, xem review.</p>

=== 20-31
<p>File đi theo thứ tự: hằng số, nạp CSV, các hàm định dạng, tám hàm vẽ, rồi bộ điều phối. Chạy module bằng <code>python -m src.viz_phantom</code> để import theo package <code>src</code>. <code>--sample-dir</code> dùng fixture có số giả để kiểm khung hình; phải phân biệt với <code>--scope sample</code>, là mẫu 1.000 căn thật của nhóm.</p>

=== 33
<p>Dòng này hoãn việc đánh giá annotation. Các kiểu như <code>dict[str, Any]</code> chỉ mô tả giao diện hàm, không kiểm dữ liệu CSV lúc chạy.</p>

=== 35-38
<p><code>argparse</code> nhận cờ CLI; <code>math</code> nhận diện giá thiếu bằng <code>isnan</code>; <code>Path</code> ghép đường dẫn; <code>Any</code> cho config và đối tượng matplotlib có giao diện linh hoạt.</p>

=== 40-42
<p><code>pandas</code> lọc, pivot và tính tỉ lệ. <code>LinearSegmentedColormap</code> dựng thang nhiệt từ nền trắng tới màu chủ đạo; <code>FuncFormatter</code> đổi nhãn trục số căn thành kiểu Việt.</p>

=== 44-48
<p>Dùng lại cấu hình chuẩn hoá, thứ tự nhóm, tập <code>PHANTOM</code>, nhãn Việt và tên <code>GONE = BIEN_MAT</code> từ bước chia nhóm. Màu, font và khung hình nhập từ <code>viz.py</code> giúp hai bộ hình thống nhất. Module này không chép lại thuật toán <code>classify</code>.</p>

=== 49-51
<p>PNG mặc định nằm trong <code>figures/phantom</code>. Riêng KPI luôn đọc <code>data/processed/kpi_phantom.csv</code>, không nối theo <code>segments.output_dir</code> hay hậu tố <code>full/sample</code>. Đổi thư mục hay chạy mẫu là chỗ dễ sai; xem <a href="#viz_phantom-L116">real_inputs</a>.</p>

=== 53-57
<p>Cam đất đánh dấu nhóm ảo hoặc điểm cần chú ý; xám nhạt biểu diễn phần chưa rõ/biến mất. <code>ON_WHITE</code> là nền sau chữ số, không phải nền của cả thanh: nó che đường tham chiếu để số vẫn đọc được.</p>

=== 59-74
<p>Schema tối thiểu của sáu đầu vào. Chỉ yêu cầu các cột mà bộ hình đọc; CSV có thêm cột vẫn hợp lệ. <code>counts.n</code> là số căn, <code>transitions.n</code> là số căn chuyển nhóm; <code>kpi_phantom.value</code> có thể là phần trăm hoặc tỉ số tuỳ KPI. Với LLM, <code>share_reviews_negative_aspect</code> là tỉ phần 0–1, khác KPI phần trăm 0–100.</p>

=== 76-86
<p>Nhãn ngắn xuống dòng phục vụ cột của ma trận hình 02; nhãn hàng dùng tên đầy đủ. Cột <code>BIEN_MAT</code> nằm ngoài bảy nhóm: căn có ở mốc đầu nhưng vắng dữ liệu mốc cuối, không tự suy ra chủ đã gỡ listing.</p>

=== 88-92
<p>Chia bảy nhóm thành hai tập để hình 05 gộp cột: <code>B_booked, L_low, H_healthy</code> có dấu vết review gần đây; bốn nhóm còn lại không có. Test <code>test_review_return_groups_cover_all_segments</code> kiểm hai tập phủ đúng bảy tên nhóm. “12 tháng” trên hình ứng với ngưỡng 365 ngày trong config hiện tại, không phải phép đếm booking.</p>

=== 94-97
<p>Ngưỡng tô màu hình 08 là <b>30 review mỗi nhóm</b>, không phải 30 căn. <code>D_never</code> và <code>N_new</code> có tổng review bằng 0 theo luật nên được giải thích khác với <code>B_ghost</code>: nhóm khoá lịch có thể từng có review cũ nhưng mẫu không chứa review của nó. Ngưỡng 30 chỉ là quy tắc trình bày, không phải kiểm định ý nghĩa thống kê.</p>

=== 99-107
<p>Từ điển dịch sáu khía cạnh LLM. Thứ tự cột vẫn do <code>config["llm"]["aspects"]</code> quyết định; tên lạ được giữ nguyên ở hàm vẽ thay vì bị loại.</p>

=== 109-110
<p>Bốn nhãn bucket phải trùng bảng KPI: 1–7, 8–20, 21–89, 90+ đêm. Đây là nhãn viết cố định; khi đổi ngưỡng dài ngày cần xem lại ý nghĩa nhãn, vì bước KPI có dùng ngưỡng cấu hình cho hai bucket cuối.</p>

=== 113
<p>Bắt đầu lớp đọc dữ liệu: mấy hàm này trả đường dẫn hoặc DataFrame, chưa tạo hình.</p>

=== 116-118
<p><code>real_inputs</code> lấy thư mục kết quả chia nhóm qua <code>cfg_get</code>; thiếu khoá sẽ báo lỗi rõ từ module luật. <code>scope</code> ở đây là phạm vi listing của bước 3, khác cột <code>scope</code> trong KPI vốn chỉ kiểu gom nhóm như <code>overall</code> hay <code>segment</code>.</p>

=== 119-127
<p>Bốn bảng chia nhóm/audit nhận hậu tố <code>_{scope}</code>. KPI dùng hằng đường dẫn; LLM dùng <code>&lt;output_dir&gt;/&lt;city&gt;/llm_segment_aspects.csv</code> không có hậu tố phạm vi. Đã kiểm bằng Python: gọi với <code>full</code> và <code>sample</code> cho cùng đường dẫn KPI. CSV commit hiện có số KPI toàn thành phố; không được hiểu <code>--scope sample</code> là đổi mọi hình sang 1.000 căn.</p>

=== 130-132
<p>Đầu vào demo đặt tên theo khoá schema, chẳng hạn <code>counts.csv</code> và <code>llm_aspects.csv</code>, cùng trong một thư mục. Duyệt <code>INPUT_COLUMNS</code> cho đường dẫn demo đủ sáu loại bảng; đây không phải dữ liệu để trích số vào báo cáo.</p>

=== 135-140
<p><code>read_input</code> đọc CSV có thể mang BOM do xuất cho Excel. Không yêu cầu pandas parse ngày thành datetime: các ngày ISO trong CSV giữ dạng chuỗi để so với config đã chuẩn hoá.</p>

=== 141-144
<p>Đọc bằng <code>utf-8-sig</code> rồi liệt kê mọi cột thiếu. Thiếu một cột cũng ném <code>ValueError</code> kèm đường dẫn; khác với thiếu cả file vốn được <code>skip_reason</code> xử lý trước khi đọc.</p>

=== 145-147
<p>CSV có header đúng nhưng không có dòng cũng bị từ chối. Trả nguyên DataFrame khi qua kiểm: chưa kiểm tính duy nhất của khoá, miền giá trị hay tính khớp giữa các bảng. Test đọc file kiểm cả thiếu cột và bảng rỗng.</p>

=== 150-152
<p>“Mốc cuối” là phần tử cuối danh sách config, không phải ngày lớn nhất trong CSV. Với YAML hiện tại là <code>2026-06-16</code>. Config cần giữ thứ tự thời gian nếu muốn hình mang nghĩa mốc mới nhất.</p>

=== 155-157
<p>Lấy cột dưới dạng mảng float, tìm vị trí tên hàng rồi lấy phần tử tương ứng. Cách này trả scalar phục vụ định dạng số. Hàm giả định tên hàng có tồn tại và duy nhất; nó không tự điền 0 cho nhóm thiếu, nên các hàm chuẩn bị bảng phải reindex hoặc kiểm trước.</p>

=== 160-164
<p><code>kpi_rows</code> là cửa lọc chung cho hình 03, 04, 06. Chọn một tên KPI, một cấp gom nhóm, ở mốc cuối; trả bản sao để ép kiểu không sửa bảng đã cache.</p>

=== 165-168
<p>Ba điều kiện nối bằng <code>&amp;</code> phải cùng đúng. Không có dòng khớp là lỗi dữ liệu, không vẽ một thanh 0 giả. Ví dụ <code>scope="segment"</code> lấy KPI theo nhóm căn, không phải bật chế độ mẫu.</p>

=== 169-171
<p>Chuỗi không phải số bị <code>errors="raise"</code> chặn. <code>n_obs</code> còn bị ép về int. Đã chạy thử: <code>value=-10, n_obs=1.9</code> vẫn được nhận và thành <code>-10, 1</code>; ép kiểu không thay thế kiểm miền và kiểm số đếm nguyên. Không nên lặp lại lời hứa “mọi sai số đều bị bắt” của đầu file.</p>

=== 174
<p>Phần tiện ích tách hình thức khỏi số liệu: các hàm định dạng không đổi mẫu số hay tính lại KPI.</p>

=== 177-179
<p>Làm tròn số đếm rồi đổi dấu ngăn nghìn từ phẩy sang chấm: 20.573 căn. Với số đếm thật vốn nguyên thì không mất thông tin. Python làm tròn điểm giữa về số chẵn; đã thử <code>2.5 → 2</code>, <code>3.5 → 4</code>, nên không dùng hàm này để chứng minh đầu vào là số nguyên.</p>

=== 182-184
<p>Nhận số đã ở đơn vị phần trăm, giữ mặc định một chữ số lẻ và thêm dấu %. Ví dụ 21,188 thành 21,2%; không nhân thêm 100. Ma trận chuyển hay LLM phải đổi tỉ phần sang % trước khi gọi.</p>

=== 187-189
<p>Tỉ số giá được in hai chữ số lẻ và dấu nhân: 1,3203 thành 1,32×. <code>chr(0xD7)</code> tạo ký tự nhân theo quy ước lint của repo; 1× là bằng trung vị nhóm so sánh, không phải 1 AUD.</p>

=== 192-194
<p>Đổi chuỗi ngày ISO sang ngày/tháng/năm để ghi trên hình. Đầu vào không phải ngày hợp lệ sẽ bị pandas báo lỗi; hàm không tự sửa ngày sai.</p>

=== 197-199
<p>Định dạng tỉ số giữa hai tỉ lệ khu vực thành “x,x lần”. Từ KPI commit, 36,4924/12,2939 ≈ 2,9683, nên tiêu đề hình 03 in “3,0 lần”; không phải chênh 3 điểm phần trăm.</p>

=== 202-204
<p>Hiệu hai ngày chia 30,44 rồi làm tròn là số tháng <em>xấp xỉ</em>, không phải đếm tháng lịch. Test và lần chạy Python đều cho cặp 12/09/2025 → 16/06/2026 bằng khoảng 9 tháng.</p>

=== 207-209
<p>Tra màu theo tư cách thuộc <code>PHANTOM</code>, không theo độ lớn tỉ lệ. Ba nhóm <code>B_ghost, D_dormant, D_never</code> luôn cam; các nhóm còn lại xanh ngay cả khi thanh cao.</p>

=== 212-215
<p>Tiêu đề thông điệp và dòng phụ đặt theo toạ độ tương đối của Figure, dùng chung font/màu. Nhờ không nằm trong Axes, tiêu đề không dịch chuyển khi đổi giới hạn trục dữ liệu.</p>

=== 218-221
<p>Dòng nguồn lấy tên thành phố từ config, viết hoa đầu từ và liệt kê mốc được truyền. Nếu không truyền hoặc truyền danh sách rỗng, dùng mốc cuối. Hình chuyển nhóm ghi hai mốc; hình gap ghi cả bốn. Test kiểm đúng chuỗi nguồn Sydney và ngày cuối.</p>

=== 224-229
<p>Ghi chú giải thích mẫu số và giới hạn suy luận; dòng dưới ghi nguồn. Docstring giải thích vì sao khoảng cách đáy tính bằng inch: hình 03 có chiều cao biến đổi theo số khu, nhưng ghi chú vẫn cần một khoảng trống vật lý ổn định.</p>

=== 230-233
<p>Chia 0,42 và 0,16 inch cho chiều cao Figure để đổi sang toạ độ tương đối. Cùng một dict kiểu chữ dùng cho hai dòng; dòng nguồn thêm chữ nghiêng. <code>linespacing</code> áp dụng khi ghi chú có xuống dòng.</p>

=== 236-239
<p>Tiện ích đặt nhãn số trong hệ toạ độ của Axes. Các khoá trong <code>style</code> đứng sau mặc định nên caller có thể đổi màu, căn ngang hoặc cỡ chữ cho từng vị trí; ví dụ chữ trắng bên trong thanh dài.</p>

=== 242-249
<p>Tạo trục thanh ngang, áp phong cách chung, chỉ giữ lưới theo trục x. Đảo trục y để mục thứ nhất hiện trên cùng, đúng thứ tự bảy nhóm hay thứ hạng giảm dần; không đảo thứ tự dữ liệu.</p>

=== 252-257
<p>Chia phần ngang còn lại thành hai khung cùng chiều rộng, chừa khoảng giữa 0,08 Figure. Hình 04 và 06 nhờ vậy có thể so hai đại lượng cạnh nhau; riêng dùng chung bố cục chưa bảo đảm chung thang đo, việc đó caller phải đặt.</p>

=== 260-267
<p>Heatmap ánh xạ từ 0 tới <code>vmax</code>, từ nền sang màu đậm, ô NaN thành xám nhạt. Hình 02 cố định <code>vmax=100</code>; hình 08 chọn theo cực đại sau khi che hàng ít review. Do đó không thể so màu giữa hai hình như cùng một thang.</p>

=== 268-272
<p>Bỏ các cạnh khung và vạch tick, đưa tên cột lên trên cho dễ đọc kiểu bảng. <code>aspect="auto"</code> cho phép ô chữ nhật theo vùng vẽ, không ép mỗi ô vuông.</p>

=== 275-277
<p>Tên một panel căn trái, đậm và chừa khoảng phía trên trục. Đây là tiêu đề cục bộ như “Căn ngắn ngày”, khác thông điệp chung của Figure.</p>

=== 280-286
<p>Ghép nhãn tiếng Việt với thông tin cỡ mẫu nếu dict <code>counts</code> có khoá tương ứng. Dict này chứa chuỗi như <code>n=1.632</code> hoặc “846 căn · 954 review”, nên hàm không giả định mọi hình có cùng mẫu số.</p>

=== 289
<p>Hình 01 là ảnh cơ cấu ở mốc cuối, không phải đồ thị xu hướng bốn mốc.</p>

=== 292-297
<p><code>draw_segments</code> ghi <code>01_segments_latest.png</code>. Docstring nhắc hạn chế bằng chứng lịch sử: hai mốc năm 2025 chưa có mốc cũ cách ít nhất 150 ngày, nên <code>D_never=0</code> không đồng nghĩa không có căn không bao giờ có khách.</p>

=== 298-300
<p>Lọc mốc cuối, đặt tên nhóm làm index rồi reindex theo thứ tự chuẩn. Chỉ lấy <code>n</code>, không dùng cột <code>share</code> đã làm tròn trong CSV: tỉ lệ trên hình được tự tính lại từ số đếm.</p>

=== 301-303
<p>Thiếu bất kỳ nhóm nào hoặc số đếm NaN sẽ báo lỗi liệt kê tên nhóm. Đủ bảy hàng mới ép số đếm về int. Test xoá <code>D_never</code> và yêu cầu hàm phải từ chối vẽ, thay vì coi thiếu dữ liệu là nhóm có 0 căn.</p>

=== 304-306
<p>Tổng số căn là mẫu số chung cho cả bảy thanh; tỉ lệ ảo bằng tổng tỉ lệ ba nhóm cam. Cộng CSV <code>segments_counts_full.csv</code> ở mốc cuối được <b>4.359/20.573 = 21,1879648%</b>; bản <code>sample</code> là 84/1.000 = 8,4%. Hai con số mô tả hai phạm vi khác nhau.</p>

=== 308-314
<p>Tạo bảy thanh theo thứ tự luật, dùng chiều dài là phần trăm. Trục x mở rộng 30% ngoài thanh dài nhất để còn chỗ ghi số; nhãn trục nói rõ mẫu số là tổng căn. Không sắp giảm dần ở hình này vì muốn giữ thứ tự nhóm xuyên suốt bộ hình.</p>

=== 315-316
<p>Ảnh thật 01 vẽ mỗi thanh kèm cả % và số căn. Nhóm khoẻ mạnh là 11.907 căn, khoảng 57,9%; ba thanh cam lần lượt 918, 1.913, 1.528 căn. Không cộng <code>B_booked</code> vào ảo chỉ vì nó cũng kín lịch.</p>

=== 318-323
<p>Tiêu đề suy từ nghịch đảo tỉ lệ ảo: khoảng 5 căn có 1 căn ảo. Đây là cách nói làm tròn, không phải cứ mỗi nhóm năm listing có đúng một căn. Nhánh 0 căn ảo tránh chia cho 0 và có test dự phòng riêng.</p>

=== 324-330
<p>Ghi rõ định nghĩa ba nhóm ảo, cảnh báo review không phải lượt ở thật và một căn chỉ nhận một nhóm theo ưu tiên luật. Sau đó ghi PNG 165 dpi với màu nền chung; đường dẫn đích do <code>run</code> truyền, hàm không trả về số liệu.</p>

=== 333
<p>Hình 02 theo dõi cohort từ mốc đầu đến mốc cuối; số căn mới chỉ xuất hiện ở cuối không nằm trong mẫu số hàng.</p>

=== 336-341
<p><code>first_transition_pair</code> chọn cặp đầu tiên được cấu hình mà cả hai đầu còn trong lần chạy. Nó không tự tìm cặp có khoảng cách xa nhất, cũng không kiểm CSV có cặp đó ở đây.</p>

=== 342-346
<p>Đổi ngày sang chuỗi trước khi kiểm tập mốc. Vòng lặp dừng ở cặp hợp lệ đầu tiên; không còn cặp thì trả <code>None</code>. Test bỏ tháng 9 khiến chọn tháng 12 → tháng 6; chỉ còn mốc mới thì không có cặp để vẽ.</p>

=== 349-355
<p><code>transition_table</code> chuẩn bị bảng đếm: hàng là nhóm nguồn, cột là bảy nhóm đích và biến mất. Docstring mô tả cặp mặc định tháng 9 → tháng 6; khi đổi config, code theo cặp vừa chọn chứ không viết cứng hai ngày đó.</p>

=== 356-359
<p>Gọi chọn cặp rồi báo lỗi nếu không có. Khi chạy qua <code>run</code>, <code>skip_reason</code> thường đã loại trường hợp này để bỏ hình có lý do; gọi trực tiếp helper vẫn nhận lỗi rõ.</p>

=== 360-362
<p>CSV có thể chứa nhiều cặp; chỉ giữ đúng <code>src/dst</code>. Cặp hợp lệ trong config mà không có trong dữ liệu là lỗi, không âm thầm dùng cặp khác có sẵn. Test đổi nguồn toàn bảng thành tháng 12 để kiểm nhánh này.</p>

=== 363-365
<p><code>pivot_table(..., aggfunc="sum")</code> cộng các dòng cùng cặp nhóm, điền ô thiếu bằng 0; reindex tạo đủ bảy hàng và tám cột theo thứ tự chuẩn. Chỉ giữ hàng tổng dương để chuẩn hoá không chia 0. Ảnh thật 02 còn sáu hàng vì <code>D_never</code> ở tháng 9 có 0 căn.</p>

=== 368-373
<p>Chuẩn hoá theo hàng: mỗi ô chia tổng số căn của chính nhóm nguồn rồi nhân 100. <code>axis=0</code> căn Series mẫu số theo index hàng. Danh sách <code>hidden</code> dùng giải thích vì sao có nhóm không xuất hiện, không xoá cột nhóm ấy ở mốc đích.</p>

=== 375-383
<p>Heatmap dùng chung thang 0–100%; tên cột ở trên là nhóm cuối, tên hàng bên trái là nhóm đầu kèm n. Vạch dọc tách cột biến mất ra khỏi bảy nhóm. Ảnh 02 đọc theo hàng ngang, đừng đọc dọc cột, để diễn giải “x% căn chuyển đi đâu”.</p>

=== 385-391
<p>Ghi % làm tròn tới số nguyên vào từng ô; ô từ 55% đổi chữ trắng, ô cùng nhóm nguồn/đích in đậm. Tổng số <em>chưa làm tròn</em> trên hàng là 100%; các số nguyên in ra có thể cộng lệch 100 do làm tròn độc lập.</p>

=== 393-395
<p>Chỉ nhắc bỏ qua mốc gap nếu config có mốc ấy trong danh sách đang chạy. Dòng phụ là thông tin bối cảnh, không phải thao tác xoá mốc tại đây: cặp chuyển nhóm đã được chọn trước.</p>

=== 396-400
<p>Nếu có hàng ngủ đông, lấy ô chéo làm tiêu đề. CSV thật cho <b>1.068/1.632 = 65,4412%</b>, nên ảnh in 65% sau khoảng 9 tháng. Nếu hàng ngủ đông không có căn thì dùng câu trung tính thay vì cố tra ô bị thiếu; test có nhánh này.</p>

=== 401-405
<p>Gắn hai mốc cụ thể và quy tắc đọc theo hàng. Chú thích phân biệt giữ nhóm với biến mất: <code>BIEN_MAT</code> chỉ là không tìm được ID trong dữ liệu cuối. Riêng hàng ngủ đông có 261/1.632 ≈ 15,99% ở cột này.</p>

=== 406-411
<p>Nếu có hàng bị ẩn, ghi tên và ngưỡng lịch sử lấy từ config (150 ngày hiện tại), rồi thêm nguồn hai mốc và lưu hình. Lý do “cần mốc cũ” phù hợp hàng <code>D_never</code> bị ẩn trong dữ liệu hiện tại; với bộ khác, một hàng 0 căn cũng có thể đơn giản vì không có listing thuộc nhóm đó.</p>

=== 414
<p>Hình 03 so sánh tỉ lệ trong khu, không xếp hạng số lượng tuyệt đối căn ảo.</p>

=== 417-421
<p><code>ranked_areas</code> trả hai bảng: khu đủ quy mô để xếp hạng và khu nhỏ giữ lại cho ghi chú. Ngưỡng giảm việc diễn giải quá mức tỉ lệ từ ít căn; nó không biến dữ liệu thành mẫu ngẫu nhiên hay tạo khoảng tin cậy.</p>

=== 422-425
<p>Lấy <code>phantom_listing_rate</code> ở cấp <code>neighbourhood_cleansed</code>, dùng <code>n_obs ≥ area_min_listings</code> rồi sắp giảm dần theo %. Config hiện là 300 căn, và đúng 300 vẫn được giữ. Đây khác ngưỡng tính KPI khu thường trong mục <code>kpi</code>.</p>

=== 426-428
<p>Không khu nào đủ lớn thì báo lỗi, còn khu dưới ngưỡng được trả riêng cũng theo thứ tự tỉ lệ giảm dần. Test kiểm cả thứ hạng và trường hợp nâng ngưỡng lên 10.000 để không còn khu hợp lệ.</p>

=== 431-436
<p><code>draw_phantom_by_area</code> ghi <code>03_phantom_rate_by_area.png</code>. Đường tham chiếu lấy từ dòng KPI <code>overall</code> đầu tiên, không lấy trung bình các % khu. Với CSV commit là 21,188%; tổng thể phải được tính theo căn, không cho mọi khu trọng số bằng nhau.</p>

=== 438-443
<p>Chiều cao tăng 0,34 inch mỗi khu; lề dưới cố định bằng inch để không chồng ghi chú. Giá trị lớn hơn mức thành phố thì tô cam, bằng hoặc thấp hơn thì tô xanh. Màu không mang nghĩa nhóm căn ở hình 01 nữa.</p>

=== 444-449
<p>Vẽ thanh và nhãn khu kèm <code>n_obs</code>; đường đứt đứng là mức thành phố. Ảnh 03 cho Pittwater đứng đầu 36,5% trên 918 căn, Auburn cuối 12,3% trên 667 căn; khu Sydney có 5.014 căn và tỉ lệ khoảng 15,9%, không đồng nhất với toàn thành phố Sydney.</p>

=== 450-453
<p>Nhãn % đặt ngoài đầu thanh, bọc nền trắng để đường tham chiếu không cắt chữ. Nhãn “Toàn thành phố 21,2%” đặt trên hàng đầu ở đúng x của đường tham chiếu.</p>

=== 455-462
<p>Thông điệp lấy cao nhất chia thấp nhất trong <em>các khu đủ ngưỡng</em>. CSV thật có 19 khu được xếp hạng, 36,4924%/12,2939% ≈ 2,9683 lần, in 3,0 lần. Đây là so tỉ lệ, không phải Pittwater có số căn ảo gấp ba toàn bộ mọi khu.</p>

=== 463-469
<p>Nêu tử số là ba nhóm ảo, mẫu số là tổng căn trong khu. Có 19 khu nhỏ không xếp hạng; Mosman cao nhất trong phần này, 36,1624% với 271 căn. Giữ ghi chú tránh người xem tưởng Mosman không có trong dữ liệu hay thấp hơn tất cả khu trên biểu đồ.</p>

=== 470-471
<p>Thêm nguồn mốc cuối và lưu PNG. File này chỉ lọc/xếp hạng KPI có sẵn, không tính lại nhãn ảo từ listing gốc.</p>

=== 474
<p>Hình 04 đặt hai câu hỏi cạnh nhau với hai mẫu số khác nhau: trong từng nhóm căn, và trong riêng các căn không số đăng ký.</p>

=== 477-480
<p>Lấy KPI ở cấp <code>segment</code>, đặt tên nhóm làm index rồi giữ các nhóm có mặt theo thứ tự chuẩn. Không tự thêm nhóm thiếu thành 0; riêng hình giá sẽ reindex đủ bảy hàng sau đó để ghi “không có giá”.</p>

=== 483-486
<p><code>night_buckets</code> chọn KPI phân bố số đêm của listing thiếu đăng ký. <code>n_obs</code> trong bảng này là số căn của bucket, khác <code>n_obs</code> trong KPI tỉ lệ tổng thể là mẫu số toàn thành phố.</p>

=== 487-489
<p>Bắt buộc có đủ bốn <code>value</code>; bucket có 0 căn và giá trị 0% vẫn hợp lệ, khác hẳn thiếu dòng hay NaN. Test bỏ bucket 21–89 phải lỗi; CSV thật có bucket này với 0 căn.</p>

=== 492-497
<p>Dựng câu tóm tắt min–max trong các nhóm ảo có số liệu. Không tính trung bình hoặc tỉ lệ ảo gộp có trọng số: “47,1% đến 60,6%” là khoảng ba tỉ lệ nhóm, lấy từ KPI đã tính.</p>

=== 498-502
<p>Nếu có nhóm khoẻ mạnh thì thêm tỉ lệ của nhóm đó; không có cả hai phía thì trả chuỗi rỗng. CSV commit có khoẻ mạnh 1,1422%. Test dùng bảng rỗng xác nhận helper không cố tìm hàng không tồn tại.</p>

=== 505-511
<p><code>draw_long_stay_license</code> đọc ba mảng thông tin: <code>long_stay_90_rate</code> theo nhóm, bốn bucket thiếu đăng ký, và tỉ lệ thiếu đăng ký <code>overall</code>. Nhãn số đêm lấy ngưỡng config (90), còn tên KPI vẫn là chuỗi <code>long_stay_90_rate</code>.</p>

=== 513-520
<p>Khung trái vẽ % đòi lưu trú từ ngưỡng dài ngày, cùng trục 0–100. Cam vẫn là nhóm ảo. Ảnh 04 bên trái có ba nhóm ảo khoảng 47,1%, 55,4%, 60,6%, trong khi khoẻ mạnh chỉ 1,1%; đây là điều kiện đặt tối thiểu, không phải số đêm đã có khách ở.</p>

=== 521-523
<p>Ghi % mỗi thanh và tiêu đề panel. Không ghi n ở đây nên khi vấn đáp cần mở CSV: <code>B_booked</code> có mẫu số 1.151, ít hơn 1.159 căn trong counts, vì KPI loại dòng thiếu <code>minimum_nights</code>; các số này đã đối chiếu CSV và <a href="#kpi-L173">hàm tính KPI</a>.</p>

=== 525-530
<p>Khung phải chỉ xét các căn thiếu đăng ký có số đêm hợp lệ, trục 0–100; bucket 90+ tô cam để nhấn sự tập trung vào lưu trú dài. Không diễn giải thanh 98% là 98% toàn bộ listing thành phố.</p>

=== 531-537
<p>Mỗi bucket in % và số căn. Dưới 75% đặt chữ đen bên phải; từ 75% trở lên đặt chữ trắng bên trong, tránh vượt mép trục. Ảnh thật bên phải có 21 căn 1–7 đêm, 4 căn 8–20, 0 căn 21–89 và 1.244 căn 90+.</p>

=== 538-539
<p>Cộng số đếm bucket được 1.269 căn để ghi tiêu đề panel. Đây là số căn thiếu đăng ký có <code>minimum_nights</code> hợp lệ; code không kiểm nó bằng số thiếu đăng ký tổng thể. Trong CSV hiện tại, hai số khớp.</p>

=== 541-546
<p>Tiêu đề lấy bucket cuối 1.244/1.269 = <b>98,0299448%</b>, in 98,0%. Dòng phụ cho bối cảnh khác: thiếu đăng ký chiếm 6,1683% trên 20.573 căn. Không đảo điều kiện thành “98% căn dài ngày thiếu đăng ký”; hình đang nói chiều ngược lại.</p>

=== 547-550
<p>Giải nghĩa tối thiểu 90 đêm trong một lần đặt, xấp xỉ ba tháng, và số đăng ký cho thuê ngắn ngày tại NSW. “Từ 90 đêm” là <code>minimum_nights ≥ 90</code>, không phải tổng đêm đã thuê trong năm.</p>

=== 551-556
<p>Ô <code>license</code> trống mới tính thiếu; chuỗi <code>Exempt</code> không thuộc tập này, theo <a href="#kpi-L200">KPI đăng ký</a>. Ghi rõ hai đặc điểm đi cùng nhau không chứng minh nguyên nhân hay vi phạm pháp luật, rồi lưu hình.</p>

=== 559
<p>Hình 05 gộp tám cột của hình 02 thành ba trạng thái để người xem đọc câu chuyện review thay vì phải cộng nhiều ô.</p>

=== 562-569
<p><code>review_return_shares</code> nhận bảng đếm đã chuẩn hoá cấu trúc từ <code>transition_table</code>, chưa nhận bảng %. Mỗi hàng vẫn là cohort nhóm nguồn; ba cột đích là có review gần đây, còn listing nhưng không review gần đây, và biến mất.</p>

=== 570-578
<p>Cộng các nhóm đích theo hai tập hằng số, giữ riêng <code>GONE</code>, rồi chia tổng hàng và nhân 100. Test xác nhận tổng ba phần là 100%. Với ngủ đông thật: (30 + 98 + 121)/1.632 = <b>15,257353%</b> có review; 1.122/1.632 = 68,75% còn trên sàn không review; 261/1.632 ≈ 15,99% biến mất.</p>

=== 581-589
<p><code>draw_review_return</code> ghi <code>05_review_return.png</code>, dùng cùng cặp mốc và mẫu số với hình 02. Xanh = có review, cam = còn trên sàn không review, xám = biến mất. Cam ở đây còn gồm <code>N_new</code>, nên không thể đọc mọi vùng cam của hình 05 là “căn ảo”.</p>

=== 591-597
<p>Mỗi thanh bắt đầu tại x=0; <code>left</code> là mép cộng dồn riêng cho từng hàng. Vòng ngoài lần lượt thêm ba lớp, <code>barh(..., left=left)</code> đặt lớp sau nối lớp trước, tạo thanh chồng 100%.</p>

=== 598-601
<p>Phần rộng ít nhất 6 điểm % mới ghi nhãn ở tâm; phần nhỏ vẫn vẽ nhưng không in số để tránh chồng chữ. <code>left[pos] += width</code> chạy cả khi không in nhãn. Vì vậy vùng cam nhỏ của khoẻ mạnh trên ảnh vẫn tồn tại dù không có con số bên trong.</p>

=== 602-606
<p>Nhãn hàng kèm n nguồn, trục x cố định 0–100 và ghi trạng thái ở ngày đích; legend nằm phía trên. Ảnh 05: hàng ngủ đông n=1.632 chia khoảng 15% xanh, 69% cam, 16% xám; đây không phải phân bố ba trạng thái của toàn bộ 20.573 căn cuối kỳ.</p>

=== 608-615
<p>Lấy phần có review của ngủ đông làm thông điệp “Chỉ 15%… sau khoảng 9 tháng”. Với nhóm vốn có review ở mốc đầu, chữ “trở lại” nên hiểu là trạng thái review ở mốc cuối, không phải tất cả đã từng mất review rồi phục hồi. Nếu thiếu hàng ngủ đông, dùng tiêu đề chung; có test dự phòng.</p>

=== 616-622
<p>Ghi định nghĩa review gần đây dựa vào ba nhóm đích, không đếm sự kiện review mới giữa hai ngày. Review là dấu vết gián tiếp của lưu trú; dữ liệu vắng không chắc listing bị gỡ. Thêm nguồn hai mốc và lưu PNG.</p>

=== 625
<p>Hình 06 tách giá theo chế độ lưu trú. Các căn đòi 21–89 đêm không thuộc hai khung hiện tại, không phải bị cộng vào một trong hai bên.</p>

=== 628-632
<p><code>price_title</code> chỉ diễn đạt mức giá niêm yết tương đối của nhóm ảo trong khung ngắn ngày. Không suy rằng giá cao gây ít review, hay giá trên Airbnb là giá giao dịch thực tế.</p>

=== 633-637
<p>Trong ba nhóm ảo, chỉ giữ nhóm có hàng và có tỉ số lớn hơn 1, rồi đổi nhãn về chữ thường để nối câu. Đúng 1 không bị gọi cao hơn; thiếu hàng không được mặc định là có giá thấp.</p>

=== 638-640
<p>Không nhóm nào vượt 1 thì dùng thông điệp dự phòng; ngược lại nối tên bằng “và”. Với CSV thật, ngủ đông 1,3203× và chưa từng có review 1,8549× được nêu tên; khoá lịch không có giá nên không xuất hiện. Test kiểm cả nhánh có và không có nhóm vượt 1.</p>

=== 643-647
<p><code>_price_panel</code> reindex đủ bảy nhóm để hai khung thẳng hàng. Giá NaN được vẽ thanh dài 0 nhưng vẫn giữ NaN trong bảng để ghi “không có giá”; không biến dữ liệu thiếu thành kết luận giá bằng 0. Vạch đứt tại 1 là bằng trung vị hàng xóm.</p>

=== 648-650
<p>Giới hạn trục lấy từ caller để hai panel dùng cùng thang. Nhãn x nói rõ tỉ số <code>giá căn / trung vị hàng xóm</code>, không phải đơn vị tiền AUD và không phải phần trăm.</p>

=== 651-657
<p>Nhóm không có ratio ghi chữ xám; nhóm có ratio ghi số lần và n quan sát. Trong ảnh thật 06, hai nhóm kín lịch đều hiện “không có giá” ở cả hai khung. <code>n</code> là số căn có đủ dữ liệu tính ratio trong khung, không phải tổng số listing của nhóm.</p>

=== 660-665
<p><code>draw_price_vs_neighbours</code> ghi <code>06_price_vs_neighbours.png</code>. Đại lượng là trung vị các tỉ số từng căn, không phải lấy trung vị giá nhóm chia một trung vị chung toàn thành phố. “Hàng xóm” đã được bước KPI ghép theo cùng khu, loại phòng và chế độ lưu trú.</p>

=== 666-670
<p>Lấy hai tên KPI riêng và hai ngưỡng config: ngắn ngày ≤ 20 đêm, dài ngày ≥ 90 đêm. Lấy cực đại hai bảng rồi nhân 1,35 để dùng chung x_max. Bước này chỉ dựng thang hình; ratio đã tính ở <a href="#kpi-L262">price_relative_to_local_median</a>, có loại căn thiếu trường ghép hoặc giá không dương.</p>

=== 672-678
<p>Khung trái ghi “dưới 21 đêm”, tương đương ≤ 20 với số đêm nguyên; khung phải từ 90 đêm. Hai khung dùng cùng thứ tự nhóm và thang x, khung phải bỏ lặp nhãn y. Ảnh 06 cho ngủ đông 1,32× (n=791) bên trái nhưng 0,96× (n=836) bên phải; không lấy hai số đó gộp thành kết luận chung rẻ/đắt.</p>

=== 680-685
<p>Tiêu đề tự gọi tên nhóm ảo có ratio ngắn ngày trên 1. Dòng phụ nêu mốc, định nghĩa nhóm so sánh và vạch 1,00×. Trong CSV thật, khoẻ mạnh ngắn ngày 0,9639× (n=11.584), chưa từng có review 1,8549× (n=529): đây là so sánh mô tả có điều kiện, không kiểm định tác động của việc thuộc nhóm.</p>

=== 686-693
<p>Ghi rõ cách tính mỗi thanh, ý nghĩa n và lý do tránh trộn giá thuê dài với ngắn ngày. Nối thêm cảnh báo tự-so-giá khi nhóm ảo chiếm đa số khung dài, rồi lưu hình. Những số cũ 1,42×/1,98× không khớp KPI commit hiện tại 1,32×/1,85×.</p>

=== 696-700
<p><code>self_peer_note</code> nhắc sự phụ thuộc của mốc so sánh vào thành phần dữ liệu. Nếu nhóm ảo chiếm đa số quan sát dài ngày thì chuẩn “hàng xóm” cũng chứa nhiều căn thuộc chính nhóm ảo; ratio gần 1 không phải một đối chứng độc lập.</p>

=== 701-703
<p>Ép n về số, ô không hợp lệ coi 0 chỉ cho phép tính ghi chú. Tỉ trọng nhóm ảo là tổng n của <code>PHANTOM</code> chia tổng n tất cả nhóm trong khung. CSV thật: (836 + 740)/(836 + 740 + 18 + 82 + 66) = <b>90,4707%</b>, nên ảnh hiện 90%.</p>

=== 704-709
<p>Từ 50% trở xuống hoặc tổng n=0 không thêm cảnh báo; trên 50% in một dòng. Test kiểm bảng rỗng, nhóm ảo thiểu số và ví dụ thống trị. Cảnh báo dùng tỉ trọng toàn khung, không chứng minh từng ô khu × loại phòng đều có đa số căn ảo.</p>

=== 712
<p>Hình 07 giải thích bất thường độ phủ tháng 3 thay vì đọc số listing giảm như bằng chứng thị trường co lại.</p>

=== 715-718
<p><code>gap_numbers</code> reindex audit theo đúng mốc và thứ tự config. Các dòng ngoài lần chạy bị bỏ; không tự sort theo ngày. Hàm trả audit cùng một dòng summary để hai panel dùng chung dữ liệu kiểm tra.</p>

=== 719-720
<p>Thiếu số căn ở một mốc thì báo lỗi chỉ rõ mốc. Việc kiểm này chỉ nhắm <code>n_listings</code>, chưa kiểm đầy đủ hai cột audit còn lại có NaN hay giá trị vô lý hay không.</p>

=== 721-724
<p>Lấy dòng summary đầu tiên, rồi kiểm <code>n_explained + n_unexplained = n_missing</code> sau ép int. CSV thật: 3.569 + 1.076 = 4.645. Test kiểm tổng sai và thiếu mốc; chạy thử thêm cho thấy đổi <code>gap_snapshot</code> trong summary sang tháng 9 vẫn được nhận, vì chưa đối chiếu với <code>segments.gap_snapshot</code>.</p>

=== 727-731
<p><code>draw_march_gap</code> ghi <code>07_march_2026_gap.png</code>. Mốc nhấn trên hình lấy từ summary, còn ngưỡng giải thích lấy từ config (7 đêm). Đổi tên hàm hay tên PNG không cần thiết để biết mốc nào thực sự vẽ: phải nhìn giá trị <code>gap_snapshot</code>.</p>

=== 733
<p><code>FuncFormatter</code> nhận giá trị tick và vị trí tick; lambda bỏ tham số vị trí để chỉ định dạng số căn kiểu 20.000. Đây là trục số đếm, không chia thành nghìn căn.</p>

=== 735-741
<p>Khung trái đọc <code>n_listings</code>, cực đại của <code>minimum_nights</code> và <code>share_blocked</code>. Cột share trong audit là tỉ phần nên nhân 100 trước khi in %. Cẩn thận: share của audit khác đơn vị <code>value</code> phần trăm trong KPI.</p>

=== 742-748
<p>Tìm vị trí gap để nhấn cam; các mốc khác xanh. Dưới ngày ghi “tối đa x đêm”, nghĩa là giá trị lớn nhất của cột minimum_nights trong snapshot, không phải trường <code>maximum_nights</code> hay hạn trên số đêm khách được ở.</p>

=== 749-755
<p>Ảnh thật 07 bên trái cho số căn lần lượt 17.730 / 20.436 / 13.563 / 20.573, cực đại minimum_nights là 999 / 500 / 7 / 500. Mốc tháng 3 chỉ khoảng 0,18% kín lịch (ảnh làm tròn 0,2%). Ba dấu hiệu đi cùng nhau cảnh báo mốc bị lọc khác, không đủ để kết luận hàng nghìn chủ đã rời thị trường.</p>

=== 757-763
<p>Khung phải có một thanh chia hai phần số đếm: giải thích được và chưa rõ lý do. Chừa khoảng dưới cho nhãn phần nhỏ; dùng xám cho phần chưa rõ chứ không tô cam như bằng chứng đã xác định.</p>

=== 764-767
<p>Thanh cộng dồn theo số căn, nhãn kèm % trên <code>n_missing</code>. Biểu thức <code>for ... in parts if n_missing else ()</code> chọn iterable rỗng khi tổng 0, nên không thực hiện phép chia 0 trong nhãn.</p>

=== 768-772
<p>Phần từ 35% trở lên đặt chữ trắng trong thanh; phần hẹp ghi bên dưới, căn theo mép phải. Ảnh thật có 3.569/4.645 = <b>76,8353%</b> bên trong và 1.076/4.645 ≈ 23,2% ghi dưới phần xám.</p>

=== 773-779
<p>Nếu không có căn vắng thì dùng giới hạn x=1 để tránh trục suy biến, in “Không áp dụng tỷ lệ” và bỏ tick số. Nếu có, trục x là số căn thực. Nhánh này bảo vệ trình bày, không thay thế kiểm dữ liệu đầu vào có số đếm âm hay không.</p>

=== 780-783
<p>Tiêu đề định nghĩa cohort audit: căn có mặt ở mọi mốc bình thường nhưng vắng ở gap. Do đó 4.645 không phải hiệu 20.436 − 13.563 hay 20.573 − 13.563. Con số <code>len(audit)-1</code> hiện là ba mốc đối chiếu; ở đây chỉ trình bày kết quả bước chia nhóm đã tính.</p>

=== 785-790
<p>Tiêu đề “căn vắng không có nghĩa là căn biến mất” là bài học về độ phủ. Dòng phụ lấy cực đại minimum_nights và % kín lịch tại đúng <code>gap_pos</code>, không dùng số của snapshot cuối để mô tả gap.</p>

=== 791-798
<p>“Giải thích được” là ở mốc cuối đòi trên 7 đêm hoặc kín lịch, khớp đặc điểm thiếu ở tháng 3; không có nghĩa đã biết chắc lịch sử từng căn tại ngày gap. Ghi lý do ma trận 02/05 dùng cặp bỏ qua gap, thêm nguồn đủ bốn mốc và lưu PNG.</p>

=== 801
<p>Hình 08 chuyển đơn vị phân tích sang review có nhãn LLM trong mẫu nhóm, không còn là toàn bộ listing thành phố.</p>

=== 804-808
<p><code>complaint_table</code> chuẩn bị ba kết quả: bảng % chê theo nhóm × aspect, bảng số review chê, và số review có nhãn mỗi nhóm. Không có review thì tỉ lệ không xác định, phải giữ NaN thay vì gán 0% như bằng chứng không ai phàn nàn.</p>

=== 810-812
<p>Hàm lồng <code>pivot</code> đổi một cột số sang ma trận đủ bảy nhóm và các aspect cấu hình. <code>aggfunc="first"</code> lấy giá trị đầu khi trùng khoá, không cộng; hợp đồng đầu vào cần mỗi cặp nhóm/aspect chỉ có một kết quả tổng hợp.</p>

=== 814-817
<p>Share LLM là tỉ phần nên nhân 100; bảng counts giữ số review. <code>n_reviews</code> lặp lại trên mỗi aspect nên lấy <code>max</code> theo nhóm, không cộng sáu lần. Reindex nhóm thiếu thành n=0, rồi che cả hàng share bằng NaN khi n=0. Test kiểm nhóm không review và đối chiếu counts/n với share.</p>

=== 818-820
<p>Tất cả nhóm đều không review có nhãn thì lỗi thay vì xuất một heatmap trống. Có ít nhất một nhóm có review mới trả ba bảng. Test <code>test_complaint_table_rejects_table_without_reviews</code> chứng minh nhánh này.</p>

=== 823-828
<p><code>draw_llm_complaints</code> ghi <code>08_llm_complaints_by_segment.png</code>. Chỉ tô màu nhóm có ít nhất 30 review, nhưng vẫn ghi số của nhóm nhỏ; quy tắc này tránh làm một ô 4/12 trông như phát hiện vững chắc khi đặt cạnh hàng có hàng trăm review.</p>

=== 829-833
<p>Thứ tự aspect lấy từ config, ba bảng lấy từ helper. Số căn lấy <code>max(n_listings)</code> theo nhóm vì n lặp trên các aspect; đây là tổng căn trong mẫu, kể cả căn không có review gán nhãn. Nhãn hàng vì vậy có thể ghi “có căn, không có review”, không đánh đồng hai độ phủ.</p>

=== 835-838
<p>Tạo bản sao share rồi che hàng có n &lt; 30 bằng NaN để heatmap hiện xám. Bảng share gốc và counts vẫn giữ nguyên để ghi nhãn. Đúng 30 review đã được tô, còn 0 review có thông báo riêng bên dưới.</p>

=== 839-843
<p>Chỉ lấy cực đại các ô đủ cỡ mẫu để đặt thang màu. Công thức đi lên bội 10 kế tiếp, tối thiểu 10: nếu peak đúng 20 thì vmax=30 chứ không giữ 20. Không có ô được tô thì vmax vẫn 10. Hình không vẽ colorbar nên đọc con số trong ô, đừng chỉ nhìn độ đậm.</p>

=== 845-849
<p>Dựng heatmap màu cam, tên cột dùng bản dịch nếu có, tên hàng kèm cả n căn và n review. Ảnh thật 08: hàng khoẻ mạnh có màu; hàng ngủ đông, kín lịch vẫn có review và mở nhiều ít review màu xám vì nhỏ hơn ngưỡng, dù vẫn hiện số. Xám không có nghĩa là tỉ lệ chê bằng 0.</p>

=== 851-857
<p>Với n=0, ghi một câu giữa hàng rồi <code>continue</code>, không chia mẫu số 0. <code>D_never/N_new</code> được ghi “theo định nghĩa không có review”; <code>B_ghost</code> ghi “không có review trong mẫu”, không kết luận chưa từng có review trong đời listing.</p>

=== 858-865
<p>Nhóm có review mới duyệt từng aspect: hàng nhỏ chữ xám; hàng đủ mẫu thì ô từ 55% thang màu đổi chữ trắng; còn lại chữ tối. Ngưỡng chữ trắng là 0,55 × vmax, không phải tỉ lệ chê 55% cố định như hình chuyển nhóm.</p>

=== 866-867
<p>Mỗi ô in % làm tròn và phân số <code>số review chê / số review của nhóm</code>. Ảnh thật hiện ngủ đông chê tiện nghi 4/12 (33%) và khoẻ mạnh 81/954 (8%); đây là số đọc trực tiếp từ PNG, chưa tự đối tính từ CSV nguồn vì bảng <code>data/processed/sydney/llm_segment_aspects.csv</code> không có trong bản commit. Không lấy fixture số giả để xác nhận các số này.</p>

=== 869-873
<p>Cộng n review của ba nhóm ảo, không cộng số lượt chê aspect vì một review có thể chê nhiều thứ. Dưới 30 thì tiêu đề cảnh báo chưa đủ kết luận; từ 30 dùng tiêu đề trung tính, chứ không tự khẳng định đủ đại diện hay có khác biệt thống kê. PNG thật ghi chỉ 12 review thuộc căn ảo; đây là quan sát trên ảnh, không phải số CSV đã tái tính.</p>

=== 874-879
<p>Phụ đề ghi tổng review có nhãn ghép với nhóm căn ở mốc cuối. Ảnh thật là 1.000 review của mẫu nhóm, không phải 20.573 căn toàn thành phố hay mọi review trong năm. Mẫu số mỗi ô là review của hàng, nên tổng % theo hàng không bắt buộc bằng 100%.</p>

=== 880-887
<p>Ghi hạn chế mẫu nhỏ, một review nhiều aspect, review có thể cũ hơn thời điểm phân nhóm và không suy rộng ra Sydney. Tuy nhiên câu “chưa đo accuracy/F1” đã lỗi thời: <code>reports/evaluation/eval_summary.csv</code> có accuracy LLM 0,97 và macro-F1 ≈ 0,936 trên 100 gold. Đếm ID duy nhất trong <code>eval_per_review.csv</code> được 85 positive, 15 mixed, không có negative; thiếu lớp này hạn chế đánh giá chứ không có nghĩa chưa công bố điểm.</p>

=== 890
<p>Phần cuối nối các hàm riêng thành API chạy một lần, dùng chung dữ liệu đã đọc.</p>

=== 892-903
<p><code>FIGURES</code> là sổ đăng ký tám PNG theo thứ tự 01–08: tên file, danh sách khoá CSV, hàm vẽ và khoá config cần có. Hình 02/05 cùng dùng transitions; 03/04/06 cùng dùng KPI; 07 cần cả audit lẫn summary. <code>None</code> chỉ nghĩa không có khoá config đặc biệt để kiểm trước, không phải hàm vẽ hoàn toàn không cần cấu hình.</p>

=== 906-912
<p><code>skip_reason</code> kiểm điều kiện để vẽ một hình, trả chuỗi nếu bỏ qua và <code>None</code> nếu được đi tiếp. Đây là phép kiểm tính sẵn có, chưa đọc nội dung CSV; dữ liệu có file nhưng lỗi schema sẽ bị chặn ở lớp sau.</p>

=== 913-917
<p>Ưu tiên báo config thiếu/rỗng trước. Riêng transitions còn cần ít nhất một cặp mà cả hai mốc nằm trong snapshots; vậy đổi bộ mốc sẽ bỏ hình đúng lý do thay vì yêu cầu dữ liệu của cặp không còn chạy. Tests kiểm cả config rỗng và cặp ở ngoài snapshots.</p>

=== 918-920
<p>Với hình gap, mốc cấu hình phải còn trong lần chạy. Đây chỉ kiểm mốc <em>config</em>; chưa đối chiếu mốc lấy từ summary ở <code>gap_numbers</code>. Hai bên có thể lệch dù đều là ngày hợp lệ, xem review.</p>

=== 921-926
<p>Với mỗi đầu vào, xét <code>exclude</code> trước kiểm file tồn tại. Nếu lần này không làm mới bảng, vẫn bỏ hình dù file cũ đang còn trên đĩa. Test <code>test_excluded_inputs_are_not_drawn_from_old_files</code> dùng LLM fixture có sẵn để kiểm việc không tái dùng số cũ. Trả lý do đầu tiên gặp, không gom mọi lý do.</p>

=== 929-942
<p>API <code>run</code> trả danh sách các PNG vừa ghi, nhận scope, bộ đường dẫn tuỳ chọn, thư mục ảnh và tập đầu vào không được dùng. Dấu <code>*</code> buộc các tham số sau config phải ghi tên khi gọi, giảm nhầm scope với đường dẫn. Docstring mô tả <code>exclude</code> là tín hiệu từ pipeline, không phải hàm tự so timestamp của file.</p>

=== 943-946
<p>Không truyền scope thì đọc <code>segments.scope</code>; không truyền inputs hoặc truyền dict rỗng thì dựng đường dẫn thật. Tạo thư mục ảnh đệ quy nếu thiếu. Cờ <code>scope</code> chỉ ảnh hưởng các đường dẫn có hậu tố như đã phân tích, không lọc thêm cột KPI theo <code>full/sample</code>.</p>

=== 948-954
<p><code>tables</code> cache DataFrame theo khoá để mỗi CSV chỉ đọc một lần; <code>paths</code> chỉ chứa kết quả lần chạy hiện tại. Duyệt sổ hình, có lý do thì in <code>[VIZ] Bỏ qua...</code> và chuyển hình sau. Nhánh này không có lệnh xoá PNG cũ; file tồn tại trong thư mục không đủ chứng minh lần chạy vừa rồi đã tạo nó.</p>

=== 955-957
<p>Hình được phép vẽ mới đọc những CSV cần, kiểm schema bằng <code>INPUT_COLUMNS</code>. Hình 03, 04, 06 dùng chung DataFrame KPI đã cache; hình 07 lỗi một bảng sẽ dừng ở lỗi đó. Không có <code>try/except</code> để nuốt lỗi nội dung và tiếp tục tạo bộ hình khó tin cậy.</p>

=== 958-962
<p>Ghép tên PNG, gọi hàm vẽ rồi mới in thông báo thành công và thêm đường dẫn vào kết quả. Nếu draw ném lỗi, hình sau không chạy, các hình đã ghi trước đó vẫn có thể còn. Test chạy đủ fixture yêu cầu trả đúng thứ tự tám tên và file PNG có dung lượng đáng kể.</p>

=== 965-970
<p>CLI nhận YAML mặc định và tuỳ chọn phạm vi với hai giá trị <code>full/sample</code>. <code>argv=None</code> để argparse đọc đối số tiến trình; tests có thể truyền list trực tiếp mà không mở subprocess.</p>

=== 971-976
<p><code>--sample-dir</code> đổi toàn bộ đầu vào sang sáu CSV demo; <code>--out</code> đổi nơi ghi PNG. Đọc config qua <code>load_config</code> như pipeline rồi gọi API; đây không phải CLI tự tính KPI thiếu. Test <code>test_cli_with_sample_dir</code> kiểm việc tạo PNG từ dữ liệu fixture.</p>

=== 979-980
<p>Chỉ chạy CLI khi thực thi trực tiếp module. Import để dùng helper hay chạy tests không tự vẽ hình, không đọc CSV nghiệp vụ.</p>

--- flow
## Chọn đầu vào
fn 0 965 | main | CLI đọc config chuẩn hoá
fn 0 929 | run | Điều phối tám hình, trả PNG vừa ghi
st 1 116 | real_inputs | Đường dẫn thật theo phạm vi
st 1 130 | sample_inputs | Hoặc sáu CSV demo
st 1 906 | skip_reason | Config, exclude, file tồn tại
st 1 135 | read_input | Kiểm cột và bảng không rỗng
## Vẽ theo thứ tự sổ hình
fn 0 292 | draw_segments | 01: cơ cấu bảy nhóm mốc cuối
fn 0 368 | draw_transitions | 02: chuyển nhóm, % theo hàng
st 1 349 | transition_table | Cặp hợp lệ đầu tiên, bỏ hàng 0
fn 0 431 | draw_phantom_by_area | 03: xếp hạng khu ≥300 căn
st 1 417 | ranked_areas | Tách khu nhỏ, giữ cho ghi chú
fn 0 505 | draw_long_stay_license | 04: hai mẫu số về đêm và đăng ký
st 1 483 | night_buckets | Đủ bốn bucket, n là số căn bucket
fn 0 581 | draw_review_return | 05: ba trạng thái chồng 100%
st 1 562 | review_return_shares | Gộp cột rồi chia tổng nhóm nguồn
fn 0 660 | draw_price_vs_neighbours | 06: hai khung giá cùng thang x
st 1 696 | self_peer_note | Nhắc thành phần chuẩn so sánh
fn 0 727 | draw_march_gap | 07: độ phủ và cohort căn vắng
st 1 715 | gap_numbers | Đủ mốc, tổng hai phần khớp
fn 0 823 | draw_llm_complaints | 08: review chê theo nhóm/aspect
st 1 804 | complaint_table | Giữ NaN khi không có review
st 1 835 | Che hàng mẫu nhỏ | Dưới 30 review không tô màu
st 0 958 | Ghi kết quả | Chỉ thêm paths sau khi vẽ thành công

--- review
mid | Chú thích đánh giá LLM lỗi thời | Dòng 883 và PNG 08 nói chưa đo accuracy/F1; CSV <code>reports/evaluation/eval_summary.csv</code> đã có accuracy LLM 0,97, macro-F1 0,935774, aspect micro-F1 0,904277 trên 100 gold. Đếm gold duy nhất được 85 positive, 15 mixed, 0 negative; hạn chế lớp negative có thật nhưng câu “chưa đo” không còn đúng.
mid | Scope có thể trộn mẫu và toàn thành phố | Đã gọi <code>real_inputs</code> với full/sample: KPI đều trỏ <code>data/processed/kpi_phantom.csv</code>, LLM cũng không có hậu tố. CSV counts sample có 84/1.000 căn ảo, còn KPI commit là 21,188% trên 20.573 căn. Chạy sample không đồng nghĩa mọi hình đã cùng phạm vi.
mid | Kiểm số hẹp hơn lời hứa đầu file | Dòng 18 nói sai số sẽ dừng hẳn, nhưng thử <code>kpi_rows</code> với value=-10 và n_obs=1.9 vẫn trả value=-10, n_obs=1. Hàm ép kiểu, chưa kiểm miền % hay số đếm nguyên; một số nhánh khác có kiểm riêng, không phải bộ kiểm dữ liệu tổng quát.
mid | Summary gap chưa đối chiếu cấu hình | <code>gap_numbers</code> dùng dòng summary đầu và kiểm tổng; thay gap_snapshot trong summary full thành 2025-09-12 vẫn được nhận dù config ghi 2026-03-21. Nếu file cũ lệch mốc, tiêu đề có thể chỉ nhầm snapshot; CSV commit hiện tại khớp config.
mid | Hình LLM có nhưng thiếu CSV để tái tạo | Đã kiểm đường dẫn thật: <code>data/processed/sydney/llm_segment_aspects.csv</code> không có, còn PNG 08 đã commit. <code>skip_reason</code> trả lý do thiếu file, nên clone hiện tại có thể tái vẽ bảy hình đầu từ các bảng tổng hợp, nhưng hình 08 cần tái sinh bảng LLM ghép nhóm. Các số 12 và 954 trong chú giải hình 08 được ghi rõ là đọc từ ảnh, không lấy từ fixture.
ok | Phân biệt thiếu bằng chứng với số 0 | Hình LLM giữ NaN cho nhóm không review và không tô hàng dưới 30; hình giá ghi thiếu giá thay vì diễn giải thanh 0 là giá 0. Tests kiểm trường hợp không review, bảng LLM rỗng và các nhánh tiêu đề dự phòng.
ok | Chặn tái dùng CSV được đánh dấu cũ | <code>exclude</code> được kiểm trước file tồn tại; test xác nhận đầu vào LLM có sẵn vẫn bị bỏ nếu lần này không làm mới. Danh sách paths trả về chỉ gồm PNG vừa tạo, nên caller nên dùng danh sách này thay vì đếm file còn trong thư mục.

--- qa
? File này có tự phân nhóm listing hay tính lại giá từ raw không?
<p>Không. Nó đọc bảng tổng hợp đã tính ở bước 3, 4b, 5b. Hình 01 tự tính % từ số đếm n; hình 06 chỉ trình bày ratio KPI đã có. Thứ tự nhóm và ba nhóm ảo được nhập từ module luật.</p>
? Đọc hình 01 và hình 02 khác nhau ở mẫu số nào?
<p>Hình 01 lấy tổng 20.573 căn cuối kỳ làm mẫu số; ba nhóm ảo là 4.359 căn, 21,188%. Hình 02 chia theo từng nhóm ở mốc đầu. Ví dụ ngủ đông có 1.632 căn nguồn, 1.068 căn giữ nhóm = 65,4412%, không phải 65% căn toàn thành phố.</p>
? Vì sao hình 03 không có Mosman dù tỉ lệ cao?
<p>Ngưỡng xếp hạng là ít nhất 300 căn. Mosman có 271 căn, 36,1624% nên nằm trong ghi chú khu nhỏ; 19 khu đủ ngưỡng mới được xếp hạng. Pittwater 36,4924% và Auburn 12,2939% là hai đầu của bảng hợp lệ.</p>
? “98% căn không có số đăng ký” có phải 98% toàn Sydney không?
<p>Không. Hình 04 bên phải lấy riêng 1.269 căn thiếu đăng ký có số đêm hợp lệ làm mẫu số: 1.244 căn đòi từ 90 đêm, bằng 98,0299%. Tỉ lệ thiếu đăng ký trên toàn bộ 20.573 căn chỉ 6,1683%. Chuỗi Exempt không tính là trống.</p>
? Hình 05 nói 15% căn ngủ đông có review trở lại được tính thế nào?
<p>Cộng ba cột đích B_booked, L_low, H_healthy: 30 + 98 + 121 = 249 căn; chia 1.632 căn ngủ đông nguồn được 15,2574%, in 15%. Đây là trạng thái có review trong cửa sổ gần đây ở mốc cuối, không phải tỉ lệ booking.</p>
? Vì sao hình giá bắt buộc đọc riêng hai khung?
<p>Giá/đêm dài ngày và ngắn ngày có chế độ khác nhau; KPI ghép hàng xóm theo cùng khu, loại phòng và khung lưu trú rồi lấy trung vị ratio theo nhóm. Ngủ đông ngắn ngày là 1,3203× (n=791), dài ngày 0,9583× (n=836). Trong khung dài, nhóm ảo chiếm khoảng 90,47% căn có giá nên chính chúng đóng góp nhiều vào chuẩn so sánh.</p>
? Vì sao không lấy hiệu hai cột listing để ra 4.645 căn vắng tháng 3?
<p>4.645 là cohort ID có ở cả ba mốc bình thường nhưng vắng ở gap, do bước audit tính. Trong đó 3.569 + 1.076 = 4.645; phần giải thích được là 76,8353%. Cột tháng 3 có 13.563 căn, nhưng hiệu số tổng listing không giữ được điều kiện cùng ID.</p>
? Ô xám hình 08 là 0% chê hay không đo được?
<p>Có hai trường hợp: nhóm không review thì share là NaN và ghi lý do; nhóm có ít hơn 30 review vẫn ghi tỉ lệ/count nhưng không tô màu. Không suy màu xám là không phàn nàn. PNG thật và CSV nguồn LLM cần phân biệt: CSV ghép nhóm không có trong bản commit nên số trên PNG chưa được đối tính lại từ bảng đó.</p>
