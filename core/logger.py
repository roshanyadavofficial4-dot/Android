import logging
import os
import sys

class AryaLogger:
    def __init__(self):
        self.log_dir = os.path.join(os.environ.get("HOME", "."), "logs")
        self.log_file = os.path.join(self.log_dir, "arya.log")
        self._setup_logger()

    def _setup_logger(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger = logging.getLogger("ARYA_OS")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # File Handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        self.logger.info("Logger initialized. I am awake, Sir, and recording my every brilliant thought.")

    def get_logger(self):
        return self.logger

# Singleton instance for easy access
arya_logger = AryaLogger().get_logger()
