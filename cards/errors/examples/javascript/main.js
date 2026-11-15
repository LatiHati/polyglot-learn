function parseAge(text) {
  const age = Number.parseInt(text, 10); // no exception: bad input gives NaN
  if (Number.isNaN(age)) throw new RangeError("not a number");
  if (age < 0) throw new RangeError("age cannot be negative");
  return age;
}

for (const raw of ["42", "abc", "-5"]) {
  try {
    console.log("ok:", parseAge(raw));
  } catch (error) {
    console.log("error:", error.constructor.name + ": " + error.message);
  } finally {
    console.log("checked", raw);
  }
}

// The trap: parsing stops at the first bad character and reports success.
console.log(Number.parseInt("12abc", 10));
console.log(Number("12abc"));
