import re

NAME_PATTERN = re.compile(r"^[A-Za-z\s]+$")
PASSWORD_UPPERCASE = re.compile(r"[A-Z]")
PASSWORD_LOWERCASE = re.compile(r"[a-z]")
PASSWORD_DIGIT = re.compile(r"\d")
PASSWORD_SPECIAL = re.compile(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\/;'~]")


def validate_full_name(name: str) -> str:
    normalized = name.strip()
    if len(normalized) < 3:
        raise ValueError("Full name must be at least 3 characters long.")
    if len(normalized) > 50:
        raise ValueError("Full name must not exceed 50 characters.")
    if not NAME_PATTERN.match(normalized):
        raise ValueError("Full name must contain only alphabets and spaces.")
    return normalized


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if len(password) > 64:
        raise ValueError("Password must not exceed 64 characters.")
    if not all(
        (
            PASSWORD_UPPERCASE.search(password),
            PASSWORD_LOWERCASE.search(password),
            PASSWORD_DIGIT.search(password),
            PASSWORD_SPECIAL.search(password),
        )
    ):
        raise ValueError(
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and one special character."
        )
    return password


def validate_passwords_match(password: str, confirm_password: str) -> None:
    if password != confirm_password:
        raise ValueError("Passwords do not match.")


def validate_project_title(title: str) -> str:
    normalized = title.strip()
    if len(normalized) < 3:
        raise ValueError("Project title must be at least 3 characters long.")
    if len(normalized) > 50:
        raise ValueError("Project title must not exceed 50 characters.")
    return normalized


def validate_project_description(description: str) -> str:
    normalized = description.strip()
    if len(normalized) < 10:
        raise ValueError("Project description must be at least 10 characters long.")
    if len(normalized) > 500:
        raise ValueError("Project description must not exceed 500 characters.")
    return normalized
