import logging

# Basic configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# Test all levels
logger.debug("Debug message - checking variable values")
logger.info("Info message - app started successfully")
logger.warning("Warning message - amount is unusually high")
logger.error("Error message - could not save transaction")
logger.critical("Critical message - database connection lost")