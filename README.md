В данном web-app вы можете создавать наборы тестов через админ панель, также проходить тесты и видеть результат.

!!! Перед запуском Docker обязательно переименуйте файл:

example.env -> .env

*Если вы не переименуете файл и запустите docker-compose, будет ошибка переменных окружения. Для исправления ошибки удалите все связанные с проектом containers и image из Docker'a. Затем переименуйте файл и заново запустите docker-compose.

Запуск проекта: 

docker-compose up

Остановка проекта: 

docker-compose stop

В проекте уже примененины миграции и добавлено несколько групп тестов.