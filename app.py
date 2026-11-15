import html

import streamlit as st
from crewai import Crew, Process
from dotenv import load_dotenv

from agents import DEPARTMENTS, create_department_agents, create_llm
from storage import StorageError, load_department_state, save_department_state
from tasks import create_department_task


load_dotenv()

st.set_page_config(
    page_title="멀티 에이전트 타이쿤",
    page_icon="🕹️",
    layout="wide",
)

DEPARTMENT_KEYS = list(DEPARTMENTS)
DEPARTMENT_PERSONAS = {
    "youtube": {"avatar": "👨‍💻", "title": "콘텐츠 크리에이터", "quest": "🎬 영상 제작 퀘스트"},
    "webnovel": {"avatar": "🧙‍♂️", "title": "스토리 마법사", "quest": "📚 세계관 제작 퀘스트"},
    "business": {"avatar": "🕵️‍♂️", "title": "신사업 탐정", "quest": "💡 신사업 탐사 퀘스트"},
}


def build_plan(department_key: str, request: str) -> str:
    llm = create_llm()
    manager, workers = create_department_agents(department_key, llm)
    task = create_department_task(department_key, workers)
    crew = Crew(
        agents=workers,
        tasks=[task],
        process=Process.hierarchical,
        manager_agent=manager,
        verbose=False,
    )
    result = crew.kickoff(inputs={"request": request})
    return str(result)


def render_bubble(content: str, bubble_class: str) -> None:
    safe_content = html.escape(content).replace("\r\n", "\n").replace("\n", "<br>")
    st.markdown(
        f'<div class="message-bubble {bubble_class}">{safe_content}</div>',
        unsafe_allow_html=True,
    )


def render_chat_message(message: dict, avatar: str) -> None:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👑"):
            render_bubble(message["content"], "player-bubble")
        return

    kind = message.get("kind", "report")
    bubble_class = "error-bubble" if kind == "error" else "npc-bubble"
    with st.chat_message("assistant", avatar=avatar):
        render_bubble(message["content"], bubble_class)


st.markdown(
    """
    <style>
    :root {
        --ink: #29233f;
        --purple: #7652bd;
        --purple-dark: #4a3971;
        --panel: #fffdf6;
        --pixel-shadow: 4px 4px 0 rgba(53, 43, 82, .18);
    }
    [data-testid="stAppViewContainer"] {
        color: var(--ink);
        background-color: #edeaff;
        background-image:
            linear-gradient(rgba(99, 79, 150, .055) 1px, transparent 1px),
            linear-gradient(90deg, rgba(99, 79, 150, .055) 1px, transparent 1px),
            linear-gradient(145deg, #f3efff 0%, #fff8f1 54%, #eaf8ff 100%);
        background-size: 18px 18px, 18px 18px, cover;
    }
    [data-testid="stHeader"] { background: rgba(247, 244, 255, .86); }
    .block-container {
        max-width: 1050px;
        padding: 1.7rem 1.25rem 6rem;
    }
    [data-testid="stSidebar"] {
        background: #e4defa;
        border-right: 3px solid #554777;
    }
    .game-panel {
        padding: 1rem;
        margin: .2rem 0 1rem;
        border: 2px solid #554777;
        border-radius: 12px;
        color: var(--ink);
        background: var(--panel);
        box-shadow: var(--pixel-shadow);
        font-family: "Courier New", "Malgun Gothic", monospace;
        font-weight: 800;
        line-height: 1.65;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        min-height: 54px;
        margin: .25rem 0;
        padding: .7rem .8rem;
        border: 2px solid #76669c;
        border-radius: 9px;
        background: #faf8ff;
        box-shadow: 2px 2px 0 rgba(53, 43, 82, .12);
    }
    h1, h2, h3 {
        color: #382d59;
        font-family: "Courier New", "Malgun Gothic", monospace;
        font-weight: 900 !important;
        text-shadow: 2px 2px 0 #d9cdf5;
    }
    .quest-tag {
        display: inline-block;
        padding: .35rem .7rem;
        margin-bottom: .35rem;
        border: 2px solid #5b497e;
        border-radius: 8px;
        color: #49396c;
        background: #e8ddff;
        box-shadow: 3px 3px 0 rgba(53, 43, 82, .17);
        font-family: "Courier New", "Malgun Gothic", monospace;
        font-size: .88rem;
        font-weight: 900;
    }
    .avatar-stage {
        display: flex;
        width: clamp(88px, 12vw, 124px);
        height: clamp(88px, 12vw, 124px);
        align-items: center;
        justify-content: center;
        border: 3px solid #554777;
        border-radius: 18px;
        background: linear-gradient(145deg, #fff 0%, #e4dcff 100%);
        box-shadow: 5px 5px 0 rgba(53, 43, 82, .2), inset 0 0 0 5px #f7f3ff;
        font-size: clamp(3rem, 7vw, 4.8rem);
        line-height: 1;
    }
    .message-bubble {
        position: relative;
        width: fit-content;
        max-width: min(100%, 850px);
        margin: .2rem 0 .7rem;
        padding: .95rem 1.1rem;
        border: 2px solid #5b4b78;
        border-radius: 18px;
        color: #302943;
        background: var(--panel);
        box-shadow: 4px 5px 0 rgba(53, 43, 82, .18);
        font-size: 1rem;
        line-height: 1.75;
        overflow-wrap: anywhere;
    }
    .npc-bubble::before, .error-bubble::before {
        position: absolute;
        top: 19px;
        left: -9px;
        width: 14px;
        height: 14px;
        border-bottom: 2px solid #5b4b78;
        border-left: 2px solid #5b4b78;
        background: var(--panel);
        content: "";
        transform: rotate(45deg);
    }
    .player-bubble {
        margin-left: auto;
        border-color: #4a7090;
        background: #e2f5ff;
    }
    .player-bubble::after {
        position: absolute;
        top: 18px;
        right: -9px;
        width: 14px;
        height: 14px;
        border-top: 2px solid #4a7090;
        border-right: 2px solid #4a7090;
        background: #e2f5ff;
        content: "";
        transform: rotate(45deg);
    }
    .error-bubble {
        border-color: #bd5a58;
        color: #7d2727;
        background: #fff0ec;
    }
    .error-bubble::before { border-color: #bd5a58; background: #fff0ec; }
    .typing-bubble {
        animation: npc-breathe .8s ease-in-out infinite alternate;
        background: #fff4cf;
    }
    @keyframes npc-breathe {
        from { transform: translateY(0); box-shadow: 4px 5px 0 rgba(53, 43, 82, .16); }
        to { transform: translateY(-2px); box-shadow: 4px 8px 0 rgba(53, 43, 82, .2); }
    }
    div.stButton > button {
        min-height: 54px;
        border: 2px solid #443561;
        border-radius: 10px;
        color: #fff;
        background: linear-gradient(180deg, #9876dc, #7652bd);
        box-shadow: 4px 4px 0 #514073;
        font-family: "Courier New", "Malgun Gothic", monospace;
        font-weight: 900;
        transition: transform .12s ease, box-shadow .12s ease, filter .12s ease;
    }
    div.stButton > button:hover {
        color: #fff;
        filter: brightness(1.08);
        transform: translate(-1px, -1px);
        box-shadow: 5px 5px 0 #514073;
    }
    div.stButton > button:active {
        transform: translate(3px, 3px);
        box-shadow: 1px 1px 0 #514073;
    }
    [data-testid="stChatInput"] {
        border: 2px solid #594779;
        border-radius: 14px;
        background: #fffdf8;
        box-shadow: 0 0 0 4px rgba(111, 84, 166, .13);
    }
    [data-testid="stChatInput"] textarea {
        min-height: 48px;
        font-size: 1rem;
    }
    [data-testid="stChatMessage"] {
        padding: .35rem .55rem;
        border-radius: 12px;
    }
    @media (max-width: 700px) {
        .block-container { padding: .8rem .65rem 5rem; }
        [data-testid="stHorizontalBlock"] { gap: .6rem; }
        .message-bubble {
            max-width: 100%;
            padding: .8rem .85rem;
            font-size: .96rem;
            line-height: 1.65;
        }
        .avatar-stage { width: 76px; height: 76px; border-radius: 14px; }
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            min-height: 58px;
            padding: .75rem;
        }
        div.stButton > button { width: 100%; }
        [data-testid="stChatInput"] textarea { min-height: 52px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

user_info = st.user
user_id = str(user_info.get("sub", "")).strip()
login_state = getattr(user_info, "is_logged_in", None)
if login_state is None:
    login_state = bool(user_id)

if not login_state or not user_id:
    st.session_state.pop("authenticated_user_id", None)
    st.title("🕹️ 에이전트 타이쿤")
    st.info("휴대폰·태블릿 등 여러 기기에서 기록을 동기화하려면 Google 로그인이 필요합니다.")
    st.button("Google 계정으로 로그인", on_click=st.login, use_container_width=True)
    st.caption("로그인 버튼이 동작하지 않으면 배포 환경의 Streamlit 인증 설정을 확인해 주세요.")
    st.stop()

st.session_state["authenticated_user_id"] = user_id
user_id = st.session_state["authenticated_user_id"]

st.sidebar.markdown(
    '<div class="game-panel">🕹️ 타이쿤 컨트롤 타워<br>부서를 골라 대화를 시작하세요!</div>',
    unsafe_allow_html=True,
)
email = user_info.get("email", "")
if email:
    st.sidebar.caption(email)
st.sidebar.button("로그아웃", on_click=st.logout, use_container_width=True)
selected_department = st.sidebar.radio(
    "부서 선택",
    options=DEPARTMENT_KEYS,
    format_func=lambda key: DEPARTMENTS[key]["name"],
)

department_name = DEPARTMENTS[selected_department]["name"]
persona = DEPARTMENT_PERSONAS[selected_department]
history_key = f"chat_{selected_department}"
plan_key = f"plan_{selected_department}"
approval_key = f"approved_{selected_department}"

try:
    department_state = load_department_state(user_id, selected_department)
except StorageError as exc:
    st.error(str(exc))
    st.stop()

st.session_state[history_key] = department_state.history
st.session_state[plan_key] = department_state.plan
st.session_state[approval_key] = department_state.approved

history = st.session_state[history_key]
if not history and st.session_state[plan_key]:
    history.append({"role": "assistant", "kind": "report", "content": st.session_state[plan_key]})


def persist_department_state() -> None:
    try:
        save_department_state(
            user_id,
            selected_department,
            history,
            st.session_state[plan_key],
            st.session_state[approval_key],
        )
    except StorageError as exc:
        st.error(str(exc))
        st.stop()


st.title("🕹️ 에이전트 타이쿤")
st.caption("메신저로 업무를 지시하고, 부서장의 보고를 말풍선으로 확인하세요.")

avatar_col, title_col = st.columns([1.1, 5], vertical_alignment="center")
with avatar_col:
    avatar_html = (
        '<div class="avatar-stage" aria-label="{} 아바타">{}</div>'.format(
            html.escape(persona["title"], quote=True),
            html.escape(persona["avatar"]),
        )
    )
    st.markdown(avatar_html, unsafe_allow_html=True)
with title_col:
    st.markdown(f'<div class="quest-tag">{persona["quest"]}</div>', unsafe_allow_html=True)
    st.header(department_name)
    st.caption(f"부서장 · {persona['title']}  |  최종 결정권자: 당신")

st.markdown(
    '<div class="game-panel">💬 부서 채팅방<br>명령을 보내면 부서장이 실무진에게 전달합니다.</div>',
    unsafe_allow_html=True,
)

for message in history:
    render_chat_message(message, persona["avatar"])

if st.session_state[plan_key]:
    if st.button("✅ 승인 및 실행", key=f"approve_{selected_department}"):
        st.session_state[approval_key] = True
        persist_department_state()
    if st.session_state[approval_key]:
        st.success("승인 상태로 기록했습니다. 외부 서비스에 실제 게시·실행되지는 않습니다.")

prompt = st.chat_input(
    f"{department_name}에 내릴 업무를 입력하세요...",
    key=f"chat_input_{selected_department}",
)

if prompt:
    prompt = prompt.strip()
    if not prompt:
        st.warning("업무 지시 내용을 입력해 주세요.")
    else:
        user_message = {"role": "user", "kind": "text", "content": prompt}
        history.append(user_message)
        render_chat_message(user_message, persona["avatar"])

        st.session_state[plan_key] = ""
        st.session_state[approval_key] = False
        start_message = {
            "role": "assistant",
            "kind": "notice",
            "content": "작업을 시작합니다!",
        }
        history.append(start_message)

        persist_department_state()

        with st.chat_message("assistant", avatar=persona["avatar"]):
            render_bubble("작업을 시작합니다! 열심히 일하는 중... 💦", "npc-bubble typing-bubble")
            try:
                with st.spinner("실무진이 움직이고 부서장이 최종 기획안을 검토하고 있습니다..."):
                    result = build_plan(selected_department, prompt)
            except (ValueError, ImportError) as exc:
                error_message = {
                    "role": "assistant",
                    "kind": "error",
                    "content": str(exc),
                }
                history.append(error_message)
                render_bubble(error_message["content"], "error-bubble")
                persist_department_state()
            except Exception as exc:
                error_message = {
                    "role": "assistant",
                    "kind": "error",
                    "content": f"기획안 생성에 실패했습니다: {exc}",
                }
                history.append(error_message)
                render_bubble(error_message["content"], "error-bubble")
                persist_department_state()
            else:
                st.session_state[plan_key] = result
                report_message = {
                    "role": "assistant",
                    "kind": "report",
                    "content": result,
                }
                history.append(report_message)
                persist_department_state()
                render_bubble(result, "npc-bubble")
