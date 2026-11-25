--- meta
title: sydney.yaml
lead: Toàn bộ tham số của pipeline cho Sydney: thành phố, 4 mốc, ngưỡng QA/KPI, mô hình LLM, và phần mở rộng của nhóm (nhãn tay, đánh giá, 7 nhóm căn). Đây là nguồn sự thật duy nhất về ngưỡng — code không hard-code các số này, chỉ hard-code giá trị mặc định khi khoá vắng. Mỗi khoá dưới đây ghi rõ nó được đọc ở dòng nào.

--- blocks
=== 1-3
<p>Ba dòng đầu là hướng dẫn, không phải dữ liệu. Lệnh chạy ở dòng 1 là đường vào duy nhất: <a href="#run_pipeline-L45">run_pipeline.parse_args</a> bắt buộc <code>--config</code>.</p>
<p>Dòng 3 liệt kê 6 khoá cần sửa khi đổi thành phố. Danh sách này <b>chưa đủ</b>: <code>data_root</code> phải đổi theo (kiểm bởi test hợp đồng), và nếu mốc khác mốc được giao thì <code>qa.expected</code> phải sửa hoặc bỏ, xem <a href="#config-L70">config.py dòng 70</a>.</p>

=== 5
<p><code>city</code> là khoá <b>bắt buộc</b> (<a href="#config-L28">REQUIRED_KEYS</a>), được kiểm là chuỗi ở <a href="#config-L51">config.py dòng 51</a>. Nó là tên thư mục ở ba nơi: <a href="#download-L70">download.py dòng 70</a> (<code>data/raw|processed/&lt;city&gt;</code>), <a href="#kpi-L908">kpi.py dòng 908</a>, và <a href="#seg_report-L116">report.py dòng 116</a>. Còn in ra ở <a href="#run_pipeline-L124">run_pipeline dòng 124</a>.</p>
<p>Test hợp đồng đòi <code>city</code> viết thường, chỉ chữ/số/gạch nối, và <b>trùng tên file</b> (<code>sydney.yaml</code> → <code>sydney</code>). Đổi tên file mà quên đổi <code>city</code> là test đỏ.</p>

=== 6
<p><code>data_root</code> <b>chỉ</b> dùng để ghép URL tải: <a href="#download-L75">download.py dòng 75</a>, dạng <code>https://data.insideairbnb.com/&lt;data_root&gt;/&lt;mốc&gt;/data/&lt;file&gt;</code>. Nó không phải đường dẫn trên đĩa — đường dẫn đĩa dùng <code>city</code>.</p>
<p>Vì vậy <code>city</code> không xuất hiện trong URL; phần <code>sydney</code> ở cuối <code>data_root</code> mới là thành phố. Test hợp đồng bắt <code>data_root</code> có đúng 3 đoạn, viết thường, đoạn cuối bằng <code>city</code>.</p>

=== 7
<p><code>currency</code> chỉ có một tác dụng: quyết định <b>tên khoá ngưỡng giá</b>. <a href="#config-L57">config.py dòng 57</a> gọi <code>_price_cap</code>, hàm này thử <code>price_max_aud</code> rồi mới tới <code>price_max</code> (<a href="#config-L38">dòng 38</a>).</p>
<p>Chú thích "đơn vị tiền của cột price" hơi rộng: code không đổi đơn vị, không nhân tỷ giá, không định dạng tiền. Đổi <code>currency</code> mà quên đổi tên khoá giá thì <a href="#config-L41">dòng 41</a> ném <code>KeyError</code> ngay khi đọc config.</p>

=== 8
<p>Bốn mốc, tăng dần. PyYAML đọc <code>2025-09-12</code> thành <code>datetime.date</code>; <a href="#config-L56">config.py dòng 56</a> đổi hết về <code>"YYYY-MM-DD"</code>. Thứ tự quan trọng vì nhiều chỗ dùng "mốc cuối": <a href="#seg_init-L39">segments</a>, <a href="#llm_segments-L119">llm_segments dòng 119</a>, <a href="#kpi-L985">kpi</a>.</p>
<p>Phải đúng <b>4 mốc khác nhau</b>: <a href="#viz-L383">viz.run</a> kiểm <code>len(snapshots) != 4</code> thì <code>ValueError</code>, và test hợp đồng cũng bắt 4 mốc tăng dần. Đổi số mốc là phải sửa <code>viz.py</code>, không chỉ yaml.</p>

=== 10
<p>Mở mục <code>qa</code>. Đây là dict bắt buộc (nằm trong <code>REQUIRED_KEYS</code>) và phải chứa <code>min_nights_cap</code>, nếu không <a href="#config-L53">config.py dòng 53</a> dừng.</p>

=== 11
<p><code>price_max_aud: 10000</code> là ngưỡng giá/đêm. Đọc ở <a href="#config-L38">config.py dòng 38</a>, chép sang tên chung <code>qa.price_max</code>, dùng ở <a href="#qa_rules-L177">qa_rules dòng 177</a>.</p>
<p>Hệ quả đã kiểm trong <code>reports/qa_report.csv</code>: mốc 16/06/2026 có 22 dòng <code>price_unusable</code>, chi tiết <code>price_missing:20; price_above_cap:2</code> — tức chỉ 2 căn vượt 10.000, 20 căn còn lại thiếu giá. Mốc 21/03/2026 có 3 dòng.</p>
<p>Chú thích dòng này nói "lớn hơn thì gắn cờ price_unusable" là <b>chưa đủ</b>: cờ đó gộp 4 luật — thiếu giá, sai kiểu, ≤ 0, hoặc &gt; ngưỡng (<a href="#qa_rules-L353">qa_rules dòng 353–358</a>).</p>

=== 12
<p><code>min_nights_cap: 365</code> đọc ở <a href="#qa_rules-L193">qa_rules dòng 193</a>: <code>minimum_nights &gt; 365</code> thì vào cờ <code>contract_violation</code>. Cũng là khoá bắt buộc phải có trong <code>qa</code> (<a href="#config-L53">config.py dòng 53</a>).</p>
<p>Trong mẫu 1.000 căn của nhóm, <code>contract_violation</code> = 0 ở cả 4 mốc (<code>qa_report.csv</code>), nên ngưỡng này không chạm dòng nào. Nhưng toàn thành phố có <code>minimum_nights</code> tới 500 (cột <code>max_minimum_nights</code> trong <code>segments_gap_audit_full.csv</code>, mốc 12/2025 và 06/2026) — nên đừng nói "dữ liệu không có căn &gt; 365", chỉ đúng với mẫu.</p>

=== 13
<p><code>dedupe_keys: [id, last_scraped]</code> là bộ khoá xác định "cùng một bản ghi". Đọc ở hai luật: trùng trong một mốc (<a href="#qa_rules-L198">qa_rules dòng 198</a>, <code>keep=False</code> đánh dấu mọi bản trùng) và trùng giữa các mốc (<a href="#qa_rules-L307">dòng 307</a>).</p>
<p>Chú thích chỉ nói trùng trong file; thực tế luật thứ hai mới là chỗ quan trọng: cùng <code>id</code> <b>và</b> cùng <code>last_scraped</code> ở hai mốc nghĩa là bản cũ bị chép sang mốc sau. Cùng <code>id</code> khác ngày cào là bình thường (chỉ đếm, không gắn cờ — <a href="#qa_rules-L313">dòng 313</a>).</p>

=== 14
<p><code>outlier_iqr_k: 3.0</code> là hệ số k của luật ngoại lệ IQR, đọc ở <a href="#qa_rules-L187">qa_rules dòng 187</a>. Ngưỡng tính trên <b>từng mốc</b>: <code>[Q1 − k·IQR, Q3 + k·IQR]</code>, với <code>IQR = Q3 − Q1</code> (<a href="#qa_rules-L186">dòng 186</a>).</p>
<p>k = 3 rộng hơn mặc định 1,5 của Tukey nên chỉ bắt giá rất lạ; hệ quả: 51 dòng <code>price_outlier</code> ở 21/03/2026 và 52 ở 16/06/2026. Cờ này là <b>warning</b>, không phải error — bị loại ở bước "bỏ thêm cảnh báo", không loại ở bước "bỏ lỗi".</p>

=== 15
<p><code>bool_columns</code> liệt kê các cột chỉ được chứa giá trị đúng/sai. Đọc ở <a href="#qa_rules-L215">qa_rules dòng 215</a>; giá trị hợp lệ là <code>t/f/true/false/1/0</code>, ngoài ra thì bật <code>bool_category_drift</code>.</p>
<p>Ba cột này là kiểu <code>t/f</code> của Inside Airbnb. Cờ là mục con của <code>contract_violation</code>, hiện 0 dòng ở cả 4 mốc.</p>

=== 16
<p><code>calendar_days: 365</code> được đọc ở <b>hai</b> nơi: <a href="#download-L514">download.py dòng 514</a> (kỳ vọng số dòng lịch = số căn × 365) và <a href="#qa_rules-L279">qa_rules dòng 279</a> (mỗi listing phải có đúng 365 ngày, thiếu thì <code>calendar_incomplete</code>).</p>
<p>Với 1.000 căn, bước 1 kỳ vọng 365.000 dòng lịch — trùng <code>n_obs</code> = 365.000 của <code>availability_rate</code> trong <code>kpi_metrics.csv</code>. Đổi số này phải đổi cả dữ liệu tải về, nên thực tế chỉ dùng 365.</p>

=== 17
<p><code>review_score_range: [0, 5]</code> đọc ở <a href="#qa_rules-L229">qa_rules dòng 229</a>; mọi cột bắt đầu bằng <code>review_scores_</code> bị kiểm nằm trong khoảng. Cờ là mục con của <code>contract_violation</code>.</p>
<p>Test hợp đồng bắt danh sách đúng 2 phần tử và <code>lo &lt; hi</code>.</p>

=== 18-20
<p><code>bbox</code> là khung toạ độ Sydney. Đọc ở <a href="#qa_rules-L239">qa_rules dòng 239</a>: không có <code>bbox</code> thì <b>bỏ qua</b> kiểm tra (<a href="#qa_rules-L240">dòng 240–241</a>); có thì lấy <code>lat</code> và <code>lon</code> ở <a href="#qa_rules-L243">dòng 243</a> và gắn <code>coord_out_of_bbox</code>.</p>
<p>Hai dòng 19–20 là <code>[nam, bắc]</code> và <code>[tây, đông]</code> — code so <code>lat &lt; lat_lo</code> hoặc <code>&gt; lat_hi</code>, nên đảo thứ tự là mọi căn thành ngoài khung. Test hợp đồng kiểm <code>lo &lt; hi</code> và trong giới hạn ±90/±180.</p>

=== 21
<p><code>report_path</code> đọc ở <a href="#qa-L137">qa.py dòng 137</a> và ghi ở <a href="#qa-L155">dòng 155</a>. <code>run_pipeline</code> chỉ đọc lại để in (<a href="#run_pipeline-L145">run_pipeline dòng 145</a>).</p>
<p>Đây là chỗ dễ hiểu nhầm: nếu QA dừng giữa vòng lặp (vỡ ràng buộc), <code>write_report</code> không chạy và file cũ vẫn nằm nguyên — nhìn đường dẫn không có nghĩa là báo cáo vừa được cập nhật.</p>

=== 22
<p>Mở mục <code>expected</code>: số lượng đề cam kết. Cả mục là <b>tuỳ chọn</b>, nhưng nếu có thì bị chặn bởi <code>expected_applies</code> (<a href="#config-L70">config.py dòng 70–82</a>) ở hai cửa: <a href="#run_pipeline-L125">run_pipeline dòng 125</a> và <a href="#download-L513">download.py dòng 513</a>.</p>
<p>Bị bỏ (do đổi mốc hoặc mẫu theo seed) thì <b>toàn bộ</b> 8 khoá con dưới đây mất tác dụng, kể cả luật <code>room_type_unknown</code> trong QA (nó đọc <code>expected.room_type_counts</code>, <a href="#qa_rules-L206">qa_rules dòng 206</a>).</p>

=== 23
<p><code>expected.snapshots</code> là mốc mà các con số bên dưới đúng. <a href="#config-L59">config.py dòng 59–60</a> chuẩn hoá về chuỗi; <a href="#config-L81">dòng 81–82</a> so <b>cả thứ tự</b> với <code>config["snapshots"]</code>.</p>
<p>Vì sao phải so: các số như <code>no_reviews_per_snapshot: [50, 30, 25, 25]</code> gắn với <b>vị trí</b> mốc. Đổi mốc mà giữ danh sách là so sai và dừng pipeline oan. Test <code>test_cli_skips_assignment_counts_when_snapshots_are_changed</code> kiểm đúng nhánh này.</p>

=== 24
<p><code>n_listings: 1000</code> được kiểm hai lần: <a href="#qa_constraints-L27">qa_constraints dòng 27–29</a> ném <code>QAConstraintError</code> nếu lệch, và <a href="#download-L416">download.py dòng 416–418</a> chỉ cảnh báo. Cũng là cỡ mẫu dự phòng khi chọn mẫu theo seed (<a href="#download-L520">dòng 520</a>).</p>

=== 25
<p><code>n_reviews: 5000</code> là tổng review <b>hợp theo review_id</b> qua 4 mốc, không phải tổng số dòng. Kiểm ở <a href="#download-L439">download.py dòng 439–440</a> (một mốc không được vượt tổng) và <a href="#download-L453">dòng 453</a> (<code>check_review_total</code> so tổng cuối).</p>

=== 26-28
<p><code>room_type_counts</code> là số căn theo loại phòng. Đọc ở <a href="#qa_constraints-L34">qa_constraints dòng 34</a> (bắt buộc khớp), <a href="#download-L419">download.py dòng 419</a> (cảnh báo), và <a href="#qa_rules-L206">qa_rules dòng 206</a> — luật <code>room_type_unknown</code> coi mọi loại <b>không có trong dict</b> là bất thường.</p>
<p>Hai loại ở đây cộng lại đúng 1.000 (875 + 125), khớp <code>n_listings</code>. Nếu dữ liệu có "Shared room" hay "Hotel room", cờ <code>room_type_unknown</code> sẽ bật — hiện <code>contract_violation</code> = 0 nên mẫu chỉ có 2 loại này.</p>

=== 29
<p><code>no_reviews_per_snapshot: [50, 30, 25, 25]</code> là số căn 0 review ở <b>từng mốc theo thứ tự</b>. Đọc ở <a href="#qa_constraints-L57">qa_constraints dòng 57</a> với chỉ số <code>idx</code>, và <a href="#download-L427">download.py dòng 427</a> với <code>position - 1</code>.</p>
<p>Vì đọc theo chỉ số, danh sách phải đủ 4 phần tử; thiếu là <code>IndexError</code>. Ở mốc cuối, 25 căn 0 review đúng bằng <code>D_never</code> 25 + <code>N_new</code> 0 của mẫu — còn 1.528 là con số <code>D_never</code> toàn thành phố, không phải của mẫu.</p>

=== 30
<p><code>missing_price_last_snapshot: 20</code> chỉ kiểm ở mốc <b>cuối</b>: <a href="#qa_constraints-L76">qa_constraints dòng 76</a> bỏ qua mọi <code>idx</code> khác, <a href="#download-L431">download.py dòng 431</a> kiểm khi <code>position == len(no_reviews)</code>.</p>
<p>Đếm ở đây tính cả chuỗi rỗng (<a href="#qa_constraints-L81">dòng 81</a>), còn mục con <code>price_missing</code> trong báo cáo chỉ tính NaN (<a href="#qa_rules-L162">qa_rules dòng 162</a>). Với dữ liệu hiện tại hai số trùng nhau: 20.</p>

=== 31
<p><code>n_areas: 8</code> đọc ở <a href="#qa_constraints-L103">qa_constraints dòng 103</a> và <a href="#download-L445">download.py dòng 445</a>: số giá trị khác nhau của <code>analysis_area</code> phải đúng 8.</p>

=== 32
<p><code>area_size_range: [120, 130]</code> đọc ở <a href="#qa_constraints-L106">qa_constraints dòng 106–109</a>. 8 khu × 120–130 căn ≈ 1.000, khớp <code>n_listings</code>. Cùng với <code>n_areas</code>, hai số này khoá cấu trúc mẫu của đề.</p>

=== 34
<p>Mở mục <code>kpi</code> (bắt buộc ở mức trên cùng, nhưng hai khoá con đều có mặc định trong code).</p>

=== 35
<p><code>area_col: neighbourhood_cleansed</code> đọc ở <a href="#kpi-L692">kpi.py dòng 692</a> (mặc định cùng giá trị) và <a href="#viz-L392">viz.py dòng 392</a> để vẽ hình 06. Đây là cột gốc của Inside Airbnb, khác <code>analysis_area</code> (mã A01–A08 của đề).</p>
<p>Hai cột này dùng cho hai mục đích khác nhau: <code>neighbourhood_cleansed</code> cho bản đồ/khu hành chính, <code>analysis_area</code> cho 8 khu chuẩn hoá của đề.</p>

=== 36
<p><code>min_area_listings: 10</code> đọc ở <a href="#kpi-L693">kpi.py dòng 693</a> (mặc định 10) và áp ở <a href="#kpi-L517">dòng 517</a>: khu có ít hơn 10 căn bị bỏ khỏi <code>availability_rate</code> theo khu.</p>
<p>Đừng lẫn với <code>segments.area_min_listings: 300</code>: 10 là ngưỡng chống nhiễu của KPI, 300 là ngưỡng xếp hạng của hình 03.</p>

=== 38
<p>Mở mục <code>llm</code> (bắt buộc ở mức trên cùng).</p>

=== 39
<p><code>provider: gemini</code> — <b>không dòng code nào đọc khoá này</b>. Pipeline luôn gọi Gemini qua <code>client.models</code>/<code>interactions</code> (<a href="#llm-L265">llm.py dòng 265</a>), không có nhánh chọn nhà cung cấp.</p>
<p>Nó vẫn phải giữ vì <code>tests/test_config_contract.py:157</code> bắt <code>llm["provider"] == "gemini"</code>. Đây là khoá "chết nhưng được test canh" — câu trả lời chuẩn khi bị hỏi.</p>

=== 40
<p><code>model: gemini-3.1-flash-lite</code> đọc ở <a href="#llm-L357">llm.py dòng 357</a> (mặc định cùng giá trị), truyền vào lời gọi ở <a href="#llm-L400">dòng 400</a>.</p>
<p>Có một chỗ lệch: <code>scripts/label_additional_reviews.py</code> ghi đè thành <code>gemini-3.5-flash-lite</code> khi chạy cohort 3 và 4 (<a href="#label_additional-L211">dòng 211–212</a>, <a href="#label_additional-L225">dòng 225</a>). Vì vậy bảng cohort và bảng chính thức không cùng model — metadata ghi lại model từng cohort.</p>

=== 41
<p><code>sample_size: 1000</code> đọc ở <a href="#llm-L99">llm.py dòng 99</a>: ưu tiên đúng 1.000 review có <code>mau_llm == "x"</code>, thiếu thì lấy ngẫu nhiên theo <code>seed</code>.</p>
<p>Cache đã commit <code>data/processed/llm_cache_pydantic.jsonl</code> có đúng 1.000 dòng, khớp cỡ mẫu.</p>

=== 42
<p><code>aspects</code> là 6 khía cạnh LLM được phép gán. Đọc ở <a href="#llm-L356">llm.py dòng 356</a>, và <b>index trực tiếp</b> ở <a href="#llm_segments-L184">llm_segments dòng 184</a> và <a href="#viz_phantom-L830">viz_phantom dòng 830</a>.</p>
<p>Khác biệt quan trọng: <code>llm.py</code> và <code>evaluate.py</code> có mặc định (<a href="#evaluate-L356">evaluate dòng 356</a>) nên thiếu khoá vẫn chạy; <code>llm_segments</code>/<code>viz_phantom</code> dùng <code>config["llm"]["aspects"]</code> nên thiếu là <code>KeyError</code>. Danh sách này cũng là một phần schema cache (metadata cohort kiểm lại, <a href="#llm_segments-L242">llm_segments dòng 242</a>).</p>

=== 43
<p><code>cache</code> là file JSONL chứa nhãn đã gắn. Nơi đọc: <a href="#llm-L355">llm.py dòng 355</a>, <a href="#llm-L137">dòng 137</a> (<code>missing_from_cache</code>), <a href="#run_pipeline-L93">run_pipeline dòng 93</a>, <a href="#llm_segments-L144">llm_segments dòng 144</a>, <a href="#evaluate-L357">evaluate dòng 357</a>.</p>
<p>Đáng chú ý: <code>kpi.py</code> dùng mặc định <b>khác</b> — <code>data/processed/llm_cache.jsonl</code> (<a href="#kpi-L926">kpi.py dòng 926</a>), và repo có sẵn file đó với 1 dòng. Vì yaml luôn đặt khoá này nên không lộ; nếu xoá khoá, KPI sẽ đọc file 1 dòng trong khi LLM/evaluate đọc file 1.000 dòng.</p>

=== 44
<p><code>request_interval_seconds: 4.2</code> đọc ở <a href="#llm-L358">llm.py dòng 358</a>, dùng làm <code>time.sleep</code> giữa các lô (<a href="#llm-L405">dòng 405</a>); lô cuối không ngủ. Chỉ có tác dụng khi thật sự gọi API, không ảnh hưởng chạy bằng cache.</p>

=== 45-46
<p><code>comparison_cohorts</code> là các lần chạy LLM khác để so sánh (chỉ thăm dò). Đọc ở <a href="#llm_segments-L179">llm_segments dòng 179</a>; thiếu cả mục thì <code>run_cohorts</code> trả <code>None</code>. Nhưng nếu có mục mà thiếu <code>additional</code> hoặc <code>official</code> thì <a href="#llm_segments-L185">dòng 185</a>/<a href="#llm_segments-L217">217</a> ném <code>KeyError</code> — chỉ kiểm "mục rỗng", không kiểm từng khoá con.</p>

=== 47
<p><code>official.cache</code> đọc ở <a href="#llm_segments-L218">llm_segments dòng 218</a>, trùng file với <code>llm.cache</code> ở dòng 43. Nhờ vậy cohort "official" chính là bảng chính thức, không đọc thêm file mới.</p>

=== 48
<p><code>official.model</code> đọc ở <a href="#llm_segments-L232">llm_segments dòng 232</a> và ghi vào cột <code>model</code> của bảng cohort (<a href="#llm_segments-L251">dòng 251</a>). Đây là <b>nhãn mô tả</b>; code không so nó với <code>llm.model</code>.</p>

=== 49
<p><code>prompt_version: original_fingerprint_not_recorded</code> đọc ở <a href="#llm_segments-L233">llm_segments dòng 233</a>, ghi vào cột <code>prompt_version_or_sha256</code> (<a href="#llm_segments-L252">dòng 252</a>).</p>
<p>Giá trị này tự nói lên giới hạn: lần chạy chính thức không lưu dấu prompt, nên chỉ ghi nhận là "không có", không bịa một phiên bản. Đây là điểm trung thực đáng nêu.</p>

=== 50-52
<p><code>additional</code> là danh sách cohort bổ sung, mỗi cohort một cặp <code>cache</code> + <code>metadata</code>. Đọc ở <a href="#llm_segments-L185">llm_segments dòng 185</a> và <a href="#kpi-L944">kpi.py dòng 944</a>.</p>
<p>Cặp đầu (<code>v4</code>) và ba cặp sau được <code>kpi.py</code> đọc <b>chung</b>: nó gom mọi <code>item["cache"]</code> (<a href="#kpi-L950">dòng 950–956</a>) rồi nối lại để tính 2 KPI LLM mở rộng; thiếu bất kỳ file nào thì bỏ cả nhóm. Các cặp 53–58 cùng dạng, khác số hiệu.</p>

=== 53-54
<p>Cặp cohort <code>v4_2</code>. <code>cache</code> đọc ở <a href="#llm_segments-L219">llm_segments dòng 219</a>, <code>metadata</code> cũng ở đó; <code>metadata</code> được kiểm khớp thành phố/mốc/schema/aspects/cỡ cohort/mã băm SHA-256 trước khi dùng (<a href="#llm_segments-L237">dòng 237–246</a>).</p>

=== 55-56
<p>Cặp cohort <code>v4_3</code>. Cùng với <code>v4_4</code>, đây là cohort chạy bằng model khác (<code>gemini-3.5-flash-lite</code> theo <code>scripts/label_additional_reviews.py:211</code>), nên model phải đọc từ metadata chứ không lấy từ yaml — lý do cột <code>model</code> ghi theo từng cohort.</p>

=== 57-58
<p>Cặp cohort <code>v4_4</code>. Tổng cộng 4 cohort bổ sung; <code>llm_segments</code> đòi hợp các cache phủ <b>đủ</b> review của nhóm, thiếu là <code>ValueError</code> (<a href="#llm_segments-L255">dòng 255–256</a>).</p>

=== 60
<p><code>seed: 42</code> là khoá bắt buộc, dùng ở ba nơi: chọn mẫu theo seed (<a href="#download-L521">download.py dòng 521</a>), lấy mẫu review ngẫu nhiên (<a href="#llm-L100">llm.py dòng 100</a>, <code>random_state</code>), và bootstrap (<a href="#evaluate-L363">evaluate dòng 363</a>). Cả ba đều có mặc định 42 nếu thiếu, nhưng <code>config.py</code> vẫn bắt khoá.</p>

=== 62-63
<p>Đường kẻ và tiêu đề phần mở rộng của nhóm. Chú thích nói đúng hợp đồng: "mục nào thiếu thì pipeline bỏ qua bước tương ứng". Nhưng mức độ "bỏ qua" khác nhau: thiếu <code>segments</code> thì bỏ 4 bước (<a href="#run_pipeline-L151">run_pipeline dòng 151</a>), thiếu <code>labels</code> chỉ bỏ 4c (<a href="#run_pipeline-L108">dòng 108</a>).</p>

=== 65
<p><code>group_code</code> là mã nhóm trong workbook đề. Trong pipeline nó <b>chỉ</b> được đọc khi config có <code>ids.workbook</code> (<a href="#download-L268">download.py dòng 268–270</a>) — mà mục <code>ids</code> ở dòng 66–67 đang bị comment, nên pipeline hiện không dùng khoá này.</p>
<p>Nó vẫn có tác dụng ngoài pipeline: <code>scripts/check_assignment_data.py</code> đọc thẳng config và dùng <code>config["group_code"]</code> ở dòng 215 để đặt tên báo cáo <code>reports/check_&lt;mã&gt;.csv</code>.</p>

=== 66-67
<p>Hai dòng bị comment: nguồn ID thay thế. Khi bật, <a href="#download-L267">download.py dòng 267–268</a> đọc workbook <code>.xlsx</code> và lọc theo <code>group_code</code>; khi tắt, <a href="#download-L273">dòng 273–274</a> đọc <code>data/samples/listing_ids.csv</code> và <code>review_ids.csv</code>.</p>
<p>Đây là lý do <code>data/samples/</code> phải có trong repo: tắt <code>ids</code> thì hai file đó là nguồn ID duy nhất.</p>

=== 69
<p>Mở mục <code>labels</code>. Cả mục là tuỳ chọn; thiếu thì <code>run_evaluation_stage</code> dùng mặc định và bỏ qua nếu file không có.</p>

=== 70
<p><code>labels.path</code> đọc ở <a href="#run_pipeline-L106">run_pipeline dòng 106</a> (chỉ để kiểm tồn tại) và <a href="#evaluate-L355">evaluate dòng 355</a> (đọc nhãn). Mặc định ở cả hai là <code>data/samples/hand_labels.csv</code>.</p>
<p>File này có 100 review gán tay (85 positive / 15 mixed / 0 negative theo <code>reports/evaluation/eval_summary.csv</code>) — vì thiếu lớp negative nên chỉ là cảnh báo, không chặn chấm điểm.</p>

=== 72
<p>Mở mục <code>eval</code>. Tuỳ chọn; <code>evaluate.run</code> đọc bằng <code>config.get("eval", {})</code> nên thiếu cả mục vẫn chạy với mặc định.</p>

=== 73
<p><code>eval.output_dir</code> đọc ở <a href="#evaluate-L359">evaluate dòng 359</a>, mặc định <code>reports/evaluation</code>. Nơi ghi <code>eval_summary.csv</code>, <code>eval_perclass.csv</code>, bảng coverage khi chỉ chẩn đoán.</p>

=== 74
<p><code>eval.figure_dir</code> đọc ở <a href="#evaluate-L360">evaluate dòng 360</a>, mặc định <code>figures/evaluation</code>. Hình <code>eval_confusion_matrices.png</code> trong repo nằm đúng thư mục này và <b>không</b> thuộc 8 hình của <code>viz.run</code>.</p>

=== 75
<p><code>bootstrap_samples: 2000</code> đọc ở <a href="#evaluate-L361">evaluate dòng 361</a>, truyền vào <code>score_method</code> ở <a href="#evaluate-L385">dòng 385</a>. Dùng cho khoảng tin cậy bootstrap của accuracy/F1; tăng số này thì CI hẹp/ổn định hơn nhưng chậm hơn.</p>

=== 76
<p><code>min_gold_size: 100</code> đọc ở <a href="#evaluate-L362">evaluate dòng 362</a>, dùng ở <a href="#evaluate-L368">dòng 368</a>. Ít nhãn tay hơn 100 thì chỉ ghi chẩn đoán coverage, không công bố accuracy/F1.</p>
<p>Chú thích nói đúng trạng thái <code>final</code>: thiếu lớp sentiment chỉ là cảnh báo (<a href="#evaluate-L375">dòng 375–377</a>), vẫn chấm và công bố. File nhãn hiện có đúng 100 dòng nên chạm đúng ngưỡng, không vượt.</p>

=== 78
<p>Mở mục <code>segments</code> — bước 3 và là công tắc của 4b/5b/6b. Chỉ cần <b>có</b> khoá này là <a href="#run_pipeline-L151">run_pipeline dòng 151</a> chạy chia nhóm; không có thì bỏ. Các khoá con bên dưới hầu hết là <b>bắt buộc</b>: <code>cfg_get</code> ném <code>KeyError</code> nếu thiếu (<a href="#seg_rules-L38">rules.py dòng 38–40</a>).</p>

=== 79
<p><code>scope: full</code> chọn nguồn dữ liệu: <code>full</code> đọc <code>data/raw/&lt;city&gt;/&lt;mốc&gt;/listings.csv.gz</code> (20.573 căn toàn thành phố), <code>sample</code> đọc <code>data/processed</code> (1.000 căn của nhóm) — <a href="#seg_load-L40">load.py dòng 40–42</a>.</p>
<p>Đọc ở <a href="#seg_init-L39">segments/__init__.py dòng 39</a>. Có thể ghi đè bằng cờ <code>--segments-scope</code> (<a href="#run_pipeline-L55">run_pipeline dòng 55</a>). Số đã kiểm ở mốc 16/06/2026: full 20.573 căn (H_healthy 11.907), sample 1.000 (H_healthy 846).</p>

=== 80
<p><code>output_dir: data/processed</code> đọc ở <a href="#seg_report-L25">report.py dòng 25</a>, và ba chỗ khác: <a href="#llm_segments-L120">llm_segments dòng 120</a>, <a href="#llm_segments-L166">166</a>, <a href="#viz_phantom-L118">viz_phantom dòng 118</a>.</p>
<p>Chú thích/docstring trong <code>report.py</code> ghi "mặc định data/processed" nhưng code <b>không có</b> mặc định: <code>cfg_get</code> ném <code>KeyError</code> nếu thiếu khoá. Đây là chỗ tài liệu lệch code — tin code.</p>

=== 81
<p><code>blocked_max_availability: 0</code> là ngưỡng "kín lịch". Đọc ở <a href="#seg_rules-L67">rules.py dòng 67</a> (<code>availability_365 &lt;= 0</code> → <code>B_ghost</code>/<code>B_booked</code>) và <a href="#seg_transitions-L77">transitions.py dòng 77</a> (tỉ lệ kín lịch) và <a href="#seg_transitions-L106">dòng 106</a> (giải thích căn vắng ở mốc gap).</p>
<p>Số đã kiểm (<code>segments_gap_audit_full.csv</code>): tỉ lệ kín lịch 9,98% (09/2025), 7,73% (12/2025), <b>0,18%</b> (03/2026), 10,10% (06/2026). Con số 0,18% là dấu hiệu mốc 03/2026 bị lọc khác cách.</p>

=== 82
<p><code>recent_review_days: 365</code> đọc ở <a href="#seg_rules-L66">rules.py dòng 66</a>: "còn khách" nghĩa là <code>days_since_review &lt;= 365</code>. NaN so sánh ra <code>False</code> nên căn chưa có review tự rơi vào nhánh "không có review" (<a href="#seg_rules-L76">dòng 76–79</a>).</p>

=== 83
<p><code>low_open_days: 180</code> đọc ở <a href="#seg_rules-L68">rules.py dòng 68</a>: <code>L_low</code> cần <code>availability_365 &gt;= 180</code> (mở ít nhất nửa năm) và số review 12 tháng trong [1, 3].</p>

=== 84
<p><code>low_reviews_ltm_max: 3</code> đọc ở <a href="#seg_rules-L69">rules.py dòng 69</a>, dùng cho <code>L_low</code>. Cận dưới là 1, nên căn 0 review không vào <code>L_low</code> mà vào <code>D_never</code>/<code>N_new</code>.</p>

=== 85
<p><code>never_seen_days: 150</code> đọc ở <a href="#seg_init-L45">segments/__init__.py dòng 45</a>, truyền vào <code>seen_before_ids</code> để tìm căn đã xuất hiện ở mốc cách ≥ 150 ngày.</p>
<p>Hệ quả đã kiểm: hai mốc 2025 không có mốc cũ đủ 150 ngày, nên <code>D_never</code> = 0 ở cả hai (<code>segments_counts_full.csv</code>); mốc 03/2026 mới có 317 và 06/2026 có 1.528. Đây là lý do không được đọc <code>D_never</code> của các mốc đầu như "không có căn nào".</p>

=== 86
<p><code>short_stay_max_nights: 20</code> đọc ở <a href="#seg_load-L80">load.py dòng 80</a> (gán <code>stay_type = ngan_ngay</code>) và <a href="#kpi-L534">kpi.py dòng 534</a> (tách nhóm khi so giá hàng xóm). Cận trên của "ngắn ngày" là <b>≤ 20</b> đêm.</p>

=== 87
<p><code>long_stay_min_nights: 90</code> đọc ở <a href="#seg_load-L81">load.py dòng 81</a> và <a href="#kpi-L533">kpi.py dòng 533</a>. Khoảng 21–89 đêm rơi vào <code>trung_han</code> và <b>không</b> được dùng khi so giá ngắn/dài ngày — đó là cách tránh bẫy gộp nhóm.</p>

=== 88
<p><code>area_min_listings: 300</code> đọc ở <a href="#viz_phantom-L423">viz_phantom dòng 423</a> và <a href="#viz_phantom-L435">dòng 435</a>: chỉ xếp hạng khu có ít nhất 300 căn trong KPI căn ảo.</p>
<p>Ví dụ đã kiểm: mốc 16/06/2026, Mosman có 36,16% căn ảo nhưng chỉ <code>n_obs</code> = 271 (&lt; 300) nên <b>không</b> vào bảng xếp hạng; Pittwater 36,49% với 918 căn thì có. Đừng lẫn với <code>kpi.min_area_listings: 10</code>.</p>

=== 89
<p><code>gap_snapshot: 2026-03-21</code> là mốc bị lọc thiếu căn. Đọc ở <a href="#seg_init-L55">segments/__init__.py dòng 55</a> (dùng <code>.get</code>, nên <b>tuỳ chọn</b>), chuẩn hoá ngày ở <a href="#config-L63">config.py dòng 63–64</a>.</p>
<p>Hai chỗ đọc kiểu khác nhau: <a href="#viz_phantom-L393">viz_phantom dòng 393</a> dùng <code>.get</code>, còn <a href="#viz_phantom-L919">dòng 919</a> index thẳng <code>config["segments"]["gap_snapshot"]</code> — bỏ khoá này thì hình 07 không bị bỏ qua mà <b>lỗi <code>KeyError</code></b>.</p>
<p>Số đã kiểm (<code>segments_gap_summary_full.csv</code>): thiếu 4.645 căn, giải thích được 3.569 (76,84%), chưa rõ 1.076.</p>

=== 90
<p><code>gap_explain_min_nights: 7</code> đọc ở <a href="#seg_transitions-L105">transitions.py dòng 105</a>, chỉ dùng khi có <code>gap_snapshot</code>: căn vắng được coi là "giải thích được" nếu ở mốc cuối đòi <b>&gt; 7</b> đêm hoặc kín lịch. Chọn 7 vì mốc gap lọc theo <code>minimum_nights &gt; 7</code>.</p>

=== 91-93
<p>Hai cặp mốc cho ma trận đổi nhóm. Đọc ở <a href="#seg_init-L50">segments/__init__.py dòng 50–52</a> (chỉ nhận cặp có cả hai mốc trong <code>snapshots</code>) và <a href="#viz_phantom-L343">viz_phantom dòng 343</a>.</p>
<p><code>config.py</code> chuẩn hoá mọi cặp về chuỗi và luôn đặt danh sách (mặc định rỗng, <a href="#config-L65">dòng 65</a>). Cả hai cặp đều kết thúc ở 06/2026 nên mốc gap 03/2026 không tham gia — đúng ý "bỏ qua mốc gap". Số đã kiểm: <code>D_dormant → D_dormant</code> 65,44% (09/2025→06/2026) và 67,12% (12/2025→06/2026).</p>

--- flow
## Đọc và kiểm
st 0 5 | city | tên thư mục, kiểm là chuỗi
st 0 8 | snapshots | 4 mốc ISO, phải đúng 4 và tăng dần
st 0 11 | qa.price_max_aud | đổi sang qa.price_max
st 0 12 | qa.min_nights_cap | khoá bắt buộc trong qa
st 0 22 | qa.expected | tuỳ chọn, bị chặn theo mốc
## Bước 1 - tải
st 0 6 | data_root | chỉ ghép URL
st 0 13 | qa.dedupe_keys | dùng cho luật trùng
st 0 16 | qa.calendar_days | số dòng lịch mỗi căn
st 0 25 | qa.expected.n_reviews | tổng review hợp ID
## Bước 2 - QA
st 0 14 | qa.outlier_iqr_k | k = 3, off cảnh báo
st 0 15 | qa.bool_columns | chỉ t/f
st 0 17 | qa.review_score_range | 0..5
st 0 18 | qa.bbox | ngoài khung -> cờ
st 0 21 | qa.report_path | nơi ghi báo cáo
## Bước 3 - chia nhóm
st 0 79 | segments.scope | full = 20.573, sample = 1.000
st 0 81 | blocked_max_availability | kín lịch
st 0 82 | recent_review_days | còn khách
st 0 85 | never_seen_days | 150 ngày
st 0 89 | gap_snapshot | mốc 03/2026 bị lọc
st 0 90 | gap_explain_min_nights | giải thích căn vắng
st 0 92 | transitions | 2 cặp mốc cho ma trận
## Bước 4 - LLM
st 0 40 | llm.model | gemini-3.1-flash-lite
st 0 41 | llm.sample_size | 1.000 review mau_llm
st 0 42 | llm.aspects | 6 khía cạnh
st 0 43 | llm.cache | nhãn đã gắn
st 0 44 | request_interval_seconds | nghỉ 4,2 s giữa lô
## Bước 4b/4c - chấm
st 0 50 | additional cohorts | 4 cache bổ sung
st 0 76 | eval.min_gold_size | 100 nhãn tay
st 0 70 | labels.path | 100 review gán tay
chips 1 | config:90 load_config ; qa:137 qa.run ; seg_init:31 segments.run ; llm:344 llm.run ; evaluate:349 evaluate.run

--- review
mid | <code>llm.provider</code> là khoá chết | Không dòng code nào đọc <code>provider</code>; pipeline luôn gọi Gemini. Tuy vậy <code>tests/test_config_contract.py:157</code> bắt <code>provider == "gemini"</code>, nên không xoá được. Ai đọc yaml tưởng đổi provider là đổi được nhà cung cấp.
mid | <code>llm.cache</code>: hai mặc định khác nhau | <code>llm.py:355</code>, <code>evaluate.py:357</code>, <code>run_pipeline.py:93</code> mặc định <code>llm_cache_pydantic.jsonl</code> (1.000 dòng); <code>kpi.py:926</code> mặc định <code>llm_cache.jsonl</code> (file trong repo chỉ 1 dòng). Đặt khoá trong yaml nên chưa lộ; bỏ khoá là KPI LLM tính trên 1 review trong khi phần khác dùng 1.000.
mid | Bỏ <code>qa.expected</code> tắt luôn một luật QA | <code>run_pipeline.py:125</code> và <code>download.py:513</code> bỏ cả mục khi mốc khác đề, nhưng <code>qa_rules.py:206</code> dùng <code>expected.room_type_counts</code> cho luật <code>room_type_unknown</code>. Hệ quả: đổi mốc thì luật loại phòng lạ cũng ngừng chạy, không chỉ các số đếm.
mid | Chú thích <code>price_max_aud</code> hẹp hơn code | Dòng 11 nói chỉ "giá lớn hơn" mới bị <code>price_unusable</code>, nhưng cờ đó gộp 4 luật: thiếu, sai kiểu, ≤ 0, > ngưỡng (<code>qa_rules.py:353–358</code>). Báo cáo 16/06/2026: 22 dòng, trong đó 20 là thiếu giá, chỉ 2 vượt 10.000.
mid | <code>segments.gap_snapshot</code> không thật sự tuỳ chọn | Dòng 89 ghi "tuỳ chọn, bỏ dòng này nếu không có mốc", nhưng <code>viz_phantom.py:919</code> index thẳng <code>config["segments"]["gap_snapshot"]</code>. Bỏ khoá: <code>segments</code> chạy được nhưng bước 6b ném <code>KeyError</code> thay vì bỏ hình 07.
low | <code>segments.output_dir</code> không có mặc định | Docstring <code>report.py:24</code> nói "mặc định data/processed" nhưng <code>cfg_get</code> (<code>rules.py:35–40</code>) ném <code>KeyError</code> khi thiếu. Đổi tên khoá là phải sửa cả yaml và không có lưới an toàn.
ok | Khoá giá theo tiền tệ có kiểm | <code>_price_cap</code> thử <code>price_max_&lt;currency&gt;</code> rồi mới tới <code>price_max</code>, báo lỗi nêu đúng tên khoá cần thêm — đổi thành phố không bị lặng lẽ dùng ngưỡng Sydney.

--- qa
? Vì sao đổi thành phố chỉ cần sửa yaml?
<p>Vì mọi ngưỡng đều đọc từ config, không hard-code: giá ở <a href="#config-L38">config.py dòng 38</a>, QA ở <code>qa_rules</code>, chia nhóm ở <code>segments/rules.py</code>, KPI ở <code>kpi.py</code>. Nhưng phải sửa đủ: <code>city</code>, <code>data_root</code> (test hợp đồng bắt 3 đoạn, đoạn cuối = city), <code>currency</code> + tên khoá <code>price_max_&lt;tiền tệ&gt;</code>, <code>snapshots</code>, <code>bbox</code>, và <code>qa.expected</code> (bỏ hoặc sửa <code>expected.snapshots</code>).</p>
? <code>llm.provider: gemini</code> có tác dụng gì?
<p>Không có trong code — không dòng nào đọc. Pipeline luôn gọi Gemini (<a href="#llm-L265">llm.py dòng 265</a>). Khoá này chỉ tồn tại vì <code>tests/test_config_contract.py:157</code> bắt buộc. Đây là câu trả lời trung thực thay vì nói "đổi provider là đổi model".</p>
? Vì sao <code>outlier_iqr_k</code> là 3.0 mà không phải 1.5?
<p>1,5 là mức Tukey, bắt khoảng 0,7% với phân phối chuẩn; 3,0 chỉ bắt giá rất lạ (khoảng ±4,7σ), phù hợp dữ liệu giá thuê lệch mạnh. Hệ quả: chỉ 51–52 dòng bị cờ <code>price_outlier</code> ở hai mốc có giá, và đây là cờ warning chứ không phải error.</p>
? <code>segments.scope: full</code> khác <code>sample</code> thế nào?
<p><code>full</code> đọc <code>data/raw</code>: 20.573 căn toàn Sydney ở mốc cuối, H_healthy 11.907. <code>sample</code> đọc <code>data/processed</code>: 1.000 căn của nhóm, H_healthy 846. Vì bước 5b (KPI căn ảo) chỉ chạy với <code>full</code>, các hình 03/04/06 cần <code>kpi_phantom.csv</code> mới; chạy <code>sample</code> thì 6b đánh dấu <code>kpi_phantom</code> là cũ và bỏ các hình đó thay vì vẽ lại từ file cũ.</p>
? Bỏ <code>qa.expected</code> thì mất những kiểm tra nào?
<p>Mất 8 khoá con: số căn, số review, tỉ lệ loại phòng, số căn 0 review theo mốc, số căn thiếu giá mốc cuối, số khu, cỡ khu. Mất thêm luật <code>room_type_unknown</code> vì luật đó đọc <code>expected.room_type_counts</code> (<a href="#qa_rules-L206">qa_rules dòng 206</a>). Vì vậy bỏ <code>expected</code> không chỉ "tắt đối chiếu số lượng".</p>
? Vì sao <code>no_reviews_per_snapshot</code> phải đúng 4 phần tử?
<p>Vì <code>qa_constraints.py:57</code> lấy <code>expected["no_reviews_per_snapshot"][idx]</code> với <code>idx</code> chạy 0..3 theo 4 mốc. Danh sách ngắn hơn sẽ <code>IndexError</code> ở mốc sau; dài hơn thì phần thừa không dùng — đúng như test hợp đồng bắt 4 mốc.</p>
? Nếu thiếu một khoá con của <code>segments</code> thì sao?
<p><code>cfg_get</code> ném <code>KeyError</code> nêu đúng tên khoá (<a href="#seg_rules-L40">rules.py dòng 40</a>). Chỉ <code>gap_snapshot</code> và <code>transitions</code> là thật sự tuỳ chọn ở bước 3 — nhưng <code>gap_snapshot</code> lại bị hình 07 đòi, nên thực tế chỉ <code>transitions</code> bỏ được an toàn.</p>
