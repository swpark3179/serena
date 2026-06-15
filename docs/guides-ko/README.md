# Serena 한국어 가이드

Serena(MCP 기반 "코딩 에이전트를 위한 IDE")를 효과적으로 사용하기 위한 한국어 가이드 모음입니다.
이 문서들은 **서비스 기동(MCP 서버 실행) 이후** 어떻게 설정하고 사용하면 더 효과적인지에 초점을 맞춥니다.

## 문서 목록

| 문서 | 내용 |
| --- | --- |
| [구성 가이드](./configuration-guide.md) | 컨텍스트/모드, `serena_config.yml`, `project.yml`, 도구 활성/비활성, 인덱싱 등 **무엇을 어떻게 설정하는가** |
| [작업 가이드](./usage-guide.md) | 프로젝트 활성화 → 온보딩 → 실제 코딩 작업까지, **기동 후 어떤 순서로 사용하면 효과적인가** |

## 빠른 시작 (요약)

```bash
# 1) MCP 서버 기동 (클라이언트가 stdio로 자동 실행하는 경우가 일반적)
serena start-mcp-server --context claude-code --project-from-cwd

# 2) (선택) 대형 프로젝트라면 미리 인덱싱하여 첫 호출 지연 제거
serena project index

# 3) 대시보드로 동작/로그/설정 확인 (기본적으로 localhost에 자동 실행됨)
#    http://localhost:24282/dashboard/index.html (포트가 사용 중이면 더 높은 포트가 할당됨)
```

> 공식 영문 문서: <https://oraios.github.io/serena/>
> 본 한국어 가이드는 공식 문서(`docs/02-usage/`)의 내용을 기동 후 활용 관점에서 재구성한 것입니다.
