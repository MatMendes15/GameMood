import sys
from pathlib import Path
from urllib import response
sys.path.append(str(Path(__file__).resolve().parent.parent))

import requests
from config import IGDB_CLIENT_ID, IGDB_CLIENT_SECRET

def obter_token_twitch():
    print("Autenticando na Twitch...")
    url = f"https://id.twitch.tv/oauth2/token?client_id={IGDB_CLIENT_ID}&client_secret={IGDB_CLIENT_SECRET}&grant_type=client_credentials"
    response = requests.post(url)
    
    print(f"Status: {response.status_code}")
    print(f"Resposta bruta: {response.text}")
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("Token obtido com sucesso!")
        return token
    else:
        raise Exception(f"Erro ao obter token: {response.status_code} - {response.text}")

def buscar_jogos(token, limite=10):
    """Busca jogos no IGDB usando uma query com a sintaxe (Apicalypse)."""
    print(f"Buscando {limite} jogos no IGDB...")
    url = "https://api.igdb.com/v4/games"
    
    headers = {
        "Client-ID": IGDB_CLIENT_ID,
        "Authorization": f"Bearer {token}",
        "Content-Type": "text/plain"
    }
    
    # Query para buscar jogos bem avaliados, pegando nome, resumo, gêneros e temas
    # Apenas jogos principais (category = 0)
    query = f"""
fields name, summary, genres.name, themes.name, 
       rating, rating_count, cover.url, 
       first_release_date, involved_companies.company.name;
where rating_count > 50;
sort rating_count desc;
limit {limite};
"""
    
    response = requests.post(url, headers=headers, data=query.strip(), timeout=10)
    
    if response.status_code == 200:
        jogos = response.json()
        print(f"Sucesso! {len(jogos)} jogos encontrados.")
        return jogos
    else:
        print(f"Erro na API IGDB: {response.status_code} - {response.text}")
        return []

if __name__ == "__main__":
    try:
        if IGDB_CLIENT_ID == "SEU_CLIENT_ID_AQUI":
            print("Atenção: Substitua as credenciais do IGDB/.env")
            sys.exit()
            
        token = obter_token_twitch()
        jogos = buscar_jogos(token, limite=3)
        
        if jogos:
            print("\nExemplo de Jogo Retornado:")
            print(f"Nome: {jogos[0].get('name')}")
            summary = jogos[0].get('summary')
            if summary:
                print(f"Resumo: {summary[:150]}...")
            else:
                print("Resumo: Não disponível")
            
    except Exception as e:
        print(f"Erro: {e}")