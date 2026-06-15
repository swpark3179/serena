# Serena 오프라인(사내) 빌드 가이드

이 빌드는 **완전한 오프라인 모드**로 동작하도록 구성되어 있다.
외부 GitHub/인터넷으로의 능동적 접속(통계 전송, 뉴스 수신, 언어 서버 자동 다운로드,
외부 LLM 제공자 호출)이 모두 차단된다.

## 1. 동작 요약

| 기능 | 기본 동작 | 오프라인 빌드에서의 동작 |
|------|-----------|--------------------------|
| 익명 사용 통계 전송 | oraios-software.de 로 메타데이터 전송 | **전송 안 함** |
| 대시보드 뉴스 수신 | oraios-software.de 에서 news.json fetch | **수신 안 함** |
| 웹 대시보드 | 활성화(127.0.0.1) | **비활성화** (오프라인 시 강제 off) |
| 언어 서버 미설치 시 | GitHub/NuGet/npm 등에서 **자동 다운로드** | **자동설치 안 함 → 설치 링크·방법 안내** |
| 토큰 카운팅(Anthropic) | 옵션으로 Anthropic API 호출 가능 | **제거됨** (의존성/코드/옵션 모두 삭제) |

## 2. 활성화 방법

오프라인 모드는 환경변수 **`SERENA_OFFLINE`** 로 제어한다.
truthy 값(`1`, `true`, `yes`, `on`, 대소문자 무시)이면 활성화된다.

```bash
export SERENA_OFFLINE=true
export SERENA_USAGE_REPORTING=false   # (SERENA_OFFLINE=true 이면 자동 적용되지만 명시 권장)
```

이 빌드의 기본 제공물에는 다음이 이미 반영되어 있다:

- **`Dockerfile`**: `ENV SERENA_OFFLINE=true`, `ENV SERENA_USAGE_REPORTING=false`
- **`.env.example`**: 위 두 변수 설정 예시
- **`serena_config.template.yml`**: `web_dashboard: False` (기본 비활성)

온라인 동작으로 되돌리려면 `SERENA_OFFLINE` 를 unset 하거나 `false` 로 설정한다
(예: `docker run -e SERENA_OFFLINE=false ...`).

## 3. 언어 서버 사전 준비 (중요)

오프라인 모드에서는 언어 서버를 **자동으로 내려받지 않는다.** 대신 시도 시점에
설치 링크·방법을 담은 에러 메시지를 출력한다. 따라서 사용할 언어의 서버를
**미리 설치**하거나, 컨테이너 이미지에 **사전 번들**해야 한다.

권장 방식:

1. **PATH 에 언어 서버 배치**: 대부분의 언어 서버는 PATH에 있으면 그대로 사용한다
   (예: `gopls`, `rust-analyzer`, `clangd`, `pasls`, `pyright`(uvx로 사전 캐싱) 등).
2. **설치 위치에 바이너리 배치**: 에러 메시지에 표시되는 대상 경로(install location)에
   바이너리를 직접 배치한다.
3. **Docker 이미지에 사전 설치**: 빌드 단계(네트워크 가능 환경)에서 필요한 언어 서버를
   설치/캐싱한 뒤, 런타임에서 `SERENA_OFFLINE=true` 로 실행한다.

> 참고: npm/uvx/nuget 기반으로 실행 시점에 패키지를 받아오는 일부 서버는 최초 1회
> 네트워크가 필요하므로, 오프라인 운용 시 반드시 사전 설치/캐싱이 필요하다.

## 4. 빌드 시 주의 (의존성)

- `anthropic` 의존성은 `pyproject.toml` 에서 제거되었다. `uv.lock` 은 자동 갱신되지 않으므로,
  락 파일 기반 설치(`uv sync --locked`)를 사용한다면 네트워크 가능한 환경에서 한 번
  `uv lock` 으로 락 파일을 재생성해야 한다.
  (단, `uv pip install -r pyproject.toml` / `uvx` 설치 경로는 락 파일을 무시하므로 영향 없음.)

## 5. 검증 포인트

오프라인 모드가 올바르게 적용되었는지 확인하려면:

- 에이전트 시작 로그에 `Offline mode is enabled; the web dashboard will not be started.` 표시
- 미설치 언어 서버 사용 시 `Offline mode is enabled (environment variable SERENA_OFFLINE) ...`
  로 시작하는 안내 메시지가 출력되고 자동 다운로드가 발생하지 않음
- 네트워크 모니터링 상 oraios-software.de / github.com 등으로의 outbound 요청이 없음

## 6. 코드 상의 핵심 변경 위치

- `src/serena/util/offline.py` — 오프라인 모드 판정/가이드 헬퍼 (신규)
- `src/serena/agent.py` — 사용 통계 전송 차단, 오프라인 시 대시보드 미기동, estimator 폴백
- `src/serena/dashboard.py` — 뉴스 fetch 차단
- `src/serena/analytics.py` — Anthropic 추정기/임포트 제거
- `src/solidlsp/language_servers/common.py` — 런타임 의존성 자동설치 차단 + 안내
- `src/solidlsp/ls_utils.py` — 모든 파일 다운로드 차단(방어적)
- `src/serena/util/dotnet.py` — .NET 런타임 자동설치 차단
- `src/solidlsp/language_servers/{haxe,pascal}_*.py` — 직접 다운로드 경로 차단
