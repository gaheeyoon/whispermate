# 유튜브 동영상 정보와 자막을 가져오기 위한 모듈
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from pathlib import Path
from openai import OpenAI
import deepl

# 유튜브 비디오 정보를 가져오는 함수
def get_youtube_video_info(video_url):
    ydl_opts = {                                # 다양한 옵션 지정
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        video_info = ydl.extract_info(video_url, download=False)    # 비디오 정보 추출
        video_id = video_info['id']                                 # 비디오 정보에서 비디오 ID 추출
        title = video_info['title']                                 # 비디오 정보에서 제목 추출
        upload_date = video_info['upload_date']                     # 비디오 정보에서 업로드 날짜 추출
        channel = video_info['channel']                             # 비디오 정보에서 채널 이름 추출
        duration = get_duration_time(video_info['duration_string'])

    return video_id, title, upload_date, channel, duration


# 유튜브 비디오 URL에서 비디오 ID를 추출하는 함수
def get_video_id(video_url):
    video_id = video_url.split('v=')[1][:11]
    return video_id 


# 유튜브 비디오 시간을 시, 분, 초로 반환하는 함수
def get_duration_time(duration):
    duration_list = duration.split(':')

    if(len(duration_list) == 2):
        return duration_list[0] + "분 " + duration_list[1] + "초"
    elif(len(duration_list) == 3):
        return duration_list[0] + "시간 " + duration_list[1] + "분 " + duration_list[2] + "초"
    

# 유튜브 동영상에서 mp3를 추출하는 함수
def download_youtube_as_mp3(video_url):
    download_folder = "./download"      # 다운로드할 폴더는 미리 생성 후 지정
    video_id = get_video_id(video_url)  # video_id 구하기
    
    outtmpl_str = f'{download_folder}/{video_id}.mp3'
    download_path = Path(outtmpl_str)

    ydl_opts = {     
        'extract_audio': True,      # 다양한 옵션 지정                    
        'format': 'bestaudio/best', # 다운로드 형식 지정 (최적)
        'outtmpl': outtmpl_str,     # 다운로드 경로 지정
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(video_url) # 다운로드

    return download_path


# 오디오에서 자막을 추출하는 함수
def audio_transcribe(input_path, resp_format, openai_api_key):  

    client = OpenAI(api_key=openai_api_key)

    # 음성 파일 열기
    with open(input_path, "rb") as f: 
        # 음성 추출  
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
            response_format=resp_format)            # 추출할 텍스트 형식 지정

    # 음성을 텍스트로 추출한 후에 텍스트 파일로 저장
    path = Path(input_path)
    if resp_format == "text":
        output_file = f"{path.parent}/{path.stem}.txt"
    else:
        output_file = f"{path.parent}/{path.stem}.srt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(transcript)

    return transcript


# 영어를 한국어로 번역하는 함수
def traslate(text, type, openai_api_key, deepl_api_key):
    if(type == "OpenAI"):
        translate_transcript = traslate_using_openAI(text, openai_api_key)
    else:
        translate_transcript = traslate_using_deepL(text, deepl_api_key)

    return translate_transcript



# OpenAI 라이브러리를 이용해 영어를 한국어로 번역하는 함수
def traslate_using_openAI(text, openai_api_key):    

    client = OpenAI(api_key=openai_api_key)

    # 대화 메시지 정의
    user_content = f"Translate the following sentences into Korean.\n {text}"
    messages = [ {"role": "user", "content": user_content} ]
    
    # Chat Completions API 호출
    response = client.chat.completions.create(
                            model="gpt-3.5-turbo",      # 사용할 모델 선택 
                            messages=messages,          # 전달할 메시지 지정
                            temperature=0.2,            # 완성의 다양성을 조절하는 온도 설정
                            n=1                         # 생성할 완성의 개수 지정
    )

    assistant_reply = response.choices[0].message.content # 첫 번째 응답 결과 가져오기
    
    return assistant_reply



# DeepL 라이브러리를 이용해 텍스트를 한국어로 번역하는 함수
def traslate_using_deepL(text, deepl_api_key):   
    translator = deepl.Translator(deepl_api_key) # translator 객체를 생성
    result = translator.translate_text(text, target_lang="KO") # 번역 결과 객체를 result 변수에 할당
    
    return result.text



# OpenAI 라이브러리를 이용해 텍스트를 요약하는 함수
def summarize_text(user_text, lang, openai_api_key): # lang 인자에 영어를 기본적으로 지정
    
    client = OpenAI(api_key=openai_api_key)

    # 대화 메시지 정의
    if lang == "en":
        messages = [ 
            {"role": "system", "content": "You are a helpful assistant in the summary."},
            {"role": "user", "content": f"Summarize the following. \n {user_text}"}
        ]
    elif lang == "ko":
        messages = [ 
            {"role": "system", "content": "You are a helpful assistant in the summary."},
            {"role": "user", "content": f"다음의 내용을 한국어로 요약해 주세요 \n {user_text}"}
        ]
        
    # Chat Completions API 호출
    response = client.chat.completions.create(
                            model="gpt-3.5-turbo",  # 사용할 모델 선택 
                            messages=messages,      # 전달할 메시지 지정
                            max_tokens=2000,        # 응답 최대 토큰 수 지정 
                            temperature=0.3,        # 완성의 다양성을 조절하는 온도 설정
                            n=1                     # 생성할 완성의 개수 지정
    )     
    summary = response.choices[0].message.content

    return summary
