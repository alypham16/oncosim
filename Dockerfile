FROM python:3.12

COPY . /code

WORKDIR /code

RUN pip install numpy pandas scipy scikit-learn matplotlib seaborn
