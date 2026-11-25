--- meta
title: run_pipeline.py
lead: Điểm vào duy nhất của pipeline. File chỉ điều phối: đọc config một lần, rồi gọi lần lượt 9 bước (tải, QA, chia nhóm, LLM, 4b, 4c, KPI, KPI căn ảo, hình, hình căn ảo) qua các hàm của <code>src/</code>. Không tự tính toán gì; mọi thứ nằm ở module riêng. Thứ tự có lý do: chia nhóm trước LLM vì 4b cần bảng nhóm; LLM trước KPI vì KPI đọc cache LLM.

--- blocks
=== 1-17
<p>Docstring đầu file là mục lục của cả pipeline, đúng thứ tự trong <code>main()</code>. Đọc kỹ ba chỗ dễ bị hỏi:</p>
<ul><li><b>5b</b> (<code>run_phantom</code>) chỉ chạy khi bước 3 làm ở scope <code>full</code>, vì nó đọc <code>data/raw</code> và <code>segments_full.csv</code>.</li>
<li><b>6b</b> vẽ "8 hình câu chuyện căn ảo"; thư mục <code>figures/phantom/</code> trong repo đúng 8 file PNG (01…08).</li>
<li>Đánh số <b>4b / 4c</b> ở đây khớp nhãn tab <code>buoc-4bc</code> của sổ tay, nhưng trong <code>main()</code> chúng chỉ là hai khối lệnh không có số riêng.</li></ul>
<p>Mỗi bước ghi sản phẩm riêng; file này không giữ trạng thái ngoài biến <code>config</code>, <code>seg</code>, <code>flagged</code>, <code>comparison</code>.</p>

=== 18-26
<p>Ba nguyên tắc vận hành, dùng để trả lời câu "sao không chạy được offline":</p>
<ul><li>Config nằm ở <code>configs/sydney.yaml</code>; xem <a href="#sydney_yaml-L5">sydney.yaml</a> và <a href="#config-L90">config.py</a>.</li>
<li>Thiếu <code>GEMINI_API_KEY</code> lẫn cache thì bước 4 báo bỏ qua, <b>không</b> sinh nhãn giả. Nhờ vậy KPI LLM không bao giờ tính trên dữ liệu bịa.</li>
<li>Mọi đường dẫn tương đối so với thư mục chạy lệnh, không so với vị trí file. Chạy từ thư mục khác sẽ ghi <code>data/</code> sai chỗ (các test CLI đều <code>chdir</code> vào thư mục tạm trước khi chạy).</li></ul>

=== 28-30
<p>Ba import chuẩn: <code>argparse</code> cho cờ dòng lệnh, <code>os</code> chỉ để đọc biến môi trường <code>GEMINI_API_KEY</code> (<a href="#run_pipeline-L96">dòng 96</a>), <code>Path</code> cho đường dẫn.</p>
<p>File này <b>không</b> có <code>from __future__ import annotations</code>, nên chú thích kiểu như <code>list[str] | None</code> (<a href="#run_pipeline-L45">dòng 45</a>) được Python tính ngay lúc định nghĩa hàm: cần Python ≥ 3.10. Đây là lý do <code>.python-version</code> ghim <code>3.10.22</code> và mypy khai <code>python_version = "3.10"</code> (<a href="#pyproject-L17">pyproject.toml dòng 17</a>).</p>

=== 32
<p><code>pandas</code> chỉ dùng cho chú thích kiểu <code>pd.DataFrame</code> trong <a href="#run_pipeline-L64">load_processed_tables</a> và để gọi <code>pd.read_csv</code> ở <a href="#run_pipeline-L86">dòng 86</a>.</p>

=== 34
<p>Một dòng import cả 9 module của các bước: <code>evaluate</code>, <code>kpi</code>, <code>llm</code>, <code>llm_segments</code>, <code>qa</code>, <code>segments</code>, <code>viz</code>, <code>viz_phantom</code>. Hệ quả: import <code>run_pipeline</code> là kéo theo matplotlib (qua <code>viz</code>) và mọi thư viện của các bước, kể cả khi định chạy <code>--help</code>.</p>
<p>Import kiểu này cũng là điểm để test thay hàm: <code>test_pipeline_cli.py</code> gán <code>run_pipeline.viz.run = …</code>, tức thay thuộc tính trên module đã import, không cần sửa <code>src/viz.py</code>.</p>

=== 35-37
<p>Ba hàm cấu hình lấy từ <code>src.config</code>: <code>load_config</code> (đọc + kiểm + chuẩn hoá), <code>expected_applies</code> (mốc còn đúng mốc được giao không), <code>without_expected</code> (bỏ đối chiếu số lượng của đề). Giải thích chi tiết ở <a href="#config-L70">config.py dòng 70–87</a>.</p>
<p><code>ID_DTYPES</code> để giữ <code>id</code>, <code>listing_id</code>, <code>host_id</code> là chuỗi; <code>is_seed_sample</code> đọc file mẫu để biết mẫu do seed hay do đề. <code>run</code> của <code>download</code> được đổi tên <code>run_download</code> cho khỏi lẫn với <code>run</code> của các module khác.</p>

=== 39-42
<p>Hai hằng số đường dẫn/tên bảng. <code>PROCESSED_ROOT</code> là <code>Path("data") / "processed"</code> — tương đối, ghép thêm <code>city</code> và mốc ở <a href="#run_pipeline-L70">dòng 70</a>. <code>TABLES</code> là tuple 3 tên bảng mỗi mốc phải có: <code>listings</code>, <code>calendar</code>, <code>reviews</code>.</p>

=== 45-46
<p><code>parse_args</code> nhận <code>argv</code> tuỳ chọn thay vì luôn đọc <code>sys.argv</code>. Nhờ tham số này, test gọi thẳng <code>parse_args(["--config", "config.yaml", "--skip-llm"])</code> mà không cần tiến trình con.</p>

=== 47
<p>Tạo parser với mô tả hiện trong <code>--help</code>: <code>"Run Airbnb Analysis Pipeline"</code> — test <code>test_cli_help_exits_zero</code> kiểm đúng chuỗi này.</p>

=== 48
<p><code>--config</code> là cờ <b>bắt buộc</b> (<code>required=True</code>). Thiếu nó, argparse in lỗi và thoát mã 2, không phải 1 — test <code>test_cli_requires_the_config_argument</code> kiểm <code>returncode == 2</code>.</p>

=== 49-53
<p><code>--skip-download</code> là cờ bật/tắt (<code>store_true</code>), mặc định <code>False</code>. Dùng khi <code>data/processed/</code> đã có sẵn, hoặc trong test/CI để không gọi mạng. Không có cờ này thì <a href="#run_pipeline-L136">dòng 136</a> gọi <code>run_download</code>.</p>

=== 54
<p><code>--skip-llm</code> chỉ tắt <b>bước 4</b> (gọi API/gắn nhãn). Nó <b>không</b> tắt 4b, 4c: hai bước đó vẫn chạy nếu cache và nhãn tay có sẵn trên đĩa. Đây là chỗ dễ trả lời sai khi bị hỏi "cờ này tắt hết LLM chưa".</p>

=== 55-60
<p><code>--segments-scope</code> chỉ nhận <code>full</code> hoặc <code>sample</code>, mặc định <code>None</code> = lấy <code>segments.scope</code> trong yaml (hiện là <code>full</code>). Truyền cờ thì ghi đè config cho riêng lần chạy; test <code>test_parse_args_exposes_segments_scope</code> kiểm cả hai trường hợp.</p>

=== 61
<p>Trả <code>argparse.Namespace</code> với 4 thuộc tính: <code>config</code>, <code>skip_download</code>, <code>skip_llm</code>, <code>segments_scope</code>.</p>

=== 64-69
<p>Docstring nói rõ vì sao QA không đọc thẳng <code>data/raw</code>: phải chạy trên đúng tập đã lọc theo danh sách ID chính thức của nhóm, tức đầu ra của bước 1. Đọc raw sẽ QA cả 20.573 căn toàn Sydney thay vì 1.000 căn của nhóm.</p>

=== 70
<p><code>root = data/processed/&lt;city&gt;</code>. Với config hiện tại là <code>data/processed/sydney</code>.</p>

=== 71
<p>Dict lồng hai tầng: <code>tables[mốc][tên_bảng] = DataFrame</code>. Đây đúng là dạng <code>qa.run()</code> nhận (<a href="#qa-L1">qa.py</a>).</p>

=== 73-74
<p>Lặp theo <code>config["snapshots"]</code>, ép <code>str()</code> lần nữa dù <code>load_config</code> đã chuẩn hoá. Rẻ và an toàn nếu ai gọi hàm này với dict thô đọc trực tiếp bằng <code>yaml.safe_load</code> (như test <code>test_load_processed_tables_reports_the_missing_path</code>).</p>

=== 75-76
<p>Thư mục của từng mốc và dict con rỗng để nhét 3 bảng vào.</p>

=== 78-79
<p>Lặp 3 tên bảng, ghép <code>&lt;mốc&gt;/&lt;tên&gt;.csv</code>.</p>

=== 80-85
<p>Không thấy file thì <b>dừng ngay</b> với <code>FileNotFoundError</code> nêu đúng đường dẫn, thay vì để QA chạy trên bảng rỗng rồi ghi báo cáo sai. Thông báo còn chỉ cách sửa: chạy lại không có <code>--skip-download</code>.</p>
<p>Hệ quả thực tế: <code>data/processed/sydney/&lt;mốc&gt;/</code> bị gitignore, nên clone repo rồi chạy <code>--skip-download</code> sẽ dừng ở đây. Test <code>test_cli_fails_with_the_missing_processed_path</code> xoá <code>reviews.csv</code> và kiểm <code>returncode != 0</code> cùng tên file trong stderr.</p>

=== 86
<p>Đọc CSV với <code>low_memory=False</code> (đọc trọn rồi mới suy kiểu, tránh cảnh báo kiểu lẫn lộn giữa các khối) và <code>dtype=ID_DTYPES</code> để <code>id</code>/<code>listing_id</code>/<code>host_id</code> là chuỗi. Nếu để pandas tự suy, ID 19 chữ số thành <code>float64</code> và mất chữ số cuối — đúng lỗi đã ghi ở <a href="#download-L55">download.py dòng 55</a>.</p>

=== 88
<p>Trả dict cho <code>qa.run</code>. Không cache lại; mỗi lần gọi đọc lại đĩa.</p>

=== 91-93
<p><code>run_llm_stage</code> tách riêng để test được mà không gọi API. Đường dẫn cache lấy từ <code>config["llm"]["cache"]</code>, thiếu thì dùng <code>llm.CACHE_PATH</code> = <code>data/processed/llm_cache_pydantic.jsonl</code> (đúng file đã commit).</p>

=== 94-95
<p><code>--skip-llm</code> in một dòng rồi thoát hàm. Không đụng cache, không gọi mạng.</p>

=== 96-98
<p>Nhánh khó nhất, đọc theo hai vế của <code>and</code>:</p>
<ul><li>Không có <code>GEMINI_API_KEY</code> (không gọi API được), <b>và</b></li>
<li>hoặc chưa có cache, hoặc <code>llm.missing_from_cache(config)</code> &gt; 0 (cache thiếu review của mẫu nhóm).</li></ul>
<p><code>missing_from_cache</code> đếm số review trong mẫu LLM chưa có nhãn trong cache. Nó là cách phát hiện cache của thành phố khác còn sót: đổi <code>city</code> trong yaml nhưng cache vẫn Sydney thì hàm trả về toàn bộ mẫu, và pipeline bỏ qua thay vì tính KPI trên cache sai. Test <code>test_llm_stage_skips_cache_of_another_group_without_key</code> giả lập <code>missing_from_cache = 1000</code> và kiểm <code>llm.run</code> không được gọi.</p>

=== 99-101
<p>Còn lại thì chạy thật. Hai trường hợp vào đây: có API key (gọi/gắn nhãn, dùng lại cache cho phần đã có), hoặc không có key nhưng cache đã phủ đủ mẫu (chỉ đọc cache).</p>

=== 104-107
<p><code>run_evaluation_stage</code> chỉ lo bước 4c. Hai đường dẫn lấy từ config với mặc định trùng mặc định của <code>evaluate.run</code>: <code>labels.path</code> và <code>llm.cache</code>.</p>

=== 108-109
<p>Không có file nhãn tay thì bỏ qua, in một dòng. Đây là trạng thái bình thường của repo sạch nếu chưa commit <code>data/samples/hand_labels.csv</code>; test E2E kiểm đúng dòng này.</p>

=== 110-114
<p>Có nhãn tay:</p>
<ul><li>Thiếu cache thì in cảnh báo "chỉ báo coverage" nhưng <b>vẫn</b> gọi <code>evaluate.run</code>. Hàm đó không lỗi: <code>diagnostic_reasons</code> thấy cache thiếu thì ghi bảng coverage và dừng (<a href="#evaluate-L368">evaluate.py dòng 368–373</a>).</li>
<li>Có cache thì chấm đầy đủ baseline + LLM trên nhãn tay, ghi <code>reports/evaluation/</code>.</li></ul>

=== 117-118
<p><code>main</code> không nhận tham số; đọc <code>sys.argv</code> qua <code>parse_args()</code> ở <a href="#run_pipeline-L119">dòng 119</a>. Docstring chỉ nói "theo thứ tự ghi ở đầu file" — đúng, danh sách bước chỉ tồn tại trong docstring, không có hằng số nào lặp lại thứ tự.</p>

=== 119
<p>Đọc cờ CLI một lần, dùng cho cả hàm.</p>

=== 121-122
<p>Đọc + chuẩn hoá config một lần duy nhất (xem <a href="#config-L90">config.py</a>). Từ đây mọi bước nhận cùng một dict; không module nào tự mở yaml, trừ khi chạy riêng bằng <code>python -m</code>.</p>

=== 124
<p>In tên thành phố qua <code>str.capitalize()</code>: viết hoa chữ đầu, <b>hạ</b> toàn bộ phần còn lại. Vì vậy <code>SYDNEY</code> → <code>Sydney</code> nhưng <code>new york</code> → <code>New york</code>. Test <code>test_main_capitalisation_is_python_str_capitalize</code> kiểm cả 4 trường hợp, kể cả <code>da-nang</code> → <code>Da-nang</code>.</p>

=== 125-129
<p>Chặn sớm việc đối chiếu số lượng của đề. Điều kiện: có <code>qa.expected</code> <b>và</b> <code>expected_applies</code> trả <code>False</code> (mốc trong config khác <code>qa.expected.snapshots</code>). Khi đó <code>without_expected</code> trả bản sao config không có khoá <code>expected</code>, và biến <code>config</code> được gán lại.</p>
<p>Vì sao phải làm trước bước 1: nếu để QA phát hiện, pipeline đã tải xong hàng trăm MB rồi mới dừng oan. Test <code>test_cli_skips_assignment_counts_when_snapshots_are_changed</code> đổi 4 mốc và kiểm pipeline vẫn thoát 0 với dòng thông báo này.</p>

=== 131-136
<p>Bước 1. <code>--skip-download</code> chỉ in dòng bỏ qua; ngược lại gọi <code>download.run(config)</code> — tải 4 file mỗi mốc (3 bảng + geojson) rồi lọc theo ID của nhóm. Xem <a href="#download-L1">download.py</a>.</p>
<p>Đường dẫn <code>data/raw</code>, <code>data/processed</code> đều tương đối, nên <code>main()</code> phải chạy từ gốc repo. Test <code>test_main_runs_download_with_the_loaded_config</code> thay <code>run_download</code> bằng hàm ghi lại config để kiểm <code>city</code> và <code>snapshots</code> được truyền đúng.</p>

=== 138-139
<p>In tiêu đề bước 2 trước khi chạy. Thứ tự in quan trọng: test E2E so từng dòng stdout, nên mọi dòng print ở file này là một phần "hợp đồng" với test.</p>

=== 140-143
<p>Chặn thứ hai, hẹp hơn: mẫu được chọn theo <b>seed</b> (bước 1 ghi <code>sample_source = "seed"</code>) thì các số 875/125, 50/30/25/25 của đề không còn nghĩa, nên bỏ <code>qa.expected</code> cho phần còn lại.</p>
<p><code>is_seed_sample</code> đọc file mẫu ở <code>data/processed/&lt;city&gt;/sample_listing_ids.csv</code>; file không tồn tại thì trả <code>False</code> (đang dùng ID chính thức). Kiểm cả <code>"expected" in config["qa"]</code> để không gọi <code>without_expected</code> vô ích.</p>

=== 144
<p><code>qa.run</code> nhận config và dict 3 bảng mỗi mốc, trả <code>flagged</code>: cùng dict nhưng mỗi DataFrame đã có thêm cột cờ (<code>qa_has_error</code>, <code>qa_has_error_excl_price</code>…). Đây là đầu vào của bước 5, nên KPI không phải đọc lại CSV.</p>
<p>Test <code>test_main_passes_qa_flagged_frames_to_kpi</code> thay <code>kpi.run</code> và kiểm <code>qa_has_error</code> có trong cả <code>listings</code> lẫn <code>calendar</code> của bảng truyền vào.</p>

=== 145
<p>In số mốc đã QA (4) và đường dẫn báo cáo. Đường dẫn lấy từ <code>config["qa"]["report_path"]</code> với mặc định <code>reports/qa_report.csv</code> — trùng mặc định trong <code>qa.write_report</code>. Với repo hiện tại, file có 60 dòng: 48 dòng <code>section=rule</code> + 12 dòng <code>section=kpi</code>, chia 14/14/16/16 theo 4 mốc.</p>

=== 147-150
<p>Ba dòng chú thích nói rõ hợp đồng của bước 3: <code>seg</code> giữ <code>scope</code> và danh sách file đã ghi; mục <code>segments</code> là tuỳ chọn nên thiếu thì bỏ qua bước 3, 4b, 5b, 6b. <code>seg = None</code> là cờ "chưa chia nhóm" dùng lại ở các bước sau.</p>

=== 151-154
<p><code>segments.run(config, scope=args.segments_scope)</code> trả dict 5 khoá: <code>scope</code>, <code>track</code>, <code>transitions</code>, <code>audit</code>, <code>paths</code>. Trong repo, <code>paths</code> có <b>6</b> file: <code>segments_counts_&lt;scope&gt;.csv</code>, <code>segments_transitions_…</code>, <code>segments_gap_audit_…</code>, <code>segments_gap_summary_…</code>, và 2 bảng lớn trong <code>data/processed/sydney/</code> (<code>segments_&lt;scope&gt;.csv</code>, <code>segments_track_&lt;scope&gt;.csv</code>).</p>
<p><code>seg["paths"][-1]</code> là bảng track, nằm trong <code>data/processed/sydney</code>, nên dòng in ra nói "vào data/processed/sydney" chứ không phải <code>data/processed</code>. Test E2E kiểm đúng chuỗi <code>"đã ghi 6 bảng phân nhóm vào data/processed/sydney"</code>.</p>

=== 155-156
<p>Config mẫu của đề không có mục <code>segments</code>: chỉ in một dòng rồi đi tiếp, không dừng. Test <code>test_cli_skips_segments_when_config_has_no_segments_section</code> xoá mục này và kiểm cả thông báo bước 3 lẫn bước 6b.</p>

=== 158-160
<p>Bước 4. Đặt ở đây, <b>sau</b> bước 3 và <b>trước</b> bước 5, vì hai lý do ngược chiều nhau:</p>
<ul><li>4b cần <code>seg["scope"]</code> và bảng nhóm để nối review với nhóm căn;</li>
<li>KPI (bước 5) đọc cache LLM để tính 2 KPI scope <code>llm</code>. Chạy KPI trước thì <code>kpi_metrics.csv</code> thiếu 2 dòng đó và hình 08 không được vẽ.</li></ul>

=== 161-162
<p>Bước 4b. Chỉ gọi khi đã chia nhóm (<code>seg</code> khác <code>None</code>); nếu không có mục <code>segments</code> trong config thì <code>comparison = None</code>. <code>llm_segments.run</code> trả <code>None</code> khi cache LLM không tồn tại, ngược lại trả đường dẫn bảng so sánh.</p>

=== 163-167
<p>Có bảng so sánh thì in đường dẫn, rồi gọi <code>run_cohorts</code> để ghi 2 bảng mở rộng (từng cohort và bảng gộp). <code>if cohort_paths:</code> để chịu được việc hàm trả <code>None</code> khi thiếu cache của các cohort. Chú thích "chỉ mang tính thăm dò" là quan trọng khi bị hỏi: các bảng này không dùng để công bố KPI.</p>

=== 168-171
<p>Không có cache LLM nhưng <b>đã có</b> bảng so sánh từ lần chạy trước: in cảnh báo bảng cũ không được cập nhật. Kiểm tra sự tồn tại của đúng tên file mà 4b ghi (<code>llm_segment_aspects.csv</code>) trong <code>segments.output_dir/&lt;city&gt;</code>.</p>
<p>Điểm cần nhớ: nhánh này <b>không</b> xoá file cũ. Việc không vẽ hình từ file cũ do bước 6b lo, qua tham số <code>exclude</code> (<a href="#run_pipeline-L199">dòng 199</a>).</p>

=== 173-174
<p>Bước 4c: chấm LLM và baseline trên nhãn tay. Tách thành hàm để test gọi riêng được và để logic "thiếu nhãn tay thì bỏ qua" nằm một chỗ.</p>

=== 176-180
<p>Bước 5. Truyền thẳng <code>flagged</code> từ bước 2. Chú thích WHY nói rõ KPI phi giá phải bỏ dòng lỗi lõi (<code>qa_has_error_excl_price</code>) nhưng <b>không</b> loại oan dòng chỉ vướng cờ giá — nếu loại cả cờ giá, tỉ lệ như <code>long_stay_restriction_rate</code> sẽ tính trên mẫu bị cắt không đều.</p>
<p>Test <code>test_cli_kpi_uses_only_rows_that_passed_qa</code> đặt <code>min_nights_cap = 2</code> để một căn bị gắn cờ, rồi kiểm <code>n_obs = 1</code> và giá trị 0,0 — chứng minh dòng bị cờ không tham gia KPI.</p>

=== 181-186
<p>Bước 5b, chỉ khi <code>seg["scope"] == "full"</code>:</p>
<ul><li>Lý do: <code>run_phantom</code> đọc <code>segments_full.csv</code> và <code>data/raw</code> (cần <code>availability_365</code>, <code>minimum_nights</code> gốc của toàn thành phố). Với scope <code>sample</code> không có dữ liệu raw của 20.573 căn, nên bỏ qua kèm thông báo thay vì lỗi.</li>
<li>Đặt sau bước 5 vì <code>run_phantom</code> tự đọc lại <code>data/raw</code> + <code>segments_full.csv</code>, không dùng kết quả bước 5; hai hàm ghi hai file khác nhau (<code>kpi_metrics.csv</code> và <code>kpi_phantom.csv</code>). Thứ tự này cũng giữ transcript luôn là "5" rồi "5b".</li></ul>
<p>Trong repo, <code>kpi_phantom.csv</code> có 216 dòng (6 cột: <code>snapshot</code>, <code>scope</code>, <code>group_name</code>, <code>kpi_name</code>, <code>value</code>, <code>n_obs</code>).</p>

=== 188-190
<p>Bước 6. <code>viz.run</code> trả danh sách file đã ghi. Trong repo, lần chạy đầy đủ ghi <b>8</b> hình vào <code>figures/</code>: 01–05 (xu hướng theo mốc), 06 (availability theo khu), 07 (commercialized theo <code>analysis_area</code>), 08 (KPI LLM — chỉ vẽ khi <code>kpi_metrics.csv</code> có dòng <code>scope=llm</code>). Hình <code>figures/evaluation/eval_confusion_matrices.png</code> do bước 4c ghi, không nằm trong danh sách này.</p>
<p>Bước này có thể ném lỗi nếu config không đúng 4 mốc khác nhau (<code>viz.run</code> kiểm trước khi vẽ), nên đổi số mốc là phải sửa cả <code>viz</code>.</p>

=== 191-192
<p><code>paths[0].parent</code> để in đúng thư mục, không hard-code "figures". Khi <code>paths</code> rỗng (không vẽ được hình nào) thì dùng chuỗi <code>"figures"</code> — chỉ để in, không dùng làm đường dẫn, nên kiểu <code>str</code> ở nhánh này không gây lỗi.</p>

=== 194-198
<p>Bước 6b. Chú thích nói rõ hợp đồng: đọc CSV của bước 3, 4b, 5b; thiếu file nào thì <code>viz_phantom</code> bỏ hình đó. Vì vậy bước này cần <code>seg</code>, không cần scope full.</p>
<p><code>stale</code> là danh sách khoá đầu vào <b>không được làm mới</b> trong lần chạy này. Mục đích: trên đĩa có thể còn CSV của lần chạy cũ; nếu vẽ từ chúng, hình sẽ mô tả dữ liệu không còn đúng với lần chạy hiện tại. Đây chính là câu trả lời cho "sao không vẽ từ file cũ còn sót".</p>

=== 199-200
<p>Không có bảng so sánh LLM (<code>comparison is None</code>) → đánh dấu <code>llm_aspects</code> là cũ. Hệ quả: hình <code>08_llm_complaints_by_segment.png</code> không được vẽ dù file CSV cũ vẫn nằm trên đĩa. Test <code>test_main_warns_when_old_comparison_cannot_be_updated</code> tạo sẵn CSV cũ và kiểm đúng dòng "Bỏ qua 08_llm_complaints_by_segment.png: … chưa được cập nhật".</p>

=== 201-202
<p>Scope không phải <code>full</code> → bước 5b vừa bị bỏ, nên <code>kpi_phantom.csv</code> trên đĩa là của lần chạy khác; đánh dấu để không vẽ các hình dùng nó.</p>

=== 203-205
<p>Gọi <code>viz_phantom.run(config, scope=seg["scope"], exclude=tuple(stale))</code>. Test <code>test_main_full_scope_runs_phantom_kpi_and_passes_fresh_tables_to_viz</code> kiểm <code>exclude</code> là tuple rỗng khi scope full và có bảng LLM. Dòng in dùng <code>viz_phantom.DEFAULT_OUTPUT_DIR</code> (<code>figures/phantom</code>), không dùng đường dẫn trả về — nếu ai đổi thư mục đầu ra của <code>viz_phantom</code>, dòng in vẫn đúng vì cùng hằng số.</p>

=== 206-207
<p>Không có mục <code>segments</code> → bỏ cả bước 6b, in một dòng. Không có ngoại lệ nào bị nuốt: đây là nhánh chủ động.</p>

=== 209
<p>Dòng cuối cùng của stdout khi thành công. Test E2E so <code>lines[-1] == DONE</code> và tổng số dòng là 38 cho project tối thiểu.</p>

=== 212-213
<p>Chỉ chạy khi gọi trực tiếp <code>python run_pipeline.py</code>. Khi bị import (test gọi <code>run_pipeline.main()</code> với <code>sys.argv</code> đã gán), khối này không chạy — nhờ vậy test điều khiển được tham số.</p>

--- flow
## Khởi động
fn 0 45 | parse_args | 4 cờ: config, skip-download, skip-llm, segments-scope
fn 0 64 | load_processed_tables | 3 bảng × 4 mốc, ID giữ dạng chuỗi
fn 0 91 | run_llm_stage | key/cache → chạy LLM, thiếu thì bỏ qua
fn 0 104 | run_evaluation_stage | nhãn tay + cache → chấm điểm
fn 0 117 | main | 9 bước theo thứ tự docstring
## Mỗi lần chạy
st 1 119 | Đọc cờ | argv → Namespace
st 1 122 | Đọc config | load_config một lần
st 1 125 | Mốc khác đề? | without_expected, bỏ đối chiếu số lượng
st 1 132 | 1. Tải + lọc | download.run, trừ khi --skip-download
st 1 140 | Mẫu theo seed? | bỏ qa.expected lần nữa
st 1 144 | 2. QA | gắn cờ từng dòng, ghi qa_report.csv
st 1 153 | 3. Chia nhóm | 6 bảng segments_*, trả seg
st 1 160 | 4. LLM | phải xong trước KPI
st 1 162 | 4b. So sánh nhóm | cần seg + cache LLM
st 1 174 | 4c. Đánh giá | cần nhãn tay
st 1 180 | 5. KPI | dùng bảng đã QA
st 1 183 | 5b. KPI căn ảo | chỉ scope full
st 1 190 | 6. Hình | 8 hình trong repo
st 1 196 | 6b. Hình căn ảo | loại input cũ khỏi figures/phantom
chips 2 | config:90 load_config ; config:70 expected_applies ; qa:1 qa.run ; seg_init:31 segments.run ; kpi:1 kpi.run ; viz:373 viz.run ; viz_phantom:929 viz_phantom.run

--- review
mid | <code>--skip-llm</code> không tắt 4b/4c | Cờ chỉ bỏ bước 4 (dòng 94–95). Nếu cache LLM có sẵn, <code>llm_segments.run</code> (dòng 162) và <code>evaluate.run</code> (dòng 114) vẫn chạy và ghi bảng, dù người dùng tưởng đã tắt LLM. Không sai về dữ liệu (chỉ đọc cache), nhưng tên cờ dễ gây hiểu lầm.
mid | Cache thiếu một phần vẫn vào 4b | <code>run_llm_stage</code> coi cache thiếu mẫu là "chưa có kết quả" và bỏ bước 4 (dòng 96), nhưng <code>llm_segments.run</code> chỉ kiểm <code>cache_path.exists()</code> (<code>src/llm_segments.py:145</code>). Cache tồn tại nhưng thiếu review → 4b vẫn ghi bảng trên mẫu hụt, không cảnh báo, và 6b không đánh dấu stale vì <code>comparison</code> khác <code>None</code>.
mid | Tên file 4b không phân biệt scope | <code>llm_segments.run</code> luôn ghi <code>llm_segment_aspects.csv</code> (<code>src/llm_segments.py:166</code>), không có hậu tố <code>_full</code>/<code>_sample</code>. Chạy <code>--segments-scope sample</code> sau một lần full sẽ ghi đè bảng chính thức; hình 08 sau đó vẽ từ bảng mẫu mà <code>stale</code> không phát hiện (chỉ kiểm <code>comparison is None</code>).
low | <code>figures_dir</code> hai kiểu | Dòng 191 trả <code>Path</code> khi có hình, <code>str</code> khi rỗng. Chỉ dùng để in nên chưa gây lỗi, nhưng nếu sau này dùng tiếp thì phải chuẩn hoá.
ok | Dừng sớm khi thiếu bảng đã xử lý | <code>FileNotFoundError</code> nêu đúng file (dòng 82–85), tránh QA/KPI chạy trên bảng rỗng rồi ghi báo cáo sai.
ok | Không sinh dữ liệu giả | Ba nhánh thiếu key/cache/nhãn tay đều in lý do và bỏ qua bước tương ứng; không có đường nào tạo nhãn LLM giả.

--- qa
? Vì sao LLM phải chạy trước KPI?
<p>Vì bước 5 đọc cache LLM để tính 2 KPI scope <code>llm</code> (<code>complaint_bearing_review_rate</code> và <code>top_complaint_aspect_share</code>). Trong repo, <code>kpi_metrics.csv</code> có đúng 2 dòng scope <code>llm</code>, snapshot <code>ALL</code>: 14,0% (n = 1.000) và 50,0% (n = 176). Chạy KPI trước thì thiếu 2 dòng này và <code>viz.run</code> không vẽ được hình 08.</p>
? Vì sao chia nhóm căn trước LLM?
<p>Bước 4b nối nhãn LLM với nhóm căn qua <code>segments_&lt;scope&gt;.csv</code> và cần <code>seg["scope"]</code>. Không có bước 3 thì <code>comparison = None</code>, 4b bị bỏ, kéo theo 6b không vẽ hình 08.</p>
? Đổi 4 mốc trong yaml thì pipeline có dừng oan không?
<p>Không. <code>expected_applies</code> so <code>qa.expected.snapshots</code> với <code>config["snapshots"]</code> (dòng 125); khác thì <code>without_expected</code> bỏ đối chiếu 1.000 căn / 875-125 / 50-30-25-25. Còn nếu giữ đúng mốc mà mẫu sai thì QA vẫn dừng với <code>QAConstraintError</code> — test <code>test_cli_still_enforces_assignment_counts_on_the_assigned_snapshots</code> kiểm điều này.</p>
? <code>stale</code> ở bước 6b để làm gì?
<p>Để không vẽ hình từ CSV cũ còn trên đĩa. Không có cache LLM thì <code>llm_aspects</code> bị loại; scope không full thì <code>kpi_phantom</code> bị loại. Ví dụ đã kiểm: CSV <code>llm_segment_aspects.csv</code> cũ vẫn còn, nhưng hình 08 bị bỏ với lý do "chưa được cập nhật".</p>
? Vì sao bước 5b cần scope full?
<p><code>run_phantom</code> đọc <code>segments_full.csv</code> và <code>data/raw</code> để có dữ liệu của 20.573 căn toàn thành phố; scope sample chỉ có 1.000 căn đã lọc và không có <code>data/raw</code>. Vì vậy dòng 183 kiểm <code>seg["scope"] == "full"</code>.</p>
? Nếu thiếu một CSV trong <code>data/processed/&lt;city&gt;/&lt;mốc&gt;/</code> thì sao?
<p><code>load_processed_tables</code> dừng với <code>FileNotFoundError</code> nêu đúng đường dẫn và nhắc chạy lại không có <code>--skip-download</code>. Test <code>test_cli_fails_with_the_missing_processed_path</code> xoá <code>reviews.csv</code> và kiểm mã thoát khác 0.</p>
? Vì sao <code>--skip-download</code> vẫn cần <code>data/processed</code>?
<p>Vì QA đọc bảng đã lọc ở <code>data/processed/&lt;city&gt;/&lt;mốc&gt;/</code>, không đọc raw. <code>--skip-download</code> chỉ bỏ bước tải, không tạo dữ liệu; thiếu bảng thì dừng ở <code>load_processed_tables</code>.</p>
