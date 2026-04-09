import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from config import EMBEDDING_MODEL, LANCEDB_URI, TABLE_GAMES, TABLE_SCIENCE

from ingest.scrape_games import obter_token_twitch, buscar_jogos
from ingest.scrape_papers import coletar_literatura

# SEÇÃO 1: INDEXAÇÃO DE JOGOS (IGDB)
def transformar_jogos_em_documentos(jogos_json):
    docs = []
    for jogo in jogos_json:
        nome = jogo.get('name', 'Sem Título')
        resumo = jogo.get('summary', 'Sem descrição disponível.')
        conteudo = f"Título: {nome}. Descrição: {resumo}"
        
        generos = [g['name'] for g in jogo.get('genres', [])] if jogo.get('genres') else []
        temas = [t['name'] for t in jogo.get('themes', [])] if jogo.get('themes') else []
        
        cover_url = ""
        if jogo.get('cover') and 'url' in jogo.get('cover'):
            cover_url = "https:" + jogo.get('cover')['url']
        
        metadata = {
            "titulo": nome,
            "generos": ", ".join(generos),
            "temas": ", ".join(temas),
            "rating": jogo.get('rating', 0.0),
            "cover_url": cover_url
        }
        docs.append(Document(page_content=conteudo, metadata=metadata))
    return docs

def indexar_jogos(quantidade=50, db=None, embedder=None):
    print(f"\n--- Iniciando Indexação de Jogos ({quantidade} jogos) ---")
    token = obter_token_twitch()
    dados = buscar_jogos(token, limite=quantidade)
    
    if not dados: return

    docs = transformar_jogos_em_documentos(dados)
    
    print(f"Atualizando tabela '{TABLE_GAMES}' no LanceDB...")
    if TABLE_GAMES in db.list_tables():
        db.drop_table(TABLE_GAMES)
        
    LanceDB.from_documents(documents=docs, embedding=embedder, connection=db, table_name=TABLE_GAMES)
    print("Jogos indexados com sucesso!")

# SEÇÃO 2: INDEXAÇÃO DE CIÊNCIA/artigos (PUBMED)
def transformar_ciencia_em_documentos(artigos_json):
    docs = []
    for artigo in artigos_json:
        conteudo = f"Estudo: {artigo['titulo_paper']}. Conclusão/Resumo: {artigo['abstract']}"
        
        metadata = {
            "titulo_paper": artigo['titulo_paper'],
            "autores": artigo['autores'],
            "ano": artigo['ano'],
            "transtorno": artigo['transtorno']
        }
        docs.append(Document(page_content=conteudo, metadata=metadata))
    return docs

def indexar_ciencia(limite_por_termo=10, db=None, embedder=None):
    print(f"\n--- Iniciando Indexação Científica ({limite_por_termo} por categoria) ---")
    dados = coletar_literatura(limite_por_termo=limite_por_termo)
    
    if not dados: return

    docs = transformar_ciencia_em_documentos(dados)
    
    print(f"Atualizando tabela '{TABLE_SCIENCE}' no LanceDB...")
    if TABLE_SCIENCE in db.list_tables():
        db.drop_table(TABLE_SCIENCE)
        
    LanceDB.from_documents(documents=docs, embedding=embedder, connection=db, table_name=TABLE_SCIENCE)
    print("Artigos científicos indexados com sucesso!")

if __name__ == "__main__":
    print("Iniciando Pipeline de Ingestão do GameMood...")
    
    db_local = lancedb.connect(LANCEDB_URI)
    embedder_local = OllamaEmbeddings(model=EMBEDDING_MODEL)
    
    # 1. Indexa os jogos
    indexar_jogos(quantidade=50, db=db_local, embedder=embedder_local)
    
    # 2. Indexa os papers
    indexar_ciencia(limite_por_termo=15, db=db_local, embedder=embedder_local)
    
    print("\n Indexação Completa! O GameMood está com dados reais.")