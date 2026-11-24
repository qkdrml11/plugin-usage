# plugin-usage

Claude Code에 설치된 플러그인을 각각 얼마나 썼는지 대화 기록에서 세어 보여주는 명령이에요. 한 번도 안 쓴 플러그인은 삭제 후보로 표시해요.

```
/plugin-usage        # 최근 30일
/plugin-usage 60     # 최근 60일
```

## 작동 방식

1. Claude 데스크톱 앱이 PC에 저장해 둔 설치 플러그인 목록(`manifest.json`)을 읽어요. 플러그인마다 어떤 스킬과 명령을 갖고 있는지 정리해요.
2. `~/.claude/projects` 등에 남아 있는 대화 기록(`.jsonl`)에서 스킬 호출, 플러그인 MCP 도구 호출, `/명령` 입력을 찾아요.
3. 플러그인별 사용 횟수와 마지막 사용일을 표로 보여줘요.

전부 PC 안에서만 돌고, 인터넷으로 보내는 건 없어요. 결과는 화면에만 표시되고 모델에게는 전달되지 않아요.

## 한계

- 이 PC의 Claude Code 기록만 셉니다. claude.ai 웹 채팅이나 Cowork에서 쓴 건 잡히지 않아요.
- 삭제는 하지 않고 후보만 알려줘요. 실제 삭제는 앱의 플러그인 관리 화면에서 직접 하세요.
- `python`이 PATH에 있어야 해요.

## 설치

터미널의 Claude Code 프롬프트에서:

```
/plugin install plugin-usage --marketplace qkdrml11/plugin-usage
```

셸에서:

```
claude plugin install plugin-usage --marketplace qkdrml11/plugin-usage
```

데스크톱 앱에서는 `/plugin`이 동작하지 않아요. 프롬프트 옆 **+** → **Plugins** → **Add marketplace**에 `qkdrml11/plugin-usage`를 입력한 다음 **Add plugin**을 누르세요.
