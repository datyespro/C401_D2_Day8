# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đậu Văn Quyền  
**Vai trò trong nhóm:** M4 — Generation & Prompting Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài:** ~650 từ

---

## 1. Tôi đã làm gì trong lab này?

Trong lab này, tôi đảm nhận vai trò **M4 — Generation & Prompting Owner**, chịu trách nhiệm chuyển hóa các dữ liệu thô từ tầng Retrieval thành câu trả lời có giá trị, an toàn và tin cậy cho người dùng. Các đóng góp cụ thể của tôi bao gồm:

**Thiết kế và Triển khai Logic Generation:**
Tôi đã xây dựng hàm `build_context_block` để đóng gói các đoạn văn bản (chunks) được tìm thấy. Thay vì chỉ đưa văn bản thô, tôi đã tích hợp thêm các Metadata quan trọng như *Department*, *Effective Date* và *Source* vào block ngữ cảnh. Điều này giúp LLM có căn cứ chính xác để thực hiện việc trích dẫn nguồn (citation) theo đúng yêu cầu.

**Kỹ thuật Prompt Engineering chống ảo giác:**
Tôi đã dành nhiều thời gian để tinh chỉnh `build_grounded_prompt`. Tôi đã thiết kế một System Prompt nghiêm ngặt với 5 quy tắc bắt buộc:
1. **Evidence-only**: Tuyệt đối không dùng kiến thức bên ngoài.
2. **Abstain**: Nếu không có dữ liệu, phải từ chối trả lời thay vì bịa chuyện.
3. **Citation**: Bắt buộc trích dẫn nguồn theo định dạng `[1], [2]`.
4. **Bullets**: Trình bày danh sách để tối ưu trải nghiệm người dùng.
5. **Language Matching**: Trả lời đúng ngôn ngữ của câu hỏi.

**Xử lý môi trường và Tư duy Kiến trúc (Refactor):**
Trong quá trình làm việc, tôi phát hiện lỗi `UnicodeEncodeError` trên hệ thống Windows khiến việc in tiếng Việt bị crash. Tôi đã chủ động triển khai mã xử lý encoding. Đặc biệt, để tránh xung đột code (Merge Conflict) khi làm việc nhóm trên Git, tôi đã đề xuất và thực hiện việc refactor đoạn mã này vào một utility chung (`utils/terminal.py`), giúp cả đội có thể sử dụng mà không làm ảnh hưởng đến logic riêng của từng thành viên.

---

## 2. Điều tôi hiểu rõ hơn sau lab này

**Sức mạnh của RAG so với LLM thuần túy:**
Trước đây tôi nghĩ Prompt Engineering chỉ là viết câu lệnh hay. Sau lab này, tôi hiểu rằng trong RAG, chất lượng của "Groundedness" (tính bám sát thực tế) phụ thuộc 50% vào cách chúng ta cấu trúc Context đưa vào và 50% vào các ràng buộc (constraints) trong prompt. 

**Cơ chế ABSTAIN (Từ chối):**
Tôi nhận ra rằng việc AI nói "Tôi không biết" đôi khi còn giá trị hơn một câu trả lời trôi chảy nhưng sai sự thật. Trong môi trường doanh nghiệp (CS & IT Helpdesk), tính chính xác là tuyệt đối. Việc thiết kế prompt để AI tự kiểm tra sự tương quan giữa Query và Context là kỹ thuật quan chủ chốt để xây dựng niềm tin cho người dùng.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn

**Sự thành công từ một "thất bại" giả định:**
Một điều thú vị là khi tôi chạy thử nghiệm lần đầu với dữ liệu mẫu (Sample data) nghèo nàn, hệ thống liên tục trả về *"Xin lỗi, dữ liệu hiện tại không đủ..."*. Ban đầu tôi lo lắng có lỗi code, nhưng sau khi phân tích, tôi nhận ra đó là một **thắng lợi về logic**. Prompt của tôi đã hoạt động quá chuẩn xác: AI thấy context không có thông tin thật nên nó đã tuân thủ tuyệt đối quy tắc `ABSTAIN` thay vì cố gắng bịa ra các con số.

**Thách thức về Encoding trên Windows:**
Việc xử lý tiếng Việt trên Command Prompt của Windows khó khăn hơn dự kiến. Nó đòi hỏi phải can thiệp vào `sys.stdout` ngay từ đầu script. Việc này dạy cho tôi bài học về việc xây dựng ứng dụng phải tính đến tính đa hình của môi trường (Cross-platform support).

---

## 4. Phân tích một câu hỏi trong grading

**Câu hỏi được chọn:** ERR-403-AUTH là lỗi gì?

**Phân tích theo kết quả thực tế:**
*   **Kết quả:** *"Xin lỗi, dữ liệu hiện tại không đủ để trả lời câu hỏi này."*
*   **Đỉnh điểm của sự chính xác:** Khi kiểm tra file tài liệu `it_helpdesk_faq.txt`, thực tế không có mã lỗi này. Đây là một "câu hỏi bẫy" trong bộ test của lab.
*   **Lỗi nằm ở đâu?**: Không có lỗi.
    *   **Retrieval**: Hoàn thành nhiệm vụ khi mang về các chunk liên quan đến bảo mật nhưng không chứa mã lỗi này.
    *   **Generation (M4)**: Thực hiện xuất sắc nhiệm vụ lọc thông tin. Dù có 10 chunks được nạp vào, nhưng vì không có bằng chứng trực tiếp, logic của tôi đã ngăn AI "suy luận lung tung" về mã lỗi 403.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì?

Nếu có thêm thời gian, tôi sẽ tập trung vào hai hướng cải tiến:
1.  **Iterative Prompt Tuning**: Thay vì một prompt cố định, tôi sẽ thử nghiệm kỹ thuật **Chain-of-Thought (CoT)**: Yêu cầu AI tự liệt kê các sự thật tìm thấy trong context trước khi đưa ra câu trả lời cuối cùng để tăng thêm độ chính xác cho các câu hỏi phức tạp.
2.  **Cấu trúc hóa nguồn trích dẫn**: Thay vì chỉ để `Sources: [it/access-control-sop.md]`, tôi sẽ biến chúng thành các hyperlink hoặc trích dẫn kèm theo tên Section cụ thể (ví dụ: *"Xem thêm tại Section 3 của tài liệu..."*) để người dùng dễ dàng tra cứu lại.

---
