import os
import json
from pathlib import Path
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai
from pypdf import PdfReader


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Etimad AI",
    page_icon="📄",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = BASE_DIR.parent / ".env"
COMPANY_FILE = BASE_DIR / "company_profile.json"

ANALYSES_DIR = BASE_DIR / "data" / "analyses"
ANALYSES_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(ENV_FILE)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error(
        "GEMINI_API_KEY غير موجود في ملف .env"
    )
    st.stop()


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=API_KEY
)


# ============================================================
# COMPANY PROFILE
# ============================================================

if not COMPANY_FILE.exists():

    st.error(
        "ملف company_profile.json غير موجود."
    )

    st.info(
        f"المسار المطلوب:\n{COMPANY_FILE}"
    )

    st.stop()


try:

    with open(
        COMPANY_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        COMPANY_PROFILE = json.load(file)

except Exception as error:

    st.error(
        "تعذر قراءة ملف الشركة."
    )

    st.exception(error)

    st.stop()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_text(value, default="غير مذكور"):

    if value is None:
        return default

    if isinstance(value, list):

        if not value:
            return default

        return ", ".join(
            str(item)
            for item in value
        )

    return str(value)


def save_analysis(
    filename,
    extracted_text,
    result,
    metadata=None
):

    timestamp = datetime.now()

    safe_filename = (
        Path(filename).stem
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    timestamp_string = timestamp.strftime(
        "%Y%m%d_%H%M%S"
    )

    analysis_folder = (
        ANALYSES_DIR
        / f"{safe_filename}_{timestamp_string}"
    )

    analysis_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Save TXT
    # --------------------------------------------------------

    report_file = (
        analysis_folder
        / "report.txt"
    )

    report_file.write_text(
        result,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Save extracted PDF text
    # --------------------------------------------------------

    text_file = (
        analysis_folder
        / "extracted_text.txt"
    )

    text_file.write_text(
        extracted_text,
        encoding="utf-8"
    )

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    data = {
        "filename": filename,
        "created_at": timestamp.isoformat(),
        "company_profile": COMPANY_PROFILE,
        "analysis": result,
        "metadata": metadata or {}
    }

    json_file = (
        analysis_folder
        / "analysis.json"
    )

    json_file.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ),
        encoding="utf-8"
    )

    return analysis_folder


def load_previous_analyses():

    results = []

    if not ANALYSES_DIR.exists():
        return results

    for folder in ANALYSES_DIR.iterdir():

        if not folder.is_dir():
            continue

        json_file = (
            folder / "analysis.json"
        )

        if not json_file.exists():
            continue

        try:

            data = json.loads(
                json_file.read_text(
                    encoding="utf-8"
                )
            )

            results.append(data)

        except Exception:
            continue

    results.sort(
        key=lambda item: item.get(
            "created_at",
            ""
        ),
        reverse=True
    )

    return results


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_pdf_text(pdf_file):

    reader = PdfReader(pdf_file)

    pages = []

    for page_number, page in enumerate(
        reader.pages,
        start=1
    ):

        text = page.extract_text() or ""

        if text.strip():

            pages.append(
                f"\n--- الصفحة {page_number} ---\n{text}"
            )

    return "\n".join(pages)


# ============================================================
# AI ANALYSIS
# ============================================================

def analyze_rfp(text):

    company_data = json.dumps(
        COMPANY_PROFILE,
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
أنت Etimad AI، نظام متخصص في تحليل كراسات
الشروط والمنافسات ومقارنتها مع ملف شركة افتراضية.

مهم جداً:

حلل الكراسة بناءً على النص الموجود فيها فقط.

لا تخترع أي معلومة غير موجودة.

إذا لم تجد معلومة في الكراسة فاكتب:

"غير مذكور في الكراسة"

إذا لم تجد معلومة في ملف الشركة فاكتب:

"غير مذكور في ملف الشركة"

هناك فرق مهم بين:

1. خبرات الشركة.
2. قدرات الشركة.
3. المشاريع السابقة للشركة.
4. مهارات ومشاريع المؤسس الشخصية.

لا تعتبر مهارة أو مشروع المؤسس تلقائياً
خبرة تجارية موثقة للشركة.

إذا كانت خبرة المؤسس مرتبطة مباشرة
بمتطلب موجود في الكراسة، يمكنك ذكرها
كنقطة قوة إضافية محتملة، مع توضيح
أنها خبرة للمؤسس وليست خبرة موثقة للشركة.

لا تخترع:

- مشاريع حكومية.
- عملاء.
- عقود.
- شهادات.
- خبرات.
- قدرات مالية.
- ضمانات.
- تواريخ.

لا تقدم استشارة قانونية.

لا تفترض أن الشركة مؤهلة للمنافسة.

درجة الملاءمة تقديرية وليست نتيجة رسمية.

============================================================
ملف الشركة الافتراضية
============================================================

{company_data}

============================================================
نص كراسة الشروط
============================================================

{text}

============================================================
التنسيق المطلوب
============================================================

# 1. ملخص المشروع

# 2. نطاق العمل

# 3. الموعد النهائي

# 4. الضمانات المطلوبة

# 5. الشروط والمتطلبات الرئيسية

# 6. المستندات والشهادات المطلوبة

# 7. معايير التقييم

# 8. درجة ملاءمة الشركة

أعط درجة تقديرية من 100.

اشرح سبب الدرجة بناءً على:

- القطاع.
- الخبرات.
- القدرات.
- المشاريع السابقة.
- متطلبات الكراسة.
- الفجوات.

لا ترفع الدرجة بسبب Arduino
إلا إذا كانت الكراسة تحتوي فعلاً
على متطلبات مرتبطة به أو بتقنيات قريبة منه.

# 9. نقاط القوة

اذكر نقاط القوة التي تدعمها
بيانات الشركة فعلياً.

# 10. الفجوات

اذكر المتطلبات التي لا يغطيها
ملف الشركة أو التي تحتاج إثباتاً.

# 11. خبرة المؤسس

افصل هذا القسم تماماً عن خبرة الشركة.

اذكر:

- Arduino.
- الإلكترونيات.
- الأنظمة المضمنة.
- النماذج الأولية.
- أي مشاريع تقنية للمؤسس.

ولكن لا تعتبرها خبرة تجارية للشركة
إلا إذا كان ملف الشركة ينص على ذلك.

# 12. معلومات تحتاج إلى تحقق

اذكر الأشياء التي يجب التحقق منها
قبل اتخاذ قرار التقديم.

# 13. المخاطر والتنبيهات

اذكر المخاطر الموجودة فعلياً
في الكراسة أو الناتجة مباشرة
من مقارنة الكراسة مع ملف الشركة.

# 14. التوصية

اختر واحدة فقط:

مناسب مبدئياً

أو

يحتاج تحقق إضافي

أو

غير مناسب مبدئياً

ثم اذكر سبباً مختصراً.

# 15. الخطوات التالية

قسم الخطوات إلى:

🔴 عاجل

🟠 مهم

🟢 لاحق

اجعل الخطوات عملية وقابلة للتنفيذ.

لا تكتب معلومات غير موجودة.
"""


    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    if not response.text:
        raise RuntimeError(
            "Gemini لم يرجع نتيجة نصية."
        )

    return response.text


# ============================================================
# PAGE HEADER
# ============================================================

st.title(
    "📄 Etimad AI"
)

st.subheader(
    "تحليل كراسات الشروط والمنافسات بالذكاء الاصطناعي"
)

st.write(
    "ارفع كراسة الشروط لتحليلها ومقارنتها "
    "مع ملف الشركة الافتراضية."
)


# ============================================================
# COMPANY SECTION
# ============================================================

st.header(
    "🏢 ملف الشركة الافتراضية"
)

company_col1, company_col2 = st.columns(
    2
)

with company_col1:

    st.markdown(
        f"**اسم الشركة:** "
        f"{safe_text(COMPANY_PROFILE.get('company_name'))}"
    )

    st.markdown(
        f"**القطاع:** "
        f"{safe_text(COMPANY_PROFILE.get('sector'))}"
    )

    st.markdown(
        f"**الحجم:** "
        f"{safe_text(COMPANY_PROFILE.get('company_size'))}"
    )

    st.markdown(
        f"**عدد الموظفين:** "
        f"{safe_text(COMPANY_PROFILE.get('employees'))}"
    )


with company_col2:

    st.markdown(
        "**خبرات الشركة:**"
    )

    for item in COMPANY_PROFILE.get(
        "experience",
        []
    ):

        st.write(
            f"• {item}"
        )


with st.expander(
    "عرض ملف الشركة الكامل"
):

    st.json(
        COMPANY_PROFILE
    )


# ============================================================
# UPLOAD
# ============================================================

st.divider()

st.header(
    "📎 كراسة الشروط"
)

st.write(
    "ارفع كراسة الشروط بصيغة PDF"
)

uploaded_file = st.file_uploader(
    "📎 رفع ملف PDF",
    type=["pdf"]
)


# ============================================================
# ANALYZE
# ============================================================

if uploaded_file:

    st.success(
        f"تم اختيار الملف: {uploaded_file.name}"
    )

    if st.button(
        "🔍 تحليل الكراسة ومقارنة الشركة",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "جاري قراءة الكراسة وتحليلها ومقارنتها مع الشركة..."
            ):

                # --------------------------------------------
                # Extract PDF
                # --------------------------------------------

                text = extract_pdf_text(
                    uploaded_file
                )

                if not text.strip():

                    st.error(
                        "لم يتم استخراج نص من ملف PDF."
                    )

                    st.stop()

                # --------------------------------------------
                # Gemini
                # --------------------------------------------

                result = analyze_rfp(
                    text
                )

            # -----------------------------------------------
            # Save
            # -----------------------------------------------

            metadata = {
                "characters_extracted": len(text),
                "company_name": COMPANY_PROFILE.get(
                    "company_name"
                ),
                "analysis_type": "RFP + Company Comparison"
            }

            analysis_folder = save_analysis(
                uploaded_file.name,
                text,
                result,
                metadata
            )

            st.success(
                f"تم التحليل والحفظ بنجاح — "
                f"{len(text):,} حرف مستخرج"
            )

            st.caption(
                f"مكان الحفظ: {analysis_folder}"
            )

            # =================================================
            # DECISION DASHBOARD
            # =================================================

            st.divider()

            st.header(
                "🎯 لوحة القرار"
            )

            st.info(
                "هذه اللوحة تعتمد على بيانات الاختبار "
                "الحالية. الدرجة والموعد والضمان "
                "سيتم ربطها تلقائياً من Gemini "
                "في المرحلة التالية."
            )

            dashboard_col1, dashboard_col2, dashboard_col3 = (
                st.columns(3)
            )

            with dashboard_col1:

                st.metric(
                    "درجة الملاءمة",
                    "تقديرية"
                )

            with dashboard_col2:

                st.metric(
                    "الموعد النهائي",
                    "راجع التحليل"
                )

            with dashboard_col3:

                st.metric(
                    "الضمان",
                    "راجع التحليل"
                )

            # =================================================
            # RESULT
            # =================================================

            st.divider()

            st.header(
                "📊 نتيجة التحليل"
            )

            st.markdown(
                result
            )

            # =================================================
            # DOWNLOADS
            # =================================================

            st.divider()

            st.header(
                "📥 تحميل النتائج"
            )

            download_col1, download_col2 = (
                st.columns(2)
            )

            with download_col1:

                st.download_button(
                    label="📄 تحميل التقرير TXT",
                    data=result,
                    file_name=(
                        f"{Path(uploaded_file.name).stem}"
                        "_etimad_analysis.txt"
                    ),
                    mime="text/plain",
                    use_container_width=True
                )

            with download_col2:

                json_data = {
                    "filename": uploaded_file.name,
                    "created_at": datetime.now().isoformat(),
                    "company_profile": COMPANY_PROFILE,
                    "extracted_text": text,
                    "analysis": result
                }

                st.download_button(
                    label="📦 تحميل البيانات JSON",
                    data=json.dumps(
                        json_data,
                        ensure_ascii=False,
                        indent=2
                    ),
                    file_name=(
                        f"{Path(uploaded_file.name).stem}"
                        "_etimad_analysis.json"
                    ),
                    mime="application/json",
                    use_container_width=True
                )

            # =================================================
            # EXTRACTED TEXT
            # =================================================

            st.divider()

            with st.expander(
                "📄 عرض النص المستخرج من الكراسة"
            ):

                st.text_area(
                    "النص المستخرج",
                    text,
                    height=500
                )

        except Exception as error:

            st.error(
                "حدث خطأ أثناء التحليل:"
            )

            st.exception(error)


# ============================================================
# PREVIOUS ANALYSES
# ============================================================

st.divider()

st.header(
    "🗂️ سجل التحليلات السابقة"
)

previous_analyses = (
    load_previous_analyses()
)

st.write(
    f"عدد التحليلات المحفوظة: "
    f"**{len(previous_analyses)}**"
)


if previous_analyses:

    for index, analysis in enumerate(
        previous_analyses,
        start=1
    ):

        filename = analysis.get(
            "filename",
            "ملف غير معروف"
        )

        created_at = analysis.get(
            "created_at",
            "وقت غير معروف"
        )

        with st.expander(
            f"📄 {filename} — {created_at}"
        ):

            st.markdown(
                analysis.get(
                    "analysis",
                    "لا توجد نتيجة."
                )
            )

            metadata = analysis.get(
                "metadata",
                {}
            )

            if metadata:

                st.caption(
                    f"عدد الأحرف المستخرجة: "
                    f"{metadata.get('characters_extracted', '-')}"
                )

else:

    st.info(
        "لا توجد تحليلات محفوظة حتى الآن."
    )