FROM acockburn/appdaemon:latest
RUN wget -O R64.zip https://github.com/Leapo/Rock64-R64.GPIO/archive/refs/heads/master.zip \
&& unzip R64.zip \
&& mkdir -p /conf/apps/R64 \
&& mv Rock64-R64.GPIO-master/R64 /conf/apps/R64 \
&& rm R64.zip

# ENTRYPOINT ["./dockerStart.sh"]