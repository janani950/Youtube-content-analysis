FROM python:3.8-slim
COPY . /app
WORKDIR /app

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip3 install spacy
RUN python3 -m spacy download en_core_web_sm

EXPOSE 5000
CMD python script.py