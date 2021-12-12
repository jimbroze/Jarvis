FROM balenalib/raspberrypi3-64-debian:latest
RUN install_packages \
  wget \
  unzip

#Install monitor deps
RUN install_packages \
  mosquitto-clients \
  bluez \
  bluez-hcidump \
  bc \
  usbutils \
  ca-certificates \
  curl \
  bluetooth

RUN wget -O monitor.zip https://github.com/andrewjfreyer/monitor/archive/refs/heads/master.zip \
  && unzip monitor.zip \
  && mkdir -p /monitor \
  && mv monitor-master/* /monitor \
  && rm monitor.zip

COPY init.sh /
RUN chmod +x /init.sh
ENTRYPOINT ["/init.sh"]

WORKDIR /monitor

CMD ["bash", "monitor.sh"]