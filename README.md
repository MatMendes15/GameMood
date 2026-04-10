# GameMood - Recomendador de Games por Estado Emocional

> **Status do Projeto:** MVP 1.1 Concluído

O **GameMood** é um aplicativo construído em Python que recomenda videogames com base no estado emocional do usuário. Diferente de recomendadores convencionais focados apenas em gênero, o GameMood cruza duas fontes distintas de conhecimento usando uma arquitetura **RAG (Retrieval-Augmented Generation) 100% local**:

1. **Catálogo de Games (IGDB):** Fichas técnicas, gêneros, descrições e popularidade.
2. **Literatura Científica (PubMed):** Artigos acadêmicos sobre o impacto dos videogames na saúde mental (ansiedade, foco, depressão, estresse).

A IA analisa como você se sente, busca na literatura médica o que é recomendado para o seu caso (ex: *jogos relaxantes diminuem o cortisol*) e busca no catálogo de jogos a melhor opção que se encaixe no seu tempo e energia disponíveis.

---

## Stack Tecnológica

Todo o processamento de IA e busca vetorial ocorre **localmente**, garantindo privacidade dos dados do usuário.

**Tecnologias utilizadas:**

* **LLM (Geração):** Google Gemma 3 (via Ollama) OBS: Pode usar o modelo que preferir.
* **Embeddings:** Nomic Embed Text (via Ollama)
* **Vector Database:** LanceDB (Serverless, armazenamento em disco local)
* **Orquestração RAG:** LangChain
* **Interface Web:** Gradio
* **APIs Externas (Ingestão):** IGDB (Twitch) e PubMed (NCBI)

---

## Arquitetura do Sistema

O sistema possui duas camadas principais:

1. **Pipeline de Ingestão (`ingest/`):**
   Conecta nas APIs reais, formata os dados, gera embeddings utilizando aceleração de GPU (Vulkan/CUDA) e salva as coleções no LanceDB.

2. **Motor RAG e UI (`rag/` e `ui/`):**
   Captura o input do usuário via Gradio, aplica filtros restritos de metadados para evitar recomendações nocivas (ex: bloquear jogos de tiro para usuários exaustos), busca os documentos mais similares no espaço vetorial e gera a justificativa ancorada em papers reais com o LLM.

---

## Pré-requisitos

* Python 3.10+
* Ollama instalado e rodando na máquina
* Credenciais da API da Twitch (IGDB)

---

## Como Rodar o Projeto

### **1. Clone o repositório e crie o ambiente virtual:**

```bash
git clone https://github.com/MatMendes15/GameMood.git
cd GameMood
python -m venv venv
source venv/bin/activate  # No Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

### **2. Baixe os modelos no Ollama:**

```bash
ollama pull >>seu-modelo<<
ollama pull nomic-embed-text
```

### **3. Configure as Variáveis de Ambiente:**

Crie um arquivo `.env` na raiz do projeto contendo as seguintes variáveis:

```env
IGDB_CLIENT_ID=sua_chave_aqui
IGDB_CLIENT_SECRET=seu_secret_aqui
LLM_MODEL=seu-modelo
EMBEDDING_MODEL=nomic-embed-text
```

### **4. Popule o Banco de Dados (Ingestão):**

Isso fará o download de 50 jogos e dezenas de artigos científicos, gerando o banco vetorial localmente.

```bash
python ingest/index_documents.py
```

### **5. Inicie a Interface:**

```bash
python ui/app.py
```

Acesse no seu navegador:
`http://127.0.0.1:7860/`

---

## Roadmap (Melhorias Futuras)

* [ ] **Cross-Encoder Re-ranking:** Implementar um modelo secundário para reordenar os resultados do LanceDB com maior precisão semântica.
* [ ] **HyDE (Hypothetical Document Embeddings):** Expandir a query do usuário com o LLM antes da busca vetorial para encontrar contextos mais profundos.

---

## Aviso Legal

*O GameMood é um projeto de estudo de Engenharia de Software e Inteligência Artificial. Suas recomendações de jogos são baseadas em processamento de linguagem natural sobre artigos científicos e não substituem de forma alguma o aconselhamento, diagnóstico ou tratamento médico, psiquiátrico ou psicológico.*
