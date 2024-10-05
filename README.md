# BE_Web-application-for-managing-personal-finances

## OPIS
Aplikacja backendowa do pracy inżynierskiej. 

___
## SPIS TREŚCI
1. [Struktura](docs/structure.md)
2. [Nazewnictwo](docs/naming-conventions.md)
3. [Wymagania](docs/requirements.md)

### Biblioteki
Wszystkie biblioteki znajdują się w pliku `requirements.txt`
Jeśli chcesz zainstalować wszystkie biblioteki lokalnie, użyj poniższej komendy:

### MinIO
Po uruchomieniu aplikacji w dockerze, a jeszcze przed testowaniem jej trzeba dodać do MinIO
odpowiednie:
- access_key: 7dOXZzemYbchFtAe5glj
- secret_key: 14ale6huGncR2HCPMDg7lJgmiqsa0pinPyKy2IRx


Aby dodać te klucze do MinIO:
1. Po uruchomieniu dockera przejdź do: http://localhost:9001/ 
2. Zaloguj się: 
   - user: minioadmin
   - password: minioadminpass
3. Przejdź do Access Keys -> Create access key i dodaj wartości jak wyżej.


## 1. Docker
**Rozwiązanie zalecane**
1. Zainstaluj Docker Desktop
2. Otwórz terminal w folderze z plikiem `docker-compose.yml` (katalog główny projektu)
3. Przekopiuj plik `.env.development` do `.env` i uzupełnij dane jeśli trzeba
```shell
cp .env.development .env
```
4. Uruchom poniższą komendę:
```shell
docker compose up
```
5. Aplikacja będzie dostępna pod adresem `http://localhost:5000`

W przypadku zmian w docker-compose.yml, aby zaktualizować kontenery, użyj poniższej komendy:
```shell
docker compose up --build
```
## 2. Lokalnie
1. Zainstaluj Python 3.11
2. Zainstaluj wszystkie biblioteki z pliku `requirements.txt`:
```shell
pip install -r requirements.txt
```
3. Uruchom aplikację:
```shell
uvicorn main:app --reload
```
4. Aplikacja będzie dostępna pod adresem `http://localhost:8000`
5. Redisa i Postgresa można uruchomić lokalnie lub z Dockerem

## 3. DBeaver
- Database -> New Database Connection -> PostgreSQL
- Database: sumy, Username: postgres, Pass: sumysecretpasswd
- Test Connection -> Finish

## 4. SQL
Nie używamy już sqla, bo jest dla lamusy. Od tego jest ORM.
Jeśli robimy jakąś zmianę w modelu, to trzeba zrobić migrację:
```shell
alembic revision --autogenerate -m "nazwa migracji"
alembic upgrade head
```
`alembic upgrade head` - wykonuje wszystkie migracje
Jest dodany do docker-compose, przy starcie więc jeśli zaciągniecie zmiany to nie musicie się martwić o migracje.

Jeśli chcecie zrobić migrację lokalnie, to musicie zainstalować `alembic` o ile nie macie go zainstalowanego z requirements.txt:
```shell
pip install alembic
```

Aby cofnąć migrację:
```shell
alembic downgrade -1
```

Jeśli dodajecie nowy model, to musicie go dodać do `database/__init__.py` tak jak pozostałe modele.

## API
Terminal:

W razie problemów [tutorial](https://fastapi.tiangolo.com/tutorial/first-steps/)

[Testowanie API - Swagger](http://127.0.0.1:8000/docs)

