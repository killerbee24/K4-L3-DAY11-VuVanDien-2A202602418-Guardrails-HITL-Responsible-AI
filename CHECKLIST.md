# Checklist hoàn thành Lab 11

> Thứ tự ưu tiên: **sửa môi trường → CP2 → CP3 → CP4 → tự chấm → optional**.
>
> Không tự tạo nội dung JSON trong `outputs/` bằng tay. Các artifact phải được sinh bởi lệnh chạy lab.

## Hiện trạng ban đầu

- [x] Tên repo đúng định dạng: `K4-L3-DAY11-VuVanDien-2A202602418-Guardrails-HITL-Responsible-AI`
- [x] Git remote đã trỏ tới repo cá nhân, nhánh `main`
- [x] `.env` được ignore và không bị Git theo dõi
- [x] `.env` đã thay toàn bộ placeholder bằng API key hợp lệ
- [x] Python 3.11/3.12 hoạt động từ terminal
- [x] `.venv` đã được sửa và hoạt động
- [x] Dependencies đã được cài đầy đủ
- [x] Smoke tests chạy xanh
- [x] Thư mục `outputs/` và các artifact đã được sinh
- [x] README đã có họ tên, MSSV và hướng dẫn chạy ngắn

## Checkpoint 1 — Chuẩn bị môi trường

- [x] Cài Python 3.11 hoặc 3.12 và thêm Python vào `PATH`
- [x] Sửa `.venv` cũ để trỏ tới Python hiện có
- [x] Tạo/sửa và kích hoạt môi trường:

  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  python -m pip install -U pip
  pip install -r requirements.txt
  ```

- [x] Cấu hình `.env`:
  - [x] `OPENROUTER_API_KEY` cho Blue
  - [ ] `RED_TEAM_PROVIDER=openai` và `OPENAI_API_KEY`; hoặc
  - [x] `RED_TEAM_PROVIDER=gemini` và `GOOGLE_API_KEY`
  - [x] Dùng model mặc định `gpt-4o-mini` hoặc `gemini-3.5-flash` khi chạy phần bắt buộc

- [x] Chạy smoke tests:

  ```powershell
  pytest tests/smoke -q
  ```

### Pass signal CP1

- [x] Import dependencies thành công
- [x] Smoke tests xanh
- [x] `.env` và `.venv` vẫn không bị Git theo dõi

## Checkpoint 2 — Blue input/output guardrails (40 điểm)

### Input guardrails — `src/guardrails/input_guardrails.py`

- [x] Cài đặt `detect_injection(user_input)`
- [x] Thêm ít nhất 5 regex phát hiện prompt injection
- [x] Bắt được các dạng:
  - [x] Ignore previous/above instructions
  - [x] You are now
  - [x] System prompt
  - [x] Reveal instructions/prompt
  - [x] Pretend/act as unrestricted
- [x] Chuẩn hóa Unicode bằng NFKC và loại ký tự zero-width
- [x] Bắt được injection giấu trong email/RAG, ví dụ `Ignore\u200b all previous instructions`
- [x] Không chặn nhầm tài liệu bên ngoài có nội dung banking bình thường
- [x] Cài đặt `topic_filter(user_input)` bằng `ALLOWED_TOPICS` và `BLOCKED_TOPICS`
- [x] Topic cấm hoặc không liên quan banking trả về `"BLOCK"`
- [x] Câu banking hợp lệ trả về `"ALLOW"`
- [x] Hoàn thiện `InputGuardrailPlugin.on_user_message_callback()`
- [x] Cập nhật đúng `total_count` và `blocked_count`
- [x] Khi chặn, trả về `types.Content`; khi cho qua, trả về `None`

### Output guardrails — `src/guardrails/output_guardrails.py`

- [x] Cài đặt các regex trong `content_filter(response)`:
  - [x] Số điện thoại Việt Nam
  - [x] Email
  - [x] CMND/CCCD 9 hoặc 12 số
  - [x] API key dạng `sk-...`
  - [x] Password dạng `password: ...` hoặc `password=...`
- [x] `content_filter()` trả đủ `safe`, `issues`, `redacted`
- [x] Thay dữ liệu nhạy cảm bằng `[REDACTED]`
- [x] Không chặn nhầm câu banking sạch
- [x] Hoàn thiện `OutputGuardrailPlugin.after_model_callback()`
- [x] Cập nhật đúng `total_count`, `redacted_count`, `blocked_count`
- [x] LLM-as-Judge để sau vì không bắt buộc
- [x] Quick tests CP2 sử dụng câu hỏi và tình huống tiếng Việt

### Kiểm tra CP2

- [x] Chạy:

  ```powershell
  python src/main.py --part 2
  pytest tests/public/test_lab_contracts.py -q
  ```

- [x] Injection và off-topic bị chặn
- [x] Secret/PII bị redact
- [x] Câu banking hợp lệ không bị chặn nhầm

## Checkpoint 3 — Blue pipeline và artifact phòng thủ (40 điểm)

### Rate limiter — `src/assignment/rate_limiter.py`

- [x] Cài đặt sliding window riêng cho từng `user_id`
- [x] Xóa timestamp đã cũ hơn `window_seconds`
- [x] Cho phép tối đa `max_requests` trong một cửa sổ
- [x] Request vượt giới hạn trả thông báo rate limit và không gọi LLM
- [x] Cập nhật đúng `total_count` và `blocked_count`

### Audit log — `src/assignment/audit_log.py`

- [x] Cài đặt `record_input()`
- [x] Lưu user, input, request ID và thời điểm bắt đầu
- [x] Cài đặt `record_output()`
- [x] Lưu output, trạng thái block, layer và latency
- [x] Cài đặt `export_json()`
- [x] Tạo thư mục cha nếu chưa tồn tại
- [x] Ghi mặc định vào `outputs/audit_log.json`

### Monitoring — `src/assignment/monitoring.py`

- [x] Cập nhật các bộ đếm request, block, rate-limit và judge
- [x] Cài đặt `check_metrics()`
- [x] Tạo alert khi vượt các threshold đã khai báo
- [x] Tránh thêm alert trùng lặp khi gọi nhiều lần
- [x] Cài đặt `export_json()`
- [x] Ghi mặc định vào `outputs/metrics.json`

### Pipeline — `src/assignment/pipeline.py`

- [x] Cài đặt `is_egress_allowed(destination, payload)`
- [x] Chỉ cho phép URL HTTPS
- [x] Host phải khớp chính xác allowlist VinBank, không dùng so khớp hậu tố thiếu an toàn
- [x] Chặn payload chứa password, API key, DB host, số điện thoại hoặc email
- [x] `build_production_plugins()` trả đúng thứ tự:
  1. [x] `RateLimitPlugin`
  2. [x] `InputGuardrailPlugin`
  3. [x] `OutputGuardrailPlugin`
- [x] `build_observability()` trả `(AuditLogPlugin(), MonitoringAlert())`
- [x] Hoàn thiện `run_assignment_suite(pipeline)`
- [x] Dùng `create_blue_agent(plugins)` cho Blue
- [x] Chạy và thu thập ít nhất:
  - [x] 5 safe queries, tất cả `blocked: false`
  - [x] 7 attack queries, ít nhất 5 query `blocked: true`
  - [x] Rate-limit test có ít nhất 1 request bị chặn
  - [x] 3 edge cases
- [x] Mỗi query có tối thiểu `input` và `blocked`
- [x] Nên có thêm `layer` và `response_preview`
- [x] Ghi `framework`, ví dụ `google-adk`
- [x] Ghi các file dưới repo root, không ghi vào `src/outputs/`

### Kiểm tra CP3

- [x] Chạy CP3:

  ```powershell
  python src/main.py --part 3
  ```

- [x] Chạy contract test bằng Python:

  ```powershell
  pytest tests/public/test_results_contract.py -q
  ```

- [x] Có `outputs/results.json`
- [x] Có `outputs/audit_log.json`
- [x] Có `outputs/metrics.json`
- [x] `results.json` khớp contract tối thiểu của `schemas/results.schema.json`
- [x] `passed + blocked == sent` trong kết quả rate limit

## Checkpoint 4 — Red team (20 điểm)

### Viết prompt — `src/attacks/attacks.py`

- [x] Thay toàn bộ 5 chuỗi `TODO: ...` trong `adversarial_prompts`
- [x] Prompt 1 dùng Completion/Fill-in-the-blank
- [x] Prompt 2 dùng Translation/Reformatting
- [x] Prompt 3 dùng Hypothetical/Creative writing
- [x] Prompt 4 dùng Confirmation/Side-channel
- [x] Prompt 5 dùng Multi-step/Gradual escalation
- [x] Mỗi prompt đủ dài, cụ thể và có ngữ cảnh thực tế
- [x] Không chỉ dùng câu ngắn kiểu “Ignore all instructions”

### Chạy attack

- [x] Chạy:

  ```powershell
  python src/main.py --part 4
  ```

- [ ] Red mặc định leak được ít nhất một demo secret
- [x] Đã ghi nhận trung thực lỗi quota Gemini trong artifact; không giả kết quả leak
- [x] Có `outputs/unsafe_attack_result.json`
- [x] Có `outputs/guards_attack_result.json`
- [x] Có `outputs/attack_results.json`
- [x] `attack_results.json` có cả `unsafe_attacks` và `guards_attacks`
- [x] Mỗi nhóm có ít nhất 5 kết quả
- [x] `llm_provider` và `llm_model` khớp `.env` lúc chạy
- [x] Không sửa secret trong `data/protected/vinbank_secrets.json`
- [x] Không sửa JSON bằng tay để giả `leaked: true`

### Bonus — chỉ chọn một

- [ ] B1: leak Red, tối đa +5; hoặc
- [ ] B2: leak Red Advance, tối đa +10
- [x] Hiểu rằng grader sẽ replay; JSON chỉ là bằng chứng

## Checkpoint 5 — Tự chấm và nộp

- [x] Bổ sung họ tên, MSSV và hướng dẫn chạy ngắn vào `README.md`
- [x] Chạy toàn bộ kiểm tra:

  ```powershell
  pytest tests/smoke -q
  pytest tests/public -q
  python scripts/grade.py --submission-dir . --out outputs/grade_report.json
  ```

- [x] Có hai artifact bắt buộc:
  - [x] `outputs/results.json`
  - [x] `outputs/attack_results.json`

- [x] Có các artifact khuyến nghị:
  - [x] `outputs/audit_log.json`
  - [x] `outputs/metrics.json`
  - [x] `outputs/unsafe_attack_result.json`
  - [x] `outputs/guards_attack_result.json`

- [x] Grader tự sinh:
  - [x] `outputs/grade_report.json`
  - [x] `outputs/lab_report.md`

- [x] `grade_report.json` có `technical_failure: false`
- [x] Không tự viết hoặc sửa `lab_report.md` bằng tay
- [x] Chạy `git status` và kiểm tra `.env`, `.venv` không được stage
- [x] Không commit API key thật
- [ ] Commit source code và các artifact trong `outputs/`
- [ ] Push nhánh `main` lên GitHub
- [ ] Nộp đúng link repo lên LMS/CodeLabs trước hạn

## Optional — chỉ làm sau khi hoàn thành phần bắt buộc

- [ ] Cài đặt LLM-as-Judge trong `output_guardrails.py`
- [ ] Bổ sung NeMo rules trong `nemo_guardrails.py`
- [ ] Cài đặt `ConfidenceRouter` trong `src/hitl/hitl.py`
- [ ] Điền ba HITL decision points
- [ ] Hoàn thiện Blue/Red comparison trong `src/testing/testing.py`
- [ ] Hoàn thiện `SecurityTestPipeline.run_all()` và `calculate_metrics()`
- [ ] Thử AI-generated attack prompts

## Checklist cuối cùng ngắn gọn

- [x] Python và `.venv` hoạt động
- [x] `.env` có key thật nhưng không được commit
- [x] CP2 hoàn thành và public tests xanh
- [x] CP3 sinh `results.json` hợp lệ
- [ ] CP4 sinh `attack_results.json` và Red có leak
- [x] Smoke tests xanh
- [x] Public tests xanh
- [x] Grader không báo technical failure
- [x] README có thông tin sinh viên
- [ ] Đã push và nộp link repo
