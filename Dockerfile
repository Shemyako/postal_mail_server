FROM python:3.8



# Установка зависимостей
# Делаем отдельным процессом заранее, что бы не собирать окружение при каждой сборке контейнера
ADD requirements.txt ./
RUN pip install pip -U \
    && pip install --no-cache-dir -r requirements.txt


WORKDIR "/root/"

# Добавление файлов проекта в контейнер
ADD . ./


CMD [ "python", "-m", "main"]