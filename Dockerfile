# Используйте официальный образ Python как родительский образ
FROM python:3.11-rc-bullseye

# Устанавливаем graphviz и обновляем pip
RUN apt-get update && apt-get install -y graphviz && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

# Задаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы зависимостей и устанавливаем их
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Копируем остальные файлы проекта
COPY . .

# Открываем порты для доступа к JupyterLab и Streamlit
EXPOSE 8501 8888
