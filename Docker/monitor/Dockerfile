FROM balenalib/raspberry-pi-debian:latest
RUN wget -O monitor.zip https://github.com/andrewjfreyer/monitor/archive/refs/heads/master.zip \
&& unzip monitor.zip \
&& mkdir -p /monitor \
&& mv monitor-master/* /monitor \
&& rm monitor.zip