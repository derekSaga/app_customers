import logging
import sys
from types import FrameType
from typing import TYPE_CHECKING

from asgi_correlation_id import correlation_id
from loguru import logger

if TYPE_CHECKING:
    from loguru import Record


from src.config.settings import settings


class InterceptHandler(logging.Handler):
    """
    Intercepta logs da biblioteca padrão `logging` e
    os redireciona para o `loguru`.
    Isso garante que logs de bibliotecas
    (como Uvicorn, SQLAlchemy) sejam formatados consistentemente.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Tenta obter o nível correspondente no Loguru
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        # Descobre a origem da chamada para manter a stack trace correta
        frame: FrameType | None = logging.currentframe()
        depth = 2
        while frame:
            filename = frame.f_code.co_filename
            module_name = frame.f_globals.get("__name__", "")

            is_logging = (
                filename == logging.__file__
                or module_name == "logging"
                or module_name.startswith("logging.")
            )
            is_this_file = filename == __file__

            if is_logging or is_this_file:
                frame = frame.f_back
                depth += 1
            else:
                break

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging() -> None:
    """
    Configura o Loguru e intercepta logs do sistema.
    Deve ser chamado no início da execução (Main e Worker).
    """
    # Define o nível de log (padrão INFO se não estiver nas settings)
    log_level = settings.LOG_LEVEL

    # Remove handlers padrão do Loguru
    logger.remove()

    # Intercepta logs da raiz e define o nível
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(log_level)

    # Remove handlers de loggers existentes para evitar duplicação
    # e garante que propaguem para o root (que é interceptado)
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Filtro para injetar Correlation ID (se disponível)
    def correlation_id_filter(record: "Record") -> bool:
        cid = correlation_id.get()
        record["extra"]["correlation_id"] = cid if cid else "N/A"
        return True

    log_format = (
        "<level>{level: <8}</level> | "
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<magenta>{extra[correlation_id]}</magenta> - "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stderr,
        level=log_level,
        format=log_format,
        filter=correlation_id_filter,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )
