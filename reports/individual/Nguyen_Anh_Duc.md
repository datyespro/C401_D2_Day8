# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Anh Đức  
**Vai trò trong nhóm:** M6 — Report & Architecture Documentation Owner  
**Ngày nộp:** _(điền ngày nộp)_  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này?

Trong lab này, tôi đảm nhận vai trò **M6 — Documentation & Report Owner**, phụ trách hai phạm vi chính:

**Phần code (`eval.py` từ dòng 210 trở xuống):**
Tôi implement hàm `generate_grading_log()` — script tự động chạy pipeline với `grading_questions.json` và xuất kết quả theo đúng format `logs/grading_run.json` mà giảng viên yêu cầu. Script xử lý cả trường hợp pipeline crash từng câu (ghi `PIPELINE_ERROR`) để không làm mất điểm toàn bộ log. Tôi cũng kích hoạt (uncomment) phần chạy `run_scorecard(VARIANT_CONFIG)` và `compare_ab()`, đảm bảo luồng eval end-to-end `baseline → variant → A/B delta` hoạt động mượt khi M3/M4/M5 hoàn thành phần của họ.

**Phần tài liệu (`docs/`):**
Tôi xây dựng `architecture.md` mô tả toàn bộ kiến trúc pipeline từ indexing đến generation, kèm sơ đồ Mermaid và bảng failure mode checklist. Tôi soạn `tuning-log.md` với format per-question detail và bảng A/B comparison theo 4 metrics, với phân tích nguyên nhân (Error Tree) hỗ trợ team debug.

Công việc của tôi kết nối trực tiếp với toàn bộ pipeline: phần log tôi tạo phụ thuộc output của M3+M4 (`rag_answer()`), phần scorecard phụ thuộc M5 (`score_*` functions), và phần tài liệu phản ánh quyết định kỹ thuật của M1+M2 (chunking, embedding model).

---

## 2. Điều tôi hiểu rõ hơn sau lab này

**Về kiến trúc RAG và A/B testing:**
Trước lab, tôi hiểu RAG theo lý thuyết gồm 3 bước Retrieve-Augment-Generate. Sau lab, tôi nhận ra việc đánh giá RAG khó hơn nhiều so với đánh giá ML thông thường — không có label duy nhất "đúng/sai", mà phải đánh giá theo 4 chiều độc lập: câu trả lời có bám context không (Faithfulness), có trả lời đúng câu hỏi không (Relevance), retriever có lấy về đúng nguồn không (Context Recall), và có đủ thông tin không (Completeness). Một pipeline có Faithfulness cao nhưng Context Recall thấp cho thấy lỗi nằm ở retrieval chứ không phải generation.

**Về A/B testing thực tế:**
A/B Rule "chỉ đổi MỘT biến" nghe đơn giản nhưng thực tế rất dễ vi phạm. Khi team đổi đồng thời chunking + hybrid + rerank, không thể biết delta đến từ biến nào — đây là lỗi kinh điển trong thử nghiệm hệ thống AI. Việc ghi tuning log theo từng variant giúp trace lại được quyết định và justify kết quả.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

⚠️ **[Phụ thuộc runtime — ĐIỀN SAU khi chạy pipeline thực tế]**

> Mô tả 1–2 điều xảy ra không đúng kỳ vọng khi chạy eval.py, ví dụ:
> - "Tôi giả định Context Recall sẽ cao vì dense vector search, nhưng thực tế q07 (câu dùng alias 'approval matrix') cho recall = 1/5 vì embedded vector của alias và term gốc không đủ gần."
> - "Hàm compare_ab() in đúng delta nhưng baseline và variant đều show *N/A* lần đầu vì M5 chưa implement score_faithfulness — phải chờ M5 xong mới có số liệu thực."
> - "Grading log tưởng đơn giản nhưng phải xử lý edge case: nếu pipeline raise NotImplementedError giữa chừng, script dừng hoàn toàn → tôi thêm try/except từng câu để log các câu còn lại vẫn được ghi."

---

## 4. Phân tích một câu hỏi trong grading

⚠️ **[Phụ thuộc runtime — ĐIỀN SAU khi grading_questions.json được public lúc 17:00]**

**Câu hỏi được chọn:** _(chọn 1 câu thú vị từ grading run)_

**Phân tích theo Error Tree:**

> Điền theo format sau đây (thay X, Y bằng số liệu thực):
>
> **Baseline:** Faithfulness X/5 | Relevance X/5 | Context Recall X/5 | Completeness X/5  
>
> **Lỗi nằm ở đâu:**
> - Indexing: [có/không] — vì...
> - Retrieval: [có/không] — vì...
> - Generation: [có/không] — vì...
>
> **Variant có cải thiện không:**
> - Context Recall từ X/5 → Y/5 (+Z) nhờ...
> - Hoặc: Không cải thiện vì...
>
> **Root cause và fix đề xuất:**
> "Pipeline fail ở bước [retrieval/generation] vì [nguyên nhân]. Fix cụ thể: [thay đổi gì]."

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

⚠️ **[Điền sau khi có scorecard — phải có evidence từ kết quả thực tế]**

> Đề xuất 1–2 cải tiến cụ thể, ví dụ:
>
> **Cải tiến 1 — Implement LLM-as-Judge tự động:**  
> Hiện tại `score_faithfulness()` và `score_completeness()` trả về `None` (chấm thủ công). Nếu có thêm giờ, tôi sẽ implement prompt LLM-as-Judge để tự động chấm, giúp scale evaluation lên 100+ câu mà không cần can thiệp thủ công. Theo SCORING.md, đây cũng trị giá +2 điểm bonus.
>
> **Cải tiến 2 — [dựa trên scorecard thực tế]:**  
> "Scorecard cho thấy X metric thấp nhất ở nhóm câu Y → tôi sẽ thử [query expansion / MMR rerank / metadata filter] theo cơ chế Z."
