FROM eclipse-mosquitto:latest
ARG USER
ARG PASSWORD
# MKDIR /mosquitto/config/
RUN mosquitto_passwd -c -b /passwd $USER $PASSWORD