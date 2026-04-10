import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate 
from config import LLM_MODEL, EMBEDDING_MODEL, LANCEDB_URI, TABLE_GAMES, TABLE_SCIENCE

def construir_filtro_lancedb(energia, generos_str):
    """Transforma os inputs do usuário em uma query SQL-like para o LanceDB."""
    filtros = []
    
    # 1. Filtro de Gêneros
    if generos_str and generos_str != "Qualquer gênero":
        lista_generos = [g.strip() for g in generos_str.split(",")]
        
        condicoes = [f"metadata.generos LIKE '%{g}%'" for g in lista_generos]
        filtro_generos = "(" + " OR ".join(condicoes) + ")"
        filtros.append(filtro_generos)
        
    # 2. Filtro de Energia (Guardrail de Saúde Mental)
    if "Baixa" in energia or "Exausto" in energia:
        filtros.append("metadata.generos NOT LIKE '%Shooter%'")
        filtros.append("metadata.generos NOT LIKE '%Fighting%'")
    elif "Alta" in energia:
        filtros.append("metadata.generos NOT LIKE '%Puzzle%' AND metadata.generos NOT LIKE '%Visual Novel%'")
        
    # 3. Filtro de Qualidade Mínima
    filtros.append("metadata.rating >= 60")
    
    if filtros:
        filtro_final = " AND ".join(filtros)
        print(f"Filtro LanceDB aplicado: {filtro_final}")
        return filtro_final
    return None

def configurar_retrievers(filtro_games=None):
    db = lancedb.connect(LANCEDB_URI)
    embedder = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vs_games = LanceDB(connection=db, embedding=embedder, table_name=TABLE_GAMES)
    vs_science = LanceDB(connection=db, embedding=embedder, table_name=TABLE_SCIENCE)
    
    kwargs_games = {"k": 3}
    if filtro_games:
        kwargs_games["filter"] = filtro_games
        
    retriever_games = vs_games.as_retriever(search_kwargs=kwargs_games)
    retriever_science = vs_science.as_retriever(search_kwargs={"k": 2})
    
    return retriever_games, retriever_science

def formatar_documentos(docs):
    textos = []
    for d in docs:
        meta = d.metadata
        if "titulo" in meta:
            textos.append(f"- JOGO: {meta.get('titulo')} | Gêneros: {meta.get('generos')} | Temas: {meta.get('temas')} | Avaliação: {meta.get('rating')}\n  {d.page_content}")
        elif "titulo_paper" in meta:
            textos.append(f"- ESTUDO: {meta.get('titulo_paper')} | Autores: {meta.get('autores')} ({meta.get('ano')}) | Foco: {meta.get('transtorno')}\n  {d.page_content}")
    return "\n\n".join(textos)

def gerar_recomendacao(humor, energia, tempo_disponivel, generos):
    print("1. Processando filtros e conectando ao banco...")
    
    filtro_sql = construir_filtro_lancedb(energia, generos)
    retriever_games, retriever_science = configurar_retrievers(filtro_games=filtro_sql)
    
    llm = ChatOllama(model=LLM_MODEL, temperature=0.1)
    
    query_usuario = f"Estado: {humor}. Energia {energia}. Busca jogos de {generos} para jogar por {tempo_disponivel}."
    
    print("2. Buscando contexto no LanceDB...")
    try:
        docs_games = retriever_games.invoke(query_usuario)
        
        if len(docs_games) == 0:
            print("Aviso: O filtro foi estrito e não encontrou nada nos 50 jogos populados. Removendo filtro para garantir uma recomendação.")
            retriever_games_fallback, _ = configurar_retrievers(filtro_games=None)
            docs_games = retriever_games_fallback.invoke(query_usuario)
            
    except Exception as e:
        print(f"Aviso: Erro no SQL do filtro. Buscando sem filtro. Erro: {e}")
        retriever_games_fallback, _ = configurar_retrievers(filtro_games=None)
        docs_games = retriever_games_fallback.invoke(query_usuario)
        
    docs_science = retriever_science.invoke(query_usuario)
    
    contexto_games = formatar_documentos(docs_games)
    contexto_science = formatar_documentos(docs_science)
    
    print("3. Montando o Prompt Estruturado...")
    
    mensagens = [
        ("system", """Você é o GameMood, um consultor de bem-estar.
Sua missão é recomendar jogos baseando-se EXCLUSIVAMENTE nos contextos fornecidos abaixo.
Regras OBRIGATÓRIAS:
1. Nunca invente jogos ou estudos científicos. Use APENAS o que está no contexto.
2. Cite o estudo científico relevante (Autor, Ano) para justificar a escolha do jogo.
3. Leve em consideração o tempo disponível da pessoa na hora de justificar.
4. Inclua um aviso médico claro no final de que isso não substitui terapia.
5. Responda de forma empática e direta em português do Brasil.

CONTEXTO CIENTÍFICO:
{contexto_science}

CONTEXTO DE GAMES:
{contexto_games}"""),
        ("human", """Meu estado atual:
- Humor: {humor}
- Energia: {energia}
- Tempo: {tempo_disponivel}
- Gêneros favoritos: {generos}

Com base na ciência fornecida, qual desses jogos você me recomenda e por quê?""")
    ]
    
    prompt_template = ChatPromptTemplate.from_messages(mensagens)
    chain = prompt_template | llm
    
    print("4. Gerando resposta com o LLM...\n")
    
    texto_completo = ""
    for chunk in chain.stream({
        "contexto_science": contexto_science,
        "contexto_games": contexto_games,
        "humor": humor,
        "energia": energia,
        "tempo_disponivel": tempo_disponivel,
        "generos": generos
    }):
        print(chunk.content, end="", flush=True)
        texto_completo += chunk.content
        
    print("\n\n===========================\n")
    return texto_completo

if __name__ == "__main__":
    print("TESTE DO RAG COM FILTROS")
    resultado = gerar_recomendacao(
        humor="me sentindo um pouco deprimido e sem foco",
        energia="Muito Baixa (Exausto)",
        tempo_disponivel="algumas horas",
        generos="RPG, Aventura"
    )