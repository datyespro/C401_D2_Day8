# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Hoàng Việt
**Vai trò trong nhóm:** Data & Indexing Owner
**Ngày nộp:** 13/04/2026 
**Độ dài yêu cầu:**

---

## 1. Tôi đã làm gì trong lab này?

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint nào bạn chủ yếu làm? Tôi chủ yếu làm ở Sprint 1, tập trung vào phần data preparation và indexing.
> - Cụ thể bạn implement hoặc quyết định điều gì? Tôi đã implement quá trình chunking tài liệu, tạo embedding cho các chunks, và xây dựng index sử dụng CHROMA DB để hỗ trợ retrieval.
> - Công việc của bạn kết nối với phần của người khác như thế nào? Công việc của tôi là nền tảng cho retrieval, giúp retrieval owner có dữ liệu đã được xử lý sẵn để triển khai các phương pháp retrieval khác nhau. 

---

## 2. Điều tôi hiểu rõ hơn sau lab này

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab. Ví dụ: chunking, grounded prompt, evaluation loop.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop. 
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide. Sau lab này, tôi hiểu rõ hơn về khái niệm chunking, tức là quá trình chia nhỏ tài liệu thành các phần nhỏ hơn để dễ dàng xử lý và tạo embedding. Tôi cũng hiểu về hybrid retrieval, kết hợp giữa dense retrieval (sử dụng embedding) và sparse retrieval (dựa trên keyword) để cải thiện hiệu suất tìm kiếm. Grounded prompt là kỹ thuật thiết kế prompt sao cho mô hình trả lời dựa trên thông tin đã được cung cấp, giúp tăng tính chính xác của câu trả lời. Cuối cùng, evaluation loop là quá trình liên tục đánh giá và cải thiện pipeline dựa trên kết quả thu được từ các câu hỏi kiểm tra.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

> Lỗi nào mất nhiều thời gian debug nhất? Tôi nhận ra kích thước chunk (chunk_size) ảnh hưởng cực lớn đến chất lượng embedding. Nếu để chunk quá nhỏ, model bị mất ngữ cảnh (context); nếu quá lớn, vector embedding bị "loãng", làm giảm độ chính xác khi truy vấn bằng ChromaDB.
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao? Ban đầu, tôi nghĩ rằng chunk nhỏ sẽ tốt hơn vì nó giúp model tập trung vào thông tin cụ thể. Tuy nhiên, thực tế cho thấy chunk quá nhỏ lại làm mất đi ngữ cảnh quan trọng, dẫn đến embedding kém chất lượng và kết quả retrieval không chính xác. Ngược lại, chunk lớn hơn giúp giữ được ngữ cảnh nhưng lại làm embedding bị loãng, cũng không tốt. Do đó, việc tìm ra kích thước chunk tối ưu là một thách thức lớn trong quá trình indexing.


---

## 4. Phân tích một câu hỏi trong scorecard

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** Sản phẩm kỹ thuật số có được hoàn tiền không?

**Phân tích:**

- Baseline trả lời sai và nhận điểm thấp. Lỗi nằm ở retrieval, khi hệ thống không tìm được thông tin chính xác về chính sách hoàn tiền cho sản phẩm kỹ thuật số trong tài liệu đã được index. Điều này có thể do việc chunking không hiệu quả, dẫn đến embedding không đủ tốt để truy vấn chính xác thông tin cần thiết.
---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

- Sử dụng hybrid retrieval: Tôi sẽ thử kết hợp giữa dense retrieval (sử dụng embedding) và sparse retrieval (dựa trên keyword) để cải thiện hiệu suất tìm kiếm. Kết quả eval cho thấy retrieval hiện tại không chính xác, có thể do embedding không đủ tốt, nên việc thêm sparse retrieval có thể giúp tăng khả năng tìm kiếm thông tin chính xác.
---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
