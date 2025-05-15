# utils/custom_logger.py
import logging
import sys

class LogColors:  # Corrected class name casing
    GREY = "\x1b[38;20m"  # Adjusted for better visibility, can be "\x1b[90m" for simple grey
    BLUE = "\x1b[34;20m"  # Can be "\x1b[34m"
    YELLOW = "\x1b[33;20m"  # Can be "\x1b[33m"
    RED = "\x1b[31;20m"  # Can be "\x1b[31m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"


class ColoredFormatter(logging.Formatter):
    """
    A custom log formatter that adds colors to log levels for console output.
    """

    def __init__(self, fmt, datefmt=None, style='%'):  # style is the character %, {, or $
        super().__init__(fmt, datefmt, style)
        self._style_char = style  # Store the style character itself
        self.log_format_template = fmt  # Store the original format string

        # Define formats with color codes applied to the levelname part
        # This approach modifies the format string before creating the final formatter
        self.FORMATS = {
            logging.DEBUG: self.log_format_template.replace("%(levelname)-8s",
                                                            f"{LogColors.GREY}%(levelname)-8s{LogColors.RESET}"),
            logging.INFO: self.log_format_template.replace("%(levelname)-8s",
                                                           f"{LogColors.BLUE}%(levelname)-8s{LogColors.RESET}"),
            logging.WARNING: self.log_format_template.replace("%(levelname)-8s",
                                                              f"{LogColors.YELLOW}%(levelname)-8s{LogColors.RESET}"),
            logging.ERROR: self.log_format_template.replace("%(levelname)-8s",
                                                            f"{LogColors.RED}%(levelname)-8s{LogColors.RESET}"),
            logging.CRITICAL: self.log_format_template.replace("%(levelname)-8s",
                                                               f"{LogColors.BOLD_RED}%(levelname)-8s{LogColors.RESET}")
        }

    def format(self, record):
        # Get the format string with color codes for the specific log level
        log_fmt_with_color = self.FORMATS.get(record.levelno, self.log_format_template)

        # Create a new Formatter instance with the potentially colored format string
        # and the stored style character.
        formatter = logging.Formatter(fmt=log_fmt_with_color, datefmt=self.datefmt, style=self._style_char)
        return formatter.format(record)


class CustomLogger:
    def __init__(self, name: str, level: int = logging.DEBUG, log_to_file: bool = False,
                 log_file_path: str = "app.log"):
        """
        Initializes a custom logger with colored console output.

        Args:
            name (str): The name of the logger.
            level (int, optional): The logging level for the logger itself. Defaults to logging.DEBUG.
            log_to_file (bool, optional): Whether to log to a file. Defaults to False.
            log_file_path (str, optional): The path to the log file if log_to_file is True. Defaults to "app.log".
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        # Base log format (without colors for file, with placeholders for console)
        base_log_format = "%(asctime)s [%(levelname)-8s] %(name)s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"

        # Remove existing handlers to prevent duplication
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Console Handler with Colors
        # The ColoredFormatter's __init__ will use the default style '%'
        console_formatter = ColoredFormatter(fmt=base_log_format, datefmt=date_format)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # File Handler (without colors)
        if log_to_file:
            try:
                # For file, use a standard formatter without color codes
                file_formatter = logging.Formatter(fmt=base_log_format, datefmt=date_format,
                                                   style='%')  # Explicitly set style
                file_handler = logging.FileHandler(log_file_path, mode='a')
                file_handler.setLevel(level)
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)
            except Exception as e:
                print(f"ERROR: Failed to initialize file handler at {log_file_path}: {e}", file=sys.stderr)

    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs):
        is_exc_info_set_by_caller = 'exc_info' in kwargs
        if not is_exc_info_set_by_caller:
            current_exc_info = sys.exc_info()
            if current_exc_info[0] is not None:  # Check if an exception is actually active
                kwargs['exc_info'] = True  # Let logger handle fetching current_exc_info
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs):
        is_exc_info_set_by_caller = 'exc_info' in kwargs
        if not is_exc_info_set_by_caller:
            current_exc_info = sys.exc_info()
            if current_exc_info[0] is not None:  # Check if an exception is actually active
                kwargs['exc_info'] = True  # Let logger handle fetching current_exc_info
        self.logger.critical(message, *args, **kwargs)


logger = CustomLogger(name="fastapi_auth", level=logging.DEBUG, log_to_file=False)

