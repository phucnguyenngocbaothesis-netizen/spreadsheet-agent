from __future__ import annotations


class LanguageUtils:
    """
    Lightweight English/Vietnamese language detection.

    This is rule-based and does not use an LLM.
    """

    VIETNAMESE_MARKERS = [
        "mình",
        "cho",
        "giúp",
        "giải thích",
        "dữ liệu",
        "biểu đồ",
        "thiếu",
        "doanh thu",
        "khu vực",
        "theo",
        "cột",
        "hàng",
        "giá trị",
        "trùng",
        "lặp",
        "tóm tắt",
        "thống kê",
        "kế hoạch",
        "quy trình",
        "đơn giản",
        "chi tiết",
        "viết",
        "vẽ",
        "xem",
        "phân tích",
    ]

    @classmethod
    def detect_language(cls, text: str) -> str:
        text_lower = str(text).lower()

        if any(marker in text_lower for marker in cls.VIETNAMESE_MARKERS):
            return "vi"

        return "en"