"""
KBO 선수 스탯 크롤러
- 대상: KBO 공식 홈페이지 TOP5 페이지
- 방식: Playwright (JS 렌더링 처리)
- 출력: data/stats.json
"""

import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

URL = "https://www.koreabaseball.com/Record/Main.aspx"

HITTER_CATEGORIES = {
    "타율": "avg",
    "홈런": "hr",
    "타점": "rbi",
    "도루": "sb",
    "득점": "r",
    "안타": "h",
    "출루율": "obp",
}

PITCHER_CATEGORIES = {
    "평균자책점": "era",
    "승": "win",
    "탈삼진": "so",
    "세이브": "sv",
    "홀드": "hld",
    "WHIP": "whip",
}


def parse_top5_section(page, label):
    """특정 카테고리 TOP5 파싱"""
    try:
        # KBO 메인 기록 페이지의 TOP5 섹션 파싱
        section = page.locator(f"text={label}").first
        if not section:
            return []

        # 해당 섹션의 상위 컨테이너에서 선수 목록 추출
        container = section.locator("xpath=ancestor::div[contains(@class,'tbl') or contains(@class,'rank') or contains(@class,'top')]").first
        rows = container.locator("li, tr").all()

        results = []
        for i, row in enumerate(rows[:5], 1):
            text = row.inner_text().strip()
            if not text:
                continue
            parts = text.split()
            if len(parts) >= 3:
                results.append({
                    "rank": i,
                    "name": parts[0],
                    "team": parts[1],
                    "value": parts[2],
                })
        return results
    except Exception as e:
        print(f"  [경고] '{label}' 파싱 실패: {e}")
        return []


def crawl_kbo_stats():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] KBO 크롤링 시작...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        print(f"  페이지 로딩: {URL}")
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(2000)  # JS 렌더링 대기

        # 전체 텍스트에서 TOP5 데이터 추출 (KBO 사이트 구조 대응)
        content = page.content()

        hitter_stats = {}
        pitcher_stats = {}

        # --- 타자 TOP5 파싱 ---
        print("  타자 스탯 파싱 중...")
        for kor_label, key in HITTER_CATEGORIES.items():
            data = parse_top5_section(page, kor_label)
            hitter_stats[key] = {
                "label": kor_label,
                "players": data
            }
            print(f"    {kor_label}: {len(data)}명 파싱")

        # --- 투수 TOP5 파싱 ---
        print("  투수 스탯 파싱 중...")
        for kor_label, key in PITCHER_CATEGORIES.items():
            data = parse_top5_section(page, kor_label)
            pitcher_stats[key] = {
                "label": kor_label,
                "players": data
            }
            print(f"    {kor_label}: {len(data)}명 파싱")

        browser.close()

    # 결과 저장
    result = {
        "updated_at": datetime.now().strftime("%Y년 %m월 %d일 %H:%M"),
        "updated_at_iso": datetime.now().isoformat(),
        "source": "https://www.koreabaseball.com/Record/Main.aspx",
        "hitter": hitter_stats,
        "pitcher": pitcher_stats,
    }

    with open("data/stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  ✅ data/stats.json 저장 완료")
    print(f"[완료] {result['updated_at']}")
    return result


if __name__ == "__main__":
    crawl_kbo_stats()
