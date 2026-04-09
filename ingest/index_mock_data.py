import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import lancedb
from langchain_core.documents import Document
from langchain_community.vectorstores import LanceDB
from langchain_ollama import OllamaEmbeddings
from config import EMBEDDING_MODEL, LANCEDB_URI, TABLE_GAMES, TABLE_SCIENCE

def popular_mock_data():
    print("Iniciando ingestão de dados fictícios...")
    
    embedder = OllamaEmbeddings(model=EMBEDDING_MODEL)
    db = lancedb.connect(LANCEDB_URI)
    
    games_docs = [
        Document(
            page_content="Stardew Valley é um jogo de simulação agrícola relaxante onde você herda a fazenda do seu avô. Envolve plantar, interagir com a comunidade e explorar no seu próprio ritmo. Atmosfera muito calma e recompensadora.",
            metadata={"titulo": "Stardew Valley", "genero": "RPG/Simulação", "pacing": "lento", "duracao_sessao": "30min", "tema": "cozy"}
        ),
        Document(
            page_content="Doom Eternal é um jogo de tiro em primeira pessoa frenético. Você luta contra hordas de demônios com música metal pesada. Exige reflexos rápidos e muita adrenalina.",
            metadata={"titulo": "Doom Eternal", "genero": "FPS", "pacing": "intenso", "duracao_sessao": "1h", "tema": "ação"}
        ),
        Document(
            page_content="Journey é uma aventura atmosférica silenciosa onde você viaja por um vasto deserto. Foco em exploração, belos visuais e uma jornada emocional profunda sem usar palavras.",
            metadata={"titulo": "Journey", "genero": "Aventura", "pacing": "lento", "duracao_sessao": "2h", "tema": "relaxante"}
        )
    ]
    
    print(f"Criando tabela de games ({TABLE_GAMES})...")
    if TABLE_GAMES in db.list_tables():
        db.drop_table(TABLE_GAMES)
    
    LanceDB.from_documents(
        documents=games_docs,
        embedding=embedder,
        connection=db,
        table_name=TABLE_GAMES
    )

    science_docs = [
        Document(
            page_content="Estudos indicam que jogos de simulação e fazenda (como Stardew Valley ou Animal Crossing) reduzem significativamente os níveis de cortisol, ajudando no alívio de ansiedade e estresse crônico após dias de trabalho exaustivo.",
            metadata={"titulo_paper": "Impacto de Jogos Cozy na Ansiedade", "autores": "Silva, J.", "ano": 2023, "transtorno": "ansiedade", "nivel_evidencia": "alto"}
        ),
        Document(
            page_content="Jogos de ação acelerada em primeira pessoa melhoram a atenção visual e os reflexos cognitivos, mas não são recomendados para induzir o sono ou relaxamento, pois elevam a frequência cardíaca.",
            metadata={"titulo_paper": "Frequência Cardíaca e FPS", "autores": "Smith, A.", "ano": 2021, "transtorno": "foco", "nivel_evidencia": "médio"}
        )
    ]

    print(f"Criando tabela científica ({TABLE_SCIENCE})...")
    if TABLE_SCIENCE in db.list_tables():
        db.drop_table(TABLE_SCIENCE)
        
    LanceDB.from_documents(
        documents=science_docs,
        embedding=embedder,
        connection=db,
        table_name=TABLE_SCIENCE
    )

    print("Ingestão mock concluída com sucesso!")

if __name__ == "__main__":
    popular_mock_data()