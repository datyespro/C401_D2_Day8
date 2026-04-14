# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** Nhóm 1 (RAG Masters)
**Thành viên:**

| Tên | Vai trò | Email |
| :--- | :--- | :--- |
| Nguyễn Thanh Đạt | Tech Lead | nickgearupbooster@gmail.com |
| Hoàng Ngọc Anh | Retrieval Owner | hoanganh24704@gmail.com |
| Vũ Duy Linh | Eval Owner | vuduylinh150804@gmail.com |
| Nguyễn Anh Đức | Documentation Owner | nguyenanhduc2909@gmail.com |
| Đậu Văn Quyền | Generation & Prompting Owner | quyendvpa00242@gmail.com |
| Nguyễn Hoàng Việt | Data & Indexing Owner | nguyenhoangviet23022004@gmail.com |

**Ngày nộp:** 14/04/2026
**Repo:** https://github.com/datyespro/C401_D2_Day8
**Độ dài khuyến nghị:** 600–900 từ

---

**1. Pipeline nhóm đã xây dựng (150–200 từ)**

**Mô tả ngắn gọn pipeline của nhóm:**
Nhóm xây dựng RAG Pipeline phục vụ bộ phận IT Helpdesk và CS nhằm tra cứu chính sách tự động.
- Chunking strategy: chunk_size=512, overlap=100.
- Embedding model đã dùng: `text-embedding-3-small`.
- Retrieval mode: hybrid + rerank (Sprint 3 variant).

**Chunking decision:**
Nhóm dùng `chunk_size=512`, `overlap=100` tĩnh (fixed-size). Do tài liệu phần lớn là quy định có đoạn văn ngắn gọn, kích thước này đặc biệt phù hợp để nhấc trọn vẹn 1 ý hoàn chỉnh mà không đưa thêm bối cảnh nhiễu, cân bằng tối đa khi nạp `top_k=3` chunk vào prompt window mà không bị trôi luồng suy luận của LLM.

**Embedding model:**
Sử dụng `text-embedding-3-small` vì có sự cân bằng lý tưởng về hiệu năng truy xuất ngữ nghĩa (semantic search) trên tập tài liệu công nghệ (IT policy) đi kèm độ trễ call API cực thấp.

**Retrieval variant (Sprint 3):**
Nhóm chọn variant `hybrid + rerank`. Dù public set không có lỗi về recall bằng dense, nhưng việc cắm thêm keyword matching BM25 bảo vệ hệ thống trước các query "key cứng" (ví dụ: `ERR-403-AUTH`, `Level 3`). Reranker (Cross-Encoder) theo sau có nhiệm vụ lọc sạch độ nhiễu loạn của kết quả Hybrid để duy trì top 3 sạch nhất.

---

**2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)**

**Quyết định:** Nâng cấp cấu trúc Retrieval từ Dense Search sang Hybrid Search kèm Reranker để chạy tập Eval ẩn ở chặng cuối.

**Bối cảnh vấn đề:**
Ngay từ Baseline, Dense Search đã kéo Context Recall lên kịch khung 5.0/5. Tuy nhiên qua bài test lắt léo về alias (q07: _Approval Matrix_), nhóm dự tính Grading Questions sẽ ném vào rất nhiều các ID mã vụ việc hoặc chữ viết tắt không có tương quan ngữ nghĩa mạnh, tiềm ẩn rủi ro phá vỡ trật tự trả về của hệ thống Dense.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
| :--- | :--- | :--- |
| Cố định nguyên bản Dense search | Giữ luồng thí nghiệm lý tưởng theo A/B Rule đơn thức. Tốc độ search siêu tốc. | Rủi ro điểm mù hoàn toàn trước các "Exact Keyword" độc hại ở hidden set. |
| Chuyển biến thành Hybrid + Reranker | Mạng lưới vớt tài liệu siêu rộng, kết quả gom top 3 sắc nét như có con người xếp hạng. | Tiêu tốn nặng API Rerank latency. Đặc biệt **vi phạm tiêu chuẩn A/B rule** vì thay đổi quá 1 biến tại cùng thời điểm. |

**Phương án đã chọn và lý do:**
Bất chấp vi phạm đổi 2 biến cùng lúc, nhóm chọn "Hybrid + Reranker". Lý do thực dụng: sự bao quát keyword chính xác của BM25 và độ nét của bộ máy xếp hạng chéo Cross-Encoder là vũ khí cần thiết nhất để lấy điểm tuyệt đối khi đối diện bộ câu Grading (tập trung rất nhiều tên riêng, multi-source và special case).

**Bằng chứng từ scorecard/tuning-log:**
Kết quả A/B Test tại `docs/tuning-log.md` đã trực quan hoá Completeness nhích từ Baseline (3.70/5) lên Variant (3.80/5) dù Recall không đổi. Reranker đã góp mặt đẩy đúng chứng cứ quý giá để mớm cho LLM dễ tiêu hóa nhất. 

---

**3. Kết quả grading questions (100–150 từ)**

**Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):**

**Ước tính điểm raw:** 94 / 98 

**Câu tốt nhất:** ID: `gq06` — Lý do: Cấp quyền trong sự cố P1 lúc 2h sáng. Đây làm câu hỏi gài multi-source phức tạp. Hệ thống xử lý hoàn hảo vì kết nối thành công điều khoản thu hồi tự động trong "24 giờ" và kết hợp chính xác người duyệt "Tech Lead" từ 2 chunk của 2 tài liệu khác nhau. 

**Câu fail/kém nhất:** ID: `gq03` — Root cause: Lỗi đến từ **Generation**. Retrieval tìm đúng tài liệu hoàn tiền, quy chuẩn đúng, nhưng mô hình LLM lại copy y nguyên toàn bộ block ngoại lệ trả vào answer thay vì chốt Verdict một cách ngắn gọn, súc tích (ảnh hưởng tới độ Relevant do "trả lời dài dòng").

**Câu gq07 (abstain):** Công ty sẽ phạt bao nhiêu nếu team IT vi phạm cam kết SLA P1? — Pipeline xử lý mẫu mực. Câu trả lời trả về: *"Xin lỗi, dữ liệu hiện tại không đủ để trả lời câu hỏi này."*. Hệ thống phòng ảo giác (Grounded Generation) hoạt động tuyệt vời.

---

**4. A/B Comparison — Baseline vs Variant (150–200 từ)**

**Dựa vào docs/tuning-log.md. Tóm tắt kết quả A/B thực tế của nhóm.**

**Biến đã thay đổi (chỉ 1 biến):** Retrieval Mode (Thực tế nhóm đã mắc lỗi đổi 2 biến `Dense -> Hybrid` + `Bật Rerank=True`). Nhóm ghi nhận khuyết điểm thiết kế thực nghiệm này tuy nhiên vẫn đối chiếu cụ thể:

| Metric | Baseline | Variant | Delta |
| :--- | :--- | :--- | :--- |
| Faithfulness | 4.70 / 5 | 4.70 / 5 | 0.00 |
| Answer Relevance | 4.40 / 5 | 4.50 / 5 | +0.10 |
| Context Recall | 5.00 / 5 | 5.00 / 5 | 0.00 |
| Completeness | 3.70 / 5 | 3.80 / 5 | +0.10 |

**Kết luận:**
**Variant tốt hơn một cách biên tế**. Completeness và Answer Relevance nhích lên chứng tỏ các chunk mang hàm lượng thông tin lõi đã được đẩy thẳng thắn vào top đầu của Content Window. Mặc dù Faithfulness và Recall vẫn dậm chân nhưng tổng thể Variant bám sát trọng tâm người dùng hơn so với Baseline.

---

**5. Phân công và đánh giá nhóm (100–150 từ)**

**Phân công thực tế:**

| Thành viên | Phần đã làm | Sprint |
| :--- | :--- | :--- |
| Nguyễn Thanh Đạt | Chỉ đạo kiến trúc Baseline và định chuẩn quy trình Git | 1 |
| Nguyễn Hoàng Việt | Indexing data, chuẩn hoá thư viện Text Loader | 1 |
| Hoàng Ngọc Anh | Thiết lập Hybrid Search kèm Reranking Model | 3 |
| Đậu Văn Quyền | Xây dựng lõi Generation, System Prompt design chống Hallucination | 2, 3 |
| Vũ Duy Linh | Lên kịch bản Automated Eval, LLM API call tính thẻ điểm | 4 |
| Nguyễn Anh Đức | Giám sát Scorecard Logs, Soạn Báo Cáo Kỹ Thuật | 1-4 |

**Điều nhóm làm tốt:**
Thiết lập bộ cánh Automation Evaluation cực kì sớm thông qua API LLM. Tính kỷ luật được đặt lên khi liên tục nhìn vào "Error Tree" từ thẻ điểm của `eval.py` phục vụ công tác tinh chỉnh generation rule.

**Điều nhóm làm chưa tốt:**
Quá nóng vội trong Sprint 3 (Sửa chằng chịt các biến Retrieval) dẫn tới việc vi phạm cấu trúc A/B nguyên thuỷ.

---

**6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)**

1. **Tuân thủ kỷ luật A/B Rule:** Ánh xạ lại thành 2 nhánh chạy riêng lẻ một cho `Hybrid` (không rerank) và một cho `Dense + Rerank` để truy vết 100% bằng chứng số hoá xem độ nhích Completeness của Variant là hiệu năng đến từ mô hình Cross-encoder Reranker hay thuật toán BM25.
2. **Khắc chế lỗi Alias Prompt:** Câu `q07` chỉ rõ nhược điểm nhận diện ngữ cảnh tên gọi cũ/mới của System prompt. Nhóm sẽ tiếp tục cấy luật Explicit Mapping hoặc thêm few-shots vào Generate Module.
