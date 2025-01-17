# ElemTools

`ElemTools` — это Python-библиотека для работы с платформой [Element](https://elemsocial.com). Она предоставляет удобные инструменты для взаимодействия с API, включая отправку постов, обработку уведомлений и событий.

## Установка

Скачайте файл `elemtools.py` и добавьте его в ваш проект. Импортируйте класс `Element`:

```python
from elemtools import Element
```

## Быстрый старт

### Инициализация
Создайте экземпляр класса Element:
```
client = Element("Любой текст", Logs=True)
```

### Основные методы

#### Отправка поста
```
await element.send_post(
    text="Ваш текст поста",
    Censoring=False,          # Включение цензуры изображений (по умолчанию False)
    clearMetaData=True        # Очистка метаданных изображений (по умолчанию True)
)
```
### Загрузка постов
```
posts = await element.load_posts(F="LATEST", start_index=0)
```
```F``` — тип загружаемых постов (по умолчанию "LATEST", доступные значения: "LATEST", "TRENDING", и т.д.).
```start_index``` — начальный индекс загрузки (по умолчанию 0).

### Обработка уведомлений
Используйте декоратор @element.on_notification для создания обработчиков уведомлений.

```
@element.on_notification(action="PostComment")
async def handle_notification(event: dict):
    print("Получено уведомление:", event.notify)
```
### Обработка новых постов
Используйте декоратор @element.on_post для создания обработчиков новых постов.

```
@element.on_post(type="LATEST")
async def handle_post(post: dict):
    print("Новый пост:", post)
```
## Запуск
Для запуска и инициализации используйте метод run:

```
element.run("your_s_key")
```

Вместо your_s_key вы можете подставить свой ключ сессии <br>
Вместо your_s_key вы можете указать почта, пароль <br>
Вместо your_s_key вы можете ничего не указывать если файл с данными о сессии уже существует <br>
