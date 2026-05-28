# 🎮 API: Microsserviço de Catálogo e Metadados de Jogos

Este é o microsserviço de Catálogo de Jogos, estruturado para atender a todos os requisitos do projeto GameVerse. Ele atua como a "vitrine" do ecossistema, centralizando e gerenciando todo o inventário de títulos disponíveis na plataforma, fornecendo os dados necessários para a Loja e para a Biblioteca do Usuário.

Desenvolvido em **FastAPI (Python)**.

---

## 🚀 Como Executar a API

Este projeto foi containerizado para facilitar a execução local utilizando Docker.

### Pré-requisitos
- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/) instalados.

### Passos para rodar
1. Execute o script de inicialização na raiz do projeto (ele executará `docker compose up --build -d`):
   ```bash
   ./run.sh
   ```
2. A aplicação FastAPI estará disponível na URL base: **http://localhost:8000**
3. O banco de dados PostgreSQL estará rodando internamente na porta `5432`.

### 📚 Documentação Interativa (Swagger)
Assim que a API estiver rodando, você pode testar os endpoints e ver a documentação completa através do Swagger UI acessando:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 📋 Requisitos e Planejamento do Projeto

Abaixo estão as informações detalhadas sobre as responsabilidades, fluxo e arquitetura que guiaram o desenvolvimento deste serviço.

### Integrantes do grupo
[Inserir nome completo de todos os integrantes aqui]

### Responsabilidades do microsserviço
* **Gerenciar o inventário:** Cadastrar, atualizar e remover jogos do catálogo.
* **Categorização:** Administrar gêneros (RPG, FPS, Indie) e plataformas (PC, Console, Cloud).
* **Curadoria de Conteúdo:** Armazenar descrições detalhadas, notas de patch e classificações indicativas.
* **Gestão de Mídia:** Vincular URLs de imagens, trailers e capas aos respectivos títulos.
* **Busca e Filtragem:** Permitir que outros serviços consultem jogos por critérios específicos.

### Dados que o serviço precisa receber
Para o cadastro ou atualização de um jogo, o serviço requer:
* **Nome do jogo:** (String)
* **Descrição:** (Text/Markdown)
* **Gêneros:** (Array de IDs ou nomes)
* **Plataformas:** (Array de IDs - ex: Steam, Epic, Xbox)
* **Mídia:** (URLs de imagens de capa e galeria)
* **Desenvolvedora/Distribuidora:** (String)
* **Requisitos de Sistema:** (Objeto JSON com CPU, GPU, RAM mínimos e recomendados)

### Dados que o serviço deve retornar
Exemplo de resposta ao consultar um jogo específico:
```json
{
  "success": true,
  "message": "Jogo localizado com sucesso",
  "data": {
    "game_id": "gv-8829",
    "title": "Cyber-Acre 2077",
    "slug": "cyber-acre-2077",
    "platforms": ["PC", "Linux"],
    "genres": ["Action", "RPG"],
    "description": "Um RPG de ação em um futuro distópico no norte do Brasil.",
    "images": {
      "thumbnail": "https://cdn.gameverse.com/covers/ca2077_thumb.jpg",
      "header": "https://cdn.gameverse.com/headers/ca2077_wide.jpg"
    },
    "active": true
  }
}
```

### Com quais serviços ele precisa se comunicar
* **Loja de Jogos (Storefront):** Para fornecer os dados que serão exibidos ao comprador.
* **Biblioteca do Usuário:** Para validar se o ID do jogo que o usuário possui ainda existe e está atualizado.
* **Busca (Search Service):** Para indexar novos títulos em motores de busca como Elasticsearch.
* **Laravel Central/API Gateway:** Para autenticação de administradores que gerenciam o catálogo.

### Fluxo principal do serviço
1. **Administrador** envia uma requisição de cadastro com os dados do novo jogo.
2. O serviço **valida** se o título já existe e se todos os campos obrigatórios estão presentes.
3. O serviço **persiste** os dados no banco de dados (Gêneros, Plataformas e Dados Gerais).
4. O serviço **emite um evento** (via RabbitMQ/Kafka ou Webhook) informando que um novo jogo foi adicionado.
5. A **Loja** recebe a atualização e passa a exibir o jogo para os usuários.
6. O **Usuário** realiza uma busca e o serviço retorna a lista filtrada de jogos.

### Rotas da API
* `GET /api/v1/catalog/games` (Listagem com paginação e filtros de gênero/plataforma)
* `POST /api/v1/catalog/games` (Criação de novo título - Restrito a Admin)
* `GET /api/v1/catalog/games/{id_ou_slug}` (Detalhes completos de um jogo específico)
* `PATCH /api/v1/catalog/games/{id}` (Atualização parcial de dados como descrição ou imagens)

### Possíveis erros
* **Jogo não encontrado:** Quando um ID inválido é solicitado.
* **Título Duplicado:** Tentativa de cadastrar um jogo com nome ou slug já existente.
* **Falha na persistência de mídia:** Erro ao tentar vincular links de imagens inválidos.
* **Dados incompletos:** Envio de formulário sem campos obrigatórios (ex: sem plataforma definida).
* **Incompatibilidade de Versão:** Tentativa de atualizar um jogo que foi removido ou arquivado.