FROM python:3.6
WORKDIR /web-shoppingmall
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 9000
CMD ["python3", "-m" , "flask", "run", "-p", "9000", "--host=0.0.0.0"]