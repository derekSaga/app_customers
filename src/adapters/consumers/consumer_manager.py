from collections.abc import Sequence

from loguru import logger

from src.usecases.ports.consumer_interface import IConsumer


class ConsumerManager:
    """
    Gerencia o ciclo de vida de múltiplos consumidores.
    Permite iniciar todos de uma vez, centralizando o controle.
    """

    def __init__(self, consumers: Sequence[IConsumer]):
        self.consumers = consumers

    def start_all(self) -> None:
        """Inicia o consumo de mensagens para 
        todos os consumidores registrados."""
        logger.info(f"Starting {len(self.consumers)} consumers...")
        for consumer in self.consumers:
            try:
                consumer.start()
            except Exception as e:
                # Loga o erro mas tenta iniciar os outros
                logger.error(f"Failed to start consumer {consumer}: {e}")