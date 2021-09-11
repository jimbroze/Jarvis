FROM alpine
COPY binday.py /binday.py
RUN apk add --update --no-cache python3  && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --upgrade \
    google-api-python-client \
    google-auth-httplib2 \
    google-auth-oauthlib
RUN mkdir /data
ENTRYPOINT ["python3", "/binday.py"]