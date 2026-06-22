"""
DC인사이드 블루아카이브 마이너 갤러리 게시글 수집기
URL: https://gall.dcinside.com/mgallery/board/lists/?id=bluearchive

[수집 범위]
- 수집 대상: 공개 게시글 제목·작성자·작성일·조회수·추천수
- 개인정보: 닉네임만 수집 (IP·이메일 등 수집 안 함)
- 용도: 비상업적 포트폴리오·연구

[robots.txt 준수]
- gall.dcinside.com은 일반 크롤러(User-agent: *)에게 접근 허용
- AI 학습봇(ClaudeBot, GPTBot 등)만 차단 — 본 스크립트는 해당 없음
- Crawl-delay 미지정 → 자체적으로 3~5초 딜레이 적용
"""

import requests
import pandas as pd
import time
import random
import json
import re
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

# ── 경로 설정 ──────────────────────────────────────────────
ROOT    = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ── 수집 설정 ──────────────────────────────────────────────
GALLERY_ID   = "bluearchive"
BASE_URL     = f"https://gall.dcinside.com/mgallery/board/lists/?id={GALLERY_ID}"
POST_BASE    = "https://gall.dcinside.com"

MAX_PAGES    = 3      # 테스트: 3페이지(약 75건). 본 수집 시 늘릴 것
DELAY_MIN    = 3.0    # 요청 간 최소 대기(초) — 서버 부담 방지
DELAY_MAX    = 5.0    # 요청 간 최대 대기(초)

# 브라우저처럼 보이는 헤더 (봇 차단 우회가 아닌 서버 식별 목적)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ko-KR,ko;q=0.9",
    "Referer": "https://gall.dcinside.com/",
}


def fetch_page(page: int, session: requests.Session) -> BeautifulSoup | None:
    """한 페이지를 요청하고 BeautifulSoup 객체를 반환."""
    url = f"{BASE_URL}&page={page}"
    try:
        resp = session.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except requests.RequestException as e:
        print(f"  ⚠ 페이지 {page} 요청 실패: {e}")
        return None


def parse_posts(soup: BeautifulSoup) -> list[dict]:
    """
    게시글 목록 테이블을 파싱해 딕셔너리 리스트로 반환.
    공지·광고·설문 등 비일반 게시글은 제외.
    """
    rows = soup.select("tr.ub-content.us-post")
    posts = []

    for row in rows:
        # 공지·광고 등 제외: data-type 속성이 비어 있는 게 일반 게시글
        # (공지는 icon_notice, 광고는 icon_ad)
        subject_td = row.select_one("td.gall_subject")
        if subject_td:
            subject_text = subject_td.get_text(strip=True)
            if subject_text in ("공지", "설문", "AD"):
                continue

        # 번호
        num_td = row.select_one("td.gall_num")
        post_no = num_td.get_text(strip=True) if num_td else ""
        if not post_no.isdigit():   # 숫자가 아니면(공지 등) 건너뜀
            continue

        # 제목 + URL
        title_a = row.select_one("td.gall_tit a")
        if not title_a:
            continue
        raw_title = title_a.get_text(separator=" ", strip=True)
        # 댓글 수 표시 "[N]" 제거
        title = re.sub(r"\s*\[\d+\]\s*$", "", raw_title).strip()
        href  = title_a.get("href", "")
        post_url = POST_BASE + href if href.startswith("/") else href

        # 댓글 수 (제목 안 span.reply_num에 있음)
        reply_span = row.select_one("td.gall_tit .reply_num")
        comment_count = ""
        if reply_span:
            comment_count = re.sub(r"[^\d]", "", reply_span.get_text())

        # 작성자 닉네임
        writer_td = row.select_one("td.gall_writer")
        nickname = ""
        if writer_td:
            nick_tag = writer_td.select_one(".nickname") or writer_td.select_one("b")
            if nick_tag:
                nickname = nick_tag.get_text(strip=True)

        # 작성일 (title 속성에 전체 날짜, 텍스트에 단축 날짜)
        date_td = row.select_one("td.gall_date")
        date_full  = date_td.get("title", "").strip() if date_td else ""  # "2025-01-01 12:00:00"
        date_short = date_td.get_text(strip=True) if date_td else ""

        # 조회수
        count_td = row.select_one("td.gall_count")
        view_count = count_td.get_text(strip=True) if count_td else ""

        # 추천수
        rec_td = row.select_one("td.gall_recommend")
        recommend = rec_td.get_text(strip=True) if rec_td else ""

        posts.append({
            "post_no":       int(post_no),
            "title":         title,
            "post_url":      post_url,
            "nickname":      nickname,
            "date_full":     date_full,
            "date_short":    date_short,
            "view_count":    int(view_count)    if view_count.isdigit()    else None,
            "recommend":     int(recommend)     if recommend.isdigit()     else None,
            "comment_count": int(comment_count) if comment_count.isdigit() else None,
        })

    return posts


def collect(max_pages: int = MAX_PAGES) -> pd.DataFrame:
    """여러 페이지를 순회하며 게시글을 수집."""
    session = requests.Session()
    all_posts = []

    print(f"\n[DC인사이드] 블루아카이브 마이너 갤러리 수집 시작")
    print(f"  대상: {BASE_URL}")
    print(f"  수집 페이지: 1~{max_pages}페이지 (페이지당 약 25건)")
    print(f"  딜레이: {DELAY_MIN}~{DELAY_MAX}초\n")

    for page in range(1, max_pages + 1):
        print(f"  [페이지 {page}/{max_pages}] 요청 중...", end=" ")
        soup = fetch_page(page, session)

        if soup is None:
            print("실패, 건너뜀")
            continue

        posts = parse_posts(soup)
        all_posts.extend(posts)
        print(f"{len(posts)}건 수집 (누계: {len(all_posts)}건)")

        # 마지막 페이지가 아니면 딜레이
        if page < max_pages:
            delay = round(random.uniform(DELAY_MIN, DELAY_MAX), 1)
            print(f"         다음 요청까지 {delay}초 대기...")
            time.sleep(delay)

    print(f"\n  총 {len(all_posts)}건 수집 완료")
    return pd.DataFrame(all_posts)


def save(df: pd.DataFrame) -> None:
    """CSV·JSON·메타 파일로 저장."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    csv_path  = RAW_DIR / "dcinside_bluearchive_raw.csv"
    json_path = RAW_DIR / "dcinside_bluearchive_raw.json"
    meta_path = RAW_DIR / "dcinside_bluearchive_meta.json"

    df.to_csv(csv_path,  index=False, encoding="utf-8-sig")
    df.to_json(json_path, orient="records", force_ascii=False, indent=2)

    meta = {
        "source":       BASE_URL,
        "gallery_id":   GALLERY_ID,
        "collected_at": timestamp,
        "total_posts":  len(df),
        "columns":      list(df.columns),
        "pages_scraped": MAX_PAGES,
        "note": "DC인사이드 블루아카이브 마이너 갤러리 공개 게시글. 비상업적 연구용.",
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"\n  저장 완료")
    print(f"    CSV  → {csv_path}")
    print(f"    JSON → {json_path}")
    print(f"    메타 → {meta_path}")


def print_summary(df: pd.DataFrame) -> None:
    """수집 결과 요약 출력."""
    print("\n" + "=" * 55)
    print("  수집 결과 요약")
    print("=" * 55)
    print(f"  총 게시글 수  : {len(df)}건")
    if "date_full" in df.columns and df["date_full"].notna().any():
        print(f"  날짜 범위     : {df['date_full'].min()} ~ {df['date_full'].max()}")
    if "recommend" in df.columns:
        top5 = df.nlargest(5, "recommend")[["post_no", "title", "recommend", "view_count"]]
        print(f"\n  [추천수 TOP 5]")
        for _, r in top5.iterrows():
            title_short = r["title"][:30] + "..." if len(r["title"]) > 30 else r["title"]
            print(f"    추천 {r['recommend']:>4} | 조회 {str(r['view_count']):>6} | {title_short}")
    print("=" * 55)


def main():
    df = collect(max_pages=MAX_PAGES)

    if df.empty:
        print("수집된 게시글이 없습니다. 네트워크 연결을 확인해주세요.")
        return

    save(df)
    print_summary(df)
    print("\n수집 완료!\n")
    return df


if __name__ == "__main__":
    main()
