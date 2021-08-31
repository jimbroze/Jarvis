FROM ghcr.io/linuxserver/duckdns
ARG SUBDOMAINS
ARG TOKEN
RUN echo url="https://www.duckdns.org/update?domains=${SUBDOMAINS}&token=${TOKEN}&ip=" | curl -v -k -K -
