[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/CDl7acob)
# Задание к курсовому проекту

Реализовать клиент-серверное приложение на FastAPI для мониторинга состояния компьютера.

Отслеживаемые параметры:

1. [done] CPU
   1. [done] Средняя загрузка
   2. [done] Загрузка по ядрам
   3. [done] Информация о процессоре, частотам и количеству ядер
2. [done] RAM
   1. [done] Memory
   2. [done] Swap
   3. [done] Информация об объеме памяти
3. [ ] Дисковое пространство
   1. [ ] Информация о томах и их объеме
   2. [ ] Использование дисков (запись/чтение)
4. [ ] Network
   1. [ ] Скорость отправки/загрузки
   2. [ ] Количество переданных данных
   3. [ ] Список подключений
5. [ ] Температуры

Приложение должно состоять из двух модулей:

1. API
   1. Возможность запросить информацию о любом параметре состояния системы
   2. Возможность получить общую краткую справку о состоянии системы
2. Dashboard
   1. Отображение информации о состоянии в реальном времени
   2. Возможность интерактивно изменять параметры отображения (частоту обновления, отображаемые данные и тп)
   3. Показывать предупреждение в случае превышения установленных порогов загрузки

Из дополнительных функций должно быть реализовано:

- [ ] Авторизация пользователя
- [ ] Тестирование (покрытие не менее 50%)
- [ ] Сохранение пользовательских настроек

> Проект должен содержать логичную структуру файлов, быть читаемым и понятным.