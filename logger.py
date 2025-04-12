class Logger:
    """
    A simple logger class with multiple logging levels:
    - DEV: For development-related messages
    - INFO: For general information
    - WARNING: For potential issues
    - ERROR: For error conditions

    Usage:
    logger = Logger(min_level="INFO")
    logger.dev("This is a development message")
    logger.info("This is an information message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    """

    # Define log levels and their priorities
    LEVELS = {"DEV": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}

    def __init__(
        self, min_level="DEV", log_to_file=False, log_file_path="application.log"
    ):
        """
        Initialize the logger with a minimum log level.

        Args:
            min_level (str): Minimum log level ("DEV", "INFO", "WARNING", "ERROR")
            log_to_file (bool): Whether to log messages to a file
            log_file_path (str): Path to the log file if log_to_file is True
        """
        self.min_level = min_level.upper()
        self.log_to_file = log_to_file
        self.log_file_path = log_file_path

        if self.min_level not in self.LEVELS:
            raise ValueError(
                f"Invalid log level: {self.min_level}. Valid levels are: {', '.join(self.LEVELS.keys())}"
            )

        # Initialize log file if needed
        if self.log_to_file:
            with open(self.log_file_path, "a") as f:
                f.write(
                    f"===== Logger initialized with minimum level: {self.min_level} =====\n"
                )

    def _should_log(self, level):
        """Check if the message with the given level should be logged."""
        return self.LEVELS[level] >= self.LEVELS[self.min_level]

    def _log(self, level, message):
        """Internal method to handle logging."""
        if not self._should_log(level):
            return

        # Format the message with timestamp
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"

        # Print to console
        print(formatted_message)

        # Write to file if enabled
        if self.log_to_file:
            with open(self.log_file_path, "a") as f:
                f.write(formatted_message + "\n")

    def dev(self, message):
        """Log a development message."""
        self._log("DEV", message)

    def info(self, message):
        """Log an information message."""
        self._log("INFO", message)

    def warning(self, message):
        """Log a warning message."""
        self._log("WARNING", message)

    def error(self, message):
        """Log an error message."""
        self._log("ERROR", message)

    def set_level(self, level):
        """Change the minimum log level."""
        level = level.upper()
        if level not in self.LEVELS:
            raise ValueError(
                f"Invalid log level: {level}. Valid levels are: {', '.join(self.LEVELS.keys())}"
            )
        self.min_level = level


logger = Logger()
