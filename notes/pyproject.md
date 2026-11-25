--- meta
title: pyproject.toml
lead: Cấu hình công cụ cho CI, không phải gói cài đặt: <code>ruff</code> (lint + format), <code>mypy</code> (type check), <code>pytest</code> + <code>coverage</code>. Ba “cổng” lint / typecheck / test trong <a href="#ci-L21">ci.yml</a> đều lấy ngưỡng từ đây; không có <code>[project]</code> hay <code>[build-system]</code> vì repo chạy bằng script, không phát hành package.

--- blocks
=== 1-6
<p>Khối comment đầu file là bản đồ của ba cổng CI:</p>
<ul><li><b>ruff</b> lo lint và format (mục <code>[tool.ruff]</code>).</li>
<li><b>mypy</b> lo kiểu (mục <code>[tool.mypy]</code>).</li>
<li><b>pytest</b> + <b>coverage</b> lo test và ngưỡng phủ (mục <code>[tool.pytest.ini_options]</code>, <code>[tool.coverage.*]</code>).</li></ul>
<p>Comment tách hai nhóm phụ thuộc: runtime ở <code>requirements.txt</code>, công cụ dev/CI ở <code>requirements-dev.txt</code>. Cả hai được gộp và ghim trong <code>requirements.lock.txt</code>; CI chỉ cài từ lockfile (<a href="#ci-L33">ci.yml dòng 33</a>). Dòng 6 ghi thứ tự chạy <code>ruff check . | ruff format --check . | mypy | pytest</code>, khớp ba job lint → typecheck → test của workflow.</p>

=== 8-11
<p>Mục <code>[tool.ruff]</code>:</p>
<ul><li><code>line-length = 120</code>: dùng chung cho cả lint và format (ruff format lấy độ dài này, không có mục riêng).</li>
<li><code>target-version = "py310"</code>: ruff hiểu code phải chạy trên Python 3.10, khớp <code>.python-version</code> (3.10.22) và <code>mypy.python_version</code> bên dưới. CI chạy ruff trên Python 3.12; <code>target-version</code> giữ quy ước 3.10 cho các luật nâng cấp cú pháp, còn cổng chạy thật trên 3.10 là leg test.</li>
<li><code>extend-exclude</code>: bỏ <code>data</code>, <code>reports</code>, <code>ci-artifacts</code>, <code>.venv</code>. Đây là thư mục dữ liệu, báo cáo và artifact CI, không phải mã nguồn; lint vào đó chỉ sinh nhiễu.</li></ul>
<p><code>test_repo_hygiene.py</code> khoá đúng hai giá trị đầu, nên đổi 120 hay <code>py310</code> là test đỏ.</p>

=== 13-14
<p><code>select</code> chọn bộ luật: <code>E</code>/<code>W</code> (pycodestyle), <code>F</code> (pyflakes), <code>I</code> (sắp import), <code>UP</code> (pyupgrade), <code>B</code> (bugbear), <code>C4</code> (comprehension), <code>SIM</code> (đơn giản hoá), <code>RUF</code> (luật riêng của ruff).</p>
<p>Không có <code>per-file-ignores</code>: <code>download.py</code> và <code>run_pipeline.py</code> không được miễn lint. Test hygiene kiểm cả điều này, nên một import thừa hay biến không dùng trong hai file đó cũng làm job lint đỏ.</p>

=== 16-18
<p>Mục <code>[tool.mypy]</code>:</p>
<ul><li><code>python_version = "3.10"</code>: mypy phân tích theo ngữ nghĩa 3.10, không theo phiên bản đang chạy (job typecheck dùng 3.12).</li>
<li><code>files = ["run_pipeline.py", "src", "tests"]</code>: CI chạy <code>mypy</code> không tham số (<a href="#ci-L57">ci.yml dòng 57</a>), mypy đọc danh sách này. <code>scripts/</code> không nằm trong danh sách, nên hai script ở đó không qua type check.</li></ul>

=== 19-25
<p>Comment dòng 19–20 giải thích lý do bật <code>check_untyped_defs</code>: vẫn phân tích thân hàm không có annotation thay vì bỏ qua cả file. Các cờ:</p>
<ul><li><code>check_untyped_defs = true</code>: bắt lỗi thật trong hàm chưa khai kiểu.</li>
<li><code>strict_equality = true</code>: so sánh <code>==</code> giữa hai kiểu không giao nhau là lỗi.</li>
<li><code>warn_unreachable = true</code>: code sau <code>return</code>/<code>raise</code> bị báo.</li>
<li><code>warn_unused_ignores = true</code>: <code># type: ignore</code> thừa cũng là lỗi; sau khi nâng thư viện, ignore cũ có thể làm đỏ CI.</li>
<li><code>warn_redundant_casts = true</code>: <code>cast()</code> về đúng kiểu sẵn có bị báo.</li></ul>
<p>Lưu ý: câu “Repo chưa có annotation nào” ở dòng 19 đã lỗi thời — nhiều hàm đã có annotation, ví dụ <code>load_config(path: str | Path) -&gt; dict[str, Any]</code> và <code>classify(df, seen_before, config) -&gt; pd.Series</code>.</p>

=== 27-36
<p>Mục pytest:</p>
<ul><li><code>testpaths = ["tests"]</code>: chạy <code>pytest</code> trần chỉ thu <code>tests/</code>.</li>
<li><code>-ra</code>: in tóm tắt mọi test không pass (skip, xfail, fail).</li>
<li><code>--strict-markers</code>: marker chưa khai báo là lỗi, không chỉ cảnh báo.</li>
<li><code>--strict-config</code>: khoá cấu hình sai là lỗi.</li>
<li><code>--cov</code> + <code>--cov-report=term-missing</code>: đo coverage và in dòng chưa phủ.</li>
<li><code>--cov-fail-under=95</code>: dưới 95% là exit 1.</li></ul>
<p>Vì <code>--cov-fail-under</code> nằm trong <code>addopts</code>, nó áp cho <b>mọi</b> lần chạy, kể cả khi chỉ chạy một file test. Đã chạy thử <code>pytest tests/test_config.py</code>: 10 test pass nhưng exit 1 vì coverage toàn repo chỉ 1,96%. Muốn chạy lẻ phải thêm <code>--no-cov</code>.</p>

=== 37-44
<p><code>filterwarnings</code>:</p>
<ul><li><code>"error"</code>: mọi warning thành lỗi, nên một <code>DeprecationWarning</code> mới của thư viện cũng làm test đỏ.</li>
<li><code>"ignore::FutureWarning"</code>: chỉ miễn <code>FutureWarning</code>.</li></ul>
<p>Comment dòng 39–42 giải thích: SDK Google đã ngừng hỗ trợ và cảnh báo vòng đời Python 3.10; phiên bản đã ghim trong lockfile nên cảnh báo không còn hành động được. Nhưng comment gọi tên <code>google-generativeai</code>, trong khi code thật import <code>from google import genai</code> (<a href="#llm-L391">llm.py dòng 391</a>) và <code>requirements.txt</code> ghim <code>google-genai==2.32.0</code>. Lý do giữ <code>ignore::FutureWarning</code> vẫn đúng, chỉ tên gói là sai.</p>

=== 46-48
<p><code>[tool.coverage.run]</code>:</p>
<ul><li><code>branch = true</code>: đo cả nhánh <code>if</code>/<code>for</code>, không chỉ dòng đã chạy. Nhờ vậy một nhánh <code>else</code> chưa bao giờ chạy vẫn bị tính là thiếu.</li>
<li><code>source = ["src", "run_pipeline"]</code>: chỉ đo các module này. <code>tests/</code> và <code>scripts/</code> không vào mẫu số.</li></ul>
<p>Hai script <code>check_assignment_data.py</code> và <code>label_additional_reviews.py</code> nằm ngoài cả <code>mypy.files</code> lẫn <code>coverage.source</code>, nên không có cổng nào canh chúng.</p>

=== 50-54
<p><code>[tool.coverage.report]</code> bỏ hai loại dòng khỏi báo cáo:</p>
<ul><li><code>pragma: no cover</code>: dòng đánh dấu chủ ý không kiểm.</li>
<li><code>if __name__ == .__main__.:</code>: khối chạy khi gọi trực tiếp file. Coverage so bằng regex, các dấu chấm không escape nên mẫu rộng hơn chuỗi literal, nhưng thực tế chỉ khớp dòng guard và không gây hại.</li></ul>
<p>Nhờ dòng thứ hai, phần <code>main()</code> của <code>run_pipeline.py</code> không bị tính là thiếu coverage khi test import module thay vì chạy CLI.</p>

--- flow
## Ruff
fn 0 8 | [tool.ruff] | Độ dài dòng và ngôn ngữ đích
st 1 9 | line-length 120 | Dùng chung cho lint và format
st 1 10 | target-version py310 | Cú pháp phải chạy trên 3.10
st 1 11 | extend-exclude | Bỏ data/reports/ci-artifacts/.venv
st 1 13 | select | E,F,W,I,UP,B,C4,SIM,RUF
## Mypy
fn 0 16 | [tool.mypy] | Check kiểu theo 3.10
st 1 18 | files | run_pipeline + src + tests
st 1 21 | check_untyped_defs | Phân tích cả hàm không annotation
st 1 22 | warn_* | Bắt code chết, ignore thừa, cast thừa
## Pytest
fn 0 27 | [tool.pytest.ini_options] | Cổng test
st 1 28 | testpaths | Chỉ thu tests/
st 1 29 | addopts | Coverage + fail-under 95
st 1 37 | filterwarnings | Warning thành lỗi, trừ FutureWarning
## Coverage
fn 0 46 | [tool.coverage.run] | Đo coverage nhánh
fn 0 50 | [tool.coverage.report] | Bỏ dòng main và pragma
chips 1 | ci:36 ruff check ; ci:57 mypy ; ci:80 pytest

--- review
mid | Comment mypy lỗi thời | Dòng 19 nói “Repo chưa có annotation nào”, nhưng nhiều hàm đã có annotation (<code>load_config</code>, <code>run</code>, <code>classify</code>...). Lý do bật <code>check_untyped_defs</code> vẫn đúng, nhưng câu mở đầu sai thực tế.
mid | Tên SDK trong comment sai | Dòng 39 nói <code>google-generativeai</code>, trong khi <code>src/llm.py</code> dòng 391 import <code>from google import genai</code> và <code>requirements.txt</code> ghim <code>google-genai==2.32.0</code>. Lý do ignore <code>FutureWarning</code> vẫn hợp lý, chỉ tên gói lệch.
mid | Ngưỡng 95% áp cả khi chạy một test | <code>--cov-fail-under=95</code> nằm trong <code>addopts</code>; đã chạy thử <code>pytest tests/test_config.py</code>, 10 test pass nhưng exit 1 vì coverage 1,96%. Chạy lẻ phải thêm <code>--no-cov</code>.
low | scripts/ ngoài mypy và coverage | <code>mypy.files</code> chỉ có <code>run_pipeline.py</code>, <code>src</code>, <code>tests</code>; <code>coverage.run.source</code> chỉ <code>src</code> + <code>run_pipeline</code>. Hai script trong <code>scripts/</code> không qua cổng nào.
ok | Ba cổng khớp test hygiene | <code>tests/test_repo_hygiene.py</code> kiểm line-length 120, target py310, <code>check_untyped_defs</code>, <code>testpaths</code>, <code>branch = true</code>; sửa một số ở đây là test đỏ ngay.

--- qa
? Vì sao <code>target-version = "py310"</code> khi CI chạy Python 3.12?
<p>Ruff và mypy cấu hình ngôn ngữ đích 3.10 vì <code>.python-version</code> là 3.10.22 và test chạy cả 3.10.22. Chạy công cụ trên 3.12 chỉ để bắt lệch phiên bản; cú pháp và kiểu vẫn cấu hình theo 3.10, còn cổng chạy thật trên 3.10 là leg test.</p>
? Vì sao <code>pytest tests/test_config.py</code> báo đỏ dù test pass?
<p>Vì <code>addopts</code> có <code>--cov</code> và <code>--cov-fail-under=95</code>. Chạy một file chỉ phủ một phần nhỏ <code>src/</code>, coverage toàn repo dưới 95% nên pytest trả exit 1. Chạy lẻ thì thêm <code>--no-cov</code>.</p>
? <code>check_untyped_defs = true</code> để làm gì?
<p>Mypy vẫn phân tích thân hàm không có annotation thay vì bỏ qua. Nhờ vậy bắt được lỗi kiểu thật trong các hàm chưa khai kiểu, đúng thực tế repo có nhiều hàm như vậy.</p>
? Vì sao <code>filterwarnings</code> đặt <code>"error"</code> rồi lại ignore <code>FutureWarning</code>?
<p><code>"error"</code> biến warning thành lỗi để CI không bỏ qua cảnh báo mới. <code>FutureWarning</code> của SDK Google bị ignore vì phiên bản đã ghim trong lockfile, cảnh báo không còn hành động được.</p>
? Vì sao file này không có <code>[project]</code>?
<p>Repo chạy bằng <code>run_pipeline.py</code>, không phát hành package lên PyPI. Chỉ cần cấu hình công cụ; thêm <code>[project]</code> sẽ kéo theo yêu cầu build metadata không dùng tới.</p>
