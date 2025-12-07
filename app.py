import streamlit as st
import random
import json
import os

TOPIC_FILE = "topics.json"

# --------------------------
# 주제 저장/불러오기 기능
# --------------------------
def load_topics():
    if not os.path.exists(TOPIC_FILE):
        return []
    with open(TOPIC_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_topic(question, number_range):
    topics = load_topics()
    topics.append({"question": question, "range": number_range})
    with open(TOPIC_FILE, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=4)

# --------------------------
# 기본 페이지 설정 + 모바일 최적화
# --------------------------
st.set_page_config(page_title="라이어 게임", page_icon="🎮", layout="centered")
st.markdown(
    "<style>body {zoom: 0.9;} .stButton>button{width:100%; font-size:18px; padding:10px 0;}</style>",
    unsafe_allow_html=True,
)

st.title("🎮 온라인 라이어 게임")

# --------------------------
# 다시 시작하기 기능
# --------------------------
def reset_game():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

if st.sidebar.button("🔄 다시 시작하기"):
    reset_game()
    st.rerun()

page = st.sidebar.selectbox("메뉴", ["게임 시작", "주제 추가"])

# =====================================================================
# 1) 주제 추가 페이지
# =====================================================================
if page == "주제 추가":
    st.header("📝 게임 주제 추가")

    q = st.text_input("1) 질문 입력")
    number_range = st.text_input("2) 숫자범위 입력 (예: 1~100)")

    if st.button("주제 저장"):
        if q.strip() == "" or number_range.strip() == "":
            st.error("모든 항목을 채워주세요.")
        else:
            save_topic(q, number_range)
            st.success("주제가 저장되었습니다!")

    st.subheader("📚 저장된 주제 목록")
    topics = load_topics()

    for i, t in enumerate(topics):
        st.write(f"{i+1}. 질문: {t['question']} / 숫자범위: {t['range']}")

# =====================================================================
# 2) 게임 시작 페이지
# =====================================================================
if page == "게임 시작":
    st.header("🎲 게임 설정")

    players = st.number_input("게임 인원 (3~10명)", min_value=3, max_value=10, value=5)
    topics = load_topics()

    if len(topics) == 0:
        st.warning("주제가 없습니다! 먼저 주제를 추가해주세요.")
        st.stop()

    selected_topic = st.selectbox("주제 선택", topics)

    if "roles" not in st.session_state:
        st.session_state.roles = None
    if "current_player" not in st.session_state:
        st.session_state.current_player = 1
    if "game_stage" not in st.session_state:
        st.session_state.game_stage = "assign"

    # --------------------------
    # 역할 배정
    # --------------------------
    if st.session_state.game_stage == "assign":

        if st.button("역할 배정 시작"):
            roles = ["시민"] * players

            # 3명 → 라이어 1명
            if players <= 3:
                liar = random.randint(0, players - 1)
                roles[liar] = "라이어"
            else:
                # 4명 이상 → 라이어 + 트롤 추가
                liar = random.randint(0, players - 1)
                troll = random.randint(0, players - 1)
                while troll == liar:
                    troll = random.randint(0, players - 1)

                roles[liar] = "라이어"
                roles[troll] = "트롤"

            st.session_state.roles = roles
            st.session_state.game_stage = "role_check"
            st.rerun()

    # --------------------------
    # 역할 확인 단계
    # --------------------------
    if st.session_state.game_stage == "role_check":
        st.subheader(f"플레이어 {st.session_state.current_player} 역할 확인")

        if st.button("역할 보기"):
            role = st.session_state.roles[st.session_state.current_player - 1]
            st.success(f"당신의 역할: **{role}**")

        if st.button("확인 완료"):
            if st.session_state.current_player == players:
                st.session_state.game_stage = "voting"
            else:
                st.session_state.current_player += 1
            st.rerun()

    # --------------------------
    # 범인 선택 단계 (타이머 제거)
    # --------------------------
    if st.session_state.game_stage == "voting":
        st.header("🔎 범인을 선택하세요!")

        choice = st.selectbox("누가 라이어인가?", list(range(1, players + 1)))

        if st.button("선택 완료"):
            selected = choice - 1
            roles = st.session_state.roles

            if roles[selected] == "라이어":
                st.success("🎉 시민 승리! (라이어를 정확히 찾아냈습니다)")
            elif roles[selected] == "트롤":
                st.error("🤡 트롤 승리! (트롤이 라이어로 지목됨)")
            else:
                st.error("😈 라이어 승리! (시민을 지목함)")

            st.write("게임이 종료되었습니다. 왼쪽의 '다시 시작하기'로 재시작하세요.")
