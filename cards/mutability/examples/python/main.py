# A name is a label on an object. Two labels can point at the same list.
a = [1, 2, 3]
b = a
b.append(4)
print(a)

# A tuple cannot be changed in place.
t = (1, 2, 3)
try:
    t[0] = 99
except TypeError as error:
    print(type(error).__name__)


# The trap: the default list is created once and shared by every call.
def add_item(item, bucket=[]):
    bucket.append(item)
    return bucket


print(add_item("x"))
print(add_item("y"))
