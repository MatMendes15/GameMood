import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import lancedb
from langchain_community.vectorstores import LanceDB
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate 
from config import LLM_MODEL, EMBEDDING_MODEL, LANCEDB_URI, TABLE_GAMES, TABLE_SCIENCE

def configurar_retrievers():
    db = lancedb.connect(LANCEDB_URI)
    embedder = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vs_games = LanceDB(connection=db, embedding=embedder, table_name=TABLE_GAMES)
    vs_science = LanceDB(connection=db, embedding=embedder, table_name=TABLE_SCIENCE)
    
    retriever_games = vs_games.as_retriever(search_kwargs={"k": 3})
    retriever_science = vs_science.as_retriever(search_kwargs={"k": 2})
    
    return retriever_games, retriever_science

def formatar_documentos(docs):
    textos = []
    for d in docs:
        meta = d.metadata
        # Se for um jogo
        if "titulo" in meta:
            textos.append(f"- JOGO: {meta.get('titulo')} | Gêneros: {meta.get('generos')} | Temas: {meta.get('temas')} | Avaliação: {meta.get('rating')}\n  {d.page_content}")
        # Se for um artigo científico
        elif "titulo_paper" in meta:
            textos.append(f"- ESTUDO: {meta.get('titulo_paper')} | Autores: {meta.get('autores')} ({meta.get('ano')}) | Foco: {meta.get('transtorno')}\n  {d.page_content}")
    return "\n\n".join(textos)

def gerar_recomendacao(humor, energia, tempo_disponivel, generos):
    print("1. Conectando ao banco de dados e LLM...")
    retriever_games, retriever_science = configurar_retrievers()
    
    llm = ChatOllama(model=LLM_MODEL, temperature=0.1)
    
    # string de busca combinando o estado do usuário
    query_usuario = f"Estado: {humor}. Energia {energia}. Busca jogos de {generos}."
    
    print("2. Buscando contexto no LanceDB...")
    docs_games = retriever_games.invoke(query_usuario)
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
3. Se o contexto de jogos não tiver nada exato, recomende o mais próximo disponível no contexto.
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
    print("=== RESPOSTA DO GAMEMOOD ===\n")
    
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
    print("TESTE DO RAG COM DADOS REAIS")
    resultado = gerar_recomendacao(
        humor="me sentindo um pouco deprimido e sem foco",
        energia="baixa",
        tempo_disponivel="algumas horas",
        generos="jogos de mundo aberto ou aventura"
    )