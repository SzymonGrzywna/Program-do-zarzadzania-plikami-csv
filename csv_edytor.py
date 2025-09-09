import sys
import os
import csv

POMOC = """
JAK UŻYWAĆ (prosto):
1) Zawsze podaj DWA pliki + przynajmniej JEDNĄ zmianę:
   python csv_edytor.py <wejscie.csv> <wyjscie.csv> x,y,wartosc [kolejne...]

2) Indeksy:
   x = kolumna od 0  (0=pierwsza, 1=druga, 2=trzecia...)
   y = wiersz od 0   (0=nagłówek, 1=pierwszy wiersz danych)

3) Nadpis oryginału = ta sama nazwa 2 razy:
   python csv_edytor.py in.csv in.csv x,y,wartosc

PRZYKŁADY NA TWOICH PLIKACH:
- Pokaż tabelę (no-op na nagłówku):
  python csv_edytor.py in.csv out.csv 0,0,auto

- Zmień pierwszy wiersz danych w in.csv na Lambo + 2025-09-09 + 7777:
  python csv_edytor.py in.csv in.csv 0,1,LamboFutreCollars 1,1,2025-09-09 2,1,7777

- Zmień cenę pierwszego filmu w filmy.csv na 35:
  python csv_edytor.py filmy.csv filmy.csv 2,1,35

WAŻNE:
- Jeśli WARTOŚĆ ma spacje → całą zmianę podaj w cudzysłowie, np. "0,1,Future Collars Movie".
"""

def uzycie():
    print(POMOC.strip())

def wczytaj_csv(sciezka):
    tabela = []
    try:
        with open(sciezka, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for wiersz in reader:
                tabela.append(list(wiersz))
    except FileNotFoundError:
        print(f"Błąd: nie znaleziono pliku wejściowego: {sciezka}", file=sys.stderr)
        sys.exit(2)
    except (PermissionError, IsADirectoryError) as e:
        print(f"Błąd: nie mogę odczytać pliku '{sciezka}': {e}", file=sys.stderr)
        sys.exit(2)
    return tabela

def zapisz_csv(sciezka, tabela):
    max_kol = max((len(w) for w in tabela), default=0)
    try:
        with open(sciezka, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for w in tabela:
                if len(w) < max_kol:
                    w = w + [""] * (max_kol - len(w))
                writer.writerow(w)
    except (PermissionError, IsADirectoryError) as e:
        print(f"Błąd: nie mogę zapisać pliku '{sciezka}': {e}", file=sys.stderr)
        sys.exit(2)

def parsuj_zmiane(tekst):

    czesci = tekst.split(",", 2)
    if len(czesci) < 3:
        raise ValueError(f"Zła składnia zmiany: '{tekst}'. Oczekiwano 'x,y,wartosc'.")
    x_str, y_str, wartosc = czesci
    try:
        x = int(x_str)
        y = int(y_str)
    except ValueError:
        raise ValueError(f"Indeksy muszą być liczbami całkowitymi: '{tekst}'.")
    if x < 0 or y < 0:
        raise ValueError(f"Indeksy nie mogą być ujemne: '{tekst}'.")
    return x, y, wartosc.strip()

def zastosuj_zmiany(tabela, zmiany):
    for z in zmiany:
        x, y, wartosc = parsuj_zmiane(z)
        while len(tabela) <= y:
            tabela.append([])
        wiersz = tabela[y]
        if len(wiersz) <= x:
            wiersz.extend([""] * (x + 1 - len(wiersz)))
        wiersz[x] = wartosc

# ----- WYDRUK TABELI -----
def _szerokosci_kolumn(tabela):
    if not tabela:
        return []
    max_kol = max(len(w) for w in tabela)
    szer = [0] * max_kol
    for w in tabela:
        for i in range(max_kol):
            wart = w[i] if i < len(w) else ""
            if len(wart) > szer[i]:
                szer[i] = len(wart)
    return [max(1, s) + 2 for s in szer]  # +2 margines

def _linia(szer, znak="-"):
    out = []
    for w in szer:
        out.append("+" + (znak * w))
    out.append("+")
    return "".join(out)

def _wiersz_centryczny(wiersz, szer):
    pola = []
    for i, w in enumerate(szer):
        tekst = wiersz[i] if i < len(wiersz) else ""
        pola.append("|" + tekst.center(w))
    pola.append("|")
    return "".join(pola)

def wypisz_tabele(tabela, naglowek=True, tytul=None):
    if not tabela:
        print("(pusty plik)")
        return
    szer = _szerokosci_kolumn(tabela)
    top = _linia(szer, "-")
    mid = _linia(szer, "=")
    bot = _linia(szer, "-")

    if tytul:
        print(tytul.center(len(top)))

    print(top)
    if naglowek and len(tabela) >= 1:
        print(_wiersz_centryczny(tabela[0], szer))
        print(mid)
        for w in tabela[1:]:
            print(_wiersz_centryczny(w, szer))
    else:
        for w in tabela:
            print(_wiersz_centryczny(w, szer))
    print(bot)

def main():

    if len(sys.argv) < 4:
        uzycie()
        sys.exit(1)

    plik_wejsciowy = sys.argv[1]
    plik_wyjsciowy = sys.argv[2]
    zmiany = sys.argv[3:]

    tabela = wczytaj_csv(plik_wejsciowy)

    try:
        zastosuj_zmiany(tabela, zmiany)
    except ValueError as e:
        print(f"Błąd: {e}", file=sys.stderr)
        sys.exit(3)

    wypisz_tabele(tabela, naglowek=True, tytul="=== ZAWARTOŚĆ PO ZMIANACH ===")
    zapisz_csv(plik_wyjsciowy, tabela)
    print(f"\nZapisano do: {os.path.abspath(plik_wyjsciowy)}")

if __name__ == "__main__":
    main()
