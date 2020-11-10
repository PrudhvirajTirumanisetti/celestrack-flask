FROM python:3
MAINTAINER PrudhviRaj Tirumanisetti
RUN pip3 install flask ephem requests geopy 
RUN apt-get update && apt-get clean 
COPY ./templates /assignment/templates
COPY ./*.py /assignment/
WORKDIR /assignment
EXPOSE 8900
CMD ["python", "-u", "app.py"]