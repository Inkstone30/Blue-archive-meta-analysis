# 블루아카이브 메타·여론·매출 데이터 분석


## 프로젝트 목표

블루아카이브는 넥슨게임즈가 서비스하는 서브컬처 장르 모바일 게임으로,
꾸준한 업데이트와 이벤트로 활발한 커뮤니티를 보유하고 있습니다.

이 프로젝트는 **"데이터로 보는 가챠 게임 생태계"** 라는 주제 아래,
게임 내 메타 데이터, 커뮤니티 반응, 매출 순위를 교차 분석합니다.

---

## 핵심 분석 질문 3가지

### Q1. 신규 학생(캐릭터) 출시는 매출 순위에 얼마나 영향을 미치는가?
- 학생 출시 전후 7일간 앱스토어/구글플레이 매출 순위 변화 측정
- 인기 캐릭터 vs 비인기 캐릭터의 매출 효과 비교
- 콜라보 이벤트와 자체 학생 출시의 매출 차이 분석

### Q2. 커뮤니티 여론(DC인사이드)은 업데이트 이후 어떻게 변화하는가?
- 업데이트 전후 게시글 제목·본문의 감성 분석 (긍/부정/중립)
- 논란이 된 사건(밸런스 패치, 서버 장애 등)과 여론 지수 상관관계
- 추천수·조회수 변화로 보는 커뮤니티 반응 강도 측정

> **데이터 소스 변경 사유**: Reddit API 정책 변경으로 PRAW 방식 제한.  
> arca.live는 Cloudflare JS Challenge로 단순 HTTP 수집 불가.  
> DC인사이드 마이너 갤러리는 robots.txt상 일반 크롤러 허용, 안정적 수집 가능.

### Q3. 어떤 특성을 가진 학생이 메타에서 오래 살아남는가?
- 레이드 클리어율 상위 학생의 공통 스탯·스킬 패턴 분석
- 출시 이후 메타 유지 기간과 스펙 지수의 상관관계
- 클러스터링으로 학생 유형 분류 (공격형/지원형/버프형 등)

---

## 폴더 구조

```
bluearc/
├── data/
│   ├── raw/          # 수집한 원본 데이터 (손대지 않음)
│   └── processed/    # 전처리·가공된 데이터
├── notebooks/        # 탐색적 분석(EDA) Jupyter 노트북
├── src/
│   ├── collectors/   # 데이터 수집 스크립트 (API, 크롤링)
│   └── analysis/     # 분석 및 모델링 스크립트
├── app/              # Streamlit 대시보드
├── reports/          # 최종 보고서, 시각화 결과물
├── requirements.txt  # Python 패키지 목록
└── README.md
```

---

## 데이터 출처 (예정)

| 데이터 | 출처 | 수집 방법 |
|--------|------|-----------|
| 앱 매출 순위 | 게볼루션(gvolution.com), AppMagic | 웹 스크래핑 |
| 커뮤니티 여론 | DC인사이드 블루아카이브 마이너 갤러리 | 웹 스크래핑 (requests + BeautifulSoup) |
| 학생 스탯·스킬 | 블루아카이브 나무위키, 팬 위키 | 웹 스크래핑 |
| 레이드 클리어 데이터 | 블루아카이브 DB 팬사이트 | 웹 스크래핑 |
| 업데이트 이력 | 공식 패치노트 | 수동 정리 |

---

## 실행 방법

### 1. 환경 설정 (처음 한 번만)

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 데이터 수집 스크립트 실행

```powershell
# 가상환경 활성화 후:

# SchaleDB 학생 데이터 수집
python src/collectors/collect_students.py

# DC인사이드 커뮤니티 게시글 수집 (기본 3페이지 ≈ 75~150건)
python src/collectors/collect_community.py
```

### 3. Jupyter 노트북 실행

```bash
jupyter notebook
# 브라우저에서 notebooks/ 폴더 열기
```

### 4. Streamlit 대시보드 실행

```bash
streamlit run app/dashboard.py
```

---

## 기술 스택

- **데이터 수집**: `requests`, `beautifulsoup4`
- **데이터 처리**: `pandas`, `numpy`
- **시각화**: `matplotlib`, `seaborn`, `plotly`
- **분석/모델링**: `scikit-learn`, `scipy`
- **감성 분석**: `textblob`
- **대시보드**: `streamlit`

---

## 진행 상황

- [x] 프로젝트 구조 설정
- [x] SchaleDB 학생 데이터 수집 (`collect_students.py` — 194명, 48컬럼)
- [x] DC인사이드 커뮤니티 게시글 수집 (`collect_community.py`)
- [ ] 탐색적 데이터 분석 (EDA)
- [ ] 핵심 질문 분석
- [ ] Streamlit 대시보드 구축
- [ ] 최종 보고서 작성
