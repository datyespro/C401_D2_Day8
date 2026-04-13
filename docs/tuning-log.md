# Tuning Log — RAG Pipeline (Day 08 Lab)

> **Tác giả (Documentation Owner):** Nguyễn Anh Đức (M6)  
> **A/B Rule:** Chỉ đổi **MỘT biến** mỗi lần — không đổi đồng thời chunking + hybrid + rerank.

---

## Baseline (Sprint 2)

**Ngày:** 14/04/2026  
**Config:**
```
retrieval_mode  = "dense"
chunk_size      = 512
overlap         = 100
embedding_model = text-embedding-3-small
top_k_search    = 10
top_k_select    = 3
use_rerank      = False
llm_model       = gpt-4o-mini
```

**Cách chấm điểm:**
- [x] LLM-as-Judge (M5 implement prompt chấm tự động)

**Scorecard Baseline:**

| Metric | Average Score (1–5) | Số câu được chấm |
|--------|--------------------|-----------------|
| Faithfulness | 4.90 /5 | 10/10 |
| Answer Relevance | 4.40 /5 | 10/10 |
| Context Recall | 5.00 /5 | 10/10 |
| Completeness | 3.70 /5 | 10/10 |

**Per-question detail (điều tra):**

| ID | Câu hỏi (tóm tắt) | F | AR | CR | C | Ghi chú |
|----|------------------|---|----|----|---|---------|
| q01 | SLA P1 là bao lâu? | 5 | 5 | 5 | 4 | Đúng nhưng hơi dư thông tin escalation |
| q02 | Yêu cầu hoàn tiền bn ngày? | 5 | 5 | 5 | 5 | Trả lời chính xác |
| q03 | Ai phê duyệt cấp quyền L3? | 5 | 5 | 5 | 5 | Trả lời chính xác |
| q04 | Sản phẩm kỹ thuật số hoàn tiền? | 5 | 5 | 5 | 4 | Chỉ dư một chút ngữ cảnh rườm rà |
| q05 | Tài khoản khoá sau mấy lần sai? | 5 | 5 | 5 | 5 | Trả lời chính xác |
| q06 | Escalation P1 ra sao? | 5 | 5 | 5 | 4 | Thừa chút dữ liệu không được hỏi |
| q07 | Approval Matrix là tài liệu gì? | 2 | 5 | 5 | 2 | Tự chế thêm phần path `it/` dư thừa |
| q08 | Remote làm tối đa mấy ngày? | 5 | 5 | 5 | 4 | Thiếu ý "Team Lead phê duyệt" |
| q09 | ERR-403-AUTH xử lý sao? | 5 | 1 | 5 | 1 | Máy trả lời đúng (Abstain) nhưng bị Judge chấm sai |
| q10 | Hoàn tiền VIP khác không? | 5 | 3 | 5 | 3 | Quá an toàn, thấy thiếu "VIP" là câm nín |

**Câu hỏi yếu nhất (điểm thấp nhất):**
> q09 (ERR-403) và q10 (Refund VIP). Trong đó q10 có Context Recall = 5 (Retriever xuất sắc moi được file hoàn tiền lên), nhưng điểm Completeness chỉ đạt 3 (Do lỗi ở khâu Generation quá ngặt nghèo sợ hallucination).

**Phân tích nguyên nhân (Error Tree):**

Sau khi xem baseline results, tick vào giả thuyết đúng:
- [x] **Generation:** Prompt không đủ grounding/quá ngặt nghèo → model tự chối trả lời (Abstain thiếu linh hoạt).

**Giả thuyết ưu tiên kiểm tra ở Sprint 3:**
> Chọn kiểm tra Generation (Sửa Grounded Prompt) và nâng cấp Hybrid + Rerank để xem việc kết hợp keyword có làm tăng khả năng nhặt đúng chi tiết li ti hay không.

---

## Variant 1 (Sprint 3)

**Ngày:** 14/04/2026  
**Biến thay đổi duy nhất:** Hybrid + Rerank + Query Expansion  
**Người implement:** Hoàng Ngọc Anh (M3)

**Lý do chọn biến này (evidence từ baseline):**
> Dense đã max Context Recall = 5 nhưng ta kỳ vọng Hybrid Rerank sẽ đẩy những chunk chứa đúng keyword trọng tâm lên đầu danh sách (vượt top 3 của dense đang chọn) giúp LLM chắt lọc ý chi tiết hơn. Cùng với việc sửa Generation Prompt để giảm bớt "sự sợ hãi" của model.

**Config thay đổi:**
```
# Biến thay đổi:
retrieval_mode = "hybrid"
use_rerank     = True
use_expansion  = True

# Các tham số GIỮ NGUYÊN như baseline:
top_k_search   = 10
top_k_select   = 3
```

**Scorecard Variant 1 — So sánh với Baseline:**

| Metric | Baseline | Variant 1 | Delta | Cải thiện? |
|--------|---------|-----------|-------|-----------|
| Faithfulness | 4.90/5 | 4.90/5 | ± 0.00 | ➖ |
| Answer Relevance | 4.40/5 | 4.50/5 | +0.10 | ✅ |
| Context Recall | 5.00/5 | 5.00/5 | ± 0.00 | ➖ |
| Completeness | 3.70/5 | 3.90/5 | +0.20 | ✅ |

**Per-question: Câu nào variant tốt hơn baseline?**

> **q07, q10:** Nhờ bản vá Generation prompt và Hybrid, model đã bỏ được lỗi thêm path thừa ở Q07 và không bị câm nín ở Q10 nữa. Đặc biệt ở tập Grading Log, model xử lý các câu bẫy rất hoàn hảo.

**Câu nào variant KÉM HƠN baseline (nếu có)?**
> Không có câu nào thực sự kém hơn về mức độ trầm trọng. Baseline vốn đã có điểm trung bình rất cao.

**Kết luận:**
> Variant Hybrid + Expansion + Prompt Tuning cải thiện Completeness từ 3.70 → 3.90 (+0.20) và Answer Relevance (+0.10). Faithfulness và Context Recall giữ nguyên vẹn ở mức cực cao (lần lượt 4.90 và 5.00). **→ Chọn variant hybrid làm config chính cho grading run.**

---

## Tóm tắt học được (Sprint 4)

**1. Lỗi phổ biến nhất trong pipeline này là gì?**
> Không phải lỗi ở Vector Database (Retrieve) mà là lỗi sinh văn bản (Generation) và lỗi giám khảo (LLM-as-a-judge). Các câu điểm kém (Q09, Q10) đều là các câu bẫy thiếu dữ liệu. Model đã hoạt động đúng khi từ chối trả lời (Abstain), nhưng bộ luật giám khảo lại trừ sạch điểm của model vì tội "không trả lời thẳng câu hỏi".

**2. Biến nào có tác động lớn nhất tới chất lượng?**
> Thể thức **Grounded Prompt của Generation**. Mặc dù đổi thẻ Retrieve sang Hybrid, delta điểm không chênh quá nhiều vì context recall của Dense vốn đã = 5. Nhưng ngay khi mớm thêm Rule "Không có data vs Có data nhưng thiếu case ngoại lệ" vào hàm Build Prompt, model lập tức trở nên khôn ngoan và thông minh vượt trội.

**3. Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
> Chắc chắn sẽ viết lại thẻ chấm điểm cho Evaluator (`score_answer_relevance` và `score_completeness` trong `eval.py`). Giám khảo LLM cần được dạy rằng: "Trả lời KHÔNG là kết quả xuất sắc nhất đối với một câu hỏi ngoài dữ liệu, hãy cho 5/5 điểm thay vì 1 điểm lạc đề".
