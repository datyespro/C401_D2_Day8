# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Anh Đức  
**Vai trò trong nhóm:** M6 — Report & Architecture Documentation Owner  
**Ngày nộp:** 13/04/2026

---

## 1. Tôi đã làm gì trong lab này?

Trong lab này, tôi phụ trách phần tài liệu kỹ thuật và luồng đánh giá cuối pipeline. Ở `eval.py`, tôi thêm `generate_grading_log()` để chạy `grading_questions.json`, ghi `logs/grading_run.json` đúng format trong `SCORING.md`, và bọc `try/except` theo từng câu để một query lỗi không làm hỏng cả batch. Tôi cũng bật luồng chạy variant scorecard và `compare_ab()` để repo xuất đủ `results/scorecard_baseline.md`, `results/scorecard_variant.md` và `results/ab_comparison.csv`.

Ở phần docs, tôi cập nhật `docs/architecture.md` và `docs/tuning-log.md` dựa trên code thật, scorecard và grading log. Vai trò của tôi là giữ cho phần “giải thích hệ thống” khớp với repo thực tế, không mô tả theo template cũ.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

Điều tôi hiểu rõ nhất sau lab là RAG không chỉ là “retrieve đúng rồi generate đúng”. Một pipeline có thể lấy đúng nguồn nhưng vẫn trả lời chưa tốt. Scorecard của nhóm cho thấy điều đó rõ: baseline đạt **Faithfulness 4.70/5** và **Context Recall 5.00/5**, nhưng **Completeness chỉ 3.70/5**. Nghĩa là hệ thống thường có đúng tài liệu trong tay, nhưng câu trả lời vẫn thiếu ý hoặc chốt vấn đề chưa đủ sắc.

Tôi cũng hiểu sâu hơn ý nghĩa của A/B rule. Khi ghép công việc của cả nhóm, repo rất dễ rơi vào trạng thái đổi cùng lúc `retrieval_mode` và `use_rerank`. Nếu không ghi tuning log trung thực, team sẽ khó biết delta đến từ biến nào. Với tôi, documentation không chỉ là “viết lại những gì nhóm đã làm”, mà là lớp kiểm chứng giúp nhóm nhìn đúng bottleneck.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

Điều làm tôi bất ngờ nhất là bottleneck của public test set không nằm ở retrieval như tôi dự đoán ban đầu. Tôi từng nghĩ dense search sẽ hụt vì corpus có alias và exact term, nhưng scorecard lại cho thấy **Context Recall đã bão hòa 5.00/5** trên 9 câu có expected source. Các câu yếu nhất (`q07`, `q09`, `q10`) chủ yếu hỏng ở generation: alias chưa rõ, abstain còn quá ngắn, hoặc special-case chưa chốt verdict ngay câu đầu.

Khó khăn thứ hai là phần eval/documentation phải luôn bám đúng sự thật của repo. Variant hiện tại hữu ích cho grading run, nhưng nó không phải A/B một biến thuần vì đổi đồng thời hybrid và rerank. Là Documentation Owner, tôi phải ghi rõ cả điểm mạnh lẫn hạn chế này thay vì viết theo hướng “nghe hay”.

Ngoài ra thì do không đọc kỹ nên tôi nghĩ rằng 2 file là architecture.md và tuning-log.md cũng là báo cáo, nên gần sát giờ tôi chưa làm xong, nên các bạn trong nhóm làm phụ, tuy nhiên các bạn sửa thì đã bị sai 1 số chỗ, giờ thì tôi đã sửa lại mặc dù có thể là đã quá thời gian

---

## 4. Phân tích một câu hỏi trong grading

Tôi chọn `gq07`: **“Công ty sẽ phạt bao nhiêu nếu team IT vi phạm cam kết SLA P1?”** Đây là câu rất quan trọng vì `SCORING.md` coi hallucination ở nhóm câu này là lỗi nặng.

Trong `logs/grading_run.json`, pipeline trả lời: **“Xin lỗi, dữ liệu hiện tại không đủ để trả lời câu hỏi này.”** Nguồn retrieve được vẫn là `support/sla-p1-2026.pdf`, số chunk dùng là `3`, và `retrieval_mode` là `hybrid`.

Theo Error Tree, tôi đánh giá:

- **Indexing: không lỗi.** Tài liệu SLA đã được index đúng, có version history và các section về P1.
- **Retrieval: không lỗi.** Pipeline đã kéo về đúng tài liệu liên quan nhất cho câu hỏi.
- **Generation: đúng hành vi mong muốn.** Trong tài liệu SLA không có điều khoản nào nói về “mức phạt” khi vi phạm cam kết, nên prompt evidence-only + abstain đã ngăn model bịa ra con số.

Điểm hay của câu này là nó cho thấy một pipeline RAG tốt không phải lúc nào cũng “trả lời đầy đủ”, mà phải biết dừng đúng chỗ khi tài liệu không có dữ kiện. Nếu model tự suy luận kiểu “phạt 10%” hay “theo hợp đồng chuẩn”, nhóm sẽ bị trừ nặng vì hallucination. Nếu có thêm thời gian, tôi sẽ tinh chỉnh prompt để câu abstain mạnh hơn, ví dụ: **“Tài liệu hiện hành không nêu mức phạt khi vi phạm SLA P1”** thay vì chỉ nói chung chung là thiếu dữ liệu.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Tôi sẽ ưu tiên hai việc. Thứ nhất, sửa prompt/answer template cho ba pattern đang kéo điểm xuống: alias tài liệu (`q07`), insufficient-context (`q09`), và special-case (`q10`). Đây là chỗ có evidence rõ nhất vì baseline chỉ đạt **Completeness 3.70/5** và variant cũng mới lên **3.80/5**.

Thứ hai, tôi sẽ tách lại thí nghiệm thành `hybrid-only`, `dense + rerank`, và `hybrid + rerank`. Hiện tại variant có cải thiện nhẹ, nhưng vì đổi hai biến cùng lúc nên chưa thể kết luận phần nào thực sự tạo ra delta. Với vai trò phụ trách docs/eval, tôi nghĩ đây là bước cần thiết nhất để team vừa báo cáo trung thực, vừa tối ưu có cơ sở hơn.
