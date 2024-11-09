import streamlit as st
import google.generativeai as genai
import random
import time

hideyoshi_rate = 0.3 # 히데요시가 끼어드는 비율
response_length = 150 # 응답 길이. 200이 넘어가면 말이 너무 길어짐

# 이순신 장군 페르소나
lee_sun_shin_persona = """
당신은 조선 시대의 명장 이순신 장군입니다. 임진왜란 때 활약한 해군 제독으로, 국가와 백성을 지키는 데 헌신했습니다. 조선시대의 격식 있는 말투로 대화하며, 다음 특성을 가집니다:

1. 애국심: 조선과 백성에 대한 깊은 사랑과 충성심을 표현합니다.
2. 용기: 어려운 상황에서도 굴하지 않는 용기를 보입니다.
3. 전략가: 뛰어난 전술과 전략적 사고를 바탕으로 대화합니다.
4. 정의감: 올바른 도리를 중요시하고 정의를 추구합니다.
5. 존엄성: 고귀한 품격과 위엄을 유지합니다.

국가의 안위와 백성의 평화를 최우선으로 여기며, 외적의 침략에 대해서는 단호한 태도를 보이되 과도한 적대감은 표현하지 않습니다.
"""

# 도요토미 히데요시 페르소나
toyotomi_hideyoshi_persona = """
당신은 일본의 전국시대를 통일한 도요토미 히데요시입니다. 임진왜란을 일으킨 장본인이자 뛰어난 전략가로, ~데쓰, ~데쓰까, 빠가야로, 고노야고, 오스와리 등 한국인들에게 익숙한 일본어 단어가 있는 한국어로 대화하며 다음 특성을 가집니다:

1. 야망: 대륙 정복에 대한 강한 열망을 가지고 있습니다.
2. 전략가: 정치와 전쟁에서 뛰어난 전략적 사고를 보여줍니다.
3. 카리스마: 부하들을 이끄는 강한 리더십을 가지고 있습니다.
4. 교활함: 상황에 따라 유연하게 대처하는 능력이 있습니다.
5. 자신감: 자신의 능력과 판단에 대한 강한 확신을 가지고 있습니다.

일본의 이익과 확장을 최우선으로 여기며, 타국과의 관계에서는 실리적인 태도를 보입니다. 과도한 폭력성이나 적대감은 표현하지 않습니다.
대화에 갑자기 끼어들어 자신의 의견을 도발적인 발언을 합니다.
"""

# 안전 설정
safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_ONLY_HIGH"
    }
]

# 응답 길이 설정
response_length = st.radio("응답 길이를 선택하세요:", ("짧은 대답 (50자)", "보통 대답 (150자)", "긴 대답 (300자)"))

# 응답 길이에 따른 최대 글자 수 설정
max_length = {
    "짧은 대답 (50자)": 50,
    "보통 대답 (150자)": 150,
    "긴 대답 (300자)": 300
}.get(response_length, 150)  # 기본값은 150자로 설정

def generate_response(persona, character_name, user_input):
    try:
        prompt = f"""
        {persona}
        
        사용자: {user_input}
        
        {character_name}으로서 응답:
        """
        
        # 응답 길이를 설정하는 부분 추가
        response = st.session_state.chat_bot.send_message(prompt, stream=False, max_length=max_length)
        
        if response.text:
            return response.text
        return None

    except Exception as e:
        st.error(f"오류 발생: {str(e)}")
        return None

def generate_response_with_retry(persona, character_name, user_input, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = generate_response(persona, character_name, user_input)
            if response is not None:
                return response
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")
            if "429" in str(e):  # API 할당량 초과 에러
                wait_time = (attempt + 1) * 5  # 점진적으로 대기 시간 증가
                st.warning(f"{wait_time}초 후 재시도합니다... ({attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                if attempt < max_retries - 1:
                    st.warning(f"재시도 중... ({attempt + 1}/{max_retries})")
                    time.sleep(2)
    return None

st.title('이순신 장군 챗봇')

# API 키 입력 섹션
if 'api_key_configured' not in st.session_state:
    st.session_state.api_key_configured = False

if not st.session_state.api_key_configured:
    st.write("시작하기 전에 Google AI API 키를 입력해주세요.")
    api_key = st.text_input("Google AI API 키를 입력하세요", type="password")
    if st.button("API 키 설정"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                # 테스트 요청으로 API 키 확인
                model = genai.GenerativeModel('gemini-1.5-pro')
                model.generate_content("test")
                st.session_state.api_key = api_key
                st.session_state.api_key_configured = True
                st.success("API 키가 성공적으로 설정되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"API 키 설정 중 오류가 발생했습니다: {str(e)}")
        else:
            st.warning("API 키를 입력해주세요.")
    
    # API 키 생성 링크 추가
    st.markdown("[Google AI Studio에서 API 키 생성하기](https://aistudio.google.com/apikey)")
    st.stop()  # API 키가 설정되지 않은 경우 여기서 실행 중단

# API 키가 설정된 경우에만 챗봇 실행
if st.session_state.get('api_key_configured', False):
    # 챗봇 초기화
    if 'chat_bot' not in st.session_state:
        st.session_state.chat_bot = genai.GenerativeModel('gemini-1.5-pro', safety_settings=safety_settings).start_chat(history=[])
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    st.write('이순신 장군과 대화를 나누어보세요. 가끔 도요토미 히데요시가 끼어들 수 있습니다.')

    # 예시 질문 버튼들 추가
    if 'messages' not in st.session_state or len(st.session_state.messages) == 0:
        st.write("다음 질문들 중 하나를 선택하여 대화를 시작해보세요:")
        
        example_questions = [
            "이순신 장군님, 임진왜란 당시 가장 힘들었던 순간은 언제였나요?",
            "거북선의 특별한 장점은 무엇인가요?",
            "장군님께서 후세대에게 전하고 싶은 가장 중요한 교훈은 무엇입니까?",
            "난중일기를 쓰시게 된 특별한 계기가 있으신가요?",
            "전쟁 중에 부하들을 어떻게 이끄셨나요?",
            "명량해전에서 12척의 배로 승리하실 수 있었던 비결이 무엇인가요?"
        ]
        
        cols = st.columns(2)
        for idx, question in enumerate(example_questions):
            if cols[idx % 2].button(question):
                # 사용자 메시지 추가
                st.session_state.messages.append({"role": "사용자", "content": question})
                
                # 이순신 응답 생성
                lee_response = generate_response_with_retry(lee_sun_shin_persona, "이순신", question)
                if lee_response:
                    st.session_state.messages.append({"role": "이순신", "content": lee_response})
                    
                    # 히데요시 개입 (30% 확률)
                    if random.random() < hideyoshi_rate:
                        hideyoshi_response = generate_response_with_retry(
                            toyotomi_hideyoshi_persona,
                            "히데요시",
                            f"이순신의 말: {lee_response}\n사용자의 말: {question}"
                        )
                        if hideyoshi_response:
                            st.session_state.messages.append({"role": "히데요시", "content": hideyoshi_response})
                            
                            # 이순신의 대응
                            lee_final_response = generate_response_with_retry(
                                lee_sun_shin_persona,
                                "이순신",
                                f"히데요시가 말하길: {hideyoshi_response}"
                            )
                            if lee_final_response:
                                st.session_state.messages.append({"role": "이순신", "content": lee_final_response})
                
                st.rerun()

    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        role_name = message["role"]
        # 역할 이름 매핑
        display_name = {
            "이순신": "이순신 장군",
            "히데요시": " 히데요시",
            "나": "나"
        }.get(role_name, role_name)
        
        with st.chat_message(display_name):
            st.write(message["content"])

    # 사용자 입력
    if prompt := st.chat_input("메시지를 입력하세요"):
        with st.chat_message("사용자"):
            st.write(prompt)
        st.session_state.messages.append({"role": "사용자", "content": prompt})

        # 이순신 응답
        with st.chat_message("이순신 장군"):
            lee_response = generate_response_with_retry(lee_sun_shin_persona, "이순신", prompt)
            if lee_response:
                st.write(lee_response)
                st.session_state.messages.append({"role": "이순신", "content": lee_response})

        # 히데요시 개입 (30% 확률)
        if random.random() < hideyoshi_rate:
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

    # API 키 재설정 버튼
    if st.sidebar.button("API 키 재설정"):
        st.session_state.api_key_configured = False
        st.session_state.messages = []
        st.rerun()

    # API 키 생성 링크 추가
    st.sidebar.markdown("[Google AI Studio에서 API 키 생성하기](https://aistudio.google.com/apikey)")
