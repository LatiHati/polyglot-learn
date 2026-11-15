---
title: Błędy
summary: Co się dzieje, gdy coś idzie źle, i kto musi to zauważyć.
source_hash: d86ab1e14277
---

## Dlaczego jest różnie {#why}

Python i JavaScript używają **wyjątków**: błąd przerywa zwykły bieg programu i wspina się po stosie
wywołań, aż złapie go jakiś blok `try`. `finally` wykonuje się w obu przypadkach. Na pierwszy rzut oka oba
przykłady to ten sam program.

Różnica leży w tym, co biblioteka standardowa uznaje za błąd.

Python zgłasza błąd wcześnie. `int("abc")` to `ValueError`. Typowy styl Pythona ma nawet nazwę: „łatwiej
prosić o wybaczenie niż o pozwolenie” — spróbuj wykonać operację i obsłuż wyjątek, zamiast najpierw
sprawdzać. Wyjątki są w Pythonie na tyle tanie, że służą do zwykłego sterowania przebiegiem; pętla `for`
kończy się, bo iterator zgłasza `StopIteration`.

JavaScript często zwraca zamiast tego **wartość specjalną**. `Number.parseInt("abc")` to `NaN`, brakująca
właściwość to `undefined`, dzielenie przez zero to `Infinity`. Program idzie dalej, a sprawdzenie należy do
wywołującego. Przykład musi sam wykryć `NaN` i ręcznie zgłosić wyjątek, żeby uzyskać zachowanie, które
Python daje za darmo. JavaScript pozwala też rzucić czymkolwiek, napisem albo liczbą, więc blok `catch`
nie może zakładać, że dostał obiekt `Error`.

Żaden z tych języków nie pokazuje w sygnaturze funkcji, że może się ona nie udać. Dowiadujesz się tego
z dokumentacji albo na produkcji. Go i Rust, w dalszej części kursu, wpisują niepowodzenie w typ zwracany,
a kompilator zmusza wywołującego, żeby się nim zajął.

## Konsekwencje {#consequences}

- Kod w Pythonie zwykle wywraca się blisko przyczyny. Kod w JavaScripcie zwykle niesie przez jakiś czas
  złą wartość (`NaN`, `undefined`) i wywraca się daleko od przyczyny albo wcale, dając zły wynik.
- W obu językach wyjątek, którego nikt nie złapał, kończy program, a na serwerze kończy żądanie. Ustal
  świadomie, gdzie jest ostatnia linia obrony.
- Asynchroniczny JavaScript dodaje drugi kanał: odrzuconą obietnicę (promise). Blok `try` łapie ją tylko
  z `await`. Zapomniane `await` gubi błąd.

## Pułapka {#trap}

**Python:** łapanie zbyt szeroko. `except Exception:` wokół bloku łapie też błędy programisty w tym
bloku. W przykładzie obsługa zgłasza zły wiek, a prawdziwym problemem jest wywołanie `.upper()` na
liczbie. Łap najwęższy typ, jaki umiesz obsłużyć.

**JavaScript:** `Number.parseInt("12abc")` zwraca `12`. Czyta tak daleko, jak się da, i zgłasza sukces.
`Number("12abc")` zwraca `NaN`. Wiedz, którego używasz przy sprawdzaniu danych wejściowych.

## Wyzwanie {#challenge}

Napisz funkcję, która czyta listę napisów i zwraca sumę tych, które są poprawnymi liczbami całkowitymi,
razem z listą napisów, które musiała pominąć. `"12abc"` ma być pominięte w obu językach. Ilu linii
potrzebował każdy język, żeby odrzucić `"12abc"`?
