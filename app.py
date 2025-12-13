import streamlit as st
import random
import json
import os

TOPIC_FILE = "topics.json"

# --------------------------
# 주제 저장/불러오기
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
# 기본 설정 (모바일 최적화)
# --------------------------
st.set_page_config(page_title="라이어 게임", page_icon="🎮", layout="centered")
st.markdown(
    "<style>body {zoom:0.9;} .stButton>button{width:100%;}</style>",
    unsafe_allow_html=True,
)

st.title("🎮 온라인 라이어 게임")

# --------------------------
# 다시 시작
# --------------------------
def reset_game():
    for k in list(st.session_state.keys()):
        del st.session_state[k]

if st.sidebar.button("🔄 다시 시작하기"):
    reset_game()
    st.rerun()

page = st.sidebar.selectbox("메뉴", ["게임 시작", "주제 추가"])

# =====================================================================
# 📝 주제 추가
# =====================================================================
if page == "주제 추가":
    st.header("📝 게임 주제 추가")

    q = st.text_input("1) 질문 입력")
    number_range = st.text_input("2) 숫자범위 입력 (예: 1~100)")

    if st.button("주제 저장"):
        if not q.strip() or not number_range.strip():
            st.error("모든 항목을 입력하세요.")
        else:
            save_topic(q, number_range)
            st.success("주제가 저장되었습니다!")

    st.subheader("📚 저장된 주제")
    for i, t in enumerate(load_topics()):
        st.write(f"{i+1}. {t['question']} / {t['range']}")

# =====================================================================
# 🎲 게임 시작
# =====================================================================
if page == "게임 시작":
    st.header("🎲 게임 설정")

    players = st.number_input("게임 인원 (3~10명)", 3, 10, 5)
    topics = load_topics()

    if len(topics) == 0:
        st.warning("주제가 없습니다. 먼저 주제를 추가하세요.")
        st.stop()

    # --------------------------
    # 역할 배정 시작
    # --------------------------
    if st.button("역할 배정 시작"):

        # 🔥 주제 랜덤 선택 (플레이어에게 비공개)
        selected_topic = random.choice(topics)

        # 역할 구성
        if players <= 3:
            roles = ["라이어"] + ["시민"] * (players - 1)
        else:
            roles = ["라이어", "트롤"] + ["시민"] * (players - 2)

        random.shuffle(roles)

        st.session_state.roles = roles
        st.session_state.topic = selected_topic
        st.session_state.current_player = 1
        st.session_state.phase = "role_check"

        st.success("역할 배정 완료! 한 명씩 역할을 확인하세요.")

    # =================================================================
    # 👤 역할 확인
    # =================================================================
    if st.session_state.get("phase") == "role_check":

        player = st.session_state.current_player
        st.subheader(f"👤 {player}번 플레이어 차례")

        if f"checked_{player}" not in st.session_state:
            st.session_state[f"checked_{player}"] = False

        if not st.session_state[f"checked_{player}"]:
            if st.button("👉 역할 확인하기"):
                st.session_state[f"checked_{player}"] = True
        else:
            role = st.session_state.roles[player - 1]
            topic = st.session_state.topic

            st.subheader(f"당신의 역할: {role}")

            if role == "라이어":
                st.warning("라이어는 질문을 볼 수 없습니다.")
                st.info(f"숫자 범위: {topic['range']}")
            else:
                st.success(f"질문: {topic['question']}")
                st.info(f"숫자 범위: {topic['range']}")

            if player < players:
                if st.button("➡️ 다음 플레이어"):
                    st.session_state.current_player += 1
                    st.rerun()
            else:
                if st.button("🎯 역할 확인 완료 → 투표"):
                    st.session_state.phase = "vote"
                    st.rerun()

    # =================================================================
    # 🗳 최종 투표
    # =================================================================
    if st.session_state.get("phase") == "vote":
        st.header("🗳 범인은 누구인가?")

        choice = st.radio("번호 선택", list(range(1, players + 1)))

        if st.button("결과 보기"):
            role = st.session_state.roles[choice - 1]

            if role == "라이어":
                st.success("🎉 시민 승리! 라이어를 정확히 찾았습니다!")
            elif role == "트롤":
                st.warning("🤡 트롤 승리! 트롤이 라이어로 지목됨!")
            else:
                st.error("😈 라이어 승리! 시민이 틀렸습니다.")
