"""
KBO 선수 스탯 크롤러 v2
- 출처: statiz.co.kr (일반 HTML, JS 렌더링 불필요)
- 방식: requests + BeautifulSoup (가볍고 안정적)
- 출력: data/stats.json
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.statiz.co.kr/",
}

BASE_URL = "https://www.statiz.co.kr/stat.php"

# 타자 카테고리: (파라미터, key, 한글 레이블)
HITTER_STATS = [
    ("HRA",  "avg", "타율"),
    ("HR",   "hr",  "홈런"),
    ("RBI",  "rbi", "타점"),
    ("SB",   "sb",  "도루"),
    ("R",    "r",   "득점"),
    ("H",    "h",   "안타"),
    ("OBP",  "obp", "출루율"),
    ("OPS",  "ops", "OPS"),
]

# 투수 카테고리
PITCHER_STATS = [
    ("ERA",  "era", "평균자책점"),
    ("W",    "win", "승"),
    ("SO",   "so",  "탈삼진"),
    ("SV",   "sv",  "세이브"),
    ("HLD",  "hld", "홀드"),
    ("WHIP", "whip","WHIP"),
]


def fetch_top5(p_type, sort_col):
    """statiz에서 특정 스탯 TOP5 가져오기"""
    params = {
        "opt": "1",
        "sopt": "0",
        "re": "0",
        "ys": "2026",
        "ye": "2026",
        "se": "0",
        "te": "",
        "po": "0",
        "as": "",
        "ae": "",
        "hi": "",
        "un": "3",       # 규정타석/이닝 이상
        "pos": "0",
        "um": "0",
        "type": p_type,  # "bat" or "pit"
        "sort": sort_col,
        "de": "1",       # 내림차순
        "pageNum": "1",
    }

    try:
        res = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=15)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # 테이블 찾기
        table = soup.find("table", {"id": "s_table"}) or soup.find("table", class_="table")
        if not table:
            print(f"  [경고] 테이블 없음: {sort_col}")
            return []

        rows = table.find("tbody").find_all("tr")
        results = []
        rank = 1

        for row in rows[:5]:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            # 선수명, 팀, 스탯값 추출 (statiz 컬럼 구조)
            name_cell = row.find("td", class_="name") or cols[1]
            team_cell = row.find("td", class_="team") or cols[2]

            name = name_cell.get_text(strip=True)
            team = team_cell.get_text(strip=True)

            # 정렬 기준 컬럼값 (헤더에서 sort_col 위치 찾기)
            headers_row = table.find("thead").find_all("th")
            col_idx = None
            for i, th in enumerate(headers_row):
                if sort_col.lower() in th.get_text(strip=True).lower():
                    col_idx = i
                    break

            if col_idx and col_idx < len(cols):
                value = cols[col_idx].get_text(strip=True)
            else:
                # fallback: 마지막 강조 컬럼
                value = cols[-1].get_text(strip=True)

            if name and team:
                results.append({
                    "rank": rank,
                    "name": name,
                    "team": team,
                    "value": value,
                })
                rank += 1

        return results

    except Exception as e:
        print(f"  [오류] {sort_col}: {e}")
        return []


def crawl():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 크롤링 시작 (statiz.co.kr)")

    hitter = {}
    for sort_col, key, label in HITTER_STATS:
        print(f"  타자 {label} 수집 중...")
        players = fetch_top5("bat", sort_col)
        hitter[key] = {"label": label, "players": players}
        print(f"    → {len(players)}명")

    pitcher = {}
    for sort_col, key, label in PITCHER_STATS:
        print(f"  투수 {label} 수집 중...")
        players = fetch_top5("pit", sort_col)
        pitcher[key] = {"label": label, "players": players}
        print(f"    → {len(players)}명")

    result = {
        "updated_at": datetime.now().strftime("%Y년 %m월 %d일 %H:%M"),
        "updated_at_iso": datetime.now().isoformat(),
        "source": "https://www.statiz.co.kr",
        "hitter": hitter,
        "pitcher": pitcher,
    }

    import os
    os.makedirs("data", exist_ok=True)
    with open("data/stats.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 완료: {result['updated_at']}")


if __name__ == "__main__":
    crawl()
