const user = { name: "Ada" };

// A missing property is not an error. It is undefined.
console.log(user.email);

// There are two "nothing" values: undefined and null.
console.log(user.email === null);
console.log(user.email == null);
console.log(typeof null);

// Using undefined as a value fails at that moment.
try {
  user.email.length;
} catch (error) {
  console.log(error.constructor.name);
}

// Optional chaining and the nullish operator were added for exactly this.
console.log(user.email?.length);
console.log(user.email ?? "no email");

// The trap: || replaces every falsy value, ?? only null and undefined.
console.log(0 || "no value");
console.log(0 ?? "no value");
