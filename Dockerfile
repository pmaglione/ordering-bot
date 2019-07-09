FROM python:3.7

#creating directory helloworld in container (linux machine)
RUN mkdir c:\home\bot

#copying files from local directory to container
COPY check_change_module.py /home/bot/check_change_module.py

#setup requeriments
RUN pip3 install -U spacy
RUN python3 -m spacy download en_core_web_lg
RUN pip3 install tabulate

#running script in container
ENTRYPOINT ["python3", "/home/bot/check_change_module.py"]
