# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Vũ Duy Linh 
**Vai trò trong nhóm:** Eval Owner
**Ngày nộp:** 13/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Trong lab này, tôi đảm nhận vai trò Eval Owner và chủ yếu tập trung thực hiện công việc ở **Sprint 4: Evaluation & Scorecard**. Cụ thể, tôi đã đóng góp:
- Xây dựng và hoàn thiện hệ thống đo lường (Eval Pipeline) cho 4 metrics cốt lõi: Faithfulness, Answer Relevance, Context Recall và Completeness.
- Áp dụng phương pháp LLM-as-a-Judge, tôi đã trực tiếp viết và tinh chỉnh các prompt cho giám khảo đánh giá trong file cấu hình.
- Lập trình hàm logic dùng Python để đánh giá Context Recall dựa trên việc đối chiếu tên tài liệu mong muốn so với danh sách metadata của chunk trả về.
- Xây dựng phần A/B Comparison để xuất báo cáo so sánh Baseline và Variant.

Công việc của tôi kết nối trực tiếp với Sprint 2 & Sprint 3 do các thành viên khác phụ trách bằng cách nhận đầu ra (generation outputs, retrieved chunks) từ hệ thống của họ để chấm điểm, từ đó cung cấp dữ liệu định lượng cho nhóm quyết định sẽ tune config như thế nào.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Tôi thấu hiểu sâu sắc hơn về **Evaluation loop** và nguyên tắc **A/B Rule**:
- **Evaluation Loop và A/B Rule:** Trước đây tôi hay có thói quen thay đổi nhiều tham số cùng lúc (vừa thêm Hybrid, vừa bật Reranker, vừa sửa lại Prompt) để hi vọng kết quả tốt hơn. Sau bài lab này, tôi đã hiểu tại sao chúng ta chỉ nên đổi MỘT biến duy nhất mỗi lần. Việc tuân thủ điều này trong thiết lập Baseline và Variant 1 giúp chúng ta chỉ đích danh đâu mới thực sự là yếu tố dẫn đến sự cải thiện (ở bài lab này là Grounded Prompt).
- **Phân tách điểm số đánh giá:** Tôi hiểu rõ hơn sự khác biệt giữa 2 khâu đánh giá. Context Recall dành riêng cho khâu Retrieval (đánh giá xem văn bản cần tìm có được lôi lên đủ không). Trong khi đó, Faithfulness và Completeness lại đánh giá khâu Generation, giúp tránh tình trạng "tài liệu tìm đúng nhưng mô hình sinh câu trả lời bịa đặt hoặc thiếu sót".

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Việc áp dụng **LLM-as-a-Judge** khiến tôi gặp không ít khó khăn và bất ngờ:
- **Khó khăn lớn nhất:** Việc tinh chỉnh Eval Prompts cho LLM chấm điểm thực sự nhạy cảm. Thường xuyên gặp tình trạng mô hình xuất chuỗi JSON không đúng format đã yêu cầu hoặc lý do chấm điểm đưa ra không nhất quán. Việc phải sử dụng chế độ `response_format={ "type": "json_object" }` của OpenAI API chính là chìa khoá gỡ rối.
- **Sự ngạc nhiên:** Giám khảo LLM chấm cực kỳ khắt khe một cách... máy móc. Lỗi làm tôi bất ngờ nhất là ở câu Q09 và Q10, dù pipeline gốc (system prompt) ép mô hình máy học từ chối trả lời (Abstain) đúng yêu cầu vì thiếu Context từ Retriever. Tuy model làm rất đúng, nhưng vị giám khảo GPT của Evaluator lại cho Answer Relevance và Completeness bằng 1 (lạc đề) chỉ vì nó không thấy nội dung "dạy cách giải quyết lỗi".

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** Q09 - "ERR-403-AUTH là lỗi gì và cách xử lý?" (Câu hỏi bẫy - Insufficient Context)

**Phân tích:**
- Mức độ trả lời ở Baseline: Mô hình trả lời rất cẩn thận, an toàn và đúng bản chất: "Xin lỗi, dữ liệu hiện tại không đủ để trả lời câu hỏi này."
- Tại sao bị điểm thấp lại Baseline: Model được Context Recall = N/A (vì không có nguồn), Faithfulness = 5 (vì không bịa đặt), nhưng Answer Relevance và Completeness chỉ được 1 điểm! Lỗi không nằm ở RAG Pipeline (bởi Retrieval rỗng và Generation đã ngoan ngoãn từ chối trả lời). Lỗi nằm hoàn toàn ở **khâu thiết lập tiêu chuẩn của Giám khảo LLM (Evaluation Prompt)**.
- Variant có cải thiện không?: Tại cấu hình Variant dùng Hybrid + Reranker, Context Retrieve dĩ nhiên vẫn không quét được mẩu data nào. Mô hình vẫn tiếp tục "Abstain" xuất sắc. Tuy nhiên, điểm chấm do Evaluator vẫn lặp lại hệt Baseline: R=1, C=1. 
- Qua đó tôi nhận ra Variant không thay đổi được kết quả khi điểm số bị ảnh hưởng bởi chính thước đo (người chấm) lỗi.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, mục tiêu hàng đầu của tôi là cải tiến hệ thống Eval Prompts (LLM-as-a-Judge) đối với các metric Relevance và Completeness. 

Cụ thể, tôi sẽ thử bổ sung luật cứng trực tiếp vào Prompt chấm điểm: "Nếu mẫu `expected_answer` mang tính chất abstain hoặc model trả lời từ chối do bị thiếu context, tuyệt đối cho 5/5 điểm thay vì 1/5." Điều này sẽ khắc phục tình trạng kết quả eval hiện nay cho thấy các câu hỏi nằm ngoài data (như Q09) đang bị giám khảo AI phạt vô cớ dù mô hình RAG hoạt động chuẩn xác 100%.

---

*Lưu file này với tên: `reports/individual/Vu_Duy_Linh.md`*
