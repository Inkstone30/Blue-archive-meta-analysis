# 아카이브 — DC인사이드 커뮤니티 수집기

이 폴더의 파일들은 "향후 확장" 가능성을 위해 보존된 코드입니다.  
현재 메인 분석(Q3: 캐릭터 스탯·메타 분석)과 직접 연관되지 않아 비활성화했습니다.

## 포함 파일

| 파일 | 설명 |
|------|------|
| `collect_community.py` | DC인사이드 블루아카이브 마이너 갤러리 크롤러 |

## 수집 내용 요약

- **대상**: `gall.dcinside.com/mgallery/board/lists/?id=bluearchive`
- **수집 데이터**: 게시글 제목·본문·작성자·날짜·조회수·추천수·댓글수
- **저장 파일**: `data/raw/dcinside_bluearchive_raw.csv`, `_with_body.csv`
- **감성분석**: KNU 감성사전 기반, 2단계 매칭(정확일치 + 역방향 서브스트링)

## 재활성화 방법

```powershell
# src/collectors/ 로 복사 후 실행
copy _archived\collect_community.py collect_community.py
python src/collectors/collect_community.py
```

## 향후 확장 아이디어

- 업데이트 이전/이후 기간 감성 지수 비교
- 신규 학생 출시 주차와 게시글 수·추천수 급증 상관관계
- 한정 학생 출시 시 부정 여론(가챠 불만) vs 긍정 여론(픽업 성공) 분포
