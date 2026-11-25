--- meta
title: .github/workflows/ci.yml
lead: Một workflow GitHub Actions, ba job song song: <code>lint</code> (ruff), <code>typecheck</code> (mypy), <code>test</code> (pytest trên hai phiên bản Python). Mọi job cài từ <code>requirements.lock.txt</code> đã ghim; test chạy ma trận 3.10.22 và 3.12 rồi luôn tải JUnit + coverage + transcript E2E lên artifact.

--- blocks
=== 1
<p>Tên workflow hiện trên tab Actions. Không ảnh hưởng logic; dùng để phân biệt khi repo có nhiều workflow.</p>

=== 3-7
<p>Ba cách kích hoạt:</p>
<ul><li><code>push</code> chỉ trên nhánh <code>main</code>: đẩy lên nhánh phụ không chạy CI cho tới khi mở pull request.</li>
<li><code>pull_request</code>: mọi PR, bất kể nhánh đích, đều chạy.</li>
<li><code>workflow_dispatch</code>: cho phép bấm chạy tay từ tab Actions.</li></ul>
<p><code>test_repo_hygiene.py</code> kiểm workflow có cả <code>push</code> lẫn <code>pull_request</code>, nên xoá một trigger là test đỏ.</p>

=== 9-10
<p><code>permissions: contents: read</code>: token của workflow chỉ đọc nội dung repo, đủ cho <code>actions/checkout</code>. Không cấp quyền ghi vì workflow không commit, không tạo release, không sửa issue, đúng nguyên tắc quyền tối thiểu.</p>

=== 12-14
<p><code>concurrency</code>: nhóm theo tên workflow + <code>github.ref</code> (nhánh hoặc tag). <code>cancel-in-progress: true</code> huỷ lần chạy cũ cùng nhánh khi có lần mới, tiết kiệm runner và tránh kết quả cũ ghi đè.</p>

=== 16-18
<p>Hai biến môi trường toàn workflow:</p>
<ul><li><code>PIP_DISABLE_PIP_VERSION_CHECK=1</code>: pip không kiểm tra phiên bản mới, bớt nhiễu log và một request mạng.</li>
<li><code>PYTHONUTF8=1</code>: bật UTF-8 mode của Python, để đọc/ghi file tiếng Việt không phụ thuộc locale runner.</li></ul>

=== 20-24
<p><code>jobs</code> chứa ba job chạy song song, không job nào <code>needs</code> job khác. Job <code>lint</code>: tên hiển thị tiếng Việt, chạy trên <code>ubuntu-latest</code>, bắt đầu danh sách <code>steps</code>.</p>

=== 25
<p><code>actions/checkout@v4</code> lấy mã nguồn vào runner. Không có <code>fetch-depth</code> đặc biệt, nên chỉ lấy commit mới nhất, đủ cho lint/test, không cần lịch sử git.</p>

=== 27-31
<p>Cài Python cho job lint: <code>setup-python@v5</code>, phiên bản 3.12, bật cache pip với khoá là <code>requirements.lock.txt</code>. Cache chỉ đổi khi lockfile đổi, nên các lần chạy sau cài nhanh hơn.</p>
<p>Job lint chạy Python 3.12 nhưng <code>target-version = "py310"</code> trong <a href="#pyproject-L10">pyproject dòng 10</a>; <code>target-version</code> giữ quy ước 3.10 cho các luật nâng cấp cú pháp, còn cổng chạy thật trên 3.10 là leg test.</p>

=== 33-34
<p>Cài đúng lockfile đã ghim, không cài <code>requirements.txt</code> trần. Nhờ vậy CI và máy dev dùng cùng phiên bản. <code>test_repo_hygiene.py</code> kiểm chuỗi <code>requirements.lock.txt</code> phải có trong workflow.</p>

=== 36-37
<p><code>ruff check --output-format=github .</code>: lint toàn repo, xuất lỗi theo định dạng GitHub để hiện annotation ngay trên dòng code trong PR. Luật lấy từ <a href="#pyproject-L13">pyproject dòng 13</a>.</p>

=== 39-40
<p><code>ruff format --check --diff .</code>: chỉ kiểm định dạng, không sửa. Nếu file chưa đúng format, job đỏ và in diff. Cố ý không chạy <code>ruff format .</code> trong CI vì CI không nên sửa code.</p>

=== 42-45
<p>Job <code>typecheck</code> cùng khuôn với lint: Ubuntu, checkout, setup Python 3.12. Tách job riêng để log lỗi kiểu không lẫn với lint.</p>

=== 46
<p>Checkout mã nguồn cho job typecheck.</p>

=== 48-52
<p>Python 3.12 + cache pip theo lockfile, giống job lint. Hai job lint và typecheck dùng chung phiên bản chạy để kết quả công cụ nhất quán.</p>

=== 54-55
<p>Cài dependencies từ lockfile. mypy cần stubs (<code>types-PyYAML</code>, <code>pandas-stubs</code>...) đã nằm trong <code>requirements-dev.txt</code> và được gộp vào lockfile.</p>

=== 57-58
<p><code>mypy</code> không tham số: đọc <code>[tool.mypy] files = ["run_pipeline.py", "src", "tests"]</code> trong <a href="#pyproject-L18">pyproject dòng 18</a>. Vì vậy danh sách file cần kiểu chỉ sửa ở một chỗ.</p>

=== 60-62
<p>Job <code>test</code>: tên có <code>${{ matrix.python-version }}</code> để phân biệt hai leg trên giao diện Actions; chạy trên Ubuntu.</p>

=== 63-67
<p>Chiến lược ma trận:</p>
<ul><li><code>fail-fast: false</code>: một leg lỗi không huỷ leg còn lại, nên thấy đủ lỗi trên cả 3.10 và 3.12.</li>
<li><code>python-version: ["3.10.22", "3.12"]</code>: 3.10.22 là bản khai trong <code>.python-version</code>; 3.12 để bắt lệch phiên bản. Test hygiene kiểm ma trận phải chứa đúng chuỗi <code>"3.10.22"</code>.</li></ul>

=== 68
<p>Bắt đầu các bước của job test, chạy lại cho từng leg của ma trận.</p>

=== 69
<p>Checkout mã nguồn cho leg hiện tại.</p>

=== 71-75
<p>Cài Python theo <code>${{ matrix.python-version }}</code>, cache pip theo lockfile. Mỗi leg có cache riêng vì phiên bản Python khác nhau.</p>

=== 77-78
<p>Cài dependencies từ lockfile đã ghim. Cùng một lockfile cho cả 3.10.22 và 3.12; <code>requirements.lock.txt</code> được compile <code>--universal</code> nên có marker cho từng nền tảng/phiên bản.</p>

=== 80-83
<p>Bước chạy test. <code>env</code> đặt <code>E2E_ARTIFACT_DIR=ci-artifacts/e2e</code>: fixture <code>e2e_artifact_dir</code> trong <code>tests/conftest.py</code> đọc biến này và tạo thư mục, để transcript E2E được upload cùng báo cáo. <code>run: |</code> mở block shell nhiều dòng.</p>

=== 84-86
<p>Lệnh pytest nối bằng dấu <code>\</code> của bash:</p>
<ul><li><code>--junitxml=ci-artifacts/junit-&lt;phiên bản&gt;.xml</code>: báo cáo JUnit riêng từng leg.</li>
<li><code>--cov-report=xml:ci-artifacts/coverage-&lt;phiên bản&gt;.xml</code>: coverage XML riêng từng leg.</li></ul>
<p>Không truyền <code>--cov</code> hay <code>--cov-fail-under</code> ở đây vì chúng đã nằm trong <code>addopts</code> của <a href="#pyproject-L29">pyproject dòng 29</a>; pytest tự đọc. Ngưỡng 95% vì thế vẫn áp.</p>

=== 88-94
<p>Tải báo cáo lên artifact:</p>
<ul><li><code>if: always()</code>: chạy cả khi test đỏ, để còn JUnit/coverage/transcript mà xem.</li>
<li><code>actions/upload-artifact@v4</code>, tên <code>test-report-py&lt;phiên bản&gt;</code> nên hai leg không ghi đè nhau.</li>
<li><code>path: ci-artifacts/</code> gom JUnit, coverage XML và thư mục <code>e2e/</code>.</li>
<li><code>if-no-files-found: warn</code>: không có file thì chỉ cảnh báo, không làm job đỏ thêm.</li></ul>
<p>Cả hai đường dẫn báo cáo đều nằm dưới <code>ci-artifacts/</code>; pytest/coverage tự tạo thư mục cha khi ghi, đã chạy thử và thấy file được tạo dù thư mục chưa tồn tại.</p>

--- flow
## Kích hoạt
fn 0 3 | on | push main, PR, chạy tay
st 1 9 | permissions | Chỉ đọc nội dung repo
st 1 12 | concurrency | Huỷ run cũ cùng ref
st 1 16 | env | Tắt check pip, ép UTF-8
## Job lint
fn 0 21 | lint | ruff check + format
st 1 25 | checkout | Lấy mã nguồn
st 1 27 | setup-python 3.12 | Cache pip theo lockfile
st 1 33 | pip install | Cài từ requirements.lock.txt
st 1 36 | ruff check | Annotation kiểu GitHub
st 1 39 | ruff format --check | Chỉ kiểm, không sửa
## Job typecheck
fn 0 42 | typecheck | mypy
st 1 46 | checkout | Lấy mã nguồn
st 1 48 | setup-python 3.12 | Cache pip
st 1 54 | pip install | Cài từ lockfile
st 1 57 | mypy | Đọc files trong pyproject
## Job test
fn 0 60 | test | pytest hai phiên bản
st 1 63 | matrix | 3.10.22 và 3.12, fail-fast false
st 1 69 | checkout | Lấy mã nguồn
st 1 71 | setup-python | Theo matrix, cache pip
st 1 77 | pip install | Cài từ lockfile
st 1 80 | pytest | JUnit + coverage XML
st 1 88 | upload-artifact | Luôn tải báo cáo
chips 1 | pyproject:8 ruff ; pyproject:16 mypy ; pyproject:27 pytest

--- review
ok | Quyền tối thiểu | <code>permissions: contents: read</code> đủ cho checkout và upload artifact; workflow không cần quyền ghi.
ok | Huỷ run cũ | <code>concurrency</code> theo workflow + ref, <code>cancel-in-progress: true</code> tránh chạy chồng trên cùng nhánh.
ok | Cài từ lockfile | Cả ba job đều <code>pip install -r requirements.lock.txt</code>; test hygiene kiểm điều này nên không lọt về cài requirements trần.
mid | Lint/typecheck không chạy trên 3.10 | Hai job này dùng Python 3.12; chỉ job test có leg 3.10.22. Rủi ro: lỗi chỉ xuất hiện khi chạy trên 3.10 mà không có test tương ứng vẫn có thể lọt qua lint/typecheck. Cấu hình <code>target-version = "py310"</code> và <code>mypy python_version = "3.10"</code> giảm rủi ro cú pháp nhưng không thay runtime thật.
low | Không đặt timeout-minutes | Job treo dùng mặc định 360 phút của GitHub; thêm <code>timeout-minutes</code> sẽ tránh tốn runner khi test kẹt.
low | push chỉ nhánh main | Đẩy lên nhánh phụ không chạy CI cho tới khi mở PR. Nếu muốn kiểm mọi nhánh, phải thêm mẫu nhánh vào <code>push</code>.

--- qa
? Vì sao CI cài từ <code>requirements.lock.txt</code> mà không phải <code>requirements.txt</code>?
<p>Lockfile ghim chính xác mọi phiên bản (kể cả phụ thuộc gián tiếp), nên CI tái lập được và không bị thư viện mới làm đỏ bất ngờ. <code>requirements.txt</code> chỉ ghi phụ thuộc trực tiếp, thường không ghim phiên bản.</p>
? Vì sao lint/typecheck chạy Python 3.12 còn test chạy cả 3.10.22?
<p>3.10.22 là phiên bản khai trong <code>.python-version</code>, nên phải có leg test đúng phiên bản đó. 3.12 để bắt lệch phiên bản. Lint/typecheck chỉ cần một môi trường chạy công cụ; chúng vẫn cấu hình ngôn ngữ đích 3.10 qua pyproject.</p>
? <code>--output-format=github</code> để làm gì?
<p>Ruff xuất lỗi theo định dạng GitHub, biến chúng thành annotation trên dòng code trong PR thay vì chỉ log trong console. Người review thấy lỗi ngay chỗ sửa.</p>
? Vì sao bước upload dùng <code>if: always()</code>?
<p>Để khi test đỏ vẫn có JUnit, coverage XML và transcript E2E mà xem nguyên nhân. Nếu không có <code>always()</code>, bước upload bị bỏ qua khi bước trước lỗi.</p>
? Job test lấy <code>--cov</code> và ngưỡng 95% ở đâu?
<p>Từ <code>addopts</code> trong <a href="#pyproject-L29">pyproject dòng 29</a>: <code>--cov</code>, <code>--cov-report=term-missing</code>, <code>--cov-fail-under=95</code>. Lệnh trong CI chỉ thêm báo cáo JUnit và coverage XML.</p>
