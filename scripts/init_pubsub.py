import os

from google.api_core.exceptions import AlreadyExists
from google.cloud import pubsub_v1
from loguru import logger

# Tenta importar settings, fallback para variáveis de ambiente ou defaults
try:
    from src.config.settings import settings

    PROJECT_ID = settings.PUBSUB_PROJECT_ID

    # Defina aqui a lista de tópicos baseada nas settings ou strings diretas
    TOPICS_CONFIG = [
        {
            "topic": settings.CUSTOMER_CREATE_TOPIC,
            "subscription": settings.CUSTOMER_CREATE_TOPIC_SUBSCRIPTION,
        },
        # Adicione novos tópicos aqui:
        # {"topic": "order-created", "subscription": "order-created-sub"},
    ]
except ImportError:
    PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "seu-projeto-gcp")
    TOPICS_CONFIG = [
        {"topic": "customer-created", "subscription": "customer-created-sub"}
    ]


def create_topic(
    publisher: pubsub_v1.PublisherClient, topic_path: str
) -> None:
    """Cria um tópico se não existir."""
    try:
        publisher.create_topic(request={"name": topic_path})
        logger.info(f"Tópico criado: {topic_path}")
    except AlreadyExists:
        logger.warning(f"Tópico já existe: {topic_path}")


def create_subscription(
    subscriber: pubsub_v1.SubscriberClient,
    subscription_path: str,
    topic_path: str,
    dead_letter_policy: dict[str, str] | None = None,
) -> None:
    """Cria uma subscription se não existir."""
    try:
        request = {
            "name": subscription_path,
            "topic": topic_path,
            "ack_deadline_seconds": 60,
        }

        if dead_letter_policy:
            request["dead_letter_policy"] = dead_letter_policy

        subscriber.create_subscription(request=request)
        logger.info(f"Subscription criada: {subscription_path}")
    except AlreadyExists:
        logger.warning(f"Subscription já existe: {subscription_path}")

        # Opcional: Atualizar a política de DLQ se a subscription já existir
        if dead_letter_policy:
            update_request = {
                "subscription": {
                    "name": subscription_path,
                    "dead_letter_policy": dead_letter_policy,
                },
                "update_mask": {"paths": ["dead_letter_policy"]},
            }
            try:
                subscriber.update_subscription(request=update_request)
                logger.info(
                    "Subscription atualizada com "
                    f"DLQ policy: {subscription_path}"
                )
            except Exception as e:
                logger.error(f"Erro ao atualizar subscription existente: {e}")


def setup_topic_resources(
    publisher: pubsub_v1.PublisherClient,
    subscriber: pubsub_v1.SubscriberClient,
    config: dict[str, str],
) -> None:
    """Configura Tópico, Subscription e DLQ para
    uma entrada de configuração."""
    topic_name = config["topic"]
    sub_name = config["subscription"]

    # Nomes DLQ
    dlq_topic_name = f"{topic_name}-dlq"
    dlq_sub_name = f"{sub_name}-dlq"

    # Caminhos completos
    main_topic_path = publisher.topic_path(PROJECT_ID, topic_name)
    main_sub_path = subscriber.subscription_path(PROJECT_ID, sub_name)

    dlq_topic_path = publisher.topic_path(PROJECT_ID, dlq_topic_name)
    dlq_sub_path = subscriber.subscription_path(PROJECT_ID, dlq_sub_name)

    # 1. Criar Tópico DLQ
    create_topic(publisher, dlq_topic_path)

    # 2. Criar Subscription da DLQ
    # DLQs geralmente não têm outra DLQ, então sem policy aqui.
    create_subscription(subscriber, dlq_sub_path, dlq_topic_path)

    # 3. Criar Tópico Principal
    create_topic(publisher, main_topic_path)

    # 4. Criar Subscription Principal apontando para a DLQ
    # Configura para enviar para a DLQ após 5 tentativas falhas
    dlq_policy = {
        "dead_letter_topic": dlq_topic_path,
        "max_delivery_attempts": 5,
    }

    create_subscription(
        subscriber,
        main_sub_path,
        main_topic_path,
        dead_letter_policy=dlq_policy,
    )


def init_pubsub() -> None:
    """Orquestra a criação dos recursos do Pub/Sub."""
    logger.info(f"Iniciando configuração do Pub/Sub no projeto: {PROJECT_ID}")

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    for config in TOPICS_CONFIG:
        setup_topic_resources(publisher, subscriber, config)

    logger.success("Configuração do Pub/Sub concluída!")


if __name__ == "__main__":
    # Garante que as variáveis de ambiente estejam carregadas se necessário
    init_pubsub()
