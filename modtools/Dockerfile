FROM python:3.7

COPY . /modtools
WORKDIR /modtools

RUN pip install pipenv

RUN pipenv install --system --deploy

CMD ["python", "inserts.py"]
