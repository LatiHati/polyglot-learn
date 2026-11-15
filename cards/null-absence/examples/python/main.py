user = {"name": "Ada"}

# Asking politely gives None. There is exactly one None.
print(user.get("email"))
print(user.get("email") is None)

# Asking directly for a missing key is an error, not None.
try:
    user["email"]
except KeyError as error:
    print("KeyError:", error)

# None has no length: using it as a value fails at that moment.
try:
    len(user.get("email"))
except TypeError as error:
    print(type(error).__name__)

# The trap: `or` replaces every falsy value, not only None.
print(user.get("email") or "no email")
print(0 or "no value")
