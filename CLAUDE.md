# CLAUDE.md — 프로젝트 컨텍스트

이 파일은 Claude Code가 프로젝트를 이해하기 위한 설명서입니다.

## 프로젝트 개요

**이름**: 블루아카이브 캐릭터 스탯·메타 분석  
**목적**: 데이터 분석 포트폴리오 구축 (단일 주제 집중형)  
**사용자**: 초보 데이터 분석가, Python 학습 중  
**플랫폼**: Windows 11, VS Code, PowerShell 터미널

### 핵심 분석 방향

SchaleDB 공개 데이터(194명, 48컬럼)를 사용해 **"스탯 숫자가 메타를 설명할 수 있는가?"** 를 검증합니다.

```
Phase 1 EDA → Phase 2 통계 검증 → Phase 3 클러스터링 → Phase 4 예측 모델
```

매출(Q1)·커뮤니티 여론(Q2) 분석은 `src/collectors/_archived/`, `notebooks/_archived/` 에 코드를 보존해두었으며, 현재 메인 스코프 외입니다.

## 게임 도메인 지식

**블루아카이브(Blue Archive)**는 넥슨게임즈(개발: NAT게임즈)가 서비스하는 서브컬처 모바일 RPG입니다.

### 핵심 용어
- **학생(Student)**: 게임 내 캐릭터. 출시 시 가챠(랜덤 뽑기)로 획득
- **레이드(Raid)**: 길드 단위 보스전. 메타 판단의 주요 척도
- **픽업(Pick-up)**: 특정 학생 출시 확률을 높이는 한정 가챠 배너
- **총력전/대결전**: 주요 레이드 컨텐츠 유형
- **EX 스킬**: 학생의 강력한 특수 기술. `ex_cost`(RegenCost)로 수치화됨
- **SS/S/A 티어**: 커뮤니티 기반 학생 등급 체계 (레이드 기준)
- **스탯 인플레이션**: 후기 출시 학생의 스탯이 전반적으로 높아지는 게임 설계 경향

### SchaleDB 데이터 구조 (주요 컬럼)
- `star_grade`: 레어도 1·2·3성
- `is_limited`: 0=상시, 1=게임 자체 한정, 2=콜라보 한정
- `tactic_role`: DamageDealer·Tanker·Healer·Supporter·Vehicle
- `adapt_street/outdoor/indoor`: 지형 적응도 0~5
- `atk/hp/def/heal_lv1`, `_lv100`: 기본·최대 스탯
- `ex_cost`: EX 스킬 발동 비용 (높을수록 강력한 경향)
- `IsReleased[0/1/2]`: JP/글로벌/중국 출시 여부

### 데이터 한계 (분석 시 항상 고려)
- 개별 출시일 미포함 → 시계열 분석 불가
- 실제 레이드 클리어율·사용률 없음 → 스탯으로만 "메타"를 추론
- 스킬 효과 텍스트 수치화 미포함
- 194명: 소규모 데이터셋 (ML 결과 해석 주의)

## 기술 스택 & 환경

- **Python**: 3.14.5 (가상환경: `.venv\Scripts\activate`)
- **패키지 관리**: `pip` + `requirements.txt`
- **노트북**: Jupyter (Phase별 분석)
- **대시보드**: Streamlit (`app/` 폴더, Phase 4 이후 예정)
- **API 키**: 현재 불필요. `.env` 파일 구조는 유지

## 폴더 역할

```
data/raw/                  - 수집한 원본 데이터. 절대 수정하지 않음
data/processed/            - 전처리·피처 엔지니어링 결과
notebooks/                 - Phase별 Jupyter 노트북 (01~04)
notebooks/_archived/       - 구 감성분석 노트북 (비활성)
src/collectors/            - 데이터 수집 스크립트
src/collectors/_archived/  - DC인사이드 수집기 (비활성, 향후 확장용)
src/analysis/              - 재사용 가능한 분석 함수·클래스
app/                       - Streamlit 대시보드 코드
reports/                   - 최종 시각화 및 보고서 출력물
```

## 코딩 가이드라인

- **초보자 친화적**: 복잡한 추상화보다 명확한 코드를 우선
- **주석 언어**: 한국어로 작성 (사용자가 이해하기 쉽게)
- **에러 처리**: API 호출 실패, 네트워크 오류에 대한 기본 처리 포함
- **데이터 보존**: raw 데이터는 절대 덮어쓰지 않음
- **API 키**: 절대 코드에 하드코딩하지 않음 — 항상 `.env` + `python-dotenv` 사용

## 분석 질문 (Phase별)

### Phase 1 — EDA
1. 역할별 스탯 프로파일 시각화 (딜러 vs 탱커 vs 힐러 vs 서포터)
2. 레어도(★1/★2/★3)별 스탯 분포 비교
3. 한정/상시 학생 스탯 평균 비교
4. 지형 적응도 조합 빈도 분석

### Phase 2 — 통계 검증
5. 레어도별 스탯 차이: ANOVA + Tukey HSD
6. 한정 여부 영향: 독립 표본 t-검정
7. EX 코스트-공격력 상관: Spearman
8. 전체 스탯 상관 행렬

### Phase 3 — 클러스터링
9. K-means (Elbow + Silhouette) → 최적 K 결정
10. 클러스터 프로파일링 및 메타 유형 명명
11. 한정 학생 클러스터 분포 분석
12. 공식 역할 vs 데이터 기반 클러스터 비교

### Phase 4 — 예측 모델
13. ★3 여부 예측: RandomForest + LogisticRegression (교차검증)
14. Feature Importance + SHAP 해석
15. 한정 여부 예측 및 혼동 행렬 분석

## 수집 스크립트 현황

| 파일 | 대상 | 수집 데이터 | 상태 |
|------|------|------------|------|
| `src/collectors/collect_students.py` | SchaleDB GitHub JSON | 학생 194명, 48컬럼 | ✅ 활성 |
| `src/collectors/_archived/collect_community.py` | DC인사이드 블루아카이브 갤러리 | 게시글 제목·본문·날짜·조회수 | 📦 아카이브 |

## 주의사항

- SchaleDB 라이선스: CC BY-NC-SA 4.0 — 비상업적 사용만 허용
- 웹 스크래핑 재개 시 robots.txt 재확인 필수 (이전 확인: 2026-06-22)
- _archived 폴더 내 파일은 직접 실행하지 않음 (경로 참조가 부모 디렉터리 기준임)
