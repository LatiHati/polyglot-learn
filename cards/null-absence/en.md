---
title: Null, or the absence of a value
summary: How a language says "there is nothing here", and when you find out.
---

## Why they differ {#why}

Every language needs a way to say "no value". The designs differ on two questions: **how many** kinds of
nothing there are, and **when** you are told that you touched one.

Python has one: `None`, a single object. Python also refuses to invent a value when you ask for something
that does not exist: `user["email"]` raises `KeyError`. If you want "nothing" instead of an error you say so,
with `.get()`. This follows a rule Python states openly: errors should never pass silently.

JavaScript has two: `undefined` ("nothing was ever put here") and `null` ("someone put nothing here on
purpose"). Reading a missing property is not an error; you get `undefined` and the program goes on. The
language was designed in ten days in 1995 to script web pages, for people who were not programmers, and a
page that keeps running was judged better than a page that stops. `typeof null === "object"` is a bug from
that first version that can no longer be fixed, because existing pages depend on it.

Both languages find out at run time. Neither can tell you before the program runs that a value may be
missing. That is the real cost, and languages later in this course (Rust, and TypeScript on top of
JavaScript) move the check to compile time.

## Consequences {#consequences}

- In Python a wrong key fails where the mistake is. In JavaScript the `undefined` travels on and fails
  later, somewhere else, with "cannot read properties of undefined".
- JavaScript code needs a habit: `?.` to read through something that may be missing, `??` to supply a
  default. Both were added in 2020, which shows how long the problem was lived with.
- APIs must decide what "missing" means. JSON has `null` and has no `undefined`, so a JavaScript object
  loses its `undefined` fields when it is sent.

## The trap {#trap}

Using "or" to supply a default. `value or "default"` in Python and `value || "default"` in JavaScript
replace **every falsy value**: `0`, `""`, an empty list. A valid count of zero becomes "no value". In
JavaScript use `??`. In Python compare with `is None`.

## Challenge {#challenge}

A function receives a user record and must return the length of the user's nickname, or `0` when there is
no nickname. An empty nickname `""` is valid and has length `0` too. Write it in both languages so that a
record without the field, a record with `None` / `null` and a record with `""` all work. Then list every
place where your first attempt was wrong.
