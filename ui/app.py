import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import gradio as gr
from rag.chain import gerar_recomendacao

def recomendar_jogo_interface(humor, energia, tempo, generos):
    """Função intermediária que liga a interface ao motor RAG."""
    generos_str = ", ".join(generos) if generos else "Qualquer gênero"
    
    resposta = gerar_recomendacao(
        humor=humor, 
        energia=energia, 
        tempo_disponivel=tempo, 
        generos=generos_str
    )
    return resposta

# tema e o design da página
tema = gr.themes.Soft(
    primary_hue="indigo",
    neutral_hue="slate"
)

with gr.Blocks(title="GameMood") as app:
    # Cabeçalho
    gr.Markdown("# 🎮 GameMood")
    gr.Markdown("### Seu consultor de bem-estar gamificado.")
    gr.Markdown("Cruza evidências científicas do PubMed com o catálogo do IGDB para recomendar o jogo ideal para o seu momento.")
    
    with gr.Row():
        # Coluna da Esquerda (Inputs)
        with gr.Column(scale=1):
            gr.Markdown("#### Como você está hoje?")
            input_humor = gr.Textbox(
                label="Descreva seu humor e estado emocional atual:",
                placeholder="Ex: Me sentindo muito ansioso após o trabalho, preciso relaxar.",
                lines=2
            )
            
            input_energia = gr.Radio(
                choices=["Muito Baixa (Exausto)", "Baixa", "Média", "Alta (Agitado)"],
                label="Nível de Energia:",
                value="Baixa"
            )
            
            input_tempo = gr.Dropdown(
                choices=["Menos de 30 minutos", "30min a 1 hora", "1 a 2 horas", "Mais de 2 horas", "Fim de semana inteiro"],
                label="Tempo Disponível para jogar:",
                value="30min a 1 hora"
            )
            
            input_generos = gr.CheckboxGroup(
                choices=["RPG", "Mundo Aberto", "Puzzle", "Aventura", "FPS", "Simulação", "Estratégia", "Plataforma", "Cozy"],
                label="Gêneros que você gosta:",
                value=["RPG", "Aventura"]
            )
            
            btn_recomendar = gr.Button("Encontrar Meu Jogo", variant="primary")
            
        # Coluna da Direita (Outputs)
        with gr.Column(scale=1):
            gr.Markdown("#### A Recomendação:")
            output_texto = gr.Markdown("Preencha seus dados ao lado e clique em encontrar. O Dr. GameMood está aguardando.")
            
            gr.Markdown("---")
            gr.Markdown("**Aviso Legal:** *O GameMood é um projeto de estudo. Recomendações de jogos não substituem aconselhamento médico, psiquiátrico ou psicológico. Em caso de crise, procure o CVV (188).*")

    btn_recomendar.click(
        fn=recomendar_jogo_interface,
        inputs=[input_humor, input_energia, input_tempo, input_generos],
        outputs=[output_texto]
    )

if __name__ == "__main__":
    print("Iniciando interface web GameMood...")
    app.launch(inbrowser=True, theme=tema)