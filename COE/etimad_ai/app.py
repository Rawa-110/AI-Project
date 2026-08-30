import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


# ==========================================
# CONFIG
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR.parent / ".env"

load_dotenv(ENV_FILE)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY غير موجود في D:\\COE\\.env"
    )

client = genai.Client(api_key=API_KEY)


# ==========================================
# PDF
# ==========================================

def extract_pdf_text(pdf_path):
    """
    استخراج النص من ملف PDF.
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"لم يتم العثور على الملف: {path}"
        )

    if path.suffix.lower() != ".pdf":
        raise ValueError(
            "النسخة الحالية تدعم PDF فقط."
        )

    reader = PdfReader(str(path))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                f"\n--- الصفحة {page_number} ---\n{text}"
            )

    return "\n".join(pages)


# ==========================================
# AI ANALYSIS
# ==========================================

def analyze_rfp(text):
    """
    إرسال نص الكراسة إلى Gemini
    وتحليل المتطلبات الأساسية.
    """

    if not text.strip():
        raise ValueError(
            "لم يتم استخراج أي نص من ملف PDF."
        )

    prompt = f"""
أنت Etimad AI، مساعد متخصص في تحليل كراسات
الشروط والمنافسات الحكومية.

حلل الكراسة التالية فقط بناءً على المعلومات
الموجودة في النص.

أخرج النتيجة بهذا التنظيم:

1. ملخص المشروع
2. نطاق العمل
3. الموعد النهائي إن وجد
4. الضمانات المطلوبة
5. الشروط والمتطلبات الرئيسية
6. المستندات والشهادات المطلوبة
7. معايير التقييم إن وجدت
8. المخاطر والتنبيهات
9. نقاط تحتاج إلى مراجعة بشرية
10. قائمة مختصرة بأهم الأشياء التي يجب على
    الشركة تجهيزها قبل التقديم

قواعد مهمة:
- لا تخترع معلومات غير موجودة.
- إذا لم تجد معلومة، اكتب: "غير مذكور في الكراسة".
- حافظ على الأرقام والتواريخ كما وردت.
- لا تقدم استشارة قانونية.
- لا تفترض أن الشركة مؤهلة للمنافسة.
- الهدف هو استخراج المعلومات من الكراسة
  ومساعدة فريق العروض على مراجعتها.

نص الكراسة:

{text}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# MAIN
# ==========================================

def main():

    print("=" * 60)
    print("                 Etimad AI MVP")
    print("=" * 60)

    print()
    print("النسخة الحالية: PDF Analysis Engine")
    print()

    pdf_path = input(
        "أدخل مسار ملف PDF: "
    ).strip().strip('"')

    try:

        print()
        print("جاري قراءة الكراسة...")

        text = extract_pdf_text(pdf_path)

        print(
            f"تم استخراج النص بنجاح "
            f"({len(text):,} حرف)."
        )

        print()
        print("جاري تحليل الكراسة بواسطة Gemini...")
        print()

        result = analyze_rfp(text)

        print("=" * 60)
        print("                 نتيجة التحليل")
        print("=" * 60)

        print()
        print(result)
        print()

    except Exception as error:

        print()
        print("=" * 60)
        print("حدث خطأ")
        print("=" * 60)
        print()
        print(error)
        print()


if __name__ == "__main__":
    main()