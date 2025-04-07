FROM python
#RUN mkdir -p /usr/src/app
#COPY . /usr/src/app
#WORKDIR /usr/src/app
COPY . .
WORKDIR /
RUN pip install --no-cache-dir -r requirements.txt
#RUN mkdocs build
#WORKDIR /usr/src/app/site
#CMD ["python", "-m", "http.server", "8000" ]
CMD ["python", "test.py" ]