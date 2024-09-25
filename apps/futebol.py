
import streamlit as st
import pandas as pd
from statsbombpy import sb


pag_1_title = 'Introdução'
pag_2_title = 'Selecionar uma Partida'
pag_3_title = 'Estatísticas'


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


def pag_1():
    if 'partidas' not in st.session_state:
        st.session_state['partidas'] = None

    if 'partida_selecionada' not in st.session_state:
        st.session_state['partida_selecionada'] = None

    st.title(pag_1_title)
    st.image('https://t4.ftcdn.net/jpg/00/86/41/89/360_F_86418998_mQ7NZfxcfR1hK1PDbVDSUkr6TFZbNRc0.jpg')
    st.write('Aplicativo para analisar estatísticas de determinadas partidas ou jogadores de futebol.')


def pag_2():
    st.title(pag_2_title)

    campeonatos = carregar_campeonatos()

    nomes_campeonatos = campeonatos['competition_name'].unique()
    filtro_campeonato = st.selectbox(label='Selecione o campeonato:', options=nomes_campeonatos)
    id_campeonato = campeonatos[campeonatos['competition_name'] == filtro_campeonato]['competition_id'].values[0]

    temporadas = campeonatos[campeonatos['competition_name'] == filtro_campeonato]['season_name'].unique()
    filtro_temporada = st.selectbox(label='Selecione o ano ou temporada:', options=temporadas)
    id_temporada = campeonatos[campeonatos['season_name'] == filtro_temporada]['season_id'].values[0]

    st.session_state['partidas'] = sb.matches(competition_id=id_campeonato, season_id=id_temporada)

    # partida_padrao = 0
    # if st.session_state['partida_selecionada'] is not None:
    #     partida_padrao = int(st.session_state['partidas'][st.session_state['partidas']['match_id'] == st.session_state['partida_selecionada']].index[0])

                                    # index=partida_padrao,

    st.session_state['partida_selecionada'] = st.selectbox(label='Selecione a partida',
                                        options=st.session_state['partidas']['match_id'],
                                        format_func=lambda id_partida: nome_partida(st.session_state['partidas'], id_partida))
    exibir_partida(st.session_state['partidas'], st.session_state['partida_selecionada'])


def pag_3():
    st.title(pag_3_title)
    exibir_partida(st.session_state['partidas'], st.session_state['partida_selecionada'])


st.sidebar.title('Navegação')
pagina = st.sidebar.radio(label='Escolha uma página:', options=(pag_1_title, pag_2_title, pag_3_title))
if pagina == pag_1_title:
    pag_1()
elif pagina == pag_2_title:
    pag_2()
else:
    pag_3()
