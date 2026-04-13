# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Hoàng Ngọc Anh  
**Vai trò trong nhóm:** Retrieval Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100–150 từ)

Trong lab này, tôi chủ yếu phụ trách phần **retrieval**, tập trung vào cả Sprint 2 và Sprint 3. Ở Sprint 2, tôi implement pipeline retrieval cơ bản sử dụng dense search với ChromaDB, bao gồm việc embedding query, truy vấn vector store và xử lý kết quả trả về. Tôi đảm bảo mỗi chunk đều có metadata đầy đủ để phục vụ việc trích dẫn (citation) trong bước generation.

Sang Sprint 3, tôi mở rộng hệ thống bằng cách xây dựng hybrid retrieval kết hợp dense và BM25. Tôi áp dụng thuật toán Reciprocal Rank Fusion (RRF) để trộn kết quả từ hai nguồn nhằm cải thiện độ chính xác. Ngoài ra, tôi cũng thử nghiệm thêm bước rerank bằng LLM để chọn ra các chunk phù hợp nhất.

Phần retrieval của tôi đóng vai trò đầu vào cho phần generation, nên ảnh hưởng trực tiếp đến chất lượng câu trả lời cuối cùng của hệ thống.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100–150 từ)

Sau lab này, tôi hiểu rõ hơn về sự khác biệt giữa dense retrieval và sparse retrieval. Dense retrieval sử dụng embedding nên có khả năng hiểu ngữ nghĩa, phù hợp với các câu hỏi paraphrase hoặc không chứa keyword rõ ràng. Tuy nhiên, nó lại dễ bỏ sót các thông tin quan trọng nếu câu hỏi chứa các từ khóa đặc biệt như mã lỗi hoặc ký hiệu.

Ngược lại, sparse retrieval (BM25) hoạt động tốt với keyword matching nhưng không hiểu được ngữ cảnh sâu. Vì vậy, việc kết hợp hai phương pháp thành hybrid retrieval là cần thiết để tận dụng điểm mạnh của cả hai.

Ngoài ra, tôi cũng hiểu rõ hơn về grounded answer — tức là ép model trả lời dựa trên context đã retrieve. Điều này giúp giảm hiện tượng hallucination và tăng độ tin cậy của hệ thống RAG.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100–150 từ)

Điều khiến tôi bất ngờ là dense retrieval không hoạt động tốt như kỳ vọng trong mọi trường hợp. Ban đầu tôi nghĩ embedding có thể xử lý tốt hầu hết các truy vấn, nhưng thực tế với các câu hỏi chứa keyword cụ thể như “P1” hoặc “refund”, kết quả trả về lại không chính xác.

Khó khăn lớn nhất là khi triển khai hybrid retrieval, đặc biệt là phần kết hợp score giữa dense và sparse. Ban đầu tôi thử cộng trực tiếp score nhưng không hiệu quả, sau đó phải chuyển sang dùng RRF mới đạt được kết quả ổn định hơn.

Ngoài ra, việc rerank bằng LLM cũng gặp vấn đề về format output. Model đôi khi không trả về đúng định dạng ID, dẫn đến lỗi khi parse và buộc tôi phải thêm cơ chế fallback để đảm bảo hệ thống không bị crash.

---

## 4. Phân tích một câu hỏi trong scorecard (150–200 từ)

**Câu hỏi:** “SLA ticket P1 là bao lâu?”

**Phân tích:**

Ở baseline chỉ sử dụng dense retrieval, hệ thống trả lời chưa chính xác. Mặc dù có retrieve được các chunk liên quan đến SLA, nhưng lại không chọn đúng đoạn chứa thông tin cụ thể về P1. Điều này dẫn đến câu trả lời thiếu hoặc sai một phần, và điểm evaluation chỉ ở mức trung bình.

Vấn đề chính nằm ở bước retrieval, không phải generation. Model hoàn toàn có khả năng trả lời đúng nếu được cung cấp đúng context. Tuy nhiên, do retrieval không chính xác nên output bị ảnh hưởng.

Khi chuyển sang hybrid retrieval, kết quả được cải thiện rõ rệt. BM25 giúp bắt được keyword “P1”, từ đó đưa đúng chunk lên top. Khi kết hợp với dense thông qua RRF, hệ thống vừa giữ được ngữ nghĩa vừa đảm bảo độ chính xác của keyword.

Sau khi thêm bước rerank, chất lượng tiếp tục được cải thiện do loại bỏ được các chunk nhiễu. Điều này cho thấy pipeline dạng funnel (search rộng → rerank → select) hoạt động rất hiệu quả trong bài toán RAG.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50–100 từ)

Nếu có thêm thời gian, tôi muốn thử query transformation như HyDE hoặc query expansion để cải thiện khả năng retrieve với các câu hỏi paraphrase. Ngoài ra, tôi cũng muốn thay thế rerank bằng cross-encoder thực sự để giảm chi phí và tăng độ ổn định.

Lý do là kết quả evaluation cho thấy vẫn còn lỗi ở bước retrieval, đặc biệt với các câu hỏi không chứa keyword rõ ràng.

---