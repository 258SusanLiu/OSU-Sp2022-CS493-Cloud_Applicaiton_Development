FROM python:3.9
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
ENV PORT=8000
EXPOSE ${PORT}
ENV GOOGLE_APPLICATION_CREDENTIALS='./docking-350805-a5fc174bb1f2.json'
CMD [ "python", "main.py" ]