def get_department_info(department: str):

    departments = {
        "IT": {
            "email": "it@company.com"
        },
        "HR": {
            "email": "hr@company.com"
        },
        "Finance": {
            "email": "finance@company.com"
        },
        "General": {
            "email": "support@company.com"
        }
    }

    return departments.get(department)