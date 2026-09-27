"""One log format for every service, so logs from all containers can be read and searched together."""

import logging

from common.middleware import current_request_id

LOG_FORMAT = "%(asctime)s %(levelname)s service=%(service)s request_id=%(request_id)s %(name)s: %(message)s"


class _ContextFilter(logging.Filter):
    """Adds the service name and current request ID to every log record."""

    def __init__(self, service_name: str):
        super().__init__()
        self.service_name = service_name

    def filter(self, record: logging.LogRecord) -> bool:
        record.service = self.service_name
        record.request_id = current_request_id() or "-"
        return True


def setup_logging(service_name: str, level: str = "INFO") -> None:
    """Configure root logging once at startup.

    Args:
        service_name: shown in every line, e.g. "documents-service".
        level: minimum level to log (DEBUG, INFO, WARNING, ERROR).
    """
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.addFilter(_ContextFilter(service_name))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
