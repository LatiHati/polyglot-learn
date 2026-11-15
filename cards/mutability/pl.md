---
title: Zmienne i mutowalność
summary: Czym naprawdę jest nazwa i kto ma prawo zmienić to, na co ona wskazuje.
source_hash: 03e5e1863eb9
---

## Dlaczego jest różnie {#why}

Python i JavaScript zgadzają się co do podstawowego modelu: zmienna to **nazwa przypięta do obiektu**, a nie
pudełko, w którym obiekt leży. Przypisanie `b = a` daje temu samemu obiektowi drugą nazwę; nic się nie
kopiuje. Dlatego w obu przykładach zmiana listy przez `b` jest widoczna przez `a`.

Różnią się tym, gdzie stawiają hamulec.

Python wiąże mutowalność z **typem**. Listę (`list`) zawsze można zmienić, krotki (`tuple`) i napisu (`str`)
nigdy. Nie ma słowa kluczowego, które robi z nazwy stałą; umownie `WIELKIE_LITERY` znaczą „nie przypisuj
ponownie” i nic tego nie pilnuje. To pasuje do założeń Pythona: mało słów kluczowych i zaufanie do
czytającego.

JavaScript wiąże hamulec z **wiązaniem nazwy**. `const` zabrania nadania nazwie nowej wartości i nie mówi
nic o obiekcie, który za nią stoi. Zamrożenie obiektu to osobny, jawny krok (`Object.freeze`) i działa tylko
na pierwszym poziomie. `const` pojawiło się w 2015 roku jako naprawa `var`, którego reguły zasięgu przez
dwadzieścia lat powodowały błędy; celem były bezpieczniejsze nazwy, a nie niezmienne dane.

## Konsekwencje {#consequences}

- Przekazanie listy albo obiektu do funkcji przekazuje ten sam obiekt. Funkcja może zmienić dane
  wywołującego. W obu językach o kopię trzeba poprosić (`list(a)`, `[...a]`) i obie kopie są płytkie.
- Wartości niemutowalne można swobodnie współdzielić, używać jako kluczy słownika (Python tego wymaga)
  i zapamiętywać w pamięci podręcznej.
- O kodzie, który niczego nie zmienia w miejscu, łatwiej się rozumuje i łatwiej uruchomić go równolegle,
  kosztem większej liczby kopii. Języki z dalszej części kursu (Rust) wpisują ten kompromis w system typów.

## Pułapka {#trap}

**Python:** argument domyślny jest obliczany raz, przy definiowaniu funkcji. `def add_item(item, bucket=[])`
ma jedną listę na wszystkie wywołania, więc drugie wywołanie nadal widzi `"x"`. Użyj `bucket=None` i twórz
listę w środku.

**JavaScript:** `const point = { x: 1 }` nie robi z obiektu stałej. `point.x = 2` działa. Nie działa tylko
`point = ...`. Ludzie czytają `const` jako „ta wartość się nie zmieni” i są zaskoczeni.

## Wyzwanie {#challenge}

Napisz funkcję, która dostaje listę liczb i zwraca nową listę z jedną dodaną liczbą, nie zmieniając listy,
którą dostała. Potem pokaż w tym samym pliku, że pierwotna lista jest nietknięta. Zrób to w obu językach.
W którym łatwiej było zmienić oryginał przez przypadek?
