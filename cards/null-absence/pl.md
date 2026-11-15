---
title: Null, czyli brak wartości
summary: Jak język mówi „tu nic nie ma” i kiedy się o tym dowiadujesz.
source_hash: 4d766dc09eee
---

## Dlaczego jest różnie {#why}

Każdy język potrzebuje sposobu na powiedzenie „brak wartości”. Projekty różnią się w dwóch sprawach:
**ile** jest rodzajów niczego i **kiedy** dowiadujesz się, że któregoś dotknąłeś.

Python ma jeden: `None`, pojedynczy obiekt. Python nie zmyśla też wartości, gdy prosisz o coś, czego nie
ma: `user["email"]` zgłasza `KeyError`. Jeśli wolisz „nic” zamiast błędu, mówisz to wprost przez `.get()`.
Wynika to z zasady, którą Python głosi otwarcie: błędy nigdy nie powinny przechodzić po cichu.

JavaScript ma dwa: `undefined` („nikt tu nigdy niczego nie włożył”) i `null` („ktoś celowo włożył tu nic”).
Odczyt brakującej właściwości nie jest błędem; dostajesz `undefined` i program idzie dalej. Język
zaprojektowano w dziesięć dni w 1995 roku do skryptów na stronach, dla ludzi, którzy nie byli
programistami, i uznano, że strona działająca dalej jest lepsza niż strona, która staje.
`typeof null === "object"` to błąd z tej pierwszej wersji, którego nie da się już naprawić, bo zależą od
niego istniejące strony.

Oba języki dowiadują się w czasie działania. Żaden nie powie przed uruchomieniem programu, że wartości
może brakować. To jest prawdziwy koszt, a języki z dalszej części kursu (Rust oraz TypeScript nałożony na
JavaScript) przenoszą to sprawdzenie do kompilacji.

## Konsekwencje {#consequences}

- W Pythonie zły klucz wywraca program tam, gdzie jest pomyłka. W JavaScripcie `undefined` wędruje dalej
  i wywraca program później, w innym miejscu, z komunikatem „cannot read properties of undefined”.
- Kod w JavaScripcie wymaga nawyku: `?.` do czytania przez coś, czego może nie być, i `??` do podania
  wartości domyślnej. Oba dodano w 2020 roku, co pokazuje, jak długo żyło się z tym problemem.
- Interfejsy muszą ustalić, co znaczy „brak”. JSON ma `null`, a nie ma `undefined`, więc obiekt
  JavaScriptu traci przy wysyłce pola o wartości `undefined`.

## Pułapka {#trap}

Podawanie wartości domyślnej przez „lub”. `value or "default"` w Pythonie i `value || "default"`
w JavaScripcie zastępują **każdą wartość fałszywą**: `0`, `""`, pustą listę. Poprawna liczba zero staje się
„brakiem wartości”. W JavaScripcie użyj `??`. W Pythonie porównuj przez `is None`.

## Wyzwanie {#challenge}

Funkcja dostaje rekord użytkownika i ma zwrócić długość jego pseudonimu albo `0`, gdy pseudonimu nie ma.
Pusty pseudonim `""` jest poprawny i też ma długość `0`. Napisz ją w obu językach tak, żeby działała dla
rekordu bez tego pola, rekordu z `None` / `null` i rekordu z `""`. Potem wypisz każde miejsce, w którym
twoja pierwsza próba była błędna.
