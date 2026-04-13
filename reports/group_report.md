# Báo Cáo Kỹ Thuật Nhóm (Group Report) — Lab Day 08: RAG Pipeline

---

## 1. Kiến Trúc Tổng Quan (System Architecture)
Nhóm đã triển khai một hệ thống Retrieval-Augmented Generation (RAG) để hỗ trợ bộ phận Helpdesk IT và Customer Service, phục vụ mục đích tra cứu tự động các chính sách quy định (SLA, hoàn tiền, HR, bảo mật). Pipeline được duy trì bằng các quy trình rõ ràng: **Vector Indexing** linh hoạt, **Hybrid Retrieval**, **Grounded Generation** (sử dụng GPT-4o-mini), và một **Automated Evaluation Pipeline**.

Sự đóng góp của từng thành viên trong các Sprint (từ Indexing, Retrieval, Generation đến Evaluation) được đóng gói chặt chẽ, tạo thành một Baseline ổn định trước khi áp dụng thay đổi mới.

## 2. Các Quyết Định Kỹ Thuật Và Đánh Đổi (Trade-offs) Cấp Nhóm

### 2.1. Nâng cấp Retrieval: Từ Dense sang Hybrid + Reranker + Query Expansion
- **Khởi đầu (Baseline - Sprint 2):** Nhóm bắt đầu cấu hình cơ bản nhất bằng **Dense Retrieval** (mô hình `text-embedding-3-small` của OpenAI, Chunk Size 512, Overlap 100). Cách tiếp cận này giúp build nhanh và bắt được ngữ nghĩa cực tốt. Context Recall ngay từ ban đầu đã chạm ngưỡng tuyệt đối (5.0/5).
- **Phát sinh & Đánh đổi của nhóm (Variant - Sprint 3):** Mặc dù Dense tốt, nhưng nó có rủi ro đối với các truy vấn chứa từ khoá cứng hoặc các ID hệ thống đặc thù (như `ERR-403-AUTH`, `Ticket P1`). Nhóm thống nhất cải tổ Retriever thành **Hybrid Search** (Dense + KeywordBM25). Việc dùng Hybrid tuy nhặt được key cứng nhưng cũng kéo theo cả các văn bản gây nhiễu, do vậy phải đánh đổi tốn kém hơn bằng cách bật thêm Cross-Encoder **Reranker** để thiết lập lại trật tự Top K. Đi cùng kỹ thuật **Query Expansion**, nhóm phải hy sinh tốc độ truy xuất (latency tăng do call LLM từ expansion + Rerank model) để duy trì sự tối ưu về Answer Relevance ở mức trần.

### 2.2. Chiến lược Chống Ảo Giác Khắt Khe ở Khâu Generation
- **Bài toán Rủi ro:** Trong bối cảnh IT và Customer Service (hoàn tiền, phân quyền), việc hệ thống tự sáng tác ra thêm một quyền lợi không có thật cho khách hàng là tối kỵ.
- **Quyết định (Grounded Prompting):** Nhóm đồng thuận thiết kế Prompt để Generation hoạt động như một con robot "thành thật". Chúng tôi chủ động đưa vào Luật (Rule): Bắt mô hình từ chối khéo léo (Abstain) ngay lập tức nếu đoạn văn lấy từ Retrieve không đủ dữ kiện, thay vì cố gắng dùng kiến thức có sẵn từ Internet để chiều lòng User. Khả năng Abstain này đã cứu hệ thống khỏi câu hỏi gài (như vụ khôi phục mã lỗi ảo ERR-403).

### 2.3. Tư Duy Đánh Giá (Evaluation) và Nguyên Tắc A/B Rule
- **Đo lường bằng LLM (LLM-as-a-Judge):** Nhóm chọn thiết kế các thẻ điểm JSON tự động bằng Prompt (`score_faithfulness`, `score_relevance`, `score_completeness`) phục vụ quy trình đánh giá quy mô lớn trên Test Dataset, gạt bỏ yếu tố cảm tính và giảm tải sức người.
- **Kỷ luật A/B Testing:** Nhóm nhận ra việc thay đổi "lẩu thập cẩm" (đổi cả chunk, thẻ nhúng, hybrid lẫn prompt cùng lúc) sẽ khiến tiến độ dự án đi vào bế tắc bởi không biết hàm số tốt lên ở đâu. Nhóm quyết định tuân thủ tiêu chuẩn: **Chỉ biến thiên Một Yếu Tố** ở mỗi lượt Sprint để ghi lại Metric Delta thực chứng. Ví dụ, Scorecard xác nhận Variant 1 tăng độ Completeness (+0.2) và Relevance (+0.1) chính là nhờ vào bản vá cho Grounded Prompt cùng kỹ thuật Query Expansion, trong khi đó Faithfulness và Context Recall liên tục ổn định.

## 3. Tổng Kết và Bài Học Nhóm
Quyết định kiến trúc của pipeline này hướng tới việc tạo ra một cỗ máy **"Biết khi nào thì nên im lặng"**. Hệ thống ưu tiên sự chắt lọc và mức độ tin cậy tuyệt đối so với tài liệu nội bộ, bất kì truy vấn out-of-domain nào cũng sẽ được khoanh vùng. Trong tương lai, nhóm xác định cần hoàn thiện thêm ở bộ đo lường (Eval) để giám khảo AI không phạt lỗi nhầm những mô hình Generation đã thực hiện Abstain đúng luật.
