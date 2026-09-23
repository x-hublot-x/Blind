"""Windows Native OCR Engine Wrapper using Windows.Media.Ocr / WinRT."""

import asyncio
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt

try:
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.globalization import Language
    from winrt.windows.storage.streams import DataWriter
    from winrt.windows.graphics.imaging import SoftwareBitmap, BitmapPixelFormat
    HAS_WINRT_OCR = True
except ImportError:
    HAS_WINRT_OCR = False


def _has_cyrillic(text: str) -> bool:
    """Checks if text contains Cyrillic characters."""
    return any('\u0400' <= c <= '\u04FF' for c in text)


def recognize_text_from_pixmap(pixmap: QPixmap) -> str:
    """Recognizes text from a QPixmap using Windows Native OCR (Windows.Media.Ocr)."""
    if not HAS_WINRT_OCR or pixmap.isNull() or pixmap.width() < 5 or pixmap.height() < 5:
        return ""

    try:
        # Scale up very small clippings to improve OCR character recognition rate
        if pixmap.width() < 120 or pixmap.height() < 40:
            scale = 2.0
            working_pixmap = pixmap.scaled(
                int(pixmap.width() * scale),
                int(pixmap.height() * scale),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        else:
            working_pixmap = pixmap

        qimg = working_pixmap.toImage().convertToFormat(QImage.Format.Format_RGBA8888)
        raw_bytes = qimg.bits().asstring(qimg.sizeInBytes())
        w = qimg.width()
        h = qimg.height()

        async def _async_recognize() -> str:
            async def _run_lang(lang_tag: str) -> str:
                try:
                    lang = Language(lang_tag)
                    if not OcrEngine.is_language_supported(lang):
                        return ""
                    engine = OcrEngine.try_create_from_language(lang)
                    if not engine:
                        return ""
                    
                    writer = DataWriter()
                    writer.write_bytes(raw_bytes)
                    sb = SoftwareBitmap.create_copy_from_buffer(
                        writer.detach_buffer(),
                        BitmapPixelFormat.RGBA8,
                        w,
                        h
                    )
                    res = await engine.recognize_async(sb)
                    lines = [line.text.strip() for line in res.lines if line.text.strip()]
                    return "\n".join(lines)
                except Exception:
                    return ""

            # 1. Try Russian recognizer
            text_ru = await _run_lang("ru")
            if text_ru and _has_cyrillic(text_ru):
                return text_ru

            # 2. Try English recognizer
            text_en = await _run_lang("en-US")
            if text_en:
                return text_en

            # 3. Fallback to whatever Russian returned if any
            return text_ru

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(_async_recognize())
        finally:
            loop.close()

    except Exception as e:
        print(f"OCR Error: {e}")
        return ""
