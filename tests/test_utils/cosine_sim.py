from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt

okt = Okt()
vectorizer = TfidfVectorizer(
    tokenizer=okt.morphs,
    token_pattern=None,)

documents = [
    """본 프로젝트는 다양한 제조사의 스마트홈 기기를 통합 제어할 수 있는 사용자 맞춤형 IoT 앱을 개발하는 것을 목표로 진행되었습니다. 
    스마트홈 기능을 100% 활용하고 사용자 편의성을 극대화한 크로스 플랫폼 모바일 애플리케이션을 구현하여, 분산된 기기 제어 환경을 통합 관리할 수 있는 솔루션을 
    제공하고자 하였습니다.
    """,
    """최근 스마트홈 기기의 수요와 종류가 급증하고 있으나, 각 제조사별로 독립적인 앱을 사용해야 하는 불편함이 존재합니다. 사용자들은 조명, 온도조절기, 보안 카메라 등 여러 기기를 제어하기 위해 다수의 앱을 설치하고 전환해야 하는 번거로움을 겪고 있습니다. 이러한 시장의 니즈를 파악하여 다양한 기기를 통합 제어할 수 있는 맞춤형 서비스 개발을 추진하게 되었습니다.""",
    """복잡한 조인 구조로 인한 데이터 조회 시간 지연 → 데이터베이스 인덱싱 구조 분석 및 API 리팩터링 진행 중""",
    "스마트홈 기능을 100% 활용하고, 사용자 편의성에 최적화된 IoT 제어 앱을 개발하는 프로젝트",
    "일부 기기 연결 시 안정성 문제 발생",
    "기기 일부 제어 실패"
]

query = "일부 기기는 연결은 가능하지만 제어 기능 동작 실패."


tfidf_matrix = vectorizer.fit_transform(documents + [query])

cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
print(type(cosine_sim))
for idx, score in enumerate(cosine_sim[0]):
    print(idx, score)