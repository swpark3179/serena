# Serena 작업 가이드 (기동 후 효과적인 사용법)

이 문서는 Serena MCP 서버를 **기동한 다음, 실제 코딩 작업을 어떤 순서와 방식으로 진행하면
가장 효과적인지**를 정리한 실전 가이드입니다.
구성/설정 방법은 [구성 가이드](./configuration-guide.md)를 참고하세요.

---

## 0. Serena를 한 문장으로

> Serena는 언어 서버(LSP)를 통해 **심볼 단위로 코드를 탐색·편집·리팩터링**하게 해주는 MCP 서버입니다.
> LLM이 "줄 번호"나 "단순 텍스트 검색" 대신, **함수/클래스/참조 관계** 수준에서 코드를 다루게 만들어
> 더 빠르고 정확하게 작업하도록 돕습니다.

따라서 효과적인 사용의 핵심은 **"LLM이 텍스트 grep 대신 심볼 도구를 쓰도록 유도하는 것"** 입니다.

---

## 1. 서비스 기동 (3가지 방식)

### (A) stdio 모드 — 가장 일반적

Claude Code, Codex, Cursor 등 대부분의 클라이언트가 Serena를 **서브프로세스로 직접 실행**합니다.
사용자가 서버를 직접 띄울 필요 없이, 클라이언트에 실행 명령만 등록하면 됩니다.

```bash
serena start-mcp-server --context claude-code --project-from-cwd
```

### (B) Streamable HTTP 모드 — 직접 기동

서버 생명주기를 사용자가 직접 관리하고, 클라이언트에 URL을 알려주는 방식입니다.

```bash
serena start-mcp-server --transport streamable-http --port 9121
# 클라이언트는 http://localhost:9121/mcp 에 연결
```

> Serena는 **상태를 가진(stateful) 서버**이며 한 번에 하나의 프로젝트만 활성화됩니다.
> 단일 인스턴스에 여러 클라이언트를 붙이는 것은 **모두 같은 프로젝트**를 작업할 때만 적합합니다.
> 서로 다른 프로젝트를 작업한다면 클라이언트마다 stdio로 각자 서버를 띄우세요.

### (C) Docker — 격리 환경

```bash
docker run --rm -i --network host \
  -v /path/to/your/projects:/workspaces/projects \
  ghcr.io/oraios/serena:latest serena
```

셸 명령 격리, 로컬에 언어 서버 미설치, 일관된 환경이 장점입니다.

### 기동 직후: 대시보드 확인

기동하면 기본적으로 localhost에 웹 대시보드가 함께 뜹니다.

```
http://localhost:24282/dashboard/index.html
```

여기서 **활성 도구 / 활성 언어 / 활성 모드 / 진행 중·과거 도구 호출 / 실시간 로그**를 확인할 수 있고,
활성 언어 서버를 실시간으로 추가·제거할 수도 있습니다. **문제가 생기면 가장 먼저 볼 곳입니다.**

---

## 2. 프로젝트 워크플로우 (권장 순서)

```
프로젝트 생성/인덱싱 → 프로젝트 활성화 → 온보딩(메모리 생성) → 코딩 작업
```

### 2.1 프로젝트 생성 & 인덱싱

```bash
serena project create            # 언어 자동 감지 후 프로젝트 설정 생성
serena project create --index    # 생성과 동시에 심볼 인덱싱
serena project index             # 기존 프로젝트 인덱싱 (필요 시 자동 생성)
```

> **대형 프로젝트라면 인덱싱을 강력히 권장**합니다. 심볼 정보를 미리 캐싱하여 첫 도구 호출의 지연을 없앱니다.
> 인덱싱은 한 번만 하면 되고, 이후 파일이 바뀌면 Serena가 자동으로 갱신합니다.

### 2.2 프로젝트 활성화

두 가지 방법:

```bash
# 방법 1: 기동 시 인자로 (ide/claude-code 같은 단일 프로젝트 컨텍스트에 적합)
serena start-mcp-server --project /path/to/my_project
```

```
# 방법 2: 대화 중 LLM에게 지시
"Activate the project /path/to/my_project"   # 최초 활성화(자동 생성)
"Activate the project my_project"            # 이름으로 활성화
```

> 단, `ide`/`claude-code` 컨텍스트에서 시작 시 프로젝트를 이미 지정했다면 `activate_project` 도구는
> 비활성화됩니다(프로젝트 전환이 불필요하다고 가정).

### 2.3 온보딩 & 메모리

프로젝트를 처음 열면 Serena가 **온보딩**을 수행하여 프로젝트 구조·컨벤션을 파악하고 **메모리**(`.md` 파일)로 저장합니다.
이후 세션에서는 이 메모리를 필요할 때 불러와 활용합니다.

- 메모리는 `<프로젝트>/.serena/memories/`에 저장됩니다.
- 메모리는 `` `mem:NAME` `` 형식으로 서로 참조할 수 있고, 이름 변경 시 참조가 동기화됩니다.
- 끊긴 참조 점검: `serena memories check`

> **효과적인 사용 팁**: 온보딩이 끝나면 생성된 메모리를 한 번 검토하세요. 부정확한 내용이 있으면
> 직접 수정하거나 LLM에게 갱신을 지시하면, 이후 모든 세션의 품질이 올라갑니다.

---

## 3. 효과적인 사용을 위한 핵심 습관

### 3.1 심볼 도구를 쓰게 유도하라

Serena의 강점은 심볼 단위 작업입니다. 다음 도구들이 대표적입니다(이름은 클라이언트마다 노출 방식이 다를 수 있음):

| 작업 | 권장 도구 | 비효율적 대안 |
| --- | --- | --- |
| 코드 구조 파악 | `get_symbols_overview` | 파일 전체 읽기 |
| 특정 심볼 찾기 | `find_symbol` | grep |
| 어디서 쓰이는지 | `find_referencing_symbols` | grep로 텍스트 검색 |
| 심볼 단위 편집 | 심볼 기반 편집 도구 | 줄 번호 기반 패치 |

지시 예시:
- ❌ "이 파일 전체를 읽고 고쳐줘"
- ✅ "`UserService` 클래스의 구조를 먼저 보고, `authenticate` 메서드만 찾아서 수정해줘"
- ✅ "`save_config` 함수를 호출하는 곳을 모두 찾아서 시그니처 변경의 영향 범위를 알려줘"

### 3.2 깨끗한 git 상태에서 시작하라

작업 전 `git status`가 깨끗하면, LLM이 `git diff`로 자신이 바꾼 내용을 확인하고 스스로 교정할 수 있습니다.
변경 검토도 쉬워집니다.

### 3.3 코드를 잘 구조화하라

Serena는 코드 구조에 의존합니다. 거대한 "God class"나 비모듈적 함수에서는 성능이 떨어집니다.
동적 타입 언어라면 **타입 어노테이션**이 심볼 분석 품질을 크게 높입니다.

### 3.4 테스트·린트·로그를 활용하라

Serena는 디버거를 쓸 수 없습니다. 대신 **프로그램 실행 결과·린트·테스트 결과**로 정확성을 판단합니다.
- 작업 시작 전 린트/테스트가 모두 통과하는 상태에서 출발하세요.
- 의미 있는 로그 메시지와 좋은 테스트 커버리지를 갖춘 코드일수록 Serena가 다루기 쉽습니다.

### 3.5 작업 성격에 맞는 모드를 켜라

- 분석/설계 단계 → `planning` (필요 시 `one-shot`과 조합해 계획서 생성)
- 실제 수정 단계 → `editing`
- 대화형 진행 → `interactive`

```bash
serena start-mcp-server --context claude-code --project-from-cwd --add-mode planning
```

### 3.6 Windows라면 줄바꿈 설정 확인

Serena는 시스템 기본 줄바꿈으로 파일을 쓰므로, Windows에서는 거대한 diff를 막기 위해:

```bash
git config --global core.autocrlf true
```

---

## 4. 여러 프로젝트 / 여러 에이전트

| 상황 | 권장 방식 |
| --- | --- |
| 한 에이전트가 여러 프로젝트를 동시에 편집 | **모노레포 폴더**(하위에 각 프로젝트, 심볼릭 링크 가능)를 하나의 프로젝트로 열기 |
| 작업 중 다른 프로젝트를 **읽기**만 | `query-projects` 모드 활성 + (LSP 백엔드는) `serena start-project-server` 실행 |
| 여러 에이전트가 **같은** 프로젝트 공유 | HTTP 모드로 단일 인스턴스 띄우고 모두 같은 URL 연결 |
| 여러 에이전트가 **다른** 프로젝트 | 프로젝트마다 stdio로 별도 인스턴스 (클라이언트가 자동 처리) |

### 모노레포 교차 참조 (TypeScript)

`find_referencing_symbols`가 형제 패키지의 사용처까지 찾게 하려면 `project.yml`에 추가:

```yaml
additional_workspace_folders:
  - ../shared-lib
  - ../api-client
```

> 워크스페이스 폴더가 늘어날수록 시작 시 인덱싱 시간이 증가하므로, 실제로 교차 참조가 필요한 패키지만 나열하세요.

---

## 5. 유용한 CLI 명령 모음

```bash
# 도구 탐색
serena tools list --all                  # 전체 도구 목록
serena tools description find_symbol      # 특정 도구 상세 설명

# 프로젝트 관리
serena project health-check               # 현재 프로젝트 상태 점검
serena project index                      # 인덱싱
serena project is_ignored_path path/to/x  # 경로가 무시되는지 확인

# 구성 관리
serena config edit                        # 전역 구성 편집
serena context list / mode list           # 컨텍스트/모드 목록

# 메모리
serena memories check                     # 끊긴 mem: 참조 점검
```

`--help`를 어떤 명령에든 붙이면 사용법을 볼 수 있습니다.

---

## 6. 자주 겪는 문제 (트러블슈팅)

| 증상 | 점검 사항 |
| --- | --- |
| 첫 도구 호출이 매우 느림 | 인덱싱 미수행 → `serena project index` 실행 |
| 심볼을 못 찾음 / 참조 누락 | `project.yml`의 `languages`가 맞는가, 언어 서버가 떴는가(대시보드 확인) |
| 편집 도구가 동작 안 함 | `read_only: true`이거나 도구가 컨텍스트/모드로 비활성화됨 |
| 모노레포에서 교차 참조 안 됨 | `additional_workspace_folders` 설정(현재 TypeScript) |
| 연결 타임아웃(uvx 사용 시) | 매 커밋마다 재동기화가 느림 → 정식 설치로 전환 권장 |
| 도구 응답이 잘림 | 전역 구성의 `default_max_tool_answer_chars`(기본 150,000) 조정 |
| 무엇이 켜져 있는지 모르겠음 | 대시보드의 상태/구성 패널 확인 |

---

## 요약: 효과적인 사용 5계명

1. **기동 시 클라이언트에 맞는 컨텍스트를 지정**한다 (`claude-code`, `ide` 등).
2. **대형 프로젝트는 미리 인덱싱**한다 (`serena project index`).
3. **온보딩 메모리를 검토·정제**하여 이후 세션 품질을 높인다.
4. **심볼 도구를 쓰도록 지시**한다 (grep/전체 읽기 대신 `find_symbol`, `find_referencing_symbols`).
5. **깨끗한 git 상태 + 통과하는 테스트/린트**에서 작업을 시작한다.
