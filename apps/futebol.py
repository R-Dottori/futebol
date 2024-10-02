
import streamlit as st
import pandas as pd
from statsbombpy import sb
from mplsoccer import Sbopen, VerticalPitch, Pitch
import matplotlib.pyplot as plt
import seaborn as sns


pag_1_title = 'Introdução'
pag_2_title = 'Escolher uma Partida'
pag_3_title = 'Estatísticas'
pag_4_title = 'Formações'
pag_5_title = 'Mapa de Gols'
pag_6_title = 'Mapa de Passes'


# FUNÇÕES DE USO GERAL
@st.cache_data
def carregar_campeonatos():
    return sb.competitions()


def nome_partida(partidas, id_partida):
    linha_partida = partidas[partidas['match_id'] == id_partida].iloc[0]
    nome_partida = f'{linha_partida["match_date"]} — {linha_partida['home_team']} x {linha_partida['away_team']}'
    return nome_partida


def exibir_partida(partidas, partida_selecionada):
    data = partidas[partidas['match_id'] == partida_selecionada]['match_date'].values[0]
    time_casa = partidas[partidas['match_id'] == partida_selecionada]['home_team'].values[0]
    gols_casa = partidas[partidas['match_id'] == partida_selecionada]['home_score'].values[0]
    time_fora = partidas[partidas['match_id'] == partida_selecionada]['away_team'].values[0]
    gols_fora = partidas[partidas['match_id'] == partida_selecionada]['away_score'].values[0]
    st.header('Partida Selecionada:')
    st.subheader(data)
    col_1, col_2 = st.columns(2)
    with col_1:
        st.subheader('Time da Casa')
        st.subheader(time_casa)
        st.metric('Gols', gols_casa)
    with col_2:
        st.subheader('Time de Fora')
        st.subheader(time_fora)
        st.metric('Gols', gols_fora)
    st.markdown(f':green[(ID da partida = {partida_selecionada})]')


def estatisticas(filtro, eventos, metodo='time'):
    if metodo == 'jogador':
        eventos_sel = eventos[eventos['player'] == filtro]
    else:
        eventos_sel = eventos[eventos['team'] == filtro]
    gols = eventos_sel[eventos_sel['shot_outcome'] == 'Goal']
    total_chutes = eventos_sel[eventos_sel['type'] == 'Shot']
    chutes_ao_gol = total_chutes[total_chutes['shot_outcome'].isin(['Goal', 'Saved', 'Post'])]
    total_passes = eventos_sel[eventos_sel['type'] == 'Pass']
    passes_completados = total_passes[total_passes['pass_outcome'].isna()]
    passes_percentual = len(passes_completados) / len(total_passes) * 100 if len(total_passes) > 0 else 0
    faltas = eventos_sel[eventos_sel['type'] == 'Foul Committed']
    cartoes_amarelos = eventos_sel[eventos_sel['foul_committed_card'] == 'Yellow Card']
    cartoes_vermelhos = eventos_sel[eventos_sel['foul_committed_card'] == 'Red Card']
    impedimentos = eventos_sel[eventos_sel['type'] == 'Offside']
    escanteios = eventos_sel[eventos_sel['pass_type'] == 'Corner']
    posse_bola_total = len(eventos[eventos['type'].isin(['Pass', 'Ball Receipt', 'Duel'])])
    posse_bola_time = len(eventos_sel[eventos_sel['type'].isin(['Pass', 'Ball Receipt', 'Duel'])])
    posse_bola = posse_bola_time / posse_bola_total  * 100 if posse_bola_total > 0 else 0
    st.subheader(filtro)
    st.metric('Gols', gols.shape[0])
    st.metric('Total de Chutes', total_chutes.shape[0])
    st.metric('Chutes ao Gol', chutes_ao_gol.shape[0])
    st.metric('Total de Passes', total_passes.shape[0])
    st.metric('Passes Completados', passes_completados.shape[0])
    st.metric('Percentual de Passes Completados', f'{round(passes_percentual, 2)}%')
    st.metric('Faltas Cometidas', faltas.shape[0])
    st.metric('Cartões Amarelos', cartoes_amarelos.shape[0])
    st.metric('Cartões Vermelhos', cartoes_vermelhos.shape[0])
    st.metric('Impedimentos', impedimentos.shape[0])
    st.metric('Escanteios', escanteios.shape[0])
    st.metric('Posse de Bola', f'{round(posse_bola, 2)}%')


def estatisticas_grafico(filtro, eventos, metodo='time'):
    if metodo == 'jogador':
        eventos_sel = eventos[eventos['player'] == filtro]
    else:
        eventos_sel = eventos[eventos['team'] == filtro]
    gols = eventos_sel[eventos_sel['shot_outcome'] == 'Goal']
    total_chutes = eventos_sel[eventos_sel['type'] == 'Shot']
    chutes_ao_gol = total_chutes[total_chutes['shot_outcome'].isin(['Goal', 'Saved', 'Post'])]
    total_passes = eventos_sel[eventos_sel['type'] == 'Pass']
    passes_completados = total_passes[total_passes['pass_outcome'].isna()]

    dict_gols = {'Total de Chutes': total_chutes.shape[0],
                'Chutes ao Gol': chutes_ao_gol.shape[0],
                'Gols': gols.shape[0],
                }

    dict_passes = {'Total de Passes': total_passes.shape[0],
                'Passes Completados': passes_completados.shape[0]}

    fig_graf, ax_graf = plt.subplots()
    sns.barplot(dict_gols, ax=ax_graf)
    sns.barplot(dict_passes, ax=ax_graf)
    plt.xticks(rotation=60)
    st.pyplot(fig_graf)
    

# CONTEÚDO DAS PÁGINAS
def pag_1():
    if all(key not in st.session_state for key in ['camp_selecionado', 'temp_selecionada', 'partida_selecionada',
    'id_partida', 'partidas', 'eventos', 'pos_campo', 'taticas']):
        st.session_state['camp_selecionado'] = 0
        st.session_state['temp_selecionada'] = 0
        st.session_state['partida_selecionada'] = 0
        st.session_state['id_partida'] = None
        st.session_state['partidas'] = None
        st.session_state['eventos'] = None
        st.session_state['pos_campo'] = None
        st.session_state['taticas'] = None

    st.title(pag_1_title)
    st.image('https://t4.ftcdn.net/jpg/00/86/41/89/360_F_86418998_mQ7NZfxcfR1hK1PDbVDSUkr6TFZbNRc0.jpg')
    st.write('Aplicativo para analisar estatísticas de partidas de futebol.')


def pag_2():
    st.title(pag_2_title)

    campeonatos = carregar_campeonatos()

    nomes_campeonatos = list(campeonatos['competition_name'].unique())
    filtro_campeonato = st.selectbox(label='Selecione o campeonato:', options=nomes_campeonatos, index=st.session_state['camp_selecionado'])
    st.session_state['camp_selecionado'] = nomes_campeonatos.index(filtro_campeonato)
    id_campeonato = campeonatos[campeonatos['competition_name'] == filtro_campeonato]['competition_id'].values[0]

    temporadas = list(campeonatos[campeonatos['competition_name'] == filtro_campeonato]['season_name'].unique())
    filtro_temporada = st.selectbox(label='Selecione o ano ou temporada:', options=temporadas, index=st.session_state['temp_selecionada'])
    st.session_state['temp_selecionada'] = temporadas.index(filtro_temporada)
    id_temporada = campeonatos[campeonatos['season_name'] == filtro_temporada]['season_id'].values[0]

    st.session_state['partidas'] = sb.matches(competition_id=id_campeonato, season_id=id_temporada)

    st.session_state['id_partida'] = st.selectbox(label='Selecione a partida',
                                        options=st.session_state['partidas']['match_id'],
                                        index=st.session_state['partida_selecionada'],
                                        format_func=lambda id_partida: nome_partida(st.session_state['partidas'], id_partida)
                                        )
    st.session_state['partida_selecionada'] = int(st.session_state['partidas'][st.session_state['partidas']['match_id'] == st.session_state['id_partida']].index[0])
    st.session_state['eventos'], _ , st.session_state['pos_campo'], st.session_state['taticas'] = Sbopen().event(st.session_state['id_partida'])

    exibir_partida(st.session_state['partidas'], st.session_state['id_partida'])


def pag_3():
    st.title(pag_3_title)

    if st.session_state['id_partida'] is not None:
        with st.spinner('Carregando...'):
            eventos = sb.events(st.session_state['id_partida'])
            nomes_times = eventos['team'].unique()

            st.header('Por Time:')
            col_1, col_2 = st.columns(2)
            with col_1:
                st.subheader('Time da Casa')
                estatisticas(filtro=nomes_times[0], eventos=eventos, metodo='time')
                
            with col_2:
                st.subheader('Time de Fora')
                estatisticas(filtro=nomes_times[1], eventos=eventos, metodo='time')

            st.header('Por Jogador:')
            filtro_time = st.radio(label='Escolha o time', options=nomes_times)
            filtro_jogador = st.selectbox(label='Escolha o jogador', options=sorted(eventos[eventos['team'] == filtro_time]['player'].dropna().unique()))
            estatisticas(filtro=filtro_jogador, eventos=eventos, metodo='jogador')
            estatisticas_grafico(filtro=filtro_jogador, eventos=eventos, metodo='jogador')

            st.header('DataFrame:')
            df_filtro_time = st.multiselect(label='Escolha o time', options=nomes_times, default=nomes_times)
            df_jogadores = eventos[eventos['team'].isin(df_filtro_time)]['player'].unique()
            df_filtro_jogador = st.multiselect(label='Escolha o jogador', options=df_jogadores, default=df_jogadores)
            eventos_filtrados = eventos[(eventos['team'].isin(df_filtro_time)) & (eventos['player'].isin(df_filtro_jogador))]
            st.write(eventos_filtrados)

            st.subheader('Baixar Dados:')
            csv_filtrado = eventos_filtrados.to_csv()
            st.download_button(
              label='Baixar',
              data=csv_filtrado,
              file_name='dados_partida.csv'
                       )
    
    else:
        st.warning('Aguardando a escolha da partida.')


def pag_4():
    st.title(pag_4_title)

    if st.session_state['id_partida'] is not None:
        with st.spinner('Carregando...'):
            plt.style.use('ggplot')

            for time in st.session_state['eventos']['team_name'].unique():
                if time == st.session_state['eventos']['team_name'].unique()[0]:
                    st.subheader(f'Time da Casa — {time}')
                    cor_time = 'blue'
                else:
                    st.subheader(f'Time de Fora — {time}')
                    cor_time = 'red'

                jogadores_iniciais = st.session_state['eventos'].loc[(
                                                                        (st.session_state['eventos']['type_name'] == 'Starting XI') &
                                                                        (st.session_state['eventos']['team_name'] == time)
                                                                    ), ['id', 'tactics_formation']]

                jogadores_iniciais = st.session_state['taticas'].merge(jogadores_iniciais, on='id')

                formacao = jogadores_iniciais['tactics_formation'].iloc[0]

                campo = VerticalPitch(goal_type='box')
                fig_formacao, ax_formacao = campo.draw(figsize=(6, 8))

                ax_nomes = campo.formation(formacao, positions=jogadores_iniciais['position_id'], kind='text',
                                                    text=jogadores_iniciais['player_name'].str.replace(' ', '\n'),
                                                    va='center', ha='center', fontsize='10', ax=ax_formacao)

                ax_numeros = campo.formation(formacao, positions=jogadores_iniciais['position_id'], kind='text',
                                 text=jogadores_iniciais['jersey_number'],
                                 va='center', ha='center', color='white', xoffset=8, fontsize='8', ax=ax_formacao)

                ax_escudo = campo.formation(formacao, positions=jogadores_iniciais['position_id'], kind='scatter',
                                            linewidth=5, xoffset=8, color=cor_time, ax=ax_formacao)

                st.pyplot(fig_formacao)
    else:
        st.warning('Aguardando a escolha da partida.')


def pag_5():
    st.title(pag_5_title)

    if st.session_state['id_partida'] is not None:
        min_tempo = st.session_state['eventos']['minute'].min() + 1
        max_tempo = st.session_state['eventos']['minute'].max() + 1

        form_tempo = st.form('Minutagem')
        intervalo = form_tempo.slider(label='Escolha o intervalo de tempo que quer visualizar:', min_value=min_tempo, max_value=max_tempo, value=(min_tempo, max_tempo))
        form_tempo.form_submit_button('Aplicar')

        with st.spinner('Carregando...'):
            eventos = st.session_state['eventos'][(st.session_state['eventos']['minute'] >= intervalo[0] - 1)
                                                    & (st.session_state['eventos']['minute'] <= intervalo[1] - 1)]

            if eventos[eventos['outcome_name'] == 'Goal']['id'].shape[0] != 0:
                for gol in eventos[eventos['outcome_name'] == 'Goal']['id']:
                    pos_campo = st.session_state['pos_campo'][st.session_state['pos_campo']['id'] == gol].copy()
                    chute = eventos[eventos['id'] == gol].dropna(axis=1, how='all').copy()

                    formacao = Sbopen().lineup(st.session_state['id_partida'])
                    formacao = formacao[['player_id', 'jersey_number', 'team_name']].copy()

                    pos_campo = pos_campo.merge(formacao, how='left', on='player_id')

                    nome_time_1 = chute['team_name'].iloc[0]
                    nome_time_2 = list(set(eventos['team_name'].unique()) - {nome_time_1})[0]

                    time_1 = pos_campo[pos_campo['team_name'] == nome_time_1]

                    time_2_goleiro = pos_campo[(pos_campo['team_name'] == nome_time_2) &
                                                (pos_campo['position_name'] == 'Goalkeeper')]

                    time_2_jogadores = pos_campo[(pos_campo['team_name'] == nome_time_2) &
                                                    (pos_campo['position_name'] != 'Goalkeeper')]

                    campo = VerticalPitch(half=True, goal_type='box', pad_bottom=-20)

                    fig_gols, ax_gols = campo.grid(figheight=8, endnote_height=0, title_height=0.1, title_space=0.02,
                                                    axis=False, grid_height=0.8)

                    atacantes = campo.scatter(time_1['x'], time_1['y'], s=600, c='#727cce', label='Atacantes', ax=ax_gols['pitch'])
                    defensores = campo.scatter(time_2_jogadores['x'], time_2_jogadores['y'], s=600, c='#5ba965', label='Defensores', ax=ax_gols['pitch'])
                    goleiro = campo.scatter(time_2_goleiro['x'], time_2_goleiro['y'], s=600, c='#c15ca5', label='Goleiro', ax=ax_gols['pitch'])
                    batedor = campo.scatter(chute['x'], chute['y'], s=600, marker='football', label='Batedor', zorder=1.2, ax=ax_gols['pitch'])
                    trajeto_chute = campo.lines(chute['x'], chute['y'], chute['end_x'], chute['end_y'],
                                                    comet=True, color='#cb5a4c', label='Chute', ax=ax_gols['pitch'])
                    angulo_chute = campo.goal_angle(chute['x'], chute['y'], color='#cb5a4c', goal='right', alpha=0.2, zorder=1.1, ax=ax_gols['pitch'])

                    for idx, num_jogador in enumerate(pos_campo['jersey_number']):
                        campo.annotate(num_jogador, (pos_campo['x'][idx], pos_campo['y'][idx]),
                                        va='center', ha='center', color='white', fontsize=15, ax=ax_gols['pitch'])

                    legenda = ax_gols['pitch'].legend(loc='center left', labelspacing=1.5)

                    for texto in legenda.get_texts():
                        texto.set_fontsize(20)
                        texto.set_va('center')

                    ax_gols['title'].text(0.5, 0.5,
                                            f'Batedor: {chute['player_name'].iloc[0]} \n Time que Marcou: {nome_time_1} \n Time que Levou: {nome_time_2} \n Tempo de Jogo: {(chute[['minute']].values[0][0]) + 1}m{chute[['second']].values[0][0]}s',
                                            va='center', ha='center', c='black', fontsize=20)
                    
                    st.pyplot(fig_gols)

            else:
                    st.warning('A partida ou intervalo escolhido não teve nenhum gol.')

    else:
        st.warning('Aguardando a escolha da partida.')


def pag_6():
    st.title(pag_6_title)

    if st.session_state['id_partida'] is not None:
        eventos = sb.events(st.session_state['id_partida'])

        nomes_times = eventos['team'].unique()
        filtro_time = st.radio(label='Escolha o time', options=nomes_times)
        filtro_jogador = st.selectbox(label='Escolha o jogador', options=sorted(eventos[eventos['team'] == filtro_time]['player'].dropna().unique()))

        min_tempo = eventos['minute'].min() + 1
        max_tempo = eventos['minute'].max() + 1

        form_tempo = st.form('Minutagem')
        intervalo = form_tempo.slider(label='Escolha o intervalo de tempo que quer visualizar:', min_value=min_tempo, max_value=max_tempo, value=(min_tempo, max_tempo))
        form_tempo.form_submit_button('Aplicar')

        with st.spinner('Carregando...'):
            eventos = eventos[(eventos['minute'] >= intervalo[0] - 1)
                                                    & (eventos['minute'] <= intervalo[1] - 1)]

            passes_completados = eventos[(eventos['player'] == filtro_jogador) & (eventos['type'] == 'Pass') & (eventos['pass_outcome'].isna())]
            passes_incompletos = eventos[(eventos['player'] == filtro_jogador) & (eventos['type'] == 'Pass') & (eventos['pass_outcome'].notna())]

            campo = Pitch()
            fig_passes, ax_passes = campo.draw(figsize=(10, 7))

            if passes_completados.shape[0] > 0:
                campo.arrows(passes_completados['location'].apply(lambda x: x[0]),
                                passes_completados['location'].apply(lambda y: y[1]),
                                passes_completados['pass_end_location'].apply(lambda x: x[0]),
                                passes_completados['pass_end_location'].apply(lambda y: y[1]),
                                color='blue', label='Passes Completados', ax=ax_passes
                            )

            if passes_incompletos.shape[0] > 0:
                campo.arrows(passes_incompletos['location'].apply(lambda x: x[0]),
                                passes_incompletos['location'].apply(lambda y: y[1]),
                                passes_incompletos['pass_end_location'].apply(lambda x: x[0]),
                                passes_incompletos['pass_end_location'].apply(lambda y: y[1]),
                                color='red', label='Passes Incompletos', ax=ax_passes
                            )

            ax_passes.legend(loc='upper left', bbox_to_anchor=(1, 1))
            st.pyplot(fig_passes)            
    
    else:
        st.warning('Aguardando a escolha da partida.')


st.sidebar.title('Navegação')
pagina = st.sidebar.radio(label='Escolha uma página:', options=(pag_1_title, pag_2_title, pag_3_title, pag_4_title, pag_5_title, pag_6_title))
if pagina == pag_1_title:
    pag_1()
elif pagina == pag_2_title:
    pag_2()
elif pagina == pag_3_title:
    pag_3()
elif pagina == pag_4_title:
    pag_4()
elif pagina == pag_5_title:
    pag_5()
else:
    pag_6()
