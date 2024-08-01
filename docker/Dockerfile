FROM node:20.15.1 as frontend
ADD . /app
WORKDIR /app/admin-frontend
RUN yarn && yarn build

FROM python:3.11
COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh
COPY ./docker/gunicorn_conf.py /gunicorn_conf.py
RUN python3 -m pip install poetry && poetry config virtualenvs.create false
WORKDIR /app
COPY ./README.md ./pyproject.toml ./poetry.lock* /app/
RUN poetry install --only=main,docker
ADD src /app/src
ADD bot.py /app/
COPY --from=frontend /app/nonebot_bison/admin_page/dist /app/nonebot_bison/admin_page/dist
ENV HOST=0.0.0.0
CMD ["/start.sh"]
