import sys

def setup_terminal():
    """Hỗ trợ in tiếng Việt trên Windows terminal bằng cách cấu hình stdout sang utf-8."""
    # Chỉ thực hiện trên Windows
    if sys.platform == "win32" and sys.stdout.encoding != 'utf-8':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except AttributeError:
            # Fallback cho Python cũ hơn 3.7
            pass
