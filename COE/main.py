from google import genai
from dotenv import load_dotenv
import os
import json
import sqlite3
from datetime import datetime


# =====================================================
# CONFIG
# =====================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY غير موجود في ملف .env"
    )

client = genai.Client(api_key=API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMPANY_FILE = os.path.join(BASE_DIR, "company.json")
DATABASE_FILE = os.path.join(BASE_DIR, "coe.db")

COMPANY_STATUSES = (
    "prospect",
    "contacted",
    "interview",
    "pilot",
    "paying_customer"
)

PRIORITIES = (
    "high",
    "medium",
    "low"
)


# =====================================================
# COMPANY PROFILE
# =====================================================

def load_company():

    if os.path.exists(COMPANY_FILE):

        with open(
            COMPANY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    company = {
        "company_name": "COE Company",
        "industry": "AI",
        "business_model": "SaaS",
        "target_customer": "Saudi companies participating in government tenders",
        "country": "Saudi Arabia",
        "currency": "SAR",
        "mission": "Build an AI-first SaaS company with minimal employees.",
        "budget": 0,
        "monthly_budget": 0,
        "owner_role": "Founder",
        "current_product": "Etimad AI"
    }

    with open(
        COMPANY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            company,
            f,
            ensure_ascii=False,
            indent=2
        )

    return company


company = load_company()


# =====================================================
# DATABASE CONNECTION
# =====================================================

def db():

    conn = sqlite3.connect(DATABASE_FILE)

    conn.row_factory = sqlite3.Row

    return conn


# =====================================================
# DATABASE INITIALIZATION
# =====================================================

def init_database():

    conn = db()
    cursor = conn.cursor()

    # -------------------------------------------------
    # GOALS
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal TEXT NOT NULL,
            priority TEXT DEFAULT 'high',
            status TEXT DEFAULT 'active',
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------------------------------
    # TASKS
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            priority TEXT DEFAULT 'medium',
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------------------------------
    # DECISIONS
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            decision TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------------------------------
    # TARGET COMPANIES
    # -------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS target_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            sector TEXT NOT NULL,

            size TEXT NOT NULL,

            fit_reason TEXT NOT NULL,

            contact_person TEXT DEFAULT '',

            contact_role TEXT DEFAULT '',

            status TEXT DEFAULT 'prospect',

            notes TEXT DEFAULT '',

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_database()


# =====================================================
# GOALS
# =====================================================

def save_goal(goal, priority="high"):

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO goals
        (goal, priority, status, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            goal,
            priority,
            "active",
            datetime.now().isoformat()
        )
    )

    goal_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return goal_id


def get_goals():

    conn = db()

    rows = conn.execute(
        """
        SELECT
            id,
            goal,
            priority,
            status,
            created_at
        FROM goals
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return rows


# =====================================================
# TASKS
# =====================================================

def save_task(task, priority="medium"):

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks
        (task, priority, status, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            task,
            priority,
            "pending",
            datetime.now().isoformat()
        )
    )

    task_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return task_id


def get_tasks():

    conn = db()

    rows = conn.execute(
        """
        SELECT
            id,
            task,
            priority,
            status,
            created_at
        FROM tasks
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return rows


def start_task(task_id):

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = 'in_progress'
        WHERE id = ?
        """,
        (task_id,)
    )

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed


def complete_task(task_id):

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = 'completed'
        WHERE id = ?
        """,
        (task_id,)
    )

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed


def delete_task(task_id):

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed


def update_task_priority(task_id, priority):

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET priority = ?
        WHERE id = ?
        """,
        (
            priority,
            task_id
        )
    )

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed


# =====================================================
# DECISIONS
# =====================================================

def save_decision(decision):

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO decisions
        (decision, created_at)
        VALUES (?, ?)
        """,
        (
            decision,
            datetime.now().isoformat()
        )
    )

    decision_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return decision_id


def get_decisions():

    conn = db()

    rows = conn.execute(
        """
        SELECT
            id,
            decision,
            created_at
        FROM decisions
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return rows


# =====================================================
# TARGET COMPANIES
# =====================================================

def save_company(
    name,
    sector,
    size,
    fit_reason,
    contact_person="",
    contact_role="",
    status="prospect",
    notes=""
):

    if status not in COMPANY_STATUSES:

        raise ValueError(
            "حالة الشركة غير صحيحة."
        )

    now = datetime.now().isoformat()

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO target_companies
        (
            name,
            sector,
            size,
            fit_reason,
            contact_person,
            contact_role,
            status,
            notes,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            sector,
            size,
            fit_reason,
            contact_person,
            contact_role,
            status,
            notes,
            now,
            now
        )
    )

    company_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return company_id


def get_target_companies():

    conn = db()

    rows = conn.execute(
        """
        SELECT
            id,
            name,
            sector,
            size,
            fit_reason,
            contact_person,
            contact_role,
            status,
            notes,
            created_at,
            updated_at
        FROM target_companies
        ORDER BY id ASC
        """
    ).fetchall()

    conn.close()

    return rows


def get_target_company(company_id):

    conn = db()

    row = conn.execute(
        """
        SELECT
            id,
            name,
            sector,
            size,
            fit_reason,
            contact_person,
            contact_role,
            status,
            notes,
            created_at,
            updated_at
        FROM target_companies
        WHERE id = ?
        """,
        (company_id,)
    ).fetchone()

    conn.close()

    return row


def update_company_status(
    company_id,
    status
):

    if status not in COMPANY_STATUSES:

        return -1

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE target_companies

        SET
            status = ?,
            updated_at = ?

        WHERE id = ?
        """,
        (
            status,
            datetime.now().isoformat(),
            company_id
        )
    )

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed


def update_company_contact(
    company_id,
    contact_person,
    contact_role
):

    conn = db()

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE target_companies

        SET
            contact_person = ?,
            contact_role = ?,
            updated_at = ?

        WHERE id = ?
        """,
        (
            contact_person,
            contact_role,
            datetime.now().isoformat(),
            company_id
        )
    )

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed


def add_company_note(
    company_id,
    note
):

    conn = db()

    cursor = conn.cursor()

    existing = conn.execute(
        """
        SELECT notes
        FROM target_companies
        WHERE id = ?
        """,
        (company_id,)
    ).fetchone()

    if not existing:

        conn.close()

        return 0

    old_notes = existing["notes"] or ""

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )

    if old_notes:

        new_notes = (
            old_notes
            + "\n"
            + f"[{timestamp}] "
            + note
        )

    else:

        new_notes = (
            f"[{timestamp}] "
            + note
        )

    cursor.execute(
        """
        UPDATE target_companies

        SET
            notes = ?,
            updated_at = ?

        WHERE id = ?
        """,
        (
            new_notes,
            datetime.now().isoformat(),
            company_id
        )
    )

    changed = cursor.rowcount

    conn.commit()
    conn.close()

    return changed


def get_company_funnel():

    conn = db()

    result = {}

    for status in COMPANY_STATUSES:

        row = conn.execute(
            """
            SELECT COUNT(*) AS total
            FROM target_companies
            WHERE status = ?
            """,
            (status,)
        ).fetchone()

        result[status] = row["total"]

    conn.close()

    return result


# =====================================================
# DATABASE DIAGNOSTICS
# =====================================================

def get_database_info():
    conn = db()

    tables = conn.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
        """
    ).fetchall()

    counts = {}

    for table in (
        "goals",
        "tasks",
        "decisions",
        "target_companies"
    ):
        try:
            row = conn.execute(
                f"SELECT COUNT(*) AS total FROM {table}"
            ).fetchone()
            counts[table] = row["total"]
        except sqlite3.Error:
            counts[table] = None

    conn.close()

    return {
        "database_file": DATABASE_FILE,
        "database_exists": os.path.exists(DATABASE_FILE),
        "tables": [row["name"] for row in tables],
        "counts": counts
    }


def show_database_info():
    info = get_database_info()

    print()
    print("=" * 65)
    print("                 فحص قاعدة بيانات COE")
    print("=" * 65)
    print()
    print(f"ملف قاعدة البيانات:")
    print(info["database_file"])
    print()
    print(f"موجود: {'نعم' if info['database_exists'] else 'لا'}")
    print()
    print("الجداول:")

    if info["tables"]:
        for table in info["tables"]:
            print(f"- {table}")
    else:
        print("- لا توجد جداول")

    print()
    print("عدد السجلات:")

    labels = {
        "goals": "الأهداف",
        "tasks": "المهام",
        "decisions": "القرارات",
        "target_companies": "الشركات"
    }

    for key, label in labels.items():
        print(f"- {label}: {info['counts'].get(key, 0)}")

    print()


# =====================================================
# MEMORY
# =====================================================

def get_memory():

    target_companies = get_target_companies()

    return {

        "company": company,

        "goals": [
            {
                "id": row["id"],
                "goal": row["goal"],
                "priority": row["priority"],
                "status": row["status"]
            }
            for row in get_goals()
        ],

        "tasks": [
            {
                "id": row["id"],
                "task": row["task"],
                "priority": row["priority"],
                "status": row["status"]
            }
            for row in get_tasks()
        ],

        "decisions": [
            {
                "id": row["id"],
                "decision": row["decision"]
            }
            for row in get_decisions()
        ],

        "target_companies": [
            {
                "id": row["id"],
                "name": row["name"],
                "sector": row["sector"],
                "size": row["size"],
                "fit_reason": row["fit_reason"],
                "contact_person": row["contact_person"],
                "contact_role": row["contact_role"],
                "status": row["status"],
                "notes": row["notes"]
            }
            for row in target_companies
        ],

        "funnel": get_company_funnel()
    }


# =====================================================
# AI CEO
# =====================================================

SYSTEM_PROMPT = """

أنت COE، المدير التنفيذي الذكي لشركة COE Company.

الشركة تريد بناء شركة SaaS تعتمد على AI
وتعمل بأقل عدد ممكن من الموظفين.

المنتج الحالي:

Etimad AI

النموذج الحالي:

Bring Your Own RFP

العميل يرفع كراسة الشروط بنفسه،
والنظام يحلل الملف ويستخرج المتطلبات
ويساعد في إعداد العرض الفني.

الهدف الحالي:

التحقق من وجود مشكلة حقيقية
وعملاء مستعدين للدفع قبل بناء المنتج
بشكل كامل.

قاعدة أساسية:

لا تعتبر أي شركة عميلاً أو مستخدماً فعلياً
إلا إذا كانت حالة الشركة في قاعدة البيانات:

paying_customer

حالات الشركات:

prospect
contacted
interview
pilot
paying_customer

معانيها:

prospect:
شركة مستهدفة ولم يتم التواصل معها.

contacted:
تم التواصل معها لكن لم تتم مقابلة تحقق.

interview:
تمت مقابلة تحقق.

pilot:
بدأت تجربة أو Pilot.

paying_customer:
دفعت فعلياً مقابل المنتج أو الخدمة.

مهمتك:

- التفكير كـ CEO.
- استخدام ذاكرة الشركة.
- تحديد الأولويات.
- إعطاء خطوات عملية.
- التفريق بين الحقيقة والاقتراح.
- عدم اختلاق معلومات.
- عدم اعتبار prospect عميلاً.
- عدم اعتبار contacted عميلاً.
- عدم اعتبار interview عميلاً.
- عدم اعتبار pilot عميلاً مدفوعاً إلا إذا كانت الذاكرة تؤكد ذلك.
- عدم الادعاء بأن عملية تمت في قاعدة البيانات إلا إذا نفذها البرنامج.
- لا تدّعي التواصل مع أي شركة.
- لا تدّعي إجراء مقابلة.
- لا تدّعي وجود عميل مدفوع بدون دليل في الذاكرة.
- أي قرار حساس يحتاج موافقة المؤسس.

حالياً أهم هدف:

الحصول على مقابلات حقيقية مع الشركات
ثم تحويل أفضل الشركات إلى Paid Pilot.

لا تبدأ باقتراح البرمجة
إذا كانت عملية التحقق من السوق لم تكتمل.

إذا كانت هناك شركة حالتها prospect:
اقترح التواصل معها.

إذا كانت contacted:
اقترح حجز مقابلة.

إذا كانت interview:
اقترح تقييم المشكلة والاستعداد للدفع.

إذا كانت pilot:
اقترح قياس الاستخدام والنتيجة والاستعداد للتحويل إلى دفع.

إذا كانت paying_customer:
اعتبرها دليلاً قوياً على Product-Market Validation.

"""


# =====================================================
# DISPLAY HELP
# =====================================================

def show_help():

    print()

    print("=" * 60)
    print("                     أوامر COE")
    print("=" * 60)

    print()
    print("الأهداف:")
    print("/هدف <النص>")
    print("/الأهداف")

    print()
    print("المهام:")
    print("/مهمة <النص>")
    print("/المهام")
    print("/قيد <رقم المهمة>")
    print("/تم <رقم المهمة>")
    print("/حذف <رقم المهمة>")
    print("/أولوية <رقم> <high|medium|low>")

    print()
    print("القرارات:")
    print("/قرار <النص>")
    print("/القرارات")

    print()
    print("الشركات:")
    print("/شركة <اسم> | <القطاع> | <الحجم> | <سبب الملاءمة>")
    print("/الشركات")
    print("/حالة الشركات")
    print("/حالة شركة <رقم>")
    print(
        "/تحديث شركة <رقم> "
        "<prospect|contacted|interview|pilot|paying_customer>"
    )
    print("/جهة شركة <رقم> <اسم> | <المنصب>")
    print("/ملاحظة شركة <رقم> <النص>")

    print()
    print("النظام:")
    print("/ذاكرة")
    print("/فحص قاعدة البيانات")
    print("/مساعدة")
    print("خروج")

    print()


# =====================================================
# SHOW MEMORY
# =====================================================

def show_memory():

    memory = get_memory()

    print()

    print("=" * 60)
    print("                     ذاكرة COE")
    print("=" * 60)

    print()
    print("الأهداف:")

    if memory["goals"]:

        for item in memory["goals"]:

            print(
                f"#{item['id']} | "
                f"{item['goal']} | "
                f"الأولوية: {item['priority']} | "
                f"الحالة: {item['status']}"
            )

    else:

        print("لا توجد أهداف.")

    print()
    print("المهام:")

    if memory["tasks"]:

        for item in memory["tasks"]:

            print(
                f"#{item['id']} | "
                f"{item['task']} | "
                f"الأولوية: {item['priority']} | "
                f"الحالة: {item['status']}"
            )

    else:

        print("لا توجد مهام.")

    print()
    print("القرارات:")

    if memory["decisions"]:

        for item in memory["decisions"]:

            print(
                f"#{item['id']} | "
                f"{item['decision']}"
            )

    else:

        print("لا توجد قرارات.")

    print()
    print("الشركات المستهدفة:")

    if memory["target_companies"]:

        for item in memory["target_companies"]:

            print(
                f"#{item['id']} | "
                f"{item['name']} | "
                f"{item['status']}"
            )

    else:

        print("لا توجد شركات.")

    print()


# =====================================================
# SHOW COMPANIES
# =====================================================

def show_companies():

    companies = get_target_companies()

    print()

    print("=" * 70)
    print("                 الشركات المستهدفة - Etimad AI")
    print("=" * 70)

    if not companies:

        print("لا توجد شركات مسجلة.")

        return

    for row in companies:

        print()

        print(
            f"#{row['id']} | {row['name']}"
        )

        print(
            f"القطاع: {row['sector']}"
        )

        print(
            f"الحجم: {row['size']}"
        )

        print(
            f"الملاءمة: {row['fit_reason']}"
        )

        print(
            f"جهة الاتصال: "
            f"{row['contact_person'] or '-'}"
        )

        print(
            f"المنصب: "
            f"{row['contact_role'] or '-'}"
        )

        print(
            f"الحالة: {row['status']}"
        )

        if row["notes"]:

            print(
                f"ملاحظات: {row['notes']}"
            )

    print()


# =====================================================
# SHOW COMPANY STATUS
# =====================================================

def show_company_status():

    funnel = get_company_funnel()

    print()

    print("=" * 50)
    print("           Funnel - Etimad AI")
    print("=" * 50)

    print(
        f"Prospect:         "
        f"{funnel['prospect']}"
    )

    print(
        f"Contacted:        "
        f"{funnel['contacted']}"
    )

    print(
        f"Interview:        "
        f"{funnel['interview']}"
    )

    print(
        f"Pilot:            "
        f"{funnel['pilot']}"
    )

    print(
        f"Paying Customer:  "
        f"{funnel['paying_customer']}"
    )

    print()

    total = sum(funnel.values())

    print(
        f"إجمالي الشركات: {total}"
    )

    print()


# =====================================================
# SHOW SINGLE COMPANY
# =====================================================

def show_single_company(company_id):

    row = get_target_company(company_id)

    if not row:

        print(
            f"COE: لم أجد الشركة #{company_id}."
        )

        return

    print()

    print("=" * 60)
    print(
        f"شركة #{row['id']}: {row['name']}"
    )
    print("=" * 60)

    print(
        f"القطاع: {row['sector']}"
    )

    print(
        f"الحجم: {row['size']}"
    )

    print(
        f"سبب الملاءمة: {row['fit_reason']}"
    )

    print(
        f"جهة الاتصال: "
        f"{row['contact_person'] or '-'}"
    )

    print(
        f"المنصب: "
        f"{row['contact_role'] or '-'}"
    )

    print(
        f"الحالة: {row['status']}"
    )

    print(
        f"الملاحظات: "
        f"{row['notes'] or '-'}"
    )

    print(
        f"آخر تحديث: {row['updated_at']}"
    )

    print()


# =====================================================
# START
# =====================================================

print("=" * 60)
print("                 COE AI CEO v0.8.1")
print("=" * 60)

print("Gemini connected.")
print("قاعدة البيانات:", DATABASE_FILE)

print(
    "الشركة:",
    company.get(
        "company_name",
        "COE Company"
    )
)

print()

show_help()


# =====================================================
# MAIN LOOP
# =====================================================

while True:

    try:

        user_input = input("أنت: ").strip()

    except (
        KeyboardInterrupt,
        EOFError
    ):

        print(
            "\nCOE: تم إيقاف النظام."
        )

        break

    if not user_input:

        continue


    # =================================================
    # EXIT
    # =================================================

    if user_input == "خروج":

        print(
            "COE: تم إيقاف النظام."
        )

        break


    # =================================================
    # HELP
    # =================================================

    if user_input == "/مساعدة":

        show_help()

        continue


    # =================================================
    # GOAL
    # =================================================

    if user_input.startswith("/هدف"):

        goal = user_input[4:].strip()

        if not goal:

            print(
                "COE: اكتب الهدف بعد /هدف"
            )

            continue

        goal_id = save_goal(goal)

        print(
            f"COE: تم حفظ الهدف #{goal_id}."
        )

        continue


    # =================================================
    # SHOW GOALS
    # =================================================

    if user_input == "/الأهداف":

        goals = get_goals()

        print()

        if not goals:

            print("لا توجد أهداف.")

        else:

            for row in goals:

                print(
                    f"#{row['id']} | "
                    f"{row['goal']} | "
                    f"الأولوية: {row['priority']} | "
                    f"الحالة: {row['status']}"
                )

        print()

        continue


    # =================================================
    # TASK
    # =================================================

    if user_input.startswith("/مهمة"):

        task = user_input[5:].strip()

        if not task:

            print(
                "COE: اكتب المهمة بعد /مهمة"
            )

            continue

        task_id = save_task(task)

        print(
            f"COE: تم حفظ المهمة #{task_id}."
        )

        continue


    # =================================================
    # SHOW TASKS
    # =================================================

    if user_input == "/المهام":

        tasks = get_tasks()

        print()

        if not tasks:

            print("لا توجد مهام.")

        else:

            for row in tasks:

                print(
                    f"#{row['id']} | "
                    f"{row['task']} | "
                    f"الأولوية: {row['priority']} | "
                    f"الحالة: {row['status']}"
                )

        print()

        continue


    # =================================================
    # START TASK
    # =================================================

    if user_input.startswith("/قيد"):

        parts = user_input.split()

        if len(parts) != 2:

            print(
                "الاستخدام: /قيد <رقم المهمة>"
            )

            continue

        try:

            task_id = int(parts[1])

        except ValueError:

            print(
                "رقم المهمة يجب أن يكون رقمًا."
            )

            continue

        changed = start_task(task_id)

        if changed:

            print(
                f"COE: تم بدء المهمة #{task_id}."
            )

        else:

            print(
                f"COE: لم أجد المهمة #{task_id}."
            )

        continue


    # =================================================
    # COMPLETE TASK
    # =================================================

    if user_input.startswith("/تم"):

        parts = user_input.split()

        if len(parts) != 2:

            print(
                "الاستخدام: /تم <رقم المهمة>"
            )

            continue

        try:

            task_id = int(parts[1])

        except ValueError:

            print(
                "رقم المهمة يجب أن يكون رقمًا."
            )

            continue

        changed = complete_task(task_id)

        if changed:

            print(
                f"COE: تم إكمال المهمة #{task_id}."
            )

        else:

            print(
                f"COE: لم أجد المهمة #{task_id}."
            )

        continue


    # =================================================
    # DELETE TASK
    # =================================================

    if user_input.startswith("/حذف"):

        parts = user_input.split()

        if len(parts) != 2:

            print(
                "الاستخدام: /حذف <رقم المهمة>"
            )

            continue

        try:

            task_id = int(parts[1])

        except ValueError:

            print(
                "رقم المهمة يجب أن يكون رقمًا."
            )

            continue

        changed = delete_task(task_id)

        if changed:

            print(
                f"COE: تم حذف المهمة #{task_id}."
            )

        else:

            print(
                f"COE: لم أجد المهمة #{task_id}."
            )

        continue


    # =================================================
    # PRIORITY
    # =================================================

    if user_input.startswith("/أولوية"):

        parts = user_input.split()

        if len(parts) != 3:

            print(
                "الاستخدام: /أولوية <رقم> <high|medium|low>"
            )

            continue

        try:

            task_id = int(parts[1])

        except ValueError:

            print(
                "رقم المهمة يجب أن يكون رقمًا."
            )

            continue

        priority = parts[2].lower()

        if priority not in PRIORITIES:

            print(
                "الأولوية يجب أن تكون: "
                "high أو medium أو low"
            )

            continue

        changed = update_task_priority(
            task_id,
            priority
        )

        if changed:

            print(
                f"COE: تم تحديث أولوية المهمة #{task_id}."
            )

        else:

            print(
                f"COE: لم أجد المهمة #{task_id}."
            )

        continue


    # =================================================
    # DECISION
    # =================================================

    if user_input.startswith("/قرار"):

        decision = user_input[5:].strip()

        if not decision:

            print(
                "COE: اكتب القرار بعد /قرار"
            )

            continue

        decision_id = save_decision(
            decision
        )

        print(
            f"COE: تم حفظ القرار #{decision_id}."
        )

        continue


    # =================================================
    # SHOW DECISIONS
    # =================================================

    if user_input == "/القرارات":

        decisions = get_decisions()

        print()

        if not decisions:

            print("لا توجد قرارات.")

        else:

            for row in decisions:

                print(
                    f"#{row['id']} | "
                    f"{row['decision']}"
                )

        print()

        continue


    # =================================================
    # ADD TARGET COMPANY
    # =================================================

    if user_input.startswith("/شركة"):

        raw = user_input[5:].strip()

        parts = [
            x.strip()
            for x in raw.split("|")
        ]

        if len(parts) != 4:

            print()

            print(
                "الاستخدام:"
            )

            print(
                "/شركة <اسم> | <القطاع> | "
                "<الحجم> | <سبب الملاءمة>"
            )

            print()

            continue

        name = parts[0]
        sector = parts[1]
        size = parts[2]
        fit_reason = parts[3]

        if not name:

            print(
                "COE: اسم الشركة مطلوب."
            )

            continue

        company_id = save_company(
            name=name,
            sector=sector,
            size=size,
            fit_reason=fit_reason
        )

        print(
            f"COE: تم حفظ الشركة #{company_id} "
            f"كـ prospect."
        )

        continue


    # =================================================
    # SHOW TARGET COMPANIES
    # =================================================

    if user_input == "/الشركات":

        show_companies()

        continue


    # =================================================
    # COMPANY FUNNEL
    # =================================================

    if user_input == "/حالة الشركات":

        show_company_status()

        continue


    # =================================================
    # SINGLE COMPANY
    # =================================================

    if user_input.startswith("/حالة شركة"):

        parts = user_input.split()

        if len(parts) != 3:

            print(
                "الاستخدام: /حالة شركة <رقم>"
            )

            continue

        try:

            company_id = int(parts[2])

        except ValueError:

            print(
                "رقم الشركة يجب أن يكون رقمًا."
            )

            continue

        show_single_company(
            company_id
        )

        continue


    # =================================================
    # UPDATE COMPANY STATUS
    # =================================================

    if user_input.startswith("/تحديث شركة"):

        parts = user_input.split()

        if len(parts) != 4:

            print()

            print(
                "الاستخدام:"
            )

            print(
                "/تحديث شركة <رقم> "
                "<prospect|contacted|interview|pilot|paying_customer>"
            )

            print()

            continue

        try:

            company_id = int(parts[2])

        except ValueError:

            print(
                "رقم الشركة يجب أن يكون رقمًا."
            )

            continue

        status = parts[3].lower()

        if status not in COMPANY_STATUSES:

            print()

            print(
                "الحالة غير صحيحة."
            )

            print(
                "الحالات المسموحة:"
            )

            print(
                "prospect"
            )

            print(
                "contacted"
            )

            print(
                "interview"
            )

            print(
                "pilot"
            )

            print(
                "paying_customer"
            )

            print()

            continue

        changed = update_company_status(
            company_id,
            status
        )

        if changed == -1:

            print(
                "COE: الحالة غير صحيحة."
            )

        elif changed:

            print(
                f"COE: تم تحديث حالة الشركة "
                f"#{company_id} إلى {status}."
            )

        else:

            print(
                f"COE: لم أجد الشركة #{company_id}."
            )

        continue


    # =================================================
    # COMPANY NOTE
    # =================================================

    if user_input.startswith("/ملاحظة شركة"):

        raw = user_input[len("/ملاحظة شركة"):].strip()

        parts = raw.split(maxsplit=1)

        if len(parts) != 2:

            print(
                "الاستخدام:"
            )

            print(
                "/ملاحظة شركة <رقم> <النص>"
            )

            continue

        try:

            company_id = int(parts[0])

        except ValueError:

            print(
                "رقم الشركة يجب أن يكون رقمًا."
            )

            continue

        note = parts[1].strip()

        if not note:

            print(
                "COE: الملاحظة فارغة."
            )

            continue

        changed = add_company_note(
            company_id,
            note
        )

        if changed:

            print(
                f"COE: تمت إضافة الملاحظة "
                f"للشركة #{company_id}."
            )

        else:

            print(
                f"COE: لم أجد الشركة #{company_id}."
            )

        continue


    # =================================================
    # DATABASE INFO
    # =================================================

    if user_input == "/فحص قاعدة البيانات":

        show_database_info()

        continue


    # =================================================
    # UPDATE COMPANY CONTACT
    # =================================================

    if user_input.startswith("/جهة شركة"):

        raw = user_input[len("/جهة شركة"):].strip()

        parts = raw.split(maxsplit=1)

        if len(parts) != 2:
            print()
            print("الاستخدام:")
            print("/جهة شركة <رقم> <اسم> | <المنصب>")
            print()
            continue

        try:
            company_id = int(parts[0])
        except ValueError:
            print("رقم الشركة يجب أن يكون رقمًا.")
            continue

        contact_parts = [
            x.strip()
            for x in parts[1].split("|", 1)
        ]

        if len(contact_parts) != 2:
            print()
            print("الاستخدام:")
            print("/جهة شركة <رقم> <اسم> | <المنصب>")
            print()
            continue

        contact_person = contact_parts[0]
        contact_role = contact_parts[1]

        if not contact_person or not contact_role:
            print("COE: اسم جهة الاتصال والمنصب مطلوبان.")
            continue

        changed = update_company_contact(
            company_id,
            contact_person,
            contact_role
        )

        if changed:
            print(
                f"COE: تم تحديث جهة الاتصال للشركة #{company_id}."
            )
        else:
            print(
                f"COE: لم أجد الشركة #{company_id}."
            )

        continue


    # =================================================
    # MEMORY
    # =================================================

    if user_input == "/ذاكرة":

        show_memory()

        continue


    # =================================================
    # GEMINI CEO
    # =================================================

    try:

        memory = get_memory()

        prompt = f"""
{SYSTEM_PROMPT}

==================================================
ذاكرة الشركة الحالية
==================================================

{json.dumps(
    memory,
    ensure_ascii=False,
    indent=2
)}

==================================================
رسالة المؤسس
==================================================

{user_input}

==================================================

أجب بالعربية.

كن عملياً ومباشراً.

لا تخترع شركات أو عملاء أو مقابلات أو مدفوعات.

إذا ذكرت شركة من الذاكرة،
استخدم اسمها وحالتها الفعلية.

إذا كانت الشركة prospect فلا تقل إنها تواصلت معنا.

إذا كانت contacted فلا تقل إن المقابلة تمت.

إذا كانت interview فلا تقل إنها عميل.

إذا كانت pilot فلا تقل إنها عميل مدفوع
إلا إذا كانت الحالة paying_customer.

إذا كانت هناك خطوة تحتاج موافقة المؤسس،
اذكر أنها "اقتراح يحتاج موافقة المؤسس".

إذا كان بالإمكان تحويل الكلام إلى مهمة،
اقترح مهمة واضحة في نهاية الرد.

لا تقل "تم الحفظ"
أو "تم التحديث"
إلا إذا قام البرنامج فعلياً بتنفيذ العملية.
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        print()

        print(
            "COE:",
            response.text
        )

        print()

    except Exception as error:

        print()

        print(
            "حدث خطأ أثناء الاتصال بـ Gemini:"
        )

        print(error)

        print()