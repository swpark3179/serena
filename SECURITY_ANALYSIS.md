# Serena 프로젝트 분석 (외부 네트워크 접속 · 업로드 관점)

> 작성일: 2026-06-15
> 분석 대상: `src/` 전체 (serena, solidlsp, interprompt) 및 루트 스크립트
> 관점: 외부 GitHub/인터넷 접속 시도, 외부 업로드 기능 유무, 전반적 동작 방식

---

## 1. 프로젝트 정체와 기능

**Serena**는 Oraios AI가 MIT 라이선스로 공개한 **"코딩 에이전트를 위한 IDE"** 이다.
LLM/에이전트(Claude Code, Codex 등)에 **MCP(Model Context Protocol)** 를 통해
IDE 수준의 **시맨틱 코드 도구**(심볼 단위 검색·편집·리팩토링)를 제공한다.

### 소스 구조 (`src/`)
- **`serena/`** — 에이전트 본체, MCP 서버, 도구(tools), 설정(config), 웹 대시보드
- **`solidlsp/`** — 다국어 LSP(Language Server Protocol) 래퍼. `language_servers/` 하위에 30개 이상의 언어 서버 구현
- **`interprompt/`** — Jinja2 기반 다국어 프롬프트 템플릿

### 동작 방식
1. MCP 서버로 실행되어 클라이언트(에이전트)에게 도구 집합을 노출
2. 프로젝트 활성화 시 해당 언어의 **언어 서버(pyright, gopls, rust-analyzer 등)를 로컬 프로세스로 기동**
3. LSP를 통해 심볼/참조/정의 정보를 얻어, 라인 번호가 아닌 **심볼 단위**로 검색·편집·리팩토링
4. 도구 종류: 파일 read/write/search, 심볼 find/edit, 메모리(`.serena/memories`), 설정, 워크플로우 등
5. 로컬 **Flask 웹 대시보드**로 로그·토큰 사용 통계를 표시 (선택적 시스템 트레이 아이콘)

---

## 2. 외부 네트워크 접속 — 분류별 분석

### 🔴 A. 사용 통계 텔레메트리 (가장 주목할 부분)

`src/serena/agent.py:720` `_send_usage_info()`:
```python
requests.get("https://oraios-software.de/serena_usage.php", params=params, timeout=1)
```
- **에이전트 시작 시 1회** 프로젝트 운영사 서버(oraios-software.de)로 전송
- **전송 내용은 메타데이터만**: `os`(OS 종류), `dashboard`(사용 여부), `version`, `backend`, `context`
  - **소스 코드·파일 내용·경로는 포함되지 않음**
- 타임아웃 1초, 실패 시 무시
- **opt-out 가능**: 환경변수 `SERENA_USAGE_REPORTING=false`, 또는 `CI=true` / `GITHUB_ACTIONS=true` 인 경우 전송 안 함

### 🟡 B. 뉴스 가져오기 (다운로드 전용)

`src/serena/dashboard.py:695`:
```python
_NEWS_JSON_URL = "https://oraios-software.de/serena_news.json"
```
- ETag 캐싱으로 GET. 대시보드에 공지를 표시하기 위한 **읽기 전용**이며 업로드 없음.

### 🟢 C. 언어 서버 바이너리 다운로드 (외부 접속의 대부분, 정상 기능)

각 언어 서버를 공식 배포처에서 내려받아 로컬에 캐싱한다:
- **GitHub Releases**: clangd, marksman, phpactor, PowerShell ES, ada, cue, bsl, verible 등
- **NuGet**: C# (roslyn-language-server)
- **RubyGems**: solargraph
- **schemastore.org**: YAML 스키마 카탈로그
- **dot.net/v1/dotnet-install** 스크립트 다운로드 후 실행 (`src/serena/util/dotnet.py`)

보안 측면 구현 (`src/solidlsp/ls_utils.py`):
- `_validate_download_host()` — **허용 호스트 화이트리스트** 검증 (리다이렉트 후 최종 URL도 재검증)
- `_verify_sha256_if_configured()` — **SHA256 체크섬 검증** 지원
- 임시 파일로 받은 뒤 검증 통과 시에만 원자적(atomic) 교체

### 🟡 D. Anthropic API (선택적, 기본값 아님)

`src/serena/analytics.py`: 토큰 카운팅 기능.
- **기본 estimator는 `tiktoken`(로컬 계산)** — `TIKTOKEN_GPT4O`
- `ANTHROPIC_CLAUDE_SONNET_4` 를 **명시적으로 선택한 경우에만** `anthropic.messages.count_tokens`로 텍스트를 전송 (토큰 수 측정 목적, API 키 필요)
- 즉, 기본 설정에서는 외부 전송이 발생하지 않음

### ⚪ E. 로컬 IPC (외부 아님 — 오해 주의)

`src/serena/dashboard.py`의 여러 `urlopen` 호출(register/unregister/heartbeat/health)과
`src/serena/jetbrains/jetbrains_plugin_client.py`는 모두 **`127.0.0.1`(localhost)** 대상이다.
대시보드 트레이 매니저·JetBrains 플러그인과의 프로세스 간 통신일 뿐 외부 전송이 아니다.

---

## 3. "외부 업로드" 기능 평가 (핵심 결론)

| 항목 | 결과 |
|------|------|
| **사용자 코드/파일을 외부로 업로드** | ❌ **없음** |
| 텔레메트리 | OS·버전·context 등 **메타데이터만**, 코드 미포함, opt-out 가능 |
| Anthropic 전송 | 선택적 토큰 카운팅에 한정 (기본 비활성) |
| `sync.py` / `repo_dir_sync.py` | **개발자 전용 로컬 git 디렉터리 동기화 스크립트** — 제3자 업로드 기능 아님 |
| 언어 서버 다운로드 | 외부에서 **받아오기만** 함 (호스트 화이트리스트 + SHA256 검증) |

### 종합

Serena는 **사용자의 소스 코드를 외부로 전송·업로드하는 기능이 없다.**
외부 접속의 대부분은 **언어 서버 바이너리를 신뢰된 배포처에서 다운로드**하는 정상 동작이며,
호스트 검증·체크섬 검증을 갖추고 있다.
유일하게 능동적으로 외부로 나가는 데이터는 **익명 사용 통계(메타데이터, 코드 미포함)** 이며,
`SERENA_USAGE_REPORTING=false`로 비활성화할 수 있다.

---

## 4. 외부 접속 차단/제어 방법 요약

| 목적 | 방법 |
|------|------|
| 사용 통계 전송 비활성화 | `SERENA_USAGE_REPORTING=false` 환경변수 설정 |
| 언어 서버 다운로드 회피 | 시스템에 언어 서버를 미리 설치 (대부분 PATH의 기존 바이너리를 우선 사용) |
| Anthropic 토큰 카운팅 회피 | 기본값(tiktoken/로컬) 유지, `ANTHROPIC_CLAUDE_SONNET_4` 선택 안 함 |
| 완전 오프라인 운용 | 언어 서버 사전 설치 + 통계 opt-out + 뉴스/대시보드 비활성화 |
