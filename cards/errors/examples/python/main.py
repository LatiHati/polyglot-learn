def parse_age(text):
    age = int(text)  # raises ValueError when the text is not a number
    if age < 0:
        raise ValueError("age cannot be negative")
    return age


for raw in ["42", "abc", "-5"]:
    try:
        print("ok:", parse_age(raw))
    except ValueError as error:
        print("error:", type(error).__name__)
    finally:
        print("checked", raw)

# The trap: a broad except also catches the bug below and hides it.
try:
    parse_age("42").upper()
except Exception:
    print("looks like a bad age, but it was a bug")
