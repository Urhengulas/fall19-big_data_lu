FROM ubuntu:18.04
MAINTAINER Stefanie Schroeck, Oliver Grasl
RUN apt-get update && apt-get install -y apt-transport-https
RUN apt-get update && apt-get install python3-pip python3 nodejs npm -y
RUN mkdir /showcase_big_data/
RUN mkdir /showcase_big_data/csv/
RUN mkdir /showcase_big_data/src/
RUN mkdir /showcase_big_data/scenarios/
RUN mkdir /showcase_big_data/notebooks/
RUN mkdir /showcase_big_data/models/
COPY ./scenarios /showcase_big_data/scenarios
COPY ./models /showcase_big_data/models
COPY ./requirements.txt /showcase_big_data
COPY ./README.md /showcase_big_data 
WORKDIR /showcase_big_data 
RUN pip3 install -r requirements.txt
RUN jupyter labextension install @jupyter-widgets/jupyterlab-manager
RUN jupyter nbextension enable --py widgetsnbextension
CMD /usr/local/bin/jupyter lab --NotebookApp.token='' --allow-root --ip=0.0.0.0
