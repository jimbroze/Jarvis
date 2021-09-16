FROM alpine
COPY binday.py /binday.py
COPY init.sh /init.sh
COPY crontab /crontab
RUN chmod 755 /crontab &&\
    /usr/bin/crontab /crontab
RUN apk add --no-cache bash
RUN apk add --update --no-cache python3  && ln -sf python3 /usr/bin/python
RUN apk add --update python3  && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --upgrade \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib
RUN mkdir /data
ENTRYPOINT ["bash", "/init.sh"]