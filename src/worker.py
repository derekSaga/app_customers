import asyncio
import signal

from loguru import logger

from src.config.logging import configure_logging
from src.di.v1.consumers import get_consumer_manager


async def main() -> None:
    """
    Entrypoint para o Worker de Consumidores.
    Responsável por processar mensagens do Pub/Sub em background.
    """
    configure_logging()
    logger.info("🚀 Iniciando Worker de Consumidores...")

    # 1. Instancia o gerenciador e configura as dependências
    consumer_manager = await get_consumer_manager()

    # 2. Inicia as subscriptions (listeners)
    consumer_manager.start_all()

    # 3. Mantém o processo rodando indefinidamente
    # O Pub/Sub client roda em background tasks, então
    # precisamos travar o loop principal.
    stop_event = asyncio.Event()

    # Configura sinais do SO para encerramento gracioso (SIGINT/SIGTERM)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: stop_event.set())

    await stop_event.wait()
    logger.info("🛑 Encerrando Worker...")


if __name__ == "__main__":
    asyncio.run(main())
