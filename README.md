![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)


## `Проект Reviews`
Проект Reviews собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка». Например, в категории «Книги» могут быть произведения «Винни-Пух и все-все-все» и «Марсианские хроники», а в категории «Музыка» — песня «Давеча» группы «Жуки» и вторая сюита Баха. Список категорий может быть расширен (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»). 
Произведению может быть присвоен жанр из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). 
Добавлять произведения, категории и жанры может только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.
Пользователи могут оставлять комментарии к отзывам.
Добавлять отзывы, комментарии и ставить оценки могут только аутентифицированные пользователи.
____
[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%236BCF7&lines=Как+запустить+проект+Reviews:)](https://git.io/typing-svg)

`Выполнить клонирование`
```bash
git clone git@github.com:Evgeniya-Shokolova/reviews.git
```
`Перейти в папку с проектом` 
```bash
cd reviews
```
`Создать виртуальное окружение:`
   Команда для Windows: -
```bash
python -m venv venv
```
Команда для Linux и macOS: - 
```bash
python3 -m venv venv
```
`Активировать виртуальное окружение:`
   Команда для Windows: -
```bash
source venv/Scripts/activate
```
Для Linux и macOS: -
```bash
source venv/bin/activate
```
`Обновить пакетный менеджер:`
   Для Windows: -
```bash
python -m pip install --upgrade pip
```
Для Linux и macOS: -
```bash
python3 -m pip install --upgrade pip
```
Установить модули из файла requirementst.txt:`
```bash
pip install -r requirements.txt
```
`Выполнить миграции:`
```bash
python manage.py migrate
```
`Запустить приложение`
```bash
python manage.py runserver
```
____

#### Авторы:
`Произведения, категории, жанры, импорт данных из csv файлов - https://github.com/mvkondrashov`

`Отзывы, комментарии, рейтинг - https://github.com/Evgeniya-Shokolova`

`Авторизация и аутентификация, права доступа, пользователи - https://github.com/xlcox`