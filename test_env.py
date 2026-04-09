import os
import lancedb
import pyarrow as pa
from langchain_ollama import ChatOllama, OllamaEmbeddings
from config import LLM_MODEL, EMBEDDING_MODEL, LANCEDB_URI

def test_ollama_llm():
    print(f"\n[1/3] Testando LLM ({LLM_MODEL}) via Ollama...")
    try:
        llm = ChatOllama(model=LLM_MODEL, temperature=0, system="Você responde sempre em português.", num_predict=100)
        resposta = llm.invoke(
            "Por que videogames podem ajudar a relaxar?")
        print(f"Sucesso! Resposta do modelo: {resposta.content}")
    except Exception as e:
        print(f"Erro no LLM: {e}")

def test_ollama_embeddings():
    print(f"\n[2/3] Testando Embeddings ({EMBEDDING_MODEL}) via Ollama...")
    try:
        embedder = OllamaEmbeddings(model=EMBEDDING_MODEL)
        vetor = embedder.embed_query("Videogames ajudam a relaxar.")
        print(f"Sucesso! Vetor gerado com {len(vetor)} dimensões.")
        return vetor
    except Exception as e:
        print(f"Erro no Embedding: {e}")
        return None

def test_lancedb(vetor_exemplo):
    print(f"\n[3/3] Testando LanceDB em {LANCEDB_URI}...")
    try:
        if not vetor_exemplo:
            print("Pulando teste do banco pois o embedding falhou.")
            return

        db = lancedb.connect(LANCEDB_URI)
        
        # Define um schema simples usando PyArrow para o teste
        schema = pa.schema([
            pa.field("id", pa.int32()),
            pa.field("text", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), len(vetor_exemplo)))
        ])
        
        # Cria ou sobrescreve uma tabela de teste
        tabela_nome = "tabela_teste_sistema"
        if tabela_nome in db.list_tables():
            db.drop_table(tabela_nome)
            
        table = db.create_table(tabela_nome, schema=schema)
        
        # Insere um dado fictício
        table.add([{"id": 1, "text": "Videogames ajudam a relaxar.", "vector": vetor_exemplo}])
        print(f"Sucesso! Tabela criada e dado inserido. Total de linhas: {len(table.to_pandas())}")
        
        # Limpa a sujeira
        db.drop_table(tabela_nome)
        print("Tabela de teste removida com sucesso.")

    except Exception as e:
        print(f"Erro no LanceDB: {e}")

if __name__ == "__main__":
    print("Iniciando Diagnóstico do Sistema GameMood...")
    test_ollama_llm()
    vetor = test_ollama_embeddings()
    test_lancedb(vetor)
    print("\nDiagnóstico concluído!")