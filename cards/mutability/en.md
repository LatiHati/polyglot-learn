---
title: Variables and mutability
summary: What a name really is, and who is allowed to change the thing it points at.
---

## Why they differ {#why}

Python and JavaScript agree on the basic model: a variable is a **name bound to an object**, not a box that
holds the object. Assigning `b = a` gives the same object a second name; nothing is copied. That is why
changing the list through `b` is visible through `a` in both examples.

They differ in where they put the brake.

Python attaches mutability to the **type**. A `list` can always be changed, a `tuple` or a `str` never can.
There is no keyword that makes a name constant; by convention `UPPER_CASE` means "do not reassign", and
nothing enforces it. This fits Python's design stance: few keywords, and trust in the reader.

JavaScript attaches the brake to the **binding**. `const` forbids giving the name a new value, and says
nothing about the object behind it. Freezing an object is a separate, explicit step (`Object.freeze`), and
it is shallow. `const` arrived in 2015, as a repair for `var`, whose scoping rules had caused bugs for
twenty years; the goal was safer names, not immutable data.

## Consequences {#consequences}

- Passing a list or an object to a function passes the same object. The function can change the caller's
  data. In both languages a copy must be asked for (`list(a)`, `[...a]`), and both copies are shallow.
- Immutable values can be shared freely, used as dictionary keys (Python requires this) and cached.
- Code that never mutates is easier to reason about and to run in parallel, at the cost of more copying.
  Languages that come later in this course (Rust) make that trade-off part of the type system.

## The trap {#trap}

**Python:** a default argument is evaluated once, when the function is defined. `def add_item(item, bucket=[])`
has one list for all calls, so the second call still sees `"x"`. Use `bucket=None` and create the list inside.

**JavaScript:** `const point = { x: 1 }` does not make the object constant. `point.x = 2` works. Only
`point = ...` fails. People read `const` as "this value never changes" and are surprised.

## Challenge {#challenge}

Write a function that takes a list of numbers and returns a new list with one number added, without
changing the list it was given. Then show, in the same file, that the original list is unchanged. Do it in
both languages. Which language made it easier to change the original by accident?
