"""
index.py — Sprint 1: Build RAG Index
====================================
Mục tiêu Sprint 1 (60 phút):
  - Đọc và preprocess tài liệu từ data/docs/
  - Chunk tài liệu theo cấu trúc tự nhiên (heading/section)
  - Gắn metadata: source, section, department, effective_date, access
  - Embed và lưu vào vector store (ChromaDB)

Definition of Done Sprint 1:
  ✓ Script chạy được và index đủ docs
  ✓ Có ít nhất 3 metadata fields hữu ích cho retrieval
  ✓ Có thể kiểm tra chunk bằng list_chunks()
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CẤU HÌNH
# =============================================================================

DOCS_DIR = Path(__file__).parent / "data" / "docs"
CHROMA_DB_DIR = Path(__file__).parent / "chroma_db"

# TODO Sprint 1: Điều chỉnh chunk size và overlap theo quyết định của nhóm
# Gợi ý từ slide: chunk 300-500 tokens, overlap 50-80 tokens
CHUNK_SIZE = 512       # tokens (ước lượng bằng số ký tự / 4)
CHUNK_OVERLAP = 100     # tokens overlap giữa các chunk


# Lazy-loaded embedding backend để tránh load model nhiều lần
_EMBEDDING_PROVIDER = None
_OPENAI_CLIENT = None
_SENTENCE_MODEL = None
_EMBEDDING_MODEL_NAME = None


# =============================================================================
# STEP 1: PREPROCESS
# Làm sạch text trước khi chunk và embed
# =============================================================================

def preprocess_document(raw_text: str, filepath: str) -> Dict[str, Any]:
    """
    Preprocess một tài liệu: extract metadata từ header và làm sạch nội dung.

    Args:
        raw_text: Toàn bộ nội dung file text
        filepath: Đường dẫn file để làm source mặc định

    Returns:
        Dict chứa:
          - "text": nội dung đã clean
          - "metadata": dict với source, department, effective_date, access

    TODO Sprint 1:
    - Extract metadata từ dòng đầu file (Source, Department, Effective Date, Access)
    - Bỏ các dòng header metadata khỏi nội dung chính
    - Normalize khoảng trắng, xóa ký tự rác

    Gợi ý: dùng regex để parse dòng "Key: Value" ở đầu file.
    """
    lines = raw_text.strip().split("\n")
    metadata = {
        "source": filepath,
        "section": "",
        "department": "unknown",
        "effective_date": "unknown",
        "access": "internal",
    }
    content_lines = []
    header_done = False
    metadata_key_map = {
        "source": "source",
        "department": "department",
        "effective date": "effective_date",
        "access": "access",
    }

    for line in lines:
        stripped = line.strip()
        if not header_done:
            # Parse metadata dạng "Key: Value" trong phần header
            meta_match = re.match(r"^([A-Za-z ]+):\s*(.+)$", stripped)
            if meta_match:
                key = meta_match.group(1).strip().lower()
                value = meta_match.group(2).strip()
                if key in metadata_key_map:
                    metadata[metadata_key_map[key]] = value
                    continue

            if stripped.startswith("==="):
                # Gặp section heading đầu tiên → kết thúc header
                header_done = True
                content_lines.append(stripped)
            elif stripped == "" or stripped.isupper():
                # Dòng tên tài liệu (toàn chữ hoa) hoặc dòng trống
                continue
            else:
                # Giữ lại ghi chú có ích trước section đầu tiên (vd: alias tên cũ)
                content_lines.append(stripped)
        else:
            content_lines.append(line.rstrip())

    cleaned_text = "\n".join(content_lines)

    # Normalize khoảng trắng nhưng vẫn giữ cấu trúc đoạn văn
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)
    cleaned_text = re.sub(r"\n[ \t]+", "\n", cleaned_text)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)  # max 2 dòng trống liên tiếp
    cleaned_text = cleaned_text.strip()

    return {
        "text": cleaned_text,
        "metadata": metadata,
    }


# =============================================================================
# STEP 2: CHUNK
# Chia tài liệu thành các đoạn nhỏ theo cấu trúc tự nhiên
# =============================================================================

def chunk_document(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Chunk một tài liệu đã preprocess thành danh sách các chunk nhỏ.

    Args:
        doc: Dict với "text" và "metadata" (output của preprocess_document)

    Returns:
        List các Dict, mỗi dict là một chunk với:
          - "text": nội dung chunk
          - "metadata": metadata gốc + "section" của chunk đó

    TODO Sprint 1:
    1. Split theo heading "=== Section ... ===" hoặc "=== Phần ... ===" trước
    2. Nếu section quá dài (> CHUNK_SIZE * 4 ký tự), split tiếp theo paragraph
    3. Thêm overlap: lấy đoạn cuối của chunk trước vào đầu chunk tiếp theo
    4. Mỗi chunk PHẢI giữ metadata đầy đủ từ tài liệu gốc

    Gợi ý: Ưu tiên cắt tại ranh giới tự nhiên (section, paragraph)
    thay vì cắt theo token count cứng.
    """
    text = doc["text"]
    base_metadata = doc["metadata"].copy()
    chunks = []

    # TODO: Implement chunking theo section heading
    # Bước 1: Split theo heading pattern "=== ... ==="
    sections = re.split(r"(===.*?===)", text)

    current_section = "General"
    current_section_text = ""

    for part in sections:
        if re.match(r"===.*?===", part):
            # Lưu section trước (nếu có nội dung)
            if current_section_text.strip():
                section_chunks = _split_by_size(
                    current_section_text.strip(),
                    base_metadata=base_metadata,
                    section=current_section,
                )
                chunks.extend(section_chunks)
            # Bắt đầu section mới
            current_section = part.strip("= ").strip()
            current_section_text = ""
        else:
            current_section_text += part

    # Lưu section cuối cùng
    if current_section_text.strip():
        section_chunks = _split_by_size(
            current_section_text.strip(),
            base_metadata=base_metadata,
            section=current_section,
        )
        chunks.extend(section_chunks)

    return chunks


def _split_by_size(
    text: str,
    base_metadata: Dict,
    section: str,
    chunk_chars: int = CHUNK_SIZE * 4,
    overlap_chars: int = CHUNK_OVERLAP * 4,
) -> List[Dict[str, Any]]:
    """
    Helper: Split text dài thành chunks với overlap.

    TODO Sprint 1:
    Hiện tại dùng split đơn giản theo ký tự.
    Cải thiện: split theo paragraph (\n\n) trước, rồi mới ghép đến khi đủ size.
    """
    if len(text) <= chunk_chars:
        # Toàn bộ section vừa một chunk
        return [{
            "text": text,
            "metadata": {**base_metadata, "section": section},
        }]

    def _safe_overlap_tail(chunk_text: str) -> str:
        """Lấy tail overlap và cố gắng bắt đầu từ ranh giới từ/ngắt dòng."""
        if overlap_chars <= 0 or len(chunk_text) <= overlap_chars:
            return chunk_text
        tail = chunk_text[-overlap_chars:]
        cut_pos = 0
        for sep in ["\n", ". ", "; ", ": ", " "]:
            idx = tail.find(sep)
            if idx != -1:
                cut_pos = max(cut_pos, idx + len(sep))
        return tail[cut_pos:].strip() if cut_pos > 0 else tail.strip()

    def _split_long_paragraph(paragraph_text: str) -> List[str]:
        """Fallback khi 1 paragraph quá dài: cắt gần ranh giới tự nhiên."""
        parts = []
        start = 0
        length = len(paragraph_text)
        while start < length:
            end = min(start + chunk_chars, length)
            candidate = paragraph_text[start:end]

            if end < length:
                last_break = max(
                    candidate.rfind("\n"),
                    candidate.rfind(". "),
                    candidate.rfind("; "),
                    candidate.rfind(": "),
                    candidate.rfind(" "),
                )
                if last_break > int(chunk_chars * 0.6):
                    end = start + last_break + 1
                    candidate = paragraph_text[start:end]

            part = candidate.strip()
            if part:
                parts.append(part)

            if end >= length:
                break

            next_start = max(end - overlap_chars, start + 1)
            start = next_start

        return parts

    chunks_text = []
    current = ""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    for paragraph in paragraphs:
        # Paragraph rất dài thì cắt nhỏ trước
        if len(paragraph) > chunk_chars:
            split_parts = _split_long_paragraph(paragraph)
        else:
            split_parts = [paragraph]

        for part in split_parts:
            if not current:
                current = part
                continue

            candidate = f"{current}\n\n{part}"
            if len(candidate) <= chunk_chars:
                current = candidate
                continue

            chunks_text.append(current.strip())
            overlap_prefix = _safe_overlap_tail(current)
            current = f"{overlap_prefix}\n\n{part}".strip() if overlap_prefix else part

    if current.strip():
        chunks_text.append(current.strip())

    return [{
        "text": chunk_text,
        "metadata": {**base_metadata, "section": section},
    } for chunk_text in chunks_text]


# =============================================================================
# STEP 3: EMBED + STORE
# Embed các chunk và lưu vào ChromaDB
# =============================================================================

def get_embedding(text: str) -> List[float]:
    """
    Tạo embedding vector cho một đoạn text.

    TODO Sprint 1:
    Chọn một trong hai:

    Option A — OpenAI Embeddings (cần OPENAI_API_KEY):
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            input=text,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    Option B — Sentence Transformers (chạy local, không cần API key):
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        return model.encode(text).tolist()
    """
    global _EMBEDDING_PROVIDER, _OPENAI_CLIENT, _SENTENCE_MODEL, _EMBEDDING_MODEL_NAME

    text = (text or "").strip()
    if not text:
        text = "empty"

    if _EMBEDDING_PROVIDER is None:
        provider = os.getenv("EMBEDDING_PROVIDER", "local").strip().lower()
        openai_api_key = os.getenv("OPENAI_API_KEY")

        # Hỗ trợ alias provider từ .env
        if provider in {"sentence-transformers", "sentence_transformers", "st"}:
            provider = "local"
        if provider not in {"openai", "local", "auto"}:
            print(f"EMBEDDING_PROVIDER='{provider}' không hợp lệ. Dùng 'local' thay thế.")
            provider = "local"

        # auto: ưu tiên OpenAI nếu có API key, nếu không dùng local
        if provider == "auto":
            provider = "openai" if openai_api_key else "local"

        if provider == "openai":
            try:
                if not openai_api_key:
                    raise ValueError("Thiếu OPENAI_API_KEY")

                from openai import OpenAI

                _OPENAI_CLIENT = OpenAI(api_key=openai_api_key)
                _EMBEDDING_PROVIDER = "openai"
                _EMBEDDING_MODEL_NAME = (
                    os.getenv("OPENAI_EMBEDDING_MODEL")
                    or os.getenv("EMBEDDING_MODEL")
                    or "text-embedding-3-small"
                )
                print(f"Embedding backend: OpenAI ({_EMBEDDING_MODEL_NAME})")
            except Exception as e:
                print(f"Không thể khởi tạo OpenAI embeddings ({e}). Fallback sang local model.")

        if _EMBEDDING_PROVIDER is None:
            from sentence_transformers import SentenceTransformer

            _EMBEDDING_PROVIDER = "sentence_transformers"
            _EMBEDDING_MODEL_NAME = (
                os.getenv("LOCAL_EMBEDDING_MODEL")
                or os.getenv("EMBEDDING_MODEL")
                or "paraphrase-multilingual-MiniLM-L12-v2"
            )
            _SENTENCE_MODEL = SentenceTransformer(_EMBEDDING_MODEL_NAME)
            print(f"Embedding backend: SentenceTransformers ({_EMBEDDING_MODEL_NAME})")

    if _EMBEDDING_PROVIDER == "openai":
        response = _OPENAI_CLIENT.embeddings.create(
            input=text,
            model=_EMBEDDING_MODEL_NAME,
        )
        return response.data[0].embedding

    return _SENTENCE_MODEL.encode(text).tolist()


def build_index(docs_dir: Path = DOCS_DIR, db_dir: Path = CHROMA_DB_DIR) -> None:
    """
    Pipeline hoàn chỉnh: đọc docs → preprocess → chunk → embed → store.

    TODO Sprint 1:
    1. Cài thư viện: pip install chromadb
    2. Khởi tạo ChromaDB client và collection
    3. Với mỗi file trong docs_dir:
       a. Đọc nội dung
       b. Gọi preprocess_document()
       c. Gọi chunk_document()
       d. Với mỗi chunk: gọi get_embedding() và upsert vào ChromaDB
    4. In số lượng chunk đã index

    Gợi ý khởi tạo ChromaDB:
        import chromadb
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_or_create_collection(
            name="rag_lab",
            metadata={"hnsw:space": "cosine"}
        )
    """
    import chromadb

    print(f"Đang build index từ: {docs_dir}")
    db_dir.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(db_dir))
    collection = client.get_or_create_collection(
        name="rag_lab",
        metadata={"hnsw:space": "cosine"},
    )

    total_chunks = 0
    doc_files = list(docs_dir.glob("*.txt"))

    if not doc_files:
        print(f"Không tìm thấy file .txt trong {docs_dir}")
        return

    for filepath in doc_files:
        print(f"  Processing: {filepath.name}")
        raw_text = filepath.read_text(encoding="utf-8")

        doc = preprocess_document(raw_text, str(filepath))
        chunks = chunk_document(doc)

        for i, chunk in enumerate(chunks):
            chunk_id = f"{filepath.stem}_{i}"
            embedding = get_embedding(chunk["text"])

            chunk_metadata = chunk["metadata"].copy()
            chunk_metadata["chunk_index"] = i

            collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk["text"]],
                metadatas=[chunk_metadata],
            )

        print(f"    → {len(chunks)} chunks indexed")
        total_chunks += len(chunks)

    print(f"\nHoàn thành! Tổng số chunks: {total_chunks}")
    print(f"ChromaDB path: {db_dir}")
    print("Collection: rag_lab")


# =============================================================================
# STEP 4: INSPECT / KIỂM TRA
# Dùng để debug và kiểm tra chất lượng index
# =============================================================================

def list_chunks(db_dir: Path = CHROMA_DB_DIR, n: int = 5) -> None:
    """
    In ra n chunk đầu tiên trong ChromaDB để kiểm tra chất lượng index.

    TODO Sprint 1:
    Implement sau khi hoàn thành build_index().
    Kiểm tra:
    - Chunk có giữ đủ metadata không? (source, section, effective_date)
    - Chunk có bị cắt giữa điều khoản không?
    - Metadata effective_date có đúng không?
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results = collection.get(limit=n, include=["documents", "metadatas"])

        print(f"\n=== Top {n} chunks trong index ===\n")
        for i, (doc, meta) in enumerate(zip(results["documents"], results["metadatas"])):
            print(f"[Chunk {i+1}]")
            print(f"  Source: {meta.get('source', 'N/A')}")
            print(f"  Section: {meta.get('section', 'N/A')}")
            print(f"  Effective Date: {meta.get('effective_date', 'N/A')}")
            print(f"  Text preview: {doc[:120]}...")
            print()
    except Exception as e:
        print(f"Lỗi khi đọc index: {e}")
        print("Hãy chạy build_index() trước.")


def inspect_metadata_coverage(db_dir: Path = CHROMA_DB_DIR) -> None:
    """
    Kiểm tra phân phối metadata trong toàn bộ index.

    Checklist Sprint 1:
    - Mọi chunk đều có source?
    - Có bao nhiêu chunk từ mỗi department?
    - Chunk nào thiếu effective_date?

    TODO: Implement sau khi build_index() hoàn thành.
    """
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("rag_lab")
        results = collection.get(include=["metadatas"])

        print(f"\nTổng chunks: {len(results['metadatas'])}")

        # TODO: Phân tích metadata
        # Đếm theo department, kiểm tra effective_date missing, v.v.
        departments = {}
        missing_date = 0
        for meta in results["metadatas"]:
            dept = meta.get("department", "unknown")
            departments[dept] = departments.get(dept, 0) + 1
            if meta.get("effective_date") in ("unknown", "", None):
                missing_date += 1

        print("Phân bố theo department:")
        for dept, count in departments.items():
            print(f"  {dept}: {count} chunks")
        print(f"Chunks thiếu effective_date: {missing_date}")

    except Exception as e:
        print(f"Lỗi: {e}. Hãy chạy build_index() trước.")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 1: Build RAG Index")
    print("=" * 60)

    # Bước 1: Kiểm tra docs
    doc_files = list(DOCS_DIR.glob("*.txt"))
    print(f"\nTìm thấy {len(doc_files)} tài liệu:")
    for f in doc_files:
        print(f"  - {f.name}")

    # Bước 2: Test preprocess và chunking (không cần API key)
    print("\n--- Test preprocess + chunking ---")
    for filepath in doc_files[:1]:  # Test với 1 file đầu
        raw = filepath.read_text(encoding="utf-8")
        doc = preprocess_document(raw, str(filepath))
        chunks = chunk_document(doc)
        print(f"\nFile: {filepath.name}")
        print(f"  Metadata: {doc['metadata']}")
        print(f"  Số chunks: {len(chunks)}")
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n  [Chunk {i+1}] Section: {chunk['metadata']['section']}")
            print(f"  Text: {chunk['text'][:150]}...")

    # Bước 3: Build index đầy đủ
    print("\n--- Build Full Index ---")
    build_index()

    # Bước 4: Kiểm tra index
    list_chunks()
    inspect_metadata_coverage()

    print("\nSprint 1 setup hoàn thành!")
    print("Sprint 1 DoD check:")
    print("  1. Index đã được build cho toàn bộ docs")
    print("  2. Mỗi chunk có metadata: source, section, effective_date, ...")
    print("  3. Đã inspect nhanh chunks và coverage metadata")


    