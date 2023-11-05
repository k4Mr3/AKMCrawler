import requests
import os
import time
import threading
from bs4 import BeautifulSoup

# Funkcja do pobierania zawartości strony internetowej i zapisywania jej do pliku z limitem czasu
def fetch_and_save_url_with_timeout(url, output_file, timeout=15):
    try:
        start_time = time.time()
        response = requests.get(url + "full/2000,/0/default.jpg", timeout=timeout)
        elapsed_time = time.time() - start_time
        if response.status_code == 200:
            with open(output_file, 'wb') as file:
                file.write(response.content)
            print(f'Pobrano i zapisano zawartość z {url} do {output_file} (czas: {elapsed_time:.2f} sekundy)')
        else:
            print(f'Nie udało się pobrać zawartości z {url}. Kod odpowiedzi: {response.status_code}')
    except requests.exceptions.Timeout:
        print(f'Przekroczono limit czasu ({timeout} sekundy) podczas pobierania z {url}. Rozpoczynam ponowną próbę.')
        fetch_and_save_url_with_timeout(url, output_file, timeout)  # Ponowne próbowanie

# Funkcja wątkowa do pobierania zawartości
def download_thread(url, output_file, timeout, semaphore):
    with semaphore:
       if not os.path.exists(output_file):
           fetch_and_save_url_with_timeout(url, output_file, timeout)
       else:
           print(f'Plik {output_file} już istnieje. Pomijam pobieranie.')


# Funkcja do pobierania zawartości strony internetowej
def pobierz_zawartosc_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Nie można pobrać zawartości URL: {e}")
        return None

# URL, który chcesz przeszukać
url_tab = [["https://caak.upjp2.edu.pl/j/5ebd26166268a00a20b4b9f5/s/0/f", "AG15"]]


ilosc = len(url_tab)

for x in range(ilosc):

    url = url_tab[x][0]
    nazwa_ksiegi = url_tab[x][1]

    # Pobierz zawartość strony
    zawartosc = pobierz_zawartosc_url(url)

    if zawartosc is not None:
        soup = BeautifulSoup(zawartosc, 'html.parser')

        # Znajdź wszystkie elementy <img> z atrybutem data-src
        img_elements = soup.find_all('img')

        urls = []

        for img in img_elements:
            data_src = img.get('data-src')
            if (data_src):
                czesci_url = data_src.split("full")
                urls.append(czesci_url[0])


    # Dowolny ciąg znaków, który dokleimy do adresów URL
    custom_suffix = ".jpg"

    # Lista wątków
    threads = []

    index=0

    # Ograniczenie liczby wątków do 4
    semaphore = threading.Semaphore(4)

    if not os.path.exists(nazwa_ksiegi):
        os.makedirs(nazwa_ksiegi)
        print(f"Folder '{nazwa_ksiegi}' został utworzony.")
    else:
        print(f"Folder '{nazwa_ksiegi}' już istnieje.")

    # Przetwarzamy każdą linię z pliku wejściowego
    for u in urls:
        url = u.strip()  # Usuwamy białe znaki na początku i końcu linii
        index+=1
        output_file = str(index) + custom_suffix  # Tworzymy nazwę pliku na podstawie adresu URL

        # Tworzymy i uruchamiamy nowy wątek dla każdej linii
        thread = threading.Thread(target=download_thread, args=(url, nazwa_ksiegi + '/' + output_file, 25, semaphore))
        thread.start()
        threads.append(thread)

    # Oczekiwanie na zakończenie wszystkich wątków
    for thread in threads:
        thread.join()

print("Wszystkie pliki zostały pobrane.")
