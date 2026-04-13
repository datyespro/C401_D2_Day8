# Tuning Log — RAG Pipeline (Day 08 Lab)

> **Tác giả (Documentation Owner):** Nguyễn Anh Đức (M6)  
> **A/B Rule:** Chỉ đổi **MỘT biến** mỗi lần — không đổi đồng thời chunking + hybrid + rerank.

---

## Baseline (Sprint 2)

**Ngày:** _(điền ngày chạy)_  
**Config:**
```
retrieval_mode  = "dense"
chunk_size      = ⚠️ ĐIỀN SAU (xem index.py của M2)
overlap         = ⚠️ ĐIỀN SAU
embedding_model = ⚠️ ĐIỀN SAU (OpenAI / MiniLM)
top_k_search    = 10
top_k_select    = 3
use_rerank      = False
llm_model       = ⚠️ ĐIỀN SAU (xem rag_answer.py của M4)
```

**Cách chấm điểm:**
- [ ] Chấm thủ công (đọc answer và chunks, chấm theo thang 1–5)
- [ ] LLM-as-Judge (M5 implement prompt chấm tự động)

**Scorecard Baseline:**

> ⚠️ **[Phụ thuộc runtime]** Điền sau khi chạy: `python eval.py`

| Metric | Average Score (1–5) | Số câu được chấm |
|--------|--------------------|-----------------|
| Faithfulness | \_\_\_ /5 | /10 |
| Answer Relevance | \_\_\_ /5 | /10 |
| Context Recall | \_\_\_ /5 | /10 |
| Completeness | \_\_\_ /5 | /10 |

**Per-question detail (điền sau khi chạy scorecard):**

| ID | Câu hỏi (tóm tắt) | F | AR | CR | C | Ghi chú |
|----|------------------|---|----|----|---|---------|
| q01 | | | | | | |
| q02 | | | | | | |
| q03 | | | | | | |
| q04 | | | | | | |
| q05 | | | | | | |
| q06 | | | | | | |
| q07 | | | | | | |
| q08 | | | | | | |
| q09 | | | | | | |
| q10 | | | | | | |

> `F` = Faithfulness | `AR` = Answer Relevance | `CR` = Context Recall | `C` = Completeness

**Câu hỏi yếu nhất (điểm thấp nhất):**
> ⚠️ ĐIỀN SAU — Ví dụ: "q07 (Approval Matrix) — context_recall = 1/5 vì dense bỏ lỡ alias tên phòng ban."

**Phân tích nguyên nhân (Error Tree):**

Sau khi xem baseline results, tick vào giả thuyết đúng:

- [ ] **Indexing:** Chunking cắt giữa điều khoản → mất ngữ cảnh
- [ ] **Indexing:** Metadata thiếu `effective_date` → retrieval lấy version cũ
- [ ] **Retrieval:** Dense bỏ lỡ exact keyword / alias / mã lỗi (ERR-xxx)
- [ ] **Retrieval:** Top-k quá ít → thiếu evidence cần thiết
- [ ] **Generation:** Prompt không đủ grounding → model thêm thông tin ngoài context
- [ ] **Generation:** Context quá dài → lost in the middle effect

**Giả thuyết ưu tiên kiểm tra ở Sprint 3:**
> ⚠️ ĐIỀN SAU — Ví dụ: "Chọn kiểm tra Retrieval (hybrid) vì q07, q09 đều dùng từ khóa kỹ thuật mà dense thường miss."

---

## Variant 1 (Sprint 3)

> ⚠️ **[Phụ thuộc M3]** Thông tin về variant do M3 (Hoàng Ngọc Anh) implement và quyết định.  
> Điền sau khi M3 xong Sprint 3.

**Ngày:** _(điền ngày chạy)_  
**Biến thay đổi duy nhất:** _(1 trong 3: hybrid / rerank / query transform)_  
**Người implement:** Hoàng Ngọc Anh (M3)

**Lý do chọn biến này (evidence từ baseline):**
> ⚠️ ĐIỀN SAU — Phải dựa trên số liệu từ baseline, ví dụ:  
> "Chọn hybrid vì q07 (alias query) và q09 (ERR-403 mã lỗi) đều thất bại với dense (context_recall = 1/5).  
> Corpus có cả ngôn ngữ tự nhiên (policy) lẫn mã lỗi kỹ thuật → BM25 giúp bắt exact keyword."

**Config thay đổi:**
```
# Biến thay đổi:
retrieval_mode = "⚠️ ĐIỀN SAU"   # hybrid / dense

# Các tham số GIỮ NGUYÊN như baseline (A/B Rule):
top_k_search   = 10
top_k_select   = 3
use_rerank     = ⚠️ ĐIỀN SAU     # True / False
# chunk_size, embedding_model, llm_model — KHÔNG thay đổi
```

**Scorecard Variant 1 — So sánh với Baseline:**

> ⚠️ ĐIỀN SAU — Sau khi chạy: `python eval.py` (phần variant đã được uncomment)

| Metric | Baseline | Variant 1 | Delta | Cải thiện? |
|--------|---------|-----------|-------|-----------|
| Faithfulness | \_/5 | \_/5 | +/- \_ | ✅/❌ |
| Answer Relevance | \_/5 | \_/5 | +/- \_ | ✅/❌ |
| Context Recall | \_/5 | \_/5 | +/- \_ | ✅/❌ |
| Completeness | \_/5 | \_/5 | +/- \_ | ✅/❌ |

**Per-question: Câu nào variant tốt hơn baseline?**

> ⚠️ ĐIỀN SAU — Ví dụ: "q07: baseline CR=1/5 → variant CR=4/5 (+3). Hybrid bắt được keyword 'P1 SLA penalty'."

| ID | Baseline (F/AR/CR/C) | Variant (F/AR/CR/C) | Variant tốt hơn? | Lý do |
|----|---------------------|--------------------|--------------------|-------|
| q01 | | | | |
| q02 | | | | |
| q03 | | | | |
| q04 | | | | |
| q05 | | | | |
| q06 | | | | |
| q07 | | | | |
| q08 | | | | |
| q09 | | | | |
| q10 | | | | |

**Câu nào variant KÉM HƠN baseline (nếu có)?**
> ⚠️ ĐIỀN SAU — Ví dụ: "q03 Faithfulness giảm: hybrid lấy thêm chunks ít liên quan → context block lớn hơn → model bị confuse."

**Kết luận:**
> ⚠️ ĐIỀN SAU — Variant 1 có tốt hơn baseline không?  
> Kết luận phải có: (1) bằng chứng số liệu, (2) câu hỏi cụ thể, (3) giải thích cơ chế.  
>  
> Ví dụ: "Variant hybrid cải thiện Context Recall từ X/5 → Y/5 (+Z), đặc biệt ở các câu có keyword kỹ thuật  
> (q07, q09). Faithfulness không thay đổi đáng kể (Δ = ±0.1), cho thấy việc tăng recall không làm  
> giảm chất lượng generation. → **Chọn variant hybrid** làm config chính cho grading run."

---

## Tóm tắt học được (Sprint 4)

> ⚠️ ĐIỀN SAU — Sau khi hoàn thành evaluation.  
> Trả lời 3 câu hỏi này giúp đạt "nhận xét sâu sắc" theo rubric SCORING.md

**1. Lỗi phổ biến nhất trong pipeline này là gì?**
> ⚠️ ĐIỀN SAU — Trả lời dựa trên scorecard thực tế.  
> Gợi ý format: "X% câu hỏi thất bại do [lỗi], biểu hiện qua [metric thấp] ở [câu cụ thể]."

**2. Biến nào có tác động lớn nhất tới chất lượng?**
> ⚠️ ĐIỀN SAU — So sánh delta của từng metric khi đổi variant.  
> Gợi ý: "Đổi từ dense → hybrid tạo ra delta lớn nhất ở Context Recall (+X), trong khi rerank chỉ ảnh hưởng Faithfulness (+Y nhỏ)."

**3. Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
> ⚠️ ĐIỀN SAU — Đề xuất cụ thể có evidence.  
> Gợi ý: "Thử Query Expansion cho q06 (multi-hop) vì câu này hỏi về 2 điều kiện từ 2 docs khác nhau — dense và hybrid đều miss."
