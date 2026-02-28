"""
Consumer Worker Entrypoint.

This module is responsible for initializing and running the message consumers
that process background tasks from a Pub/Sub subscription.

It sets up the necessary components, starts the consumers, and handles
graceful shutdown on receiving SIGINT or SIGTERM signals.
"""
import asyncio
import signal

from loguru import logger

from src.config.logging import configure_logging
from src.di.v1.consumers import get_consumer_manager


async def main() -> None:
    """
    Asynchronous main function to run the consumer worker.

    This function performs the following steps:
    1. Configures application-wide logging.
    2. Retrieves the configured consumer manager via dependency injection.
    3. Starts all registered consumers, which begin listening for messages.
    4. Waits for a shutdown signal (SIGINT or SIGTERM) to gracefully
       stop the worker.
    """
    configure_logging()
    logger.info("🚀 Starting Consumer Worker...")

    # 1. Instantiate the manager and configure dependencies
    consumer_manager = await get_consumer_manager()

    # 2. Start all subscriptions (listeners)
    consumer_manager.start_all()

    # 3. Keep the process running indefinitely.
    # The Pub/Sub client runs in background tasks, so we need to block
    # the main loop to prevent the script from exiting.
    stop_event = asyncio.Event()

    # Configure OS signals for graceful shutdown (SIGINT/SIGTERM)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    logger.info("Worker is running. Waiting for shutdown signal...")
    await stop_event.wait()

    logger.info("🛑 Shutting down Worker...")
    # Note: The Pub/Sub client's background threads are daemonic and will
    # exit when the main thread exits. For more complex shutdown logic,
    # you might need to explicitly stop the consumers.


if __name__ == "__main__":
    asyncio.run(main())
