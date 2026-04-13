# Tuning Log — RAG Pipeline (Day 08 Lab)

> **Tác giả (Documentation Owner):** Nguyễn Anh Đức (M6)
> **A/B Rule chuẩn:** Chỉ đổi **một biến** mỗi lần.
> **Lưu ý run thực tế:** variant trong repo hiện tại đổi **hai biến cùng lúc** (`dense -> hybrid` và `use_rerank: False -> True`), nên phần kết luận dưới đây được ghi theo trạng thái chạy thật và có nêu rõ hạn chế.

---
 
## Baseline (Sprint 2)

**Ngày:** 14/04/2026  
**Config:**

```text
retrieval_mode  = "dense"
chunk_size      = 512
overlap         = 100
embedding_model = "text-embedding-3-small"
top_k_search    = 10
top_k_select    = 3
use_rerank      = False
llm_model       = "gpt-4o-mini"
```

**Cách chấm điểm:**

- [ ] Chấm thủ công
- [x] LLM-as-Judge qua các prompt trong `prompt/prompt.md`

**Scorecard Baseline:**

| Metric | Average Score (1–5) | Số câu được chấm |
|--------|--------------------:|-----------------:|
| Faithfulness | 4.70 / 5 | 10 / 10 |
| Answer Relevance | 4.40 / 5 | 10 / 10 |
| Context Recall | 5.00 / 5 | 9 / 10 |
| Completeness | 3.70 / 5 | 10 / 10 |

**Per-question detail:**

| ID | Câu hỏi (tóm tắt) | F | AR | CR | C | Ghi chú |
|----|-------------------|---:|---:|---:|---:|---------|
| q01 | SLA ticket P1 | 5 | 5 | 5 | 4 | Trả đúng, nhưng thêm chi tiết escalation/stakeholder ngoài expected answer |
| q02 | Số ngày được yêu cầu hoàn tiền | 5 | 5 | 5 | 5 | Ổn định, đúng trọng tâm |
| q03 | Phê duyệt Level 3 | 5 | 5 | 5 | 5 | Retrieve và tổng hợp đúng |
| q04 | Digital product có được refund không | 5 | 5 | 5 | 4 | Đúng ngoại lệ, nhưng diễn đạt chưa gọn bằng expected answer |
| q05 | Số lần login sai trước khi khóa | 5 | 5 | 5 | 5 | Đúng hoàn toàn |
| q06 | Escalation của P1 | 5 | 5 | 5 | 4 | Đúng trigger 10 phút nhưng lan sang full workflow |
| q07 | "Approval Matrix" là tài liệu nào | 2 | 5 | 5 | 2 | Retrieve đúng doc nhưng answer không nói rõ alias tên cũ → tên mới |
| q08 | Remote tối đa mấy ngày/tuần | 5 | 5 | 5 | 4 | Thiếu điều kiện Team Lead phê duyệt |
| q09 | ERR-403-AUTH | 5 | 1 | N/A | 1 | Abstain đúng, nhưng không cho guidance liên hệ IT như expected answer |
| q10 | Refund khẩn cấp cho VIP | 5 | 3 | 5 | 3 | Nêu quy trình chung nhưng chưa chốt rõ "không có flow VIP riêng" |

> `F` = Faithfulness | `AR` = Answer Relevance | `CR` = Context Recall | `C` = Completeness

**Câu hỏi yếu nhất:**

`q09` là câu thấp nhất toàn bộ scorecard vì đây là case "insufficient context": pipeline abstain đúng nên faithfulness vẫn cao, nhưng relevance/completeness thấp do expected answer muốn thêm guidance an toàn. Nếu chỉ xét các câu có tài liệu nguồn trong corpus, `q07` là câu yếu nhất vì lỗi nằm ở khâu diễn giải alias tên tài liệu, không phải retrieval.

**Phân tích nguyên nhân (Error Tree):**

- [ ] **Indexing:** Chunking cắt giữa điều khoản → mất ngữ cảnh
- [ ] **Indexing:** Metadata thiếu `effective_date` → retrieval lấy version cũ
- [ ] **Retrieval:** Dense bỏ lỡ exact keyword / alias / mã lỗi trên public set
- [ ] **Retrieval:** Top-k quá ít → thiếu evidence cần thiết
- [x] **Generation:** Prompt/answer format chưa xử lý tốt alias, special case, helpful abstain
- [x] **Generation:** Context có lúc dài hơn nhu cầu thật → câu trả lời lan sang chi tiết phụ

**Giả thuyết ưu tiên kiểm tra ở Sprint 3:**

Nếu chỉ nhìn public set, bottleneck lớn nhất là generation chứ không phải retrieval. Tuy nhiên để hoàn thành Sprint 3 và chuẩn bị cho hidden/grading questions có khả năng chứa alias, keyword kỹ thuật và truy vấn đa tài liệu, nhóm vẫn thử một variant retrieval-side là `hybrid + rerank`.

---

## Variant 1 (Sprint 3)

**Ngày chạy:** 14/04/2026  
**Biến thay đổi thực tế:** `retrieval_mode: dense -> hybrid` và `use_rerank: False -> True`  
**Người implement:** Hoàng Ngọc Anh (M3)

**Lý do chọn variant này:**

- Corpus có cả văn bản tự nhiên lẫn exact term như `P1`, `Level 3`, `VPN`, `store credit`.
- Có alias/tên cũ của tài liệu: `"Approval Matrix for System Access"` trong `access_control_sop.txt`.
- Hidden/grading questions thực tế có nhiều câu đa nguồn hoặc nhiều điều kiện ghép, ví dụ VPN + remote, temporary access trong incident P1, password expiry + reset.

Nói ngắn gọn: public set chưa cho thấy retrieval đang fail, nhưng hidden set có khả năng cao làm lộ nhóm lỗi này nên variant được chọn theo hướng "an toàn cho grading".

**Config thay đổi:**

```text
retrieval_mode = "hybrid"
top_k_search   = 10
top_k_select   = 3
use_rerank     = True

# Giữ nguyên:
chunk_size      = 512
overlap         = 100
embedding_model = "text-embedding-3-small"
llm_model       = "gpt-4o-mini"
```

**Scorecard Variant 1 — So sánh với Baseline:**

| Metric | Baseline | Variant 1 | Delta | Cải thiện? |
|--------|---------:|----------:|------:|-----------|
| Faithfulness | 4.70 / 5 | 4.70 / 5 | 0.00 | ❌ |
| Answer Relevance | 4.40 / 5 | 4.50 / 5 | +0.10 | ✅ |
| Context Recall | 5.00 / 5 | 5.00 / 5 | 0.00 | ➖ |
| Completeness | 3.70 / 5 | 3.80 / 5 | +0.10 | ✅ |

**Per-question: câu nào variant tốt hơn baseline?**

| ID | Baseline (F/AR/CR/C) | Variant (F/AR/CR/C) | Kết quả | Lý do |
|----|----------------------|---------------------|---------|-------|
| q01 | 5/5/5/4 | 5/5/5/5 | Tốt hơn | Variant trả gọn hơn, bao đủ hai ý chính: 15 phút và 4 giờ |
| q02 | 5/5/5/5 | 5/5/5/5 | Hòa | Không khác biệt đáng kể |
| q03 | 5/5/5/5 | 5/5/5/5 | Hòa | Retrieve và answer đều ổn định |
| q04 | 5/5/5/4 | 5/5/5/4 | Hòa | Vẫn đúng nhưng còn thêm chi tiết phụ |
| q05 | 5/5/5/5 | 5/5/5/5 | Hòa | Không khác biệt |
| q06 | 5/5/5/4 | 5/5/5/4 | Hòa | Trước đấy variant kéo thêm procedural details nên judge giảm faithfulness, đã fix lại |
| q07 | 2/5/5/2 | 2/5/5/2 | Hòa | Hybrid không sửa được lỗi alias; vấn đề nằm ở generation |
| q08 | 5/5/5/4 | 5/5/5/4 | Hòa | Vẫn thiếu điều kiện Team Lead phê duyệt |
| q09 |5/1/None/1 |5/1/None/1 | Hòa | Vẫn abstain quá ngắn, thiếu next-step guidance |
| q10 | 5/3/5/3 | 5/4/5/3 | Tốt hơn | Câu mở đầu bám sát ý "không có quy trình VIP riêng" hơn baseline |

**Câu nào variant kém hơn baseline?**

Trước đó: `q06` là ví dụ rõ nhất. Retrieval vẫn đúng source, nhưng hybrid + rerank đưa vào context thêm chi tiết vận hành incident nên câu trả lời dài hơn mức cần thiết. Judge coi đó là bớt "focused" và giảm faithfulness từ `5` xuống `4`.

**Kết luận:**

Variant `hybrid + rerank` **không tạo ra bước nhảy lớn** trên public scorecard:

- Relevance tăng nhẹ `+0.10`
- Completeness tăng nhẹ `+0.10`
- Context Recall không đổi
- Faithfulness giảm nhẹ `-0.10`

Điều này cho thấy public set không còn là retrieval problem rõ rệt; recall đã bão hòa từ baseline. Tuy vậy, variant vẫn hữu ích ở góc độ vận hành vì hidden/grading questions có xu hướng nhiều keyword và multi-source hơn public set. Do run hiện tại đổi 2 biến cùng lúc, chưa thể kết luận phần cải thiện đến từ hybrid hay từ rerank.

**Quyết định thực dụng cho repo hiện tại:** giữ `hybrid` làm retrieval mode cho grading run, nhưng ở vòng tối ưu tiếp theo cần tách lại thí nghiệm:

1. `dense + rerank`
2. `hybrid` không rerank
3. `hybrid + rerank`

Khi đó mới đo được biến nào thật sự có ích.

---

## Tóm tắt học được (Sprint 4)

**1. Lỗi phổ biến nhất trong pipeline này là gì?**

Lỗi phổ biến nhất không phải "không retrieve ra đúng tài liệu" mà là **answer synthesis chưa đủ sắc**. Ở baseline có **7/10 câu** chưa đạt `Completeness = 5`, nổi bật là `q07`, `q09`, `q10`. Các lỗi lặp lại là:

- không nêu rõ alias tên cũ ↔ tên mới,
- abstain đúng nhưng chưa đưa ra hướng xử lý an toàn,
- trả lời special-case chưa chốt verdict ngay dòng đầu.

**2. Biến nào có tác động lớn nhất tới chất lượng?**

Trên public set, không có biến retrieval nào tạo delta lớn. Variant `hybrid + rerank` chỉ cải thiện `Answer Relevance` và `Completeness` mỗi metric `+0.10`, trong khi `Context Recall` giữ nguyên `5.00/5`. Vì vậy, nếu ưu tiên tăng điểm nhanh ở vòng tiếp theo, tác động lớn nhất nhiều khả năng đến từ **prompting/answer formatting**, không phải mở rộng retrieval thêm nữa.

**3. Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**

Ba việc nên làm tiếp theo:

1. Tách thí nghiệm `hybrid-only` và `rerank-only` để tuân thủ A/B rule.
2. Sửa prompt cho 3 pattern đang lỗi:
   - câu hỏi alias tài liệu phải trả cả tên cũ và tên mới,
   - câu hỏi ngoài phạm vi phải abstain kèm next-step an toàn,
   - câu hỏi special-case phải kết luận verdict ở câu đầu rồi mới nêu policy chung.
3. Ràng buộc output theo template ngắn hơn để giảm tình trạng answer đưa quá nhiều chi tiết phụ như ở `q06` và `q10`.
