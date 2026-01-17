import pytest
from pytestarch import Rule, get_evaluable_architecture


class TestArchitecture:
    @pytest.fixture(scope="module")
    def evaluable(
        self,
    ):
        """
        Cria a representação avaliável da arquitetura.
        Escaneia a pasta src/ para construir o grafo de dependências.
        """
        # Usa caminhos absolutos para garantir a construção correta do grafo
        return get_evaluable_architecture(".", "src")

    def test_domain_isolation(self, evaluable):
        """
        O Domain (núcleo) deve ser puro.
        Não pode depender de camadas externas (Use Cases, Adapters, API)
        nem de frameworks de infraestrutura (FastAPI, SQLAlchemy).
        """
        # Lista de pacotes/módulos que o Domain NÃO pode importar
        forbidden_dependencies = [
            ".src.usecases",
            ".src.adapters",
            ".src.main",
        ]

        for dependency in forbidden_dependencies:
            # Se for um pacote (ex: src.usecases), usamos
            # are_sub_modules_of para pegar tudo dentro dele
            # Se for um módulo específico ou lib externa, a lógica é a mesma
            rule = (
                Rule()
                .modules_that()
                .are_sub_modules_of(dependency)
                .should_not()
                .be_imported_by_modules_that()
                .are_sub_modules_of(".src.domain")
            )
            rule.assert_applies(evaluable)

    def test_usecases_isolation(self, evaluable):
        """
        Use Cases contêm regras de aplicação.
        Podem usar o Domain, mas não devem saber
        COMO os dados são persistidos (Adapters)
        nem como são expostos (API/FastAPI).
        """
        forbidden_dependencies = [
            ".src.adapters",
            ".src.main",
        ]

        for dependency in forbidden_dependencies:
            rule = (
                Rule()
                .modules_that()
                .are_sub_modules_of(dependency)
                .should_not()
                .be_imported_by_modules_that()
                .are_sub_modules_of(".src.usecases")
            )
            rule.assert_applies(evaluable)

    def test_adapters_isolation(self, evaluable):
        """
        Adapters (Repositórios, Integrações)
        implementam as portas dos Use Cases.
        A API usa os Adapters, e não o contrário.
        """
        forbidden_dependencies = [
            ".src.main",
        ]

        for dependency in forbidden_dependencies:
            rule = (
                Rule()
                .modules_that()
                .are_sub_modules_of(dependency)
                .should_not()
                .be_imported_by_modules_that()
                .are_sub_modules_of(".src.adapters")
            )
            rule.assert_applies(evaluable)
