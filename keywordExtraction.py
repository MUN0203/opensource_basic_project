# -*- coding: utf-8 -*-
from krwordrank.word import KRWordRank
from krwordrank.hangle import normalize
from konlpy.tag import Okt

def keywordExtraction(text):

    # 텍스트 정규화: 영문·숫자 표준화, 중복 공백 제거 등
    normalized_text = normalize(text, english=True, number=True)

    # 문장 단위 분리
    sentences = [sent.strip() for sent in normalized_text.split('\n') if sent.strip()]

    # KRWordRank를 이용한 키워드(단어) 추출
    min_count = 2
    max_length = 10
    beta = 0.85
    max_iter = 10

    wordrank_extractor = KRWordRank(min_count=min_count, max_length=max_length, verbose=True)
    keywords, rank, graph = wordrank_extractor.extract(sentences, beta, max_iter)

    # 추출된 키워드 사전에서 단어만 리스트로 얻기
    candidate_words = list(keywords.keys())

    # Konlpy의 Okt 형태소 분석기로 후보 단어 중 '모든 형태소가 명사'인 경우만 필터링
    okt = Okt()
    noun_keywords = []
    for word in candidate_words:
        pos_tags = okt.pos(word)
        if all(pos == 'Noun' for (_, pos) in pos_tags):
            noun_keywords.append(word)

    return noun_keywords