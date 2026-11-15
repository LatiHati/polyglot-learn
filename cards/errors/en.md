---
title: Errors
summary: What happens when something goes wrong, and who has to notice.
---

## Why they differ {#why}

Python and JavaScript both use **exceptions**: an error interrupts the normal flow and climbs up the call
stack until some `try` block catches it. `finally` runs either way. On the surface the two examples are
the same program.

The difference is in what the standard library considers an error.

Python raises early. `int("abc")` is a `ValueError`. The common Python style even has a name, "easier to
ask forgiveness than permission": try the operation and handle the exception, instead of checking first.
Exceptions are cheap enough in Python to be used for ordinary control flow; a `for` loop ends because an
iterator raises `StopIteration`.

JavaScript often returns a **special value** instead. `Number.parseInt("abc")` is `NaN`, a missing property
is `undefined`, dividing by zero is `Infinity`. The program keeps going and it is the caller's job to
check. The example has to test for `NaN` and throw by hand to get the behaviour Python gives for free.
JavaScript also lets you throw anything, a string or a number, so a `catch` block cannot assume it
received an `Error`.

Neither language shows in a function's signature that it can fail. You find out from the documentation or
in production. Go and Rust, later in this course, put failure into the return type instead, and the
compiler makes the caller deal with it.

## Consequences {#consequences}

- Python code tends to fail close to the cause. JavaScript code tends to carry a bad value (`NaN`,
  `undefined`) for a while and fail far from the cause, or not at all and produce a wrong result.
- In both, an exception nobody catches ends the program, or in a server ends the request. Decide on
  purpose where the last line of defence is.
- Asynchronous JavaScript adds a second channel: a rejected promise. A `try` block catches it only with
  `await`. Forgetting `await` loses the error.

## The trap {#trap}

**Python:** catching too much. `except Exception:` around a block also catches bugs inside the block. In
the example the handler reports a bad age, while the real problem is calling `.upper()` on a number.
Catch the narrowest type you can handle.

**JavaScript:** `Number.parseInt("12abc")` returns `12`. It reads as far as it can and reports success.
`Number("12abc")` returns `NaN`. Know which one you are using when you validate input.

## Challenge {#challenge}

Write a function that reads a list of strings and returns the sum of those that are valid whole numbers,
together with the list of strings it had to skip. `"12abc"` must be skipped in both languages. How many
lines did each language need to refuse `"12abc"`?
