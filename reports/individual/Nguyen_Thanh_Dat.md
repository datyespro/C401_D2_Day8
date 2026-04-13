# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Thành Đạt
**Vai trò trong nhóm:** Tech Lead  
**Ngày nộp:** 14/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Với vai trò Tech Lead, tôi chịu trách nhiệm chính ở Sprint 1 (khởi tạo cấu trúc) và tham gia rà soát luồng dữ liệu toàn tuyến. Cụ thể, tôi thiết lập file `.gitignore` để chặn rò rỉ `.env` và thư mục `chroma_db/`, đồng thời thiết kế `team_blueprint.md`. Để đảm bảo 6 thành viên làm việc song song không bị Git Conflict (Surgical Changes), tôi đã chuẩn hóa giao thức đầu vào/ra của các hàm thành chuẩn `List[Dict]`.
Ngoài ra, trong lúc debug hệ thống ở Sprint 4, tôi đã trực tiếp phân tích file `index.py` (cấu trúc chunking 512 tokens + regex metadata) và hỗ trợ M4 sửa lại hàm `build_grounded_prompt()` để vá lỗi mô hình bị quá an toàn (over-conservative) khi sinh câu trả lời, giúp điểm Completeness bật tăng từ 3.70 lên 3.90.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Khái niệm tôi thực sự "sáng mắt" ra sau Lab này là **Sự phân tách giữa Retrieval và Generation**. Ban đầu, tôi luôn nghĩ hễ mô hình trả lời sai hoặc bảo "Không biết" thì tự động là do Retrieval tìm kiếm dở.
Qua việc soi điểm `score_context_recall` bằng 5 (100% tài liệu được moi lên đầy đủ) mà điểm `Completeness` lại chỉ đạt 1, tôi hiểu sâu sắc rằng: Retriever xịn đến mấy cũng vô nghĩa nếu bộ Prompt của khâu Generation (Grounded Prompt) thiết lập các rule bảo vệ (Guardrails) quá ngặt nghèo. Việc làm chủ LLM không chỉ ở vector search mà còn ở nghệ thuật "mớm lời" — phân nhánh rõ ràng các trường hợp Abstain (từ chối) thực sự với việc phải tổng hợp luật chung nếu gặp các case dị biệt (như case khách VIP chưa được định nghĩa).

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều khiến tôi bất ngờ và mất thời gian debug nhất là **hiện tượng Evaluator (LLM-as-a-judge) chấm điểm oan**. Ở câu [Q09 - Lỗi ERR-403], dữ liệu thật sự không có trong DB. Mô hình AI của nhóm đã làm cực tốt và ngoan ngoãn khi trả lời đúng rule: *"Xin lỗi, không có dữ liệu"*. Thế nhưng judge lại phang điểm Relevance = 1 & Completeness = 1.
Chúng tôi bị loay hoay với giả thuyết là Retriever bị hỏng, nhưng sau khi đào sâu vào cơ chế chấm, tôi nhận ra lỗ hổng nằm ở chính System prompt của Evaluator. Do chưa cover edge-case "Câu trả lời đúng của bài toán này là việc mày phải từ chối trả lời", giám khảo LLM cứ khăng khăng ép phải có info thì mới cho điểm cao, tạo ra nghịch lý Faithfulness = 5 nhưng Relevance = 1.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** [Q10] "Nếu cần hoàn tiền khẩn cấp cho khách hàng VIP, quy trình có khác không?"

**Phân tích:**
- Ở cấu hình Baseline (Dense Search), hệ thống lấy được chính xác file `refund-v4.pdf` (Context Recall = 5). Tuy nhiên, model lại sinh ra câu: "Xin lỗi, dữ liệu hiện tại không đủ để trả lời", dẫn đến Relevance = 1 và Completeness = 1.
- Sang cấu hình Variant (Hybrid + Re-rank), điểm số vẫn không cải thiện.
- Lỗi nằm hoàn toàn ở khâu **Generation**. Bối cảnh (Context) có đầy đủ về quy trình hoàn tiền, nhưng vì không chứa đích danh từ khóa "VIP / khẩn cấp", model LLM đã bị rule `ABSTAIN` gốc kìm hãm, dẫn đến ảo tưởng là không có đủ dữ liệu.
- Cách fix: Thay vì nhét thêm thuật toán tìm kiếm, tôi quyết định chia Rule ABSTAIN trong prompt thành 2 nhánh: Nếu hoàn toàn không có data thì mới từ chối; còn nếu có policy thì phải sinh ra câu: *"Tài liệu không phân biệt thẻ VIP, quy trình chung vẫn là..."*. Kết quả: Model đã trả lời trơn tru, logic.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Tôi sẽ ưu tiên sửa lại prompt của Evaluator (`score_completeness` và `score_answer_relevance` trong `eval.py`). Tôi sẽ lập trình thêm một filter: "Nếu mảng `expected_sources` là một danh sách rỗng, và Expected Answer mang ý nghĩa từ chối, hãy Auto Pass và cho model 5/5 điểm tuyệt đối nếu nó nói 'Không đủ dữ liệu'". Kết quả benchmark scorecard hiện nay chưa công bằng 100% cho khả năng từ chối ảo giác (Abstain) của model do chưa fix lỗi này.
