## 1. Nazwy Klas
- Używaj **PascalCase** dla nazw klas w Pythonie.
- Przykład: `EventManager`, `UserService`.

## 2. Nazwy Plików
- Używaj **snake_case** dla nazw plików w Pythonie.
- Przykład: `event_manager.py`, `user_service.py`.
- Pliki z definicjami schematów powinny być nazwane zgodnie z ich funkcją, na przykład: `events_schema.py`, `users_schema.py`.

## 3. Nazwy Funkcji
- Używaj **snake_case** dla nazw funkcji.
- Przykład: `create_event()`, `get_user_by_id()`.

## 4. Nazwy Zmiennych
- Używaj **snake_case** dla nazw zmiennych.
- Przykład: `event_id`, `user_details`.

## 5. Konfiguracja Baz Danych
- Pliki konfiguracyjne bazy danych powinny być nazwane zgodnie z ich funkcją.
- Przykład: `postgres_config.py`, `database_setup.py`.

## 6. Schematy Pydantic
- Używaj **PascalCase** dla nazw schematów Pydantic.
- Przykład: `CreateEventSchema`, `ResponseUserSchema`.

## 7. Obsługa Błędów
- Używaj klas z prefiksem `Error` dla klas wyjątków niestandardowych.
- Przykład: `DetailedHTTPError`, `DatabaseConnectionError`.

## 8. Wzorce Nazewnictwa dla CRUD
- Funkcje CRUD powinny być nazwane w standardowym formacie: `create_<resource>()`, `read_<resource>()`, `update_<resource>()`, `delete_<resource>()`.
- Przykład: `create_event()`, `get_events()`.
