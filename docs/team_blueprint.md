# Kế Hoạch Làm Việc Nhóm & Ranh Giới Code (Team Blueprint)

**Quy tắc tối thượng (Surgical Changes):** Mỗi người CHỈ sửa code trong "Scope" của mình. Không tự ý format, xóa hoặc sửa đổi hàm của người khác.

---

## 1. M2: Data & Indexing Owner
**"Người tạo khung lưu trữ Vector và chia nhỏ văn bản"**

- **File phụ trách:** Duy nhất file `index.py`
- **Scope làm việc:** Từ dòng 40 đến lệnh `build_index()` (khoảng dòng 318).
- **Các hàm cấm xâm phạm:** `list_chunks()`, và `inspect_metadata_coverage()` (thuộc về QA/Test).
- **Viết code vào các hàm sau:**
  1. `preprocess_document`: Tách siêu dữ liệu Metadata (Source, Department) bằng regex và clean khoảng trắng.
  2. `chunk_document` & `_split_by_size`: Chia cắt theo các thẻ `===` thay vì đếm token mù quáng để tránh gãy chữ.
  3. `get_embedding` & `build_index`: Code logic gọi API `text-embedding-3-small` hoặc `SentenceTransformer` và nối với `chromadb`.

---

## 2. M3: Retrieval & Search Owner
**"Người lục lọi tài liệu bằng toán học"**

- **File phụ trách:** Nửa trên của file `rag_answer.py`
- **Scope làm việc:** Từ dòng 40 đến dòng 230.
- **Viết code vào các hàm sau:**
  1. `retrieve_dense`: (Giai đoạn đầu) Query thẳng vào ChromaDB bằng Embedding đầu vào.
  2. `retrieve_sparse`: Dùng thử rank-bm25 (Keyword matching).
  3. *Tuning (Sprint 3):* Triển khai hàm `retrieve_hybrid` (kết hợp Dense + Sparse bằng RRF) hoặc hàm `rerank` (Dùng thư viện Cross-encoder).
- **Giao diện chốt với Gen Owner:** Các hàm này có trả về bất cứ gì đi chăng nữa, thì Output bắt buộc phải là một mảng Dictionary `List[Dict]`!

---

## 3. M4: LLM Generation & Prompting
**"Người chế tác Prompt và quản lý Bot trả lời"**

- **File phụ trách:** Nửa dưới của file `rag_answer.py`
- **Scope làm việc:** Từ dòng 235 đến 421.
- **Viết code vào các hàm sau:**
  1. `build_context_block`: Nhận `List[Dict]` từ M3, xử lý thành 1 cục String bọc bởi các trích dẫn `[1]`, `[2]`.
  2. `build_grounded_prompt`: Thiết kế kỹ nghệ Prompt để AI không ảo giác. Đảm bảo 4 quy tắc: Evidence-only, Abstain, Citation, Short/clear.
  3. `call_llm`: Dùng `OpenAI` client hoặc `Gemini` client để sinh câu trả lời, trả về 1 chuỗi string duy nhất.
  4. `rag_answer`: Nối toàn bộ pipeline lại với nhau ở đây để trả về Dict hoàn chỉnh.

---

## 4. M5: Test Data & Evaluation Engineer
**"Người cố gắng đập vỡ hệ thống bằng góc nhìn User"**

- **File phụ trách:** `data/test_questions.json` và nửa đầu `eval.py`
- **Scope làm việc:** `eval.py` từ dòng 55 đến dòng 206.
- **Viết code vào các phần sau:**
  1. Thiết kế JSON: Nghĩ ra các case hiểm (hỏi ngoài vùng dữ liệu, gõ mã lỗi) theo các docs ở `data/docs/`.
  2. Các hàm chấm điểm: `score_faithfulness`, `score_answer_relevance`, `score_context_recall`, `score_completeness`. Triển khai chấm thủ công hoặc dùng `LLM-as-a-judge` (viết thêm code Prompt để AI tự chấm điểm).

---

## 5. M6: Report & Architecture Documentation
**"Người tổng hợp chiến dịch và phân tích số liệu A/B"**

- **File phụ trách:** Nửa dưới `eval.py` và toàn bộ thư mục `docs/`.
- **Scope làm việc:** `eval.py` từ dòng 210 xuống tận cùng.
- **Tính năng cần phát triển:**
  1. Chạy các hàm `run_scorecard` để lấy Score cuối cùng.
  2. Phân tích qua `compare_ab()`: Đánh giá Data chênh lệch giữa `baseline` và `variant`.
  3. Xây dựng tài liệu: Vẽ kiến trúc vào `docs/architecture.md` và ghi nhận xét sâu sắc (để có điểm cao) vào `docs/tuning-log.md`.
