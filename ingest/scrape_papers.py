import sys
from pathlib import Path
import requests
import xml.etree.ElementTree as ET
import time

sys.path.append(str(Path(__file__).resolve().parent.parent))

def buscar_ids_pubmed(termo, limite=10):
    """Busca artigos no PubMed e retorna uma lista de IDs (PMIDs)."""
    print(f"Buscando IDs no PubMed para: '{termo}'...")
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",
        "term": termo,
        "retmax": limite,
        "retmode": "json"
    }
    
    response = requests.get(url, params=params)
    print(f"URL chamada: {response.url}") 
    print(f"Resposta bruta: {response.text[:300]}") 
    if response.status_code == 200:
        ids = response.json().get("esearchresult", {}).get("idlist", [])
        print(f"Encontrados {len(ids)} artigos.")
        return ids
    else:
        print(f"Erro ao buscar no PubMed: {response.status_code}")
        return []

def extrair_dados_artigos(ids, transtorno):
    """Busca os detalhes (Título, Ano, Abstract) a partir dos IDs em formato XML."""
    if not ids:
        return []
        
    print("Baixando resumos e detalhes dos artigos...")
    ids_str = ",".join(ids)
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pubmed",
        "id": ids_str,
        "retmode": "xml"
    }
    
    response = requests.get(url, params=params)
    artigos = []
    
    if response.status_code == 200:
        # Fazer parse do XML que o PubMed retorna
        root = ET.fromstring(response.content)
        
        for article in root.findall(".//PubmedArticle"):
            try:
                # Título
                titulo = article.find(".//ArticleTitle").text
                
                # Abstract
                abstract_tags = article.findall(".//AbstractText")
                abstract = " ".join([t.text for t in abstract_tags if t.text])
                
                if not abstract:
                    continue 
                    
                # Ano de Publicação
                ano_tag = article.find(".//PubDate/Year")
                ano = ano_tag.text if ano_tag is not None else "N/A"
                
                # Primeiro Autor (para citação)
                autor_tag = article.find(".//AuthorList/Author/LastName")
                autor = autor_tag.text if autor_tag is not None else "Desconhecido"
                
                artigos.append({
                    "titulo_paper": titulo,
                    "autores": autor,
                    "ano": ano,
                    "abstract": abstract,
                    "transtorno": transtorno
                })
            except Exception as e:
                print(f"Erro ao processar artigo: {e}")
                continue
                
        print(f"Extraídos dados completos de {len(artigos)} artigos válidos.")
        return artigos
    else:
        print(f"Erro ao extrair detalhes: {response.status_code}")
        return []

def coletar_literatura(limite_por_termo=5):
    """ Buscas por diferentes estados mentais."""
    buscas = {
    "ansiedade": "video games AND (anxiety OR stress) AND hasabstract",
    "foco": "video games AND (cognitive OR attention OR focus) AND hasabstract",
    "depressão": "video games AND (depression OR mood) AND hasabstract"
    }
    
    literatura_total = []
    ids_vistos = set()  
    
    for transtorno, query in buscas.items():
        ids = buscar_ids_pubmed(query, limite=limite_por_termo)
        ids_novos = [id for id in ids if id not in ids_vistos] 
        ids_vistos.update(ids_novos)
        artigos = extrair_dados_artigos(ids_novos, transtorno)
        literatura_total.extend(artigos)
        time.sleep(1)
        
    return literatura_total

if __name__ == "__main__":
    print("--- Teste de Coleta do PubMed ---")
    resultados = coletar_literatura(limite_por_termo=7)
    print(f"\nTotal de artigos únicos coletados: {len(resultados)}")
    
    if resultados:
        print("\nExemplo de Artigo Retornado:")
        print(f"Título: {resultados[0]['titulo_paper']}")
        print(f"Autor/Ano: {resultados[0]['autores']}, {resultados[0]['ano']}")
        print(f"Transtorno: {resultados[0]['transtorno']}")
        print(f"Abstract: {resultados[0]['abstract'][:200]}...")