
import streamlit as st
import pandas as pd
from statsbombpy import sb
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch, FontManager, Sbopen


pag_1_title = 'Introdução'
pag_2_title = 'Escolher uma Partida'
pag_3_title = 'Visualizações'


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


def pag_1():
    if all(key not in st.session_state for key in ['camp_selecionado', 'temp_selecionada', 'partida_selecionada', 'id_partida', 'partidas']):
        st.session_state['camp_selecionado'] = 0
        st.session_state['temp_selecionada'] = 0
        st.session_state['partida_selecionada'] = 0
        st.session_state['id_partida'] = None
        st.session_state['partidas'] = None
        

    st.title(pag_1_title)
    st.image('https://t4.ftcdn.net/jpg/00/86/41/89/360_F_86418998_mQ7NZfxcfR1hK1PDbVDSUkr6TFZbNRc0.jpg')
    st.write('Aplicativo para analisar estatísticas de determinadas partidas ou jogadores de futebol.')


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
    exibir_partida(st.session_state['partidas'], st.session_state['id_partida'])


def pag_3():
    st.title(pag_3_title)

    if st.session_state['id_partida'] is not None:
        with st.spinner('Carregando...'):
            exibir_partida(st.session_state['partidas'], st.session_state['id_partida'])          

        with st.spinner('Carregando...'):
            plt.style.use('ggplot')
            parser = Sbopen()
            df_event, df_related, df_freeze, df_tactics = parser.event(st.session_state['id_partida'])
            df_lineup = parser.lineup(st.session_state['id_partida'])
            df_lineup = df_lineup[['player_id', 'jersey_number', 'team_name']].copy()

            st.header('Formações')
            for time in df_event['team_name'].unique():
                st.subheader(time)
                # starting players
                starting_xi_df_event = df_event.loc[((df_event['type_name'] == 'Starting XI') &
                                            (df_event['team_name'] == time)), ['id', 'tactics_formation']]

                # joining on the team name and formation to the lineup
                starting_xi = df_tactics.merge(starting_xi_df_event, on='id')

                # filter only succesful ball receipts from the starting XI
                starting_xi_event_df = df_event.loc[((df_event['type_name'] == 'Ball Receipt') &
                                (df_event['outcome_name'].isnull()) &
                                (df_event['player_id'].isin(starting_xi['player_id']))
                                ), ['player_id', 'x', 'y']]

                # merge on the starting positions to the df_events
                starting_xi_event_df = starting_xi_event_df.merge(starting_xi, on='player_id')
                formation = starting_xi_event_df['tactics_formation'].iloc[0]

                pitch = VerticalPitch(goal_type='box')
                fig, ax = pitch.draw(figsize=(6, 8.72))
                ax_text = pitch.formation(formation, positions=starting_xi.position_id, kind='text',
                                        text=starting_xi.player_name.str.replace(' ', '\n'),
                                        va='center', ha='center', fontsize=10, ax=ax)

                # scatter markers
                ax_scatter = pitch.formation(formation, positions=starting_xi.position_id, kind='scatter',
                                            linewidth=5, xoffset=-8, ax=ax)
                st.pyplot(fig)
            
            st.header('Mapa dos Gols')            
            if df_event[df_event['outcome_name'] == 'Goal']['id'].shape[0] != 0:
                    for goal in df_event[df_event['outcome_name'] == 'Goal']['id']:
                            SHOT_ID = goal

                            df_freeze_frame = df_freeze[df_freeze.id == SHOT_ID].copy()
                            df_shot_event = df_event[df_event.id == SHOT_ID].dropna(axis=1, how='all').copy()

                            # add the jersey number
                            df_freeze_frame = df_freeze_frame.merge(df_lineup, how='left', on='player_id')
                            # strings for team names
                            team1 = df_shot_event.team_name.iloc[0]
                            team2 = list(set(df_event.team_name.unique()) - {team1})[0]

                            # subset the team shooting, and the opposition (goalkeeper/ other)
                            df_team1 = df_freeze_frame[df_freeze_frame.team_name == team1]
                            df_team2_goal = df_freeze_frame[(df_freeze_frame.team_name == team2) &
                                                    (df_freeze_frame.position_name == 'Goalkeeper')]
                            df_team2_other = df_freeze_frame[(df_freeze_frame.team_name == team2) &
                                                    (df_freeze_frame.position_name != 'Goalkeeper')]
                                                    # Setup the pitch
                            pitch = VerticalPitch(half=True, goal_type='box', pad_bottom=-20)

                            # We will use mplsoccer's grid function to plot a pitch with a title axis.
                            fig, axs = pitch.grid(figheight=8, endnote_height=0,  # no endnote
                                            title_height=0.1, title_space=0.02,
                                            # Turn off the endnote/title axis. I usually do this after
                                            # I am happy with the chart layout and text placement
                                            axis=False,
                                            grid_height=0.83)

                            # Plot the players
                            sc1 = pitch.scatter(df_team1.x, df_team1.y, s=600, c='#727cce', label='Atacantes', ax=axs['pitch'])
                            sc2 = pitch.scatter(df_team2_other.x, df_team2_other.y, s=600,
                                            c='#5ba965', label='Defensores', ax=axs['pitch'])
                            sc4 = pitch.scatter(df_team2_goal.x, df_team2_goal.y, s=600,
                                            ax=axs['pitch'], c='#c15ca5', label='Goleiro')

                            # plot the shot
                            sc3 = pitch.scatter(df_shot_event.x, df_shot_event.y, marker='football',
                                            s=600, ax=axs['pitch'], label='Batedor', zorder=1.2)
                            line = pitch.lines(df_shot_event.x, df_shot_event.y,
                                    df_shot_event.end_x, df_shot_event.end_y, comet=True,
                                    label='Chute', color='#cb5a4c', ax=axs['pitch'])

                            # plot the angle to the goal
                            pitch.goal_angle(df_shot_event.x, df_shot_event.y, ax=axs['pitch'], alpha=0.2, zorder=1.1,
                                    color='#cb5a4c', goal='right')

                            # fontmanager for google font (robotto)
                            robotto_regular = FontManager()

                            # plot the jersey numbers
                            for i, label in enumerate(df_freeze_frame.jersey_number):
                                    pitch.annotate(label, (df_freeze_frame.x[i], df_freeze_frame.y[i]),
                                            va='center', ha='center', color='white',
                                            fontproperties=robotto_regular.prop, fontsize=15, ax=axs['pitch'])

                            # add a legend and title
                            legend = axs['pitch'].legend(loc='center left', labelspacing=1.5)
                            for text in legend.get_texts():
                                    text.set_fontproperties(robotto_regular.prop)
                                    text.set_fontsize(20)
                                    text.set_va('center')

                            # title
                            axs['title'].text(0.5, 0.5,
                                    f'Batedor: {df_shot_event.player_name.iloc[0]} \n Time que Marcou: {team1} \n Time que Levou: {team2}',
                                    va='center', ha='center', color='black',
                                    fontproperties=robotto_regular.prop, fontsize=25)

                            st.pyplot(fig)
            else:
                    st.warning('A partida escolhida não teve nenhum gol.')

    else:
        st.warning('Aguardando seleção de partida.')


# def pag_4():
#     st.title(pag_4_title)
#     campeonatos = carregar_campeonatos()

#     nomes_campeonatos = campeonatos['competition_name'].unique()
#     filtro_campeonato = st.selectbox(label='Selecione o campeonato:', options=nomes_campeonatos)
#     id_campeonato = campeonatos[campeonatos['competition_name'] == filtro_campeonato]['competition_id'].values[0]

#     temporadas = campeonatos[campeonatos['competition_name'] == filtro_campeonato]['season_name'].unique()
#     filtro_temporada = st.selectbox(label='Selecione o ano ou temporada:', options=temporadas)
#     id_temporada = campeonatos[campeonatos['season_name'] == filtro_temporada]['season_id'].values[0]

#     st.session_state['partidas'] = sb.matches(competition_id=id_campeonato, season_id=id_temporada)
    
#     filtro_selecao = st.selectbox(label='Selecione uma seleção:', options=sorted(pd.unique(st.session_state['partidas'][['home_team', 'away_team']].values.ravel())))
#     jogadores_selecao = []
#     for id_partida in st.session_state['partidas'][(st.session_state['partidas']['home_team'] == filtro_selecao) | (st.session_state['partidas']['away_team'] == filtro_selecao)]['match_id']:
#         for time, jogadores in sb.lineups(match_id=id_partida).items():
#             if time == filtro_selecao:
#                 for jogador in jogadores['player_name']:
#                     if jogador not in jogadores_selecao:
#                         jogadores_selecao.append(jogador)

#     filtro_jogador = st.selectbox(label='Selecione um jogador:', options=sorted(jogadores_selecao))
#     total_gols = 0
#     for id_partida in st.session_state['partidas'][(st.session_state['partidas']['home_team'] == filtro_selecao) | (st.session_state['partidas']['away_team'] == filtro_selecao)]['match_id']:      
#         partida = sb.events(match_id=id_partida)
#         gols = partida[(partida['shot_outcome'] == 'Goal') & (partida['player'] == filtro_jogador)].shape[0]
#         total_gols += gols
#     st.markdown(f'{filtro_jogador} marcou {total_gols} gol(s) em {filtro_campeonato} na temporada de {filtro_temporada}')


st.sidebar.title('Navegação')
pagina = st.sidebar.radio(label='Escolha uma página:', options=(pag_1_title, pag_2_title, pag_3_title))
if pagina == pag_1_title:
    pag_1()
elif pagina == pag_2_title:
    pag_2()
else:
    pag_3()
