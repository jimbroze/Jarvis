FROM eclipse-mosquitto:latest
ARG PASSWORD
# MKDIR /mosquitto/config/
RUN mosquitto_passwd -c -b /passwd homeassistant $PASSWORD