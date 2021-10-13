message = data.get("message")
if not message:
    logger.error("No message provided")

# Send to the appropriate log level
received_level = str(data.get("level")).lower()
if received_level == "DEBUG":
    logger.debug(message)
elif received_level == "INFO":
    logger.info(message)
elif received_level == "WARNING":
    logger.warning(message)
elif received_level == "ERROR":
    logger.error(message)
elif received_level == "CRITICAL":
    logger.critical(message)
elif received_level == "FATAL":
    logger.fatal(message)
else:
    logger.info(message)
