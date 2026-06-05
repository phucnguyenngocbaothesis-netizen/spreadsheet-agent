from core.language_utils import LanguageUtils


def test_language_utils_detects_vietnamese():
    language = LanguageUtils.detect_language("cho mình xem giá trị thiếu")

    assert language == "vi"


def test_language_utils_detects_english():
    language = LanguageUtils.detect_language("show missing values")

    assert language == "en"