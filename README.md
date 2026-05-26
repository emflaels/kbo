# ⚾ KBO 선수 스탯 자동 업데이트

KBO 공식 홈페이지에서 선수 스탯을 자동으로 크롤링해 GitHub Pages로 서비스합니다.

## 📁 파일 구조

```
kbo-stats/
├── index.html                  # 메인 페이지 (GitHub Pages)
├── crawl.py                    # KBO 크롤러
├── data/
│   └── stats.json              # 크롤링 결과 (자동 갱신)
└── .github/
    └── workflows/
        └── update.yml          # GitHub Actions 자동화
```

## 🚀 배포 방법 (5분)

### 1단계 · GitHub 저장소 만들기

```bash
# 이 폴더를 GitHub에 올리기
git init
git add .
git commit -m "첫 커밋"
git remote add origin https://github.com/[내아이디]/kbo-stats.git
git push -u origin main
```

### 2단계 · GitHub Pages 켜기

1. 저장소 → **Settings** → **Pages**
2. Source: `gh-pages` 브랜치 선택 → **Save**
3. 잠시 후 `https://[내아이디].github.io/kbo-stats` 접속 가능

### 3단계 · Actions 권한 설정

1. 저장소 → **Settings** → **Actions** → **General**
2. Workflow permissions: **Read and write permissions** 체크 → Save

---

## ⏰ 업데이트 주기

| 시간 (KST) | 설명 |
|---|---|
| 오전 10:00 | 전날 최종 기록 반영 |
| 오후 3:00 | 경기 중반 기록 |
| 오후 9:00 | 당일 경기 종료 후 |

수동으로도 실행 가능: **Actions** → `KBO Stats Auto Update` → **Run workflow**

---

## 🔧 로컬 테스트

```bash
# 의존성 설치
pip install playwright
playwright install chromium

# 크롤러 실행
python crawl.py

# 로컬 서버로 확인 (index.html이 data/stats.json을 fetch함)
python -m http.server 8080
# → http://localhost:8080 접속
```

---

## ⚠️ 주의사항

- KBO 사이트 구조 변경 시 `crawl.py`의 파싱 로직 수정 필요
- GitHub Actions 무료 플랜: 월 2,000분 (충분함)
- 크롤링은 과도한 요청 없이 하루 3회만 실행
