import my_yt_tran  # 유튜브 동영상 정보와 자막을 가져오기 위한 모듈 임포트
import streamlit as st
from openai import OpenAI
from pathlib import Path
from annotated_text import annotated_text
import streamlit_ext as ste

# 유튜브 동영상을 번역하는 함수
def translate_youtube_video(video_url):

    # 유튜브 동영상 플레이어 추가
    st.video(video_url, format='video/mp4')

    # 유튜브 동영상 제목 가져오기
    _, yt_title, _, _, yt_duration = my_yt_tran.get_youtube_video_info(video_url)
    st.write(f"[제목] {yt_title}")              # 제목 및 상영 시간 출력
    st.write(f"[길이] {yt_duration}")           # 제목 및 상영 시간 출력
    st.divider()

    # 유튜브 동영상에서 mp3 추출하기
    download_path, video_id = my_yt_tran.download_youtube_as_mp3(video_url)

    # 음성 추출하기
    with st.expander("음성 추출 결과 (영문)", expanded=False):
        st.write(f"≫≫≫ 유튜브에서 mp3 파일 다운로드 완료 ({download_path.name})")

        transcript = my_yt_tran.audio_transcribe(download_path, r_format, openai_api_key)

        # 추출 결과 출력(전체)
        st.write(f"≫≫≫ 음성 추출 결과\n\n {transcript}")

    # 음성 추출 번역하기
    with st.expander("음성 추출 결과 (번역)", expanded=False):

        translate_transcript = my_yt_tran.traslate(download_path, r_format, transcript, trans_method, openai_api_key, deepl_api_key)

        # 추출 결과 출력(전체)
        st.write(f"≫≫≫ 음성 추출 번역 결과\n\n {translate_transcript}")
    
    download_folder = "./download"      # 다운로드할 폴더는 미리 생성 후 지정  
    output_file = f"{download_folder}/{video_id}.srt"
    file_name = f"{video_id}.srt"

    if r_format == "text":
        output_file = f"{download_folder}/{video_id}.txt"
        file_name = f"{video_id}.txt"
        
    with open(output_file, encoding='utf-8') as f:
        text_data = f.read()
        ste.download_button(
            label="음성 추출 결과 다운로드",
            data = text_data,
            file_name=file_name
        )

    # 요약하기
    if(summary_choose == "요약함"):
        with st.expander("요약 결과 (번역)", expanded=False):
            summary_en = my_yt_tran.summarize_text(transcript, "en", openai_api_key)
            st.write(f"≫≫≫ 요약 결과 (영문)\n\n {summary_en}")
            
            st.write("\n\n")
            
            translate_summary = my_yt_tran.traslate(download_path, "summary", summary_en, trans_method, openai_api_key, deepl_api_key)
            st.write(f"≫≫≫ 요약 결과 (한글)\n\n {translate_summary}")


# ------------------- 콜백 함수 --------------------
def url_reset():
    st.session_state['input'] = ""

# ------------- 사이드바 화면 구성 --------------------------  
# OpenAI API Key 입력 받기
openai_api_key = st.sidebar.text_input(label="OPENAI API 키", placeholder="Enter Your API Key", value="", type="password")

# DeepL API Key 입력 받기
deepl_api_key = st.sidebar.text_input(label="DeepL API 키", placeholder="Enter Your API Key", value="", type="password")


st.sidebar.divider()
# 유튜브 동영상 URL 입력 받기
url_text = st.sidebar.text_input("유튜브 동영상 URL", key="input")

# 유튜브 동영상 URL 내용 지우기
# clicked_for_clear = st.sidebar.button('URL 입력 내용 지우기', on_click=url_reset)


st.sidebar.divider()
# 번역 도구 선택하기
trans_method = st.sidebar.radio('번역 도구 선택', ['OpenAI', 'DeepL'], index=1, horizontal=True)

st.sidebar.divider()
# 출력 형식 선택하기
output_format = st.sidebar.radio('번역 형식 선택', ['텍스트(txt)', '자막(srt)'], index=1, horizontal=True)
if(output_format == "텍스트(txt)"):
    r_format = "text"
else:
    r_format = "srt"

st.sidebar.divider()
# 요약 여부 선택하기
summary_choose = st.sidebar.radio('요약 여부 선택', ['요약함', '요약 안 함'], index=1, horizontal=True)


st.sidebar.divider()
# 번역하기 버튼
clicked_for_sum = st.sidebar.button('번역하기')



# ------------- 메인 화면 구성 --------------------------     
# 제목 
st.title("유튜브 동영상 번역 프로그램")
st.divider()



if not openai_api_key:
    annotated_text(("ERROR", "OpenAI API 키를 입력해주세요.", "#faa"))

elif (trans_method == "DeepL" and not deepl_api_key):
    annotated_text(("ERROR", "DeepL API 키를 입력하거나, 번역 방법을 OpenAI로 선택해주세요.", "#faa"))

# 텍스트 입력이 있으면 수행
elif url_text and clicked_for_sum: 
    yt_video_url = url_text.strip()
    translate_youtube_video(yt_video_url)

st.divider()

# 기본 설명
with st.expander("사용법", expanded=False):
    st.write(
    """     
    **[OpenAI를 활용하여 번역하기]**
    1. 도서 179쪽을 참고하여 OpenAI API 키를 발급 받아주세요.
    2. OPENAI API 키에 1에서 발급 받은 API 키를 입력해주세요.
    3. 번역하고자 하는 동영상 URL을 입력하고 [번역하기] 버튼을 눌러주세요.

    **[DeepL을 활용하여 번역하기]**
    1. 도서 179쪽을 참고하여 OpenAI API 키를 발급 받아주세요.
    2. 도서 149쪽을 참고하여 DeepL API 키를 발급 받아주세요.
    3. OpenAI API 키에 1에서 발급 받은 API 키를 입력해주세요.
    4. DeepL API 키에 2에서 발급 받은 API 키를 입력해주세요.
    5. 번역하고자 하는 동영상 URL을 입력하고 [번역하기] 버튼을 눌러주세요.

    **[참고]**
    - 유튜브 영상을 텍스트로 변환하는 데에는 OepnAI의 Whisper AI를 활용했습니다.
    - 이 과정에서 API 키가 필요하며, OpenAI API 사용료가 부과됩니다. 
    - 텍스트를 한글로 번역하는 데에는 OpenAI의 GPT-3, DeepL을 활용했습니다.
    - 이 과정에서 API 키가 필요하며, OepnAI API 또는 DeepL API 사용료가 부과됩니다. 
    """
    )

with st.expander("출처", expanded=False):
    st.write(
    """     
    유튜브 동영상 번역 프로그램은 위키북스의 도서를 참고하여 만들었습니다.
    - 참고 도서 1: ≪만들면서 배우는 나만의 인공지능 서비스, 최은석 지음≫
    - 참고 도서 2: ≪진짜 챗GPT API 활용법, 김준성, 브라이스 유, 안상준 지음≫
    """
    )

    st.markdown("")
