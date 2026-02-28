"""
Manages the lifecycle of multiple message consumers.

This module provides a `ConsumerManager` class that allows for centralized
control over starting and stopping a collection of consumer instances.
"""
from collections.abc import Sequence

from loguru import logger

from src.usecases.ports.consumer_interface import IConsumer


class ConsumerManager:
    """
    Manages the lifecycle of a collection of message consumers.

    This class centralizes the control of multiple consumers, allowing them
    to be started simultaneously. It is designed to be resilient, logging
    errors if a specific consumer fails to start but continuing with the
    others.

    Attributes:
        consumers: A sequence of consumer instances that implement the
            `IConsumer` interface.
    """

    def __init__(self, consumers: Sequence[IConsumer]):
        """
        Initializes the ConsumerManager with a sequence of consumers.

        Args:
            consumers: A sequence of objects that adhere to the `IConsumer`
                interface, each representing a message consumer.
        """
        self.consumers = consumers

    def start_all(self) -> None:
        """
        Starts the message consumption for all registered consumers.

        This method iterates through the list of consumers and calls the
        `start()` method on each one. It logs the start of the process and
        any errors encountered while starting a specific consumer.
        """
        logger.info(f"Starting {len(self.consumers)} consumers...")
        for consumer in self.consumers:
            try:
                consumer.start()
            except Exception as e:
                # Log the error but attempt to start the other consumers
                logger.error(f"Failed to start consumer {consumer}: {e}")
