import re
from pathlib import Path
from typing import Dict

class PromptLoader:
    """
    Trình quản lý Load Prompt.
    Sử dụng Cache (singleton) để tránh phải đọc lại file từ ổ cứng liên tục
    nếu load nhiều prompt trong một lần chạy chương trình.
    """
    _cache: Dict[str, Dict[str, str]] = {}

    @classmethod
    def load_all(cls, file_path: Path) -> Dict[str, str]:
        # Trả về ngay nếu file đã được đưa vào bộ nhớ
        if str(file_path) in cls._cache:
            return cls._cache[str(file_path)]
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Warning: Không tìm thấy file {file_path}")
            return {}

        prompts = {}
        # Đảm bảo có newline ở đầu (mẹo để regex phân tách block đều hoạt động cho line đầu)
        content = "\n" + content
        
        # Tách file dựa trên heading (ví dụ \n## FAITHFULNESS_PROMPT=)
        blocks = re.split(r'\n##\s+', content)
        
        for block in blocks:
            if not block.strip():
                continue
            
            # Dòng đầu tiên của text sau khi tách là Tên Heading
            # Phần Text còn lại phía dưới là thân Prompt
            lines = block.split('\n', 1)
            if len(lines) < 2:
                continue
                
            heading_line = lines[0].strip()
            prompt_text = lines[1].strip()
            
            # Xoá các kí tự thiết lập biến ở heading như "="
            heading_key = heading_line.replace("=", "").strip()
            
            # Cleanup phần văn bản
            # 1. Thường xuyên chèn """ """ ở markdown
            if prompt_text.startswith('"""') and prompt_text.endswith('"""'):
                prompt_text = prompt_text[3:-3].strip()
            # 2. Hoặc lỡ tay dùng format markdown code_block: ```text ... ```
            elif prompt_text.startswith('```') and prompt_text.endswith('```'):
                prompt_lines = prompt_text.split('\n')
                if len(prompt_lines) >= 2:
                    prompt_text = '\n'.join(prompt_lines[1:-1]).strip()
            
            prompts[heading_key] = prompt_text
            
        # Lưu vào cache để tối ưu hiệu năng
        cls._cache[str(file_path)] = prompts
        return prompts

def load_prompt_from_md(file_path: Path, heading: str) -> str:
    """
    Hàm tiện ích giúp load một prompt bằng tên gọi từ file markdown.
    
    Ví dụ:
        load_prompt_from_md(PROMPT_PATH, "FAITHFULNESS_PROMPT")
        load_prompt_from_md(PROMPT_PATH, "## ANSWER_RELEVANCE =")
    """
    # Làm sạch chuỗi đầu vào của người dùng chuẩn bị truy xuất
    clean_heading = heading.replace("##", "").replace("=", "").strip()
    
    prompts = PromptLoader.load_all(file_path)
    
    if clean_heading not in prompts:
        # Fallback thử tìm bằng text-contains trong trường hợp người gõ thừa thiếu ký tự
        for key, value in prompts.items():
            if clean_heading in key or key in clean_heading:
                return value
        raise ValueError(f"Không tìm thấy prompt '{clean_heading}' trong file {file_path.name}")
        
    return prompts[clean_heading]
