// A name is a label on an object. Two labels can point at the same array.
const a = [1, 2, 3];
const b = a;
b.push(4);
console.log(JSON.stringify(a));

// A frozen array cannot be changed in place.
const frozen = Object.freeze([1, 2, 3]);
try {
  frozen.push(4);
} catch (error) {
  console.log(error.constructor.name);
}

// The trap: const stops rebinding the name, not changing the object.
const point = { x: 1 };
point.x = 2;
console.log(point.x);
try {
  point = { x: 3 };
} catch (error) {
  console.log(error.constructor.name);
}
