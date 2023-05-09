import streamlit as st
from PIL import Image
import requests
import pandas as pd
import numpy as np
import pydeck as pdk
from pydeck.types import String
import folium
from streamlit_folium import st_folium
import requests
from datetime import datetime
from haversine import haversine

# ======================== 사이드바 ========================
# 이미지 올리기
img ='https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbsG7Rw%2Fbtseqb1XFui%2FVPbpTzdZKLVxiKzlHN42BK%2Fimg.png'
st.sidebar.image(img,width=300)

st.sidebar.header("오늘 강원도에 산불이 일어날까요?")
# 선택박스 만들기 
city = st.sidebar.selectbox('시군구를 선택하세요',
                            ['강릉', '춘천', '홍성','횡성','원주'])


st.sidebar.write('해당 시군구:', city)

# ======================== 주소크롤링 ========================

# NCP 콘솔에서 복사한 클라이언트ID와 클라이언트Secret 값
client_id = "6y408zj3ij"
client_secret = "7QgK6w9TjDBFEBQOITmYrE9ohLoQYAcP7E3T5brR"

# 주소 텍스트
endpoint = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"

# 헤더
headers = {
    "X-NCP-APIGW-API-KEY-ID": client_id,
    "X-NCP-APIGW-API-KEY": client_secret,
}

# 요청
query = city
url = f"{endpoint}?query={query}"

res = requests.get(url, headers=headers)
data = res.json()

위도_city = data["addresses"][0]["y"]
경도_city = data["addresses"][0]["x"]

# ======================== 메인 화면 ========================

st.title('사부작사부작-리턴즈')

st.header('산불을 예측해보자!')

위도받기 = st.number_input('위도 입력')
경도받기 = st.number_input('경도 입력')

# ======================== 지도 시각화 ========================

m = folium.Map(location=[위도_city, 경도_city], zoom_start=13)

# ClickForLatLng 객체 생성
# click_handler = folium.ClickForLatLng()
click_handler = folium.LatLngPopup()

# ClickForLatLng 객체를 Folium 지도에 추가
m.add_child(click_handler)


st_data = st_folium(m, width=500, height = 500)

# ======================== 압력받은 위도 경도 기준으로 가장 가까운 지점 기상 정보 출력 ========================

지점 = pd.read_csv('관측지점_번호포함.csv')

now = datetime.now()
current_time = now.strftime("%H%M")[:2] + '00'
current_date = now.strftime("%Y%m%d")

예측위치 = (위도받기, 경도받기)

거리_list = []

for i in range(len(지점)):
    
    관측위도 = 지점['위도'][i]
    관측경도 = 지점['경도'][i]
    관측위치 = (관측위도, 관측경도)
    
    거리 = (haversine(관측위치, 예측위치), i)
    거리_list.append(거리)
    
비교 = []

for b in range(len(거리_list)):
    비교.append(거리_list[b][0])
    
min_index = 비교.index(min(비교))
    
최근접_관측번호 = 지점.loc[min_index, '지점번호']

# ======

response = requests.get(f'https://apihub.kma.go.kr/api/typ01/cgi-bin/url/nph-aws2_min?stn={최근접_관측번호}&disp=0&help=2&authKey=NermpuOATlGq5qbjgF5RBQ')
response.content

# '기온(°C)', '풍향(deg)', '풍속(m/s)', '강수량(mm)', '습도(%)'
data = response.content

# 데이터를 문자열로 변환하고 공백을 기준으로 분할
data_str = data.decode('utf-8')
data_list = data_str.split()

# 컬럼명 설정
columns = ['YYMMDDHHMI', 'STN', 'WD1', 'WS1', 'WDS', 'WSS', 'WD10', 'WS10', 'TA', 'RE', 'RN-15m', 'RN-60m',
            'RN-12H', 'RN-DAY', 'HM', 'PA', 'PS', 'TD']

# 데이터프레임 생성
df = pd.DataFrame([data_list], columns=columns)

df = df[['STN', 'TA', 'WD10', 'WS10', 'RN-DAY', 'HM']].rename(columns={ 'STN' : '지점번호',
                                                                        'TA' : '기온(°C)',
                                                                        'WD10' : '풍향(deg)',
                                                                        'WS10' : '풍속(m/s)',
                                                                        'RN-DAY' : '강수량(mm)',
                                                                        'HM' : '습도(%)'})

st.dataframe(df)
