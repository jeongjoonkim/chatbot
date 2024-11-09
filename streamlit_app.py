import streamlit as st
import google.generativeai as genai
import random
import time

# API 키 설정 - .env 파일이나 Streamlit Secrets로 관리하는 것을 추천합니다
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]  # Streamlit Cloud에서 설정
genai.configure(api_key=GOOGLE_API_KEY)

# ... 페르소나 정의는 동일하게 유지 ...

# 세션 상태 초기화
if 'chat_bot' not in st.session_state:
    st.session_state.chat_bot = genai.GenerativeModel('gemini-1.5-pro', safety_settings=safety_settings).start_chat(history=[])
if 'messages' not in st.session_state:
    st.session_state.messages = []

st.title('이순신 장군 챗봇')
st.write('이순신 장군과 대화를 나누어보세요. 가끔 도요토미 히데요시가 끼어들 수 있습니다.')

# 채팅 히스토리 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요"):
    # 사용자 메시지 표시
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 이순신 응답
    with st.chat_message("이순신"):
        lee_response = generate_response_with_retry(lee_sun_shin_persona, "이순신", prompt)
        if lee_response:
            st.write(lee_response)
            st.session_state.messages.append({"role": "이순신", "content": lee_response})

    # 히데요시 개입 (50% 확률)
    if random.random() < 0.49:
        with st.chat_message("히데요시"):
            hideyoshi_response = generate_response_with_retry(
                toyotomi_hideyoshi_persona,
                "히데요시",
                f"이순신의 말: {lee_response}\n사용자의 말: {prompt}"
            )
            if hideyoshi_response:
                st.write(hideyoshi_response)
                st.session_state.messages.append({"role": "히데요시", "content": hideyoshi_response})

        # 이순신의 대응
        with st.chat_message("이순신"):
            lee_final_response = generate_response_with_retry(
                lee_sun_shin_persona,
                "이순신",
                f"히데요시가 말하길: {hideyoshi_response}"
            )
            if lee_final_response:
                st.write(lee_final_response)
                st.session_state.messages.append({"role": "이순신", "content": lee_final_response})
