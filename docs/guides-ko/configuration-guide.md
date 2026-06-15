# Serena 구성 가이드

이 문서는 Serena MCP 서버를 **기동하기 전/후에 무엇을 어떻게 설정해야 효과적인지**를 정리한 가이드입니다.
실제 코딩 작업 순서는 [작업 가이드](./usage-guide.md)를 참고하세요.

---

## 1. 구성의 4개 계층

Serena는 다층(multi-layer) 구성 방식을 사용합니다. 아래로 갈수록 우선순위가 높아지며,
하위 계층이 상위 계층을 **확장(extend)** 하거나 **재정의(override)** 합니다.

| 계층 | 파일/위치 | 적용 범위 | 용도 |
| --- | --- | --- | --- |
| 1. 전역 구성 | `~/.serena/serena_config.yml` | 모든 프로젝트 | 기본 백엔드, 기본 도구/모드, 타임아웃, 로깅, 대시보드 |
| 2. 프로젝트 구성 | `<프로젝트>/.serena/project.yml` | 단일 프로젝트 | 언어, 무시 규칙, 초기 프롬프트, 프로젝트별 도구/모드 |
| 3. 컨텍스트 + 모드 | `resources/config/contexts`, `modes` | 세션 | 클라이언트 환경 + 작업 스타일에 맞춘 조합형 설정 |
| 4. CLI 인자 | `serena start-mcp-server [options]` | 세션 | 위 모든 설정을 최종적으로 덮어쓰기 |

> **핵심 원칙**: 모든 프로젝트에 공통으로 적용할 것은 전역 구성에, 특정 프로젝트에만 적용할 것은
> `project.yml`에, 세션마다 달라지는 것은 컨텍스트/모드 또는 CLI 인자로 분리하세요.

---

## 2. 전역 구성 (`serena_config.yml`)

처음 Serena를 실행하면 자동으로 생성됩니다.

```bash
# 편집기로 직접 열기
serena config edit
```

| OS | 경로 |
| --- | --- |
| Linux / macOS / Git-Bash | `~/.serena/serena_config.yml` |
| Windows (CMD/PowerShell) | `%USERPROFILE%\.serena\serena_config.yml` |

설정 가능한 주요 항목:

- **언어 백엔드 기본값** — 언어 서버(LSP, 기본값) 또는 JetBrains 플러그인
- **기본 도구 집합** — 활성/비활성 도구
- **기본 모드** — `base_modes`(항상 적용), `default_modes`(프로젝트/CLI로 재정의 가능)
- **도구 실행 파라미터** — `tool_timeout`(기본 240초), `default_max_tool_answer_chars`(기본 150,000자)
- **전역 무시 규칙**, **로깅 설정**, **대시보드/GUI 설정**
- **언어 서버별 고급 설정** (`ls_specific_settings`)

### 데이터 디렉터리 변경

설정·언어 서버·로그가 저장되는 디렉터리는 기본적으로 `~/.serena`입니다.
`SERENA_HOME` 환경 변수로 변경할 수 있습니다.

```bash
export SERENA_HOME=/data/serena
```

### 프로젝트별 `.serena` 폴더 위치 변경

기본적으로 각 프로젝트는 루트의 `.serena` 폴더에 메모리/캐시를 저장합니다.
중앙 집중식으로 모으려면 전역 구성의 `project_serena_folder_location`을 사용합니다.

```yaml
# 모든 프로젝트 메타데이터를 공용 디렉터리에 모으기
project_serena_folder_location: "/projects-metadata/$projectFolderName/.serena"
```

플레이스홀더: `$projectDir`(프로젝트 루트 절대 경로), `$projectFolderName`(프로젝트 폴더명)

---

## 3. 프로젝트 구성 (`project.yml`)

프로젝트별 설정으로, 보통 프로젝트와 함께 버전 관리합니다.

```bash
# 현재 디렉터리에 프로젝트 생성 (언어 자동 감지)
serena project create

# 생성과 동시에 인덱싱
serena project create --index
```

생성 후 `<프로젝트>/.serena/project.yml`을 직접 편집합니다. 자주 쓰는 항목:

| 키 | 설명 |
| --- | --- |
| `project_name` | LLM에게 프로젝트를 이름으로 활성화하라고 지시할 때 사용 |
| `languages` | 언어 서버를 띄울 언어 목록. 첫 번째 언어가 기본/폴백 |
| `ignore_all_files_in_gitignore` | `.gitignore` 규칙으로 파일 무시 (기본 `true`) |
| `ignored_paths` | 추가로 무시할 경로(gitignore 문법) |
| `read_only` | `true`면 모든 편집 도구 비활성 (탐색/리뷰 전용) |
| `excluded_tools` / `included_optional_tools` | 프로젝트별 도구 제외/추가 |
| `initial_prompt` | 프로젝트 활성화 시 **항상** LLM에 전달되는 프롬프트(코딩 컨벤션 등) |
| `default_modes` / `added_modes` | 프로젝트의 기본 모드 재정의 / 추가 |
| `language_backend` | 이 프로젝트의 백엔드(`LSP` 또는 `JetBrains`) |
| `additional_workspace_folders` | 모노레포 교차 패키지 참조(현재 TypeScript 지원) |

### 로컬 오버라이드 (`project.local.yml`)

`project.yml`과 같은 폴더에 `project.local.yml`을 두면, 여기에 정의된 키가 우선 적용됩니다.
이 파일은 기본적으로 git에서 무시되므로, **개인 환경 전용 설정**(예: 로컬 언어 서버 경로)에 적합합니다.

### `initial_prompt` 활용 (효과적인 사용 팁)

`initial_prompt`는 프로젝트의 "헌법"과 같습니다. 코딩 스타일, 아키텍처 원칙, 금지 사항을 적어두면
세션마다 반복 설명할 필요가 없습니다. (이 저장소의 `project.yml`이 좋은 예시입니다 — 객체지향 스타일,
dataclass 사용, reStructuredText docstring 등을 명시.)

---

## 4. 컨텍스트(Context)와 모드(Mode)

조합형 설정의 핵심입니다. **컨텍스트는 "어디서 실행되는가"**, **모드는 "어떤 작업을 하는가"** 를 정의합니다.

### 4.1 컨텍스트 — 시작 시 1개 고정

시작 시 `--context`로 지정하며, 세션 도중에는 변경할 수 없습니다.

| 컨텍스트 | 용도 |
| --- | --- |
| `desktop-app` | Claude Desktop 등 (기본값). 전체 도구 제공 |
| `claude-code` | Claude Code 전용. CC 내장 기능과 중복되는 도구 비활성 |
| `codex` | OpenAI Codex 최적화 |
| `ide` | VSCode/Cursor/Cline 등 IDE 어시스턴트. 파일/셸은 IDE가 처리 |
| `agent` | Agno 등 자율 에이전트용 (OpenAI 호환 필요 시 `oaicompat-agent`) |

> **단일 프로젝트 컨텍스트** (`ide`, `claude-code`): 시작 시 프로젝트를 지정하면 도구 집합이 그 프로젝트에
> 필요한 최소한으로 제한되고, 프로젝트 전환 도구(`activate_project`)는 비활성화됩니다.

```bash
serena context list                 # 사용 가능한 컨텍스트 목록
serena context create my-context    # 커스텀 컨텍스트 생성
serena context edit my-context
```

### 4.2 모드 — 동시에 여러 개 활성 가능

작업 스타일을 세분화합니다. 여러 모드를 조합할 수 있습니다.

| 모드 | 용도 |
| --- | --- |
| `planning` | 계획/분석 중심 |
| `editing` | 직접 코드 수정 최적화 |
| `interactive` | 대화형 주고받기 (기본 권장) |
| `one-shot` | 단일 응답 완료 (보통 `planning`과 조합해 리포트/초안 생성) |
| `onboarding` / `no-onboarding` | 온보딩 수행 / 건너뛰기 |
| `no-memories` | 모든 메모리 도구 비활성 |
| `query-projects` | 다른 Serena 프로젝트를 읽기 위한 도구 활성 |

활성 모드는 다음의 합집합입니다:
`base_modes`(전역, 항상) + `default_modes`(전역, 프로젝트/CLI로 재정의 가능) + `added_modes`(프로젝트/CLI 추가)

```bash
serena mode list
serena mode create my-mode
serena mode edit my-mode
```

> ⚠️ `interactive`와 `one-shot`처럼 의미상 충돌하는 모드는 조합하지 마세요. Serena가 충돌을 막아주지는 않습니다.

---

## 5. CLI 인자 — 최종 재정의

`start-mcp-server`의 인자가 위 모든 설정을 덮어씁니다. 자주 쓰는 옵션:

| 옵션 | 설명 |
| --- | --- |
| `--project <path\|name>` | 작업할 프로젝트를 이름/경로로 지정 |
| `--project-from-cwd` | 현재 디렉터리에서 상위로 올라가며 `.serena/project.yml` 또는 `.git`을 찾아 자동 활성화 (CLI 에이전트에 적합) |
| `--context <name>` | 운영 컨텍스트 지정 |
| `--mode <name>` | 기본 모드 재정의 (여러 번 지정 가능) |
| `--add-mode <name>` | 모드 추가 |
| `--language-backend JetBrains` | JetBrains 백엔드 사용 |
| `--transport streamable-http --port <port>` | HTTP 모드로 기동 |
| `--open-web-dashboard <true\|false>` | 시작 시 대시보드 자동 열기 여부 |

```bash
# 예: Claude Code에서 현재 디렉터리 프로젝트로, 계획 모드 추가하여 기동
serena start-mcp-server --context claude-code --project-from-cwd --add-mode planning
```

전체 옵션은 `serena start-mcp-server --help`로 확인하세요.

---

## 6. 언어 서버별 고급 설정 (`ls_specific_settings`)

전역(`serena_config.yml`) 또는 프로젝트(`project.yml`) 양쪽에서 설정 가능하며, 프로젝트 설정이 우선합니다.

### 가장 흔한 케이스: 직접 설치한 언어 서버 사용 (`ls_path`)

```yaml
ls_specific_settings:
  python:
    ls_path: "/usr/local/bin/pyright-langserver"   # Serena 관리 설치 대신 직접 설치본 사용
```

`ls_path`를 지원하는 언어: `bash`, `cpp`, `kotlin`, `php`, `python`, `rust`, `typescript`, `yaml` 등 다수.
설정 시 Serena의 자동 다운로드/설치를 건너뜁니다.

### 자주 쓰는 예시

```yaml
# Go: 빌드 태그/환경 지정
ls_specific_settings:
  go:
    gopls_settings:
      buildFlags: ["-tags=integration"]
      env: { GOOS: "linux", CGO_ENABLED: "0" }

# Java: 사내망/오프라인 환경 (upstream JDTLS 모드)
  java:
    jdtls_path: "/opt/jdtls/libexec"
    lombok_path: "/home/me/.m2/.../lombok-1.18.38.jar"

# Kotlin: 힙 크기 조정
  kotlin:
    jvm_options: "-Xmx4G -XX:+UseG1GC"
```

> 언어별 전체 설정 표는 공식 문서 [Configuration](https://oraios.github.io/serena/02-usage/050_configuration.html)
> 또는 저장소의 `docs/02-usage/050_configuration.md`를 참고하세요.

---

## 7. 커스텀 프롬프트

Serena의 모든 프롬프트(시스템 프롬프트 포함)는 재정의할 수 있습니다.
데이터 디렉터리의 `prompt_templates` 폴더에 동일한 이름의 `.yml`을 추가하면 됩니다.

```yaml
# ~/.serena/prompt_templates/system_prompt.yml
prompts:
  system_prompt: |
    원하는 내용으로 시스템 프롬프트를 재정의...
```

기본 프롬프트를 복사해 출발점으로 삼는 것을 권장합니다.

---

## 8. 보안 관련 구성

- **읽기 전용 모드**: 탐색/리뷰만 시키려면 `project.yml`의 `read_only: true` 또는 `read-only` 관련 모드 사용.
- **HTTP 모드 외부 노출**: 기본은 localhost만 허용. `--host`로 리스닝 주소를 바꿀 때는 보안 영향을 반드시 검토.
- **사용 통계 수집 거부**: `SERENA_USAGE_REPORTING=false` 환경 변수 설정 (개인/프로젝트 정보는 수집되지 않음).
- **셸 명령 격리**: 더 강한 격리가 필요하면 Docker로 기동 (자세한 내용은 `DOCKER.md`).

---

## 빠른 점검 체크리스트

기동 전:
- [ ] 작업 클라이언트에 맞는 `--context` 선택 (`claude-code`, `ide`, `desktop-app` 등)
- [ ] `project.yml`의 `languages`가 실제 사용 언어와 일치하는가
- [ ] 코딩 컨벤션을 `initial_prompt`에 넣었는가
- [ ] 대형 프로젝트라면 `serena project index`로 사전 인덱싱했는가

기동 후:
- [ ] 대시보드(`http://localhost:24282/dashboard/index.html`)에서 활성 도구/언어/모드 확인
- [ ] 필요 시 대시보드에서 언어 서버를 실시간 추가/제거
