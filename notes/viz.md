--- meta
title: viz.py
lead: Bước 6 đọc <code>data/processed/kpi_metrics.csv</code>, kiểm dữ liệu rồi vẽ 7 PNG thường và thêm hình 08 nếu có KPI LLM. File này không tính lại KPI và không tự lấy dữ liệu toàn thành phố: phạm vi số liệu phụ thuộc CSV do bước 5 ghi. Cần nhớ ba điểm khi đọc hình: trục tỷ lệ bắt đầu từ 0, khu vực được chọn theo số quan sát, hai cột LLM có hai mẫu số khác nhau.

--- blocks
=== 1-12
<p>Giới thiệu hợp đồng của bước trực quan hóa: đọc kết quả đã tính, không tạo số mẫu hay nội suy. Năm hình đầu là năm KPI qua bốn mốc; hình 06–07 so khu vực tại mốc cuối; hình 08 là kết quả LLM gộp review, không phải đường theo thời gian.</p>
<p>Chữ “KPI thực tế” nghĩa là số từ pipeline, không có nghĩa mẫu đại diện toàn Sydney. CSV đã commit có <code>n_obs=1.000</code> cho các KPI listing toàn mẫu; không được nhầm với 20.573 căn trong phân tích căn ảo ở <a href="#f-viz_phantom">viz_phantom.py</a>.</p>

=== 14-22
<p>Hai cách gọi cùng một logic: CLI <code>python -m src.viz</code> hoặc <code>viz.run(config)</code>. Hai cờ <code>--kpi</code>, <code>--out</code> đổi đường dẫn vào/ra; mặc định là đường dẫn tương đối với thư mục làm việc. Vì vậy ví dụ yêu cầu chạy từ gốc repo nhóm.</p>

=== 24
<p>Hoãn đánh giá chú thích kiểu. Các kiểu như <code>list[Path]</code> và <code>dict[str, Any]</code> mô tả giao diện hàm, không tự kiểm dữ liệu khi chạy; các kiểm tra thật nằm trong <code>extract_*</code>.</p>

=== 26-30
<p><code>argparse</code> đọc CLI; <code>math.isfinite</code> loại vô cực; <code>dataclass</code> giữ đặc tả biểu đồ; <code>Path</code> quản lý đường dẫn. <code>Any</code> dành cho dict cấu hình và đối tượng trục matplotlib, không phải schema đầu vào.</p>

=== 32-36
<p><code>pandas</code> đọc CSV, lọc bảng, đổi số và ngày. <code>FigureCanvasAgg</code> gắn bộ kết xuất ra ảnh với <code>Figure</code>, không cần cửa sổ đồ họa hay <code>pyplot.show()</code>. <code>load_config</code> dùng chung chuẩn hóa YAML với pipeline.</p>

=== 38-43
<p>Hai đường dẫn mặc định và sáu cột tối thiểu của bảng KPI dạng dài. Mỗi dòng biểu diễn một KPI, tại một snapshot, một scope và một nhóm, kèm <code>value</code> và mẫu số <code>n_obs</code>. Ví dụ <code>overall/all</code> khác <code>neighbourhood_cleansed/Sydney</code>; chữ Sydney ở nhóm là tên một khu, không phải dòng toàn mẫu.</p>

=== 46-55
<p><code>ChartSpec</code> gom năm thuộc tính đồng hành để không ghép nhầm tên KPI, tiêu đề, nhãn trục, tên PNG và đơn vị. <code>frozen=True</code> ngăn gán lại các trường sau khởi tạo. Comment giải thích vì sao giữ tên file 01–03: tương thích tài liệu cũ, dù nay có thêm hình.</p>

=== 58-66
<p>Hình <code>01_availability_rate_by_snapshot.png</code> đọc <code>availability_rate</code>. <b>Đọc ảnh thật:</b> bốn điểm 49,65% → 50,08% → 52,18% → 50,76%, đường gần ngang quanh 50 trên trục 0–100. Đây là tỷ lệ ngày lịch có <code>available='t'</code>, không phải tỷ lệ căn trống và cũng không phải tỷ lệ đã đặt.</p>
<p>Tự đọc lại <code>data/processed/kpi_metrics.csv</code>: mẫu số mỗi mốc là 365.000 ngày hợp lệ. Công thức ở <a href="#kpi-L361">kpi.py</a>; viz chỉ lấy số đã tính.</p>

=== 67-73
<p>Hình <code>02_long_stay_restriction_rate_by_snapshot.png</code> đọc <code>long_stay_restriction_rate</code>. Ảnh thật có 7,20% → 8,00% → 3,50% → 4,40%; đường sát đáy vì vẫn dùng thang 0–100. Mốc cuối tương ứng 44/1.000 căn có yêu cầu tối thiểu từ 7 đêm.</p>
<p>Ngưỡng này là 7 đêm trong <a href="#kpi-L371">KPI thường</a>, khác ngưỡng 90 đêm của phân tích căn ảo. Tiêu đề ở đây viết cứng ngưỡng, không đọc từ metadata của CSV.</p>

=== 74-80
<p>Hình <code>03_high_utilization_listing_rate_by_snapshot.png</code> đọc <code>high_utilization_listing_rate</code>. Ảnh thật lên đỉnh 25,60% ở tháng 12, rồi về 22,80%; bốn giá trị là 23,20 / 25,60 / 24,30 / 22,80%, mỗi mẫu số 1.000 căn trong CSV.</p>
<p>“Khai thác cao” được <a href="#kpi-L386">kpi.py</a> xác định bằng <code>estimated_occupancy_l365d &gt;= 180</code>. Đây là occupancy ước tính của 365 ngày qua, không phải lấy <code>100 - availability_rate</code> của lịch tương lai.</p>

=== 81-87
<p>Hình <code>04_professional_host_presence_by_snapshot.png</code> đọc <code>professional_host_presence</code>. Ảnh thật dao động 50,95% → 51,69% → 47,97% → 52,03%. Đơn vị là <b>host</b>: CSV có mẫu số lần lượt 738 / 739 / 740 / 738; mốc cuối quy đổi thành 384/738 host bằng cách nhân tỷ lệ CSV với mẫu số rồi làm tròn tử số.</p>
<p>“Chuyên nghiệp” ở đây chỉ là quy ước host có hơn một listing, không phải chứng nhận nghề nghiệp. <a href="#kpi-L404">KPI</a> gom host trước khi tính, nên không được lấy 52,03% nhân với 1.000 căn.</p>

=== 88-95
<p>Hình <code>05_high_rated_listing_share_by_snapshot.png</code> đọc <code>high_rated_listing_share</code>. Ảnh thật giảm đều 36,53% → 35,46% → 34,46% → 32,82%. CSV cho mẫu số 950 / 970 / 975 / 975 listing có điểm; mốc cuối là 320/975, không phải 320/1.000.</p>
<p>Ngưỡng từ 4,9 điểm nằm trong <a href="#kpi-L431">kpi.py</a>. Đường giảm mô tả tỷ trọng đạt ngưỡng trong mẫu có điểm ở từng mốc; riêng hình này không chứng minh chất lượng của từng căn giảm.</p>

=== 96-99
<p>Tên file cố định cho hai hình khu vực. Hình 06 dùng scope từ <code>config.kpi.area_col</code>; hình 07 luôn dùng <code>analysis_area</code>. Hai hệ khu vực khác nhau: không đối chiếu A05 với Pittwater chỉ dựa vào vị trí cột.</p>

=== 101-112
<p>Danh mục sáu KPI phần trăm được dùng để chọn kiểm miền 0–100. Không suy bằng hậu tố <code>_rate</code>, vì <code>professional_host_presence</code> và <code>high_rated_listing_share</code> cũng là phần trăm. <code>frozenset</code> phù hợp tra thành viên và không bị sửa bằng <code>add</code>.</p>
<p>Hai KPI LLM không nằm trong tập này nhưng vẫn được kiểm phần trăm riêng ở <a href="#viz-L399">dòng 399</a>. Hình 07 cũng truyền thẳng <code>rate=True</code>.</p>

=== 113-118
<p><code>DejaVu Sans</code> là font có chữ tiếng Việt; ảnh thật hiển thị đầy đủ dấu. <code>INK</code> là màu chữ đậm, <code>ACCENT</code> xanh ngọc là màu chung cho đường và cột. Màu xanh này không mã hóa nhóm hay mức độ rủi ro.</p>

=== 119-124
<p><code>MUTED</code> làm nhạt chữ phụ, <code>GRID</code> là lưới và viền trục, <code>BG</code> trắng cho cả Figure và ảnh lưu. Đây là hằng số trình bày, không tham gia tính KPI.</p>

=== 127-131
<p><code>load_kpi</code> kiểm file tồn tại trước khi đọc; thông báo hướng người chạy quay lại bước KPI. Bốn cột khóa được ép chuỗi để ngày và tên nhóm khớp điều kiện lọc. <code>value</code>, <code>n_obs</code> được kiểm số sau khi chọn đúng các dòng cần vẽ.</p>

=== 132-137
<p>Lấy hiệu tập cột để liệt kê đủ cột thiếu, sắp tên cho thông báo ổn định. CSV có header đủ nhưng không có dòng bị từ chối riêng. Cột thừa được phép; hàm này chưa kiểm khóa trùng hay miền số. <code>tests/test_viz.py</code> kiểm cả đọc thành công, thiếu file, thiếu cột và bảng rỗng.</p>

=== 140-147
<p>Hàm kiểm số dùng chung cho đường, cột khu vực và LLM. <code>to_numeric(errors='coerce')</code> chấp nhận chuỗi số, đổi chữ không đọc được thành NaN để báo lỗi thống nhất. Hai Series đổi kiểu là biến cục bộ; hàm không gán đè các cột trong bảng đầu vào.</p>

=== 148-151
<p>Giá trị phải vừa không thiếu vừa hữu hạn: kiểm NaN chưa đủ để bắt <code>inf</code>. Mẫu số phải hữu hạn và lớn hơn 0, nên KPI không có quan sát không được vẽ thành 0%. Test có từng ca <code>None</code>, vô cực và mẫu số 0.</p>
<p>Giới hạn kiểm tra: không yêu cầu <code>n_obs</code> là số nguyên. Chạy Python với <code>value=50, n_obs=0.5</code> vẫn nhận <code>[50.0]</code>; đó là kiểm điều kiện dương, chưa phải kiểm đầy đủ ngữ nghĩa “số quan sát”.</p>

=== 152-157
<p>Chuyển kết quả sang list float cho matplotlib. Với tỷ lệ, cả 0 và 100 đều hợp lệ; ngoài đoạn đóng này thì lỗi. Với đại lượng thường chỉ cấm âm, không áp trần 100. Việc kiểm diễn ra trước khi lưu bất kỳ hình nào trong đường chạy <code>run</code>.</p>

=== 160-168
<p><code>extract_series</code> chọn đồng thời ba khóa <code>scope='overall'</code>, <code>group_name='all'</code>, tên KPI. Giữ snapshot, giá trị, mẫu số trên bản sao; không lấy trung bình các khu vực vì mẫu số giữa khu khác nhau.</p>
<p>Docstring gọi đây là “toàn thành phố”, nhưng code chỉ biết nhãn <code>overall</code>. Với CSV đã commit, đó là tổng hợp trên mẫu được giao, không tự mở rộng tới dữ liệu full.</p>

=== 169-171
<p>Kiểm đủ mọi mốc mà config yêu cầu. Thiếu một mốc thì báo lỗi kèm danh sách, không thay bằng 0, không nối đường bắc qua chỗ thiếu. Các dòng snapshot ngoài config không bù được mốc đang thiếu.</p>

=== 172-176
<p>Lọc bỏ mốc ngoài danh sách trước khi kiểm trùng; hai dòng cùng mốc được chọn là lỗi, không tùy tiện lấy dòng đầu hay lấy trung bình. Sau đó đặt index rồi <code>.loc[snapshots]</code> để giữ <b>thứ tự config</b>, không phải thứ tự CSV hay tự sắp ngày.</p>
<p>Test đảo thứ tự dòng CSV vẫn ra đúng dãy. Chạy thử đảo danh sách config với CSV thật cho dãy availability 50,7595 → 52,18 → 50,0811 → 49,6477; hàm tôn trọng cả danh sách ngày đảo ngược.</p>

=== 179-185
<p>Áp phong cách chung: nền trắng, bỏ viền trên/phải, làm nhạt viền trái/dưới. Tham số là Axes; không tạo biểu đồ mới nên cùng kiểu được dùng cho cả đường lẫn cột.</p>

=== 186-188
<p>Lưới ngang mảnh giúp đọc tỷ lệ, đặt phía dưới dữ liệu để không cắt ngang marker. <code>length=0</code> bỏ vạch tick nhỏ nhưng vẫn giữ nhãn; cỡ chữ tick là 10. Hai hình khu vực sẽ đổi sang lưới dọc để hợp hướng cột ngang.</p>

=== 191-195
<p>Tạo Figure theo inch rồi gắn canvas Agg. Khi lưu ở 165 dpi, hình đường 10,5 × 5,8 inch cho kích thước xấp xỉ 1.732 × 957 pixel như ảnh đã commit. Không cần display của hệ điều hành; các test vẽ được PNG offline.</p>

=== 198-202
<p><code>draw_trend</code> nhận dữ liệu đã trích và một <code>ChartSpec</code>, dựng Figure rồi đặt Axes bằng tỷ lệ khung hình: trái 0,09, dưới 0,22, rộng 0,86, cao 0,63. Khoảng trống dưới dành cho ngày và nhãn trục, phía trên dành tiêu đề.</p>

=== 203-207
<p>Trục x dùng vị trí nguyên 0, 1, 2, 3; ngày chỉ là nhãn <code>dd/mm/YYYY</code>. Các điểm cách đều dù số ngày giữa các snapshot không bằng nhau. Đây là đường nối bốn lần chụp, không phải mô hình diễn biến hằng ngày hay hồi quy theo khoảng thời gian thực.</p>
<p>Đường xanh dày, marker tròn và <code>zorder=3</code> giúp thấy từng điểm trên lưới. Giới hạn x nới 0,2 mỗi đầu để marker không chạm viền.</p>

=== 208-209
<p>Nhãn y lấy từ đặc tả từng KPI nên phân biệt ngày, listing, host. Nhãn x luôn là thời điểm chụp dữ liệu. Font và màu phụ dùng chung để nhãn không lấn át số ngay trên điểm.</p>

=== 210-211
<p>Với đơn vị <code>%</code>, trục y cố định 0–100 để không phóng đại chênh lệch nhỏ. Vì cả năm đặc tả đều là %, cả năm ảnh thật có chung thang này. Nếu dùng đơn vị khác, code chừa trần 1,36 lần giá trị lớn nhất và tối thiểu là 1; docstring “trục tỷ lệ cố định” chỉ mô tả nhánh phần trăm.</p>

=== 212-218
<p><code>zip(..., strict=True)</code> yêu cầu số điểm và số giá trị bằng nhau, tránh bỏ âm thầm phần thừa. Nhãn phần trăm có hai chữ số thập phân; nhánh khác dùng dạng số gọn và thêm đơn vị nếu có. Dịch chữ lên 13 point tính từ marker, không cộng 13 vào giá trị KPI.</p>

=== 219-224
<p>Căn chữ theo tâm điểm, cỡ 11 và in đậm. Vì vậy trên ảnh thật có thể đọc số chính xác đến hai chữ số mà không cần ước lượng từ đường. CSV vẫn giữ nhiều chữ số hơn phần hiển thị.</p>

=== 225-226
<p>Tiêu đề đặt theo tọa độ Figure, tách khỏi vùng dữ liệu. <code>savefig</code> ghi đúng đường dẫn được truyền ở 165 dpi, nền trắng; hàm không tự tạo thư mục cha. <code>run</code> tạo thư mục trước khi gọi, còn người gọi riêng phải chuẩn bị đầu ra.</p>

=== 229-234
<p><code>extract_neighbourhoods</code> đọc ba cột <code>group_name/value/n_obs</code> của KPI availability, đúng snapshot và scope khu vực được cấu hình. <code>area_col</code> ở đây là <b>giá trị của cột scope</b>, không phải tên cột được tra trực tiếp trong bảng KPI.</p>

=== 235-239
<p>Không có dữ liệu khu thì lỗi, không lặng lẽ bỏ hình 06. Tên khu thiếu hoặc lặp trong tập đã chọn cũng bị chặn; sau đó kiểm tỷ lệ và mẫu số trên toàn tập khu vực, kể cả các khu sẽ không vào top 10.</p>

=== 240-242
<p>Gán lại hai cột dạng số để xếp hạng theo số, không theo thứ tự từ điển của chuỗi. <b>Chọn 10 khu nhiều quan sát nhất trước, rồi mới sắp theo tỷ lệ tăng dần</b>. Không phải 10 khu trống nhiều nhất. Nếu ít hơn 10 khu thì giữ số khu có sẵn; test dùng 12 khu để kiểm đúng phép chọn và thứ tự.</p>

=== 245-248
<p>Nhãn <code>n</code> của hình 06 là số listing <b>ước tính</b> từ ngày hợp lệ chia 365, làm tròn rồi ép tối thiểu 1. Với CSV thật: Sydney có 100.010/365 = 274, Pittwater 19.710/365 = 54; đây là hai nhãn đã thấy trên ảnh.</p>
<p>Không có thao tác đếm ID căn ở đây. Chạy thử 912,5 ngày cho 2,5 rồi <code>round</code> thành 2; quy tắc làm tròn này và việc ép tối thiểu 1 có thể che độ thiếu lịch nếu đầu vào không đủ 365 ngày/căn. Chú thích dưới hình đã nói rõ tính ước lượng.</p>

=== 251-257
<p>Hình 06 dùng khung rộng 11,5 × 7 inch, chừa lề trái 24% cho tên khu dài kèm <code>n</code>. Bật lưới theo x, tắt lưới y vì độ dài cột ngang biểu diễn tỷ lệ.</p>

=== 258-264
<p>Lấy list giá trị và ghép nhãn khu với mẫu số theo từng dòng; <code>strict=True</code> bảo đảm không lệch số nhãn. <code>barh</code> vẽ y từ 0 trở lên, nên tập đã sắp tăng dần sẽ hiện <b>khu cao nhất ở trên cùng</b>. Trục x tới 102 để chừa chỗ chữ.</p>
<p><b>Đọc ảnh 06 thật:</b> Pittwater trên cùng 68,23% (54 listing ước tính), Sydney 47,37% (274), Auburn cuối 35,35% (32). Cột dài hơn nghĩa tỷ lệ ngày còn trống cao hơn trong các khu đã chọn, không có nghĩa nhiều căn hơn.</p>

=== 265-266
<p>Ghi tỷ lệ hai số lẻ ở bên phải mỗi cột, cách đầu cột 1,2 đơn vị phần trăm. Đây là tọa độ dữ liệu, khác độ lệch theo point trong hình đường. Chữ hiển thị 68,23% là làm tròn từ 68,2344 trong CSV.</p>

=== 267-275
<p>Tiêu đề cố định “snapshot cuối” ở tọa độ chung của Figure; các dòng còn lại chọn cỡ 16, chữ đậm, màu mực và font tiếng Việt. Từ “cuối” chưa tự bảo đảm là ngày lớn nhất: ngày nào được truyền vào thì vẽ ngày đó.</p>

=== 276-283
<p>Phụ đề đưa ngày thực và tên scope vào hình, giải thích tiêu chí top 10 theo <code>n_obs</code>. Ảnh đã commit ghi 2026-06-16 và <code>neighbourhood_cleansed</code>; đây là căn cứ để không gọi nhầm hình này là tám khu <code>analysis_area</code>.</p>

=== 284-292
<p>Dòng lưu ý dưới ảnh công khai <code>n_obs / 365</code> là ước tính số listing, tránh đọc nhãn <code>n</code> như số ngày. Cỡ chữ nhỏ hơn dữ liệu, đặt dưới trục; cuối cùng lưu PNG cùng dpi/nền với các hình khác.</p>

=== 295-302
<p><code>extract_commercialized</code> luôn lọc <code>scope='analysis_area'</code> và KPI <code>commercialized_listing_rate</code> tại một mốc. Không dùng <code>area_col</code>, không áp top 10, không tính tỷ lệ lại từ các cột vẽ.</p>

=== 303-307
<p>Chặn thiếu toàn bộ KPI, tên khu thiếu/trùng, giá trị hoặc mẫu số không hợp lệ. Đây là cùng nguyên tắc với hình 06: không vẽ dữ liệu mơ hồ thành một ảnh trông có vẻ hợp lệ.</p>

=== 308-309
<p>Đổi giá trị thành số rồi sắp tăng dần để <code>barh</code> hiện tỷ lệ cao ở trên. Không cần đổi <code>n_obs</code> trong bảng trả về vì hàm vẽ hình 07 không dùng cột đó làm nhãn, nhưng mẫu số vẫn đã được kiểm.</p>

=== 312-318
<p>Khung hình 07 cùng kích thước hình 06; lề trái chỉ 16% vì nhãn A01…A08 ngắn. Lưới dọc và nền/viền dùng chung để so độ dài cột, không có bản đồ địa lý trong hình này.</p>

=== 319-325
<p>Nhãn chỉ lấy <code>group_name</code>; trục x cố định 0–100. <b>Đọc ảnh 07 thật:</b> từ trên xuống A05 70,63%, A02 69,05%, A04 58,33%, A06 57,50%, A07 55,04%, A01 49,59%, A03 45,38%, A08 38,10%.</p>
<p>“Thương mại” là <code>Entire home/apt</code> đồng thời host có hơn một listing, theo <a href="#kpi-L449">công thức KPI</a>. Nhân tỷ lệ CSV với mẫu số rồi làm tròn tử số cho A05 là 89/126, A08 là 48/126; mẫu số tám khu cộng thành 1.000. Không suy thành số host hay tỷ lệ căn ảo.</p>

=== 326-327
<p>Gắn tỷ lệ ở đầu cột để phân biệt A05 với A02 dù chiều dài gần nhau. Hình không in <code>n_obs</code>; muốn biết cỡ mẫu từng khu phải đọc CSV, không lấy tỷ lệ cao đồng nghĩa nhiều quan sát.</p>

=== 328-336
<p>Tiêu đề nêu rõ “khu vực phân tích”, phân biệt với khu hành chính ở hình 06. Chữ đậm 16 và màu/font dùng chung; không làm biến đổi thứ tự hay số liệu.</p>

=== 337-338
<p>Ngày snapshot là phụ đề riêng, sau đó lưu ảnh. Ảnh thật ghi 2026-06-16; đó là mốc cuối trong cấu hình hiện tại, không phải ngày được tự tìm từ CSV.</p>

=== 341-345
<p>Hình 08 nhận bảng KPI LLM và list giá trị đã kiểm. Chừa lề trái 36% cho nhãn dài có mẫu số; dùng cùng phong cách trục nhưng không thay lưới ngang thành lưới dọc như hai hình khu vực.</p>

=== 346-353
<p>Mỗi dòng <code>itertuples()</code> thành một nhãn: KPI review ghi <code>n</code> là review; KPI còn lại ghi tên aspect và <code>n</code> là lượt nhắc. Với CSV thật: <code>complaint_bearing_review_rate</code> có 1.000 review; <code>top_complaint_aspect_share</code> có 176 lượt nhắc phàn nàn, nhóm <code>amenities</code>.</p>
<p>Nhánh <code>else</code> chỉ đúng vì <code>run</code> đã lọc đúng hai tên KPI. Gọi hàm trực tiếp với KPI lạ sẽ bị đặt nhãn như aspect; hàm vẽ không tự kiểm schema nghiệp vụ.</p>

=== 354-358
<p>Vẽ theo thứ tự dòng đầu vào trên thang 0–100, nhãn trục nhấn mạnh hai mẫu số khác nhau. <b>Đọc ảnh 08 thật:</b> cột dưới 14,00% tương ứng 140/1.000 review có phàn nàn; cột trên amenities 50,00% tương ứng 88/176 lượt nhắc phàn nàn.</p>
<p>Không cộng 14% với 50%, không nói một nửa số review phàn nàn về amenities. Một review có thể góp nhiều aspect, nên mẫu số lượt nhắc khác số review.</p>

=== 359-361
<p>Ghi tỷ lệ cạnh cột; <code>min(value + 1, 95)</code> chặn vị trí chữ ở 95 khi giá trị gần 100 để đỡ tràn mép phải. Tiêu đề giới hạn kết luận vào mẫu review đã phân tích; không mô tả nhãn LLM là nhãn tay.</p>

=== 362-370
<p>Dòng phụ đề xuất hiện nguyên văn trên ảnh đã commit: “Không phải nhãn tay; chưa đo accuracy/F1. Không suy rộng toàn thành phố.” Hai ý về nhãn và phạm vi vẫn đúng; riêng “chưa đo” đã lỗi thời.</p>
<p>Tự đọc <code>reports/evaluation/eval_summary.csv</code>: phương pháp <code>llm</code> có 100 gold, 100 được chấm, accuracy 0,97 và macro-F1 0,935774. Code vẫn in chữ cũ dù kết quả đánh giá đã có; đây là nhận xét <code>mid</code>, không phải lý do sửa số 14% hay 50%.</p>

=== 373-382
<p><code>run</code> là bộ điều phối công khai. Dấu <code>*</code> buộc đường dẫn tùy chọn phải truyền bằng tên, giảm nhầm thứ tự input/output. Trả list <code>Path</code> của các hình vừa tạo để pipeline biết kết quả.</p>
<p>Cam kết “kiểm trước, vẽ sau” bảo vệ khỏi lỗi dữ liệu được phát hiện ở phần trích xuất. Đây không phải giao dịch ghi file: nếu <code>savefig</code> hỏng giữa chừng do lỗi I/O thì những file trước đó không được hoàn tác.</p>

=== 383-387
<p>Ép ngày thành chuỗi, bắt đúng bốn giá trị khác nhau, rồi thử parse từng ngày trước cả đọc CSV. Test có cấu hình ba mốc, bốn mốc trùng và chuỗi ngày sai. Không có kiểm ngày tăng dần hay thao tác sắp ngày; “cuối” ở dưới là phần tử cuối danh sách.</p>

=== 389-391
<p>Đổi đường dẫn thành <code>Path</code>, đọc một lần, rồi trích đủ năm dãy trước khi tạo thư mục. <code>checked</code> giữ cặp đặc tả và list số tương ứng; thiếu một KPI hay một mốc đều chặn cả lượt vẽ tại đây.</p>

=== 392-394
<p>Lấy scope khu từ <code>config.kpi.area_col</code>, mặc định <code>neighbourhood_cleansed</code> nếu không có mục cấu hình. Cả hình 06 và 07 dùng <code>snapshots[-1]</code>. Với cấu hình hiện tại là 16/06/2026; đảo danh sách sẽ chọn 12/09/2025, dù tên file vẫn là <code>latest</code>.</p>

=== 395-399
<p>LLM chỉ lọc scope và hai tên KPI, <b>không lọc snapshot, không kiểm trùng, không bắt đủ cả hai KPI</b>. Các dòng hiện tại có snapshot <code>ALL</code>, khác bốn mốc, vì cùng mẫu review được gộp. Có dòng nào thì kiểm số và vẽ dòng đó; không có thì list rỗng và bỏ hình 08.</p>
<p>Chạy thử bằng bản sao CSV trong bộ nhớ, thêm hai dòng LLM có snapshot <code>1900-01-01</code>, thay các thao tác ghi bằng mock: <code>run</code> vẫn chuyển cả bốn dòng và giá trị 14 / 50 / 14 / 50 vào hàm vẽ. Vì vậy đầu vào gộp nhiều cohort cần được chọn trước khi gọi.</p>

=== 401-403
<p>Chỉ sau tất cả kiểm tra mới tạo thư mục, cho phép tạo cha và tái dùng thư mục có sẵn. Danh sách kết quả bắt đầu rỗng. Không dọn PNG của lượt chạy trước; danh sách trả về nói các hình vừa vẽ, không phản ánh mọi file đang nằm trong thư mục.</p>

=== 404-408
<p>Lặp năm cặp đã kiểm theo thứ tự <code>CHARTS</code>, ghép tên file, vẽ, in log và thêm đường dẫn. Log có sau lệnh vẽ; nếu vẽ ném lỗi thì không thêm đường dẫn đó. Năm lần gọi dùng cùng thứ tự snapshot nên dễ đối chiếu các ảnh.</p>

=== 410-413
<p>Vẽ hình 06 từ bảng khu đã chọn, truyền cả ngày và tên scope để in phụ đề. Thêm vào sau năm đường; không trích lại CSV ở giai đoạn ghi hình.</p>

=== 415-418
<p>Vẽ hình 07 theo <code>analysis_area</code>, log gọi đúng tên scope cố định. Đến đây nếu không có LLM thì đã đủ bảy file PNG; test kiểm tên file, kích thước hơn 1.000 byte và bảy log <code>[VIZ]</code>.</p>

=== 419-424
<p>Hình 08 là tùy chọn duy nhất: chỉ tạo khi bảng LLM không rỗng. Không có nhánh <code>else</code> xóa hình 08 cũ, nên khi xem một thư mục tái sử dụng cần đối chiếu list trả về. Test riêng thêm hai dòng LLM và kiểm file thứ tám có chữ ký PNG.</p>

=== 427-433
<p><code>main(argv)</code> tách giao diện dòng lệnh khỏi hàm nghiệp vụ; test truyền list đối số trực tiếp. Ba cờ chọn YAML, CSV KPI và thư mục xuất; <code>parse_args</code> xử lý trợ giúp và đối số sai. Mô tả “ít nhất 3 biểu đồ” là mức tối thiểu cũ; đường chạy hợp lệ hiện nay vẽ bảy hoặc tám hình.</p>

=== 434-435
<p>Đọc YAML qua <code>load_config</code> để dùng chung kiểm khóa và chuẩn hóa ngày, sau đó gọi đúng <code>run</code>. Chạy CLI cần YAML đủ khóa của hệ thống dù riêng viz chỉ dùng snapshot và scope khu; test CLI dựng config đủ rồi đổi cả đường dẫn vào/ra.</p>

=== 438-439
<p>Chỉ tự gọi <code>main()</code> khi chạy module như chương trình. Import <code>src.viz</code> chỉ định nghĩa hàm và hằng số, chưa đọc CSV hay tạo hình, nên pipeline và test có thể gọi từng hàm riêng.</p>

--- flow
## Cửa vào
fn 0 427 | main | CLI đọc config và đường dẫn
chips 1 | config:90 load_config
fn 0 373 | run | Kiểm tất cả trước khi vẽ
st 1 383 | Bốn mốc khác nhau | Parse ngày, giữ thứ tự config
fn 1 127 | load_kpi | File tồn tại, đủ sáu cột, có dòng
fn 1 160 | extract_series | overall/all, đủ mốc, không trùng
chips 2 | 140 _validate_numeric ; 58 CHARTS
fn 1 229 | extract_neighbourhoods | Top 10 n_obs rồi sắp value
fn 1 295 | extract_commercialized | analysis_area tại phần tử cuối
st 1 395 | LLM tùy chọn | scope llm, hai tên KPI, kiểm số
st 1 401 | Tạo thư mục | Bắt đầu giai đoạn ghi ảnh
## Kết xuất
fn 1 198 | draw_trend | Năm đường, thang phần trăm 0–100
chips 2 | 191 _figure ; 179 _style_axes
fn 1 251 | draw_neighbourhoods | Hình 06: tỷ lệ ngày trống theo khu
chips 2 | 245 _area_label
fn 1 312 | draw_commercialized_by_area | Hình 07: tám khu phân tích
fn 1 341 | draw_llm_kpis | Hình 08: hai mẫu số khác nhau
st 1 424 | Trả paths | Bảy hoặc tám đường dẫn đã ghi

--- review
mid | Hình 08 nói chưa đo F1 dù đã có | <a href="#viz-L362">Phụ đề</a> và ảnh thật vẫn ghi “chưa đo accuracy/F1”. Đọc lại <code>reports/evaluation/eval_summary.csv</code> cho LLM: 100/100 gold được chấm, accuracy 0,97, macro-F1 0,935774. Đây là chữ lỗi thời, không phải số KPI phàn nàn bị sai.
mid | overall không đồng nghĩa toàn thành phố | <a href="#viz-L160">Docstring extract_series</a> gọi là “toàn thành phố”, nhưng điều kiện chỉ chọn <code>overall/all</code>. CSV thực tế có 1.000 quan sát listing cho KPI lưu trú tối thiểu và occupancy; đó là mẫu được giao. Không suy rộng sang tập full chỉ dựa vào nhãn overall.
mid | latest là cuối config | <a href="#viz-L392">snapshots[-1]</a> không phải ngày lớn nhất. Chạy Python với config đảo thứ tự và CSV thật xác nhận dãy đường cũng đảo, phần tử cuối là 2025-09-12. Bốn ngày vẫn vượt kiểm tra khác nhau/hợp lệ; tiêu đề “snapshot cuối” cần đọc theo thứ tự cấu hình.
mid | LLM nhận cả dòng trùng và khác mốc | Chạy <code>run</code> với CSV thật cộng hai bản sao dòng LLM đổi snapshot sang 1900-01-01, dùng mock để không ghi file: hàm vẽ nhận đủ bốn dòng 14/50/14/50. <a href="#viz-L395">Bộ lọc</a> không bảo đảm đúng một cặp KPI hay một cohort, dù CSV hiện tại chỉ có hai dòng ALL hợp lệ.
ok | Kiểm trước giai đoạn ghi | Đã chạy <code>python -B -m pytest -q -p no:cacheprovider tests/test_viz.py</code>: 34 pass. Test thiếu dữ liệu khu xác nhận chưa tạo thư mục ảnh; test kiểm số bắt NaN, inf, mẫu số 0 và tỷ lệ ngoài 0–100. Các test PNG dùng fixture riêng, không lấy số fixture làm số báo cáo.

--- qa
? Vì sao hình đường không phóng đại biến động dù các giá trị khá gần nhau?
<p><a href="#viz-L210">Trục y</a> của mọi ChartSpec hiện tại cố định 0–100%. Ảnh 01 chỉ dao động 49,65–52,18%, nên đường gần ngang. Nhãn trên điểm cho hai số lẻ; không cần cắt trục để thấy chênh lệch. Trục x là bốn vị trí cách đều, không phải số ngày thực.</p>
? Hình 06 chọn mười khu trống nhiều nhất phải không?
<p>Không. <a href="#viz-L240">nlargest</a> chọn mười khu có <code>n_obs</code> lớn nhất rồi mới sắp tỷ lệ. Ảnh thật đặt Pittwater 68,23% trên cùng và Auburn 35,35% dưới cùng trong tập được chọn. Sydney có 274 listing ước tính nhưng tỷ lệ 47,37%, nên không đứng đầu theo độ dài cột.</p>
? n trong hình 06 và hình 04 có cùng nghĩa không?
<p>Không. Hình 06 tính <a href="#viz-L245">round(n_obs/365)</a>, là số listing ước tính từ ngày lịch hợp lệ. Hình 04 là tỷ lệ trên host đã gom trùng ở KPI: CSV mốc cuối có 738 host, trong đó 384 host có hơn một listing, được 52,03%.</p>
? Hai cột 14% và 50% trên hình 08 có thể cộng hoặc so trực tiếp không?
<p>Không vì <a href="#viz-L346">mẫu số khác nhau</a>: từ CSV, 14% = 140/1.000 review có phàn nàn; 50% = 88/176 lượt nhắc phàn nàn thuộc amenities. Lượt nhắc không phải review. Đây là mẫu LLM, không tự đại diện cho mọi review ở Sydney.</p>
? Nếu thiếu KPI hoặc sai số thì có vẽ một phần không?
<p><a href="#viz-L389">run</a> trích và kiểm cả năm đường, hai bảng khu và LLM trước khi tạo thư mục. Thiếu mốc, trùng mốc được chọn, NaN, vô cực, mẫu số không dương hay tỷ lệ ngoài miền đều bị chặn. Cơ chế này bảo vệ lỗi dữ liệu, không hoàn tác file nếu lỗi ghi ảnh xảy ra giữa chừng.</p>
? Chú thích chưa đo accuracy/F1 trên ảnh 08 còn đúng không?
<p>Không. Chữ ở <a href="#viz-L362">draw_llm_kpis</a> vẫn cũ, nhưng <code>reports/evaluation/eval_summary.csv</code> đã có accuracy LLM 0,97 và macro-F1 0,935774 trên 100 gold. Cần tách chất lượng dự đoán được đánh giá với KPI tỷ lệ phàn nàn trong mẫu.</p>
? Khi nào run trả bảy hình, khi nào trả tám hình?
<p>Đầu vào thường hợp lệ luôn cho bảy hình. Có ít nhất một dòng <code>scope='llm'</code> thuộc hai tên KPI ở <a href="#viz-L395">bộ lọc LLM</a> và số hợp lệ thì thêm hình 08. Không có dòng LLM thì bỏ vẽ hình 08, nhưng không xóa PNG cũ trong thư mục xuất.</p>
