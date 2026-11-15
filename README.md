# 에이전트 타이쿤

Streamlit 웹앱으로, 휴대폰·태블릿·PC에서 같은 Google 계정으로 로그인하면 부서별 대화와 기획안 및 승인 상태를 공유합니다. 각 화면은 실행할 때 Supabase에서 최신 기록을 불러옵니다.

## 설정

Google OAuth, Supabase, Gemini 설정은 모두 Streamlit Secrets에서 읽습니다. 환경 변수나 `.env` 파일은 사용하지 않습니다. 앱의 **Settings → Secrets** 또는 로컬의 `.streamlit/secrets.toml`에 다음 형식으로 설정하세요.

```toml
SUPABASE_URL = "https://<프로젝트 ID>.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "<Supabase service_role 키>"
GOOGLE_API_KEY = "<Gemini API 키>"

[auth]
redirect_uri = "https://<앱 주소>/oauth2callback"
cookie_secret = "<충분히 긴 임의 문자열>"
client_id = "<Google OAuth 클라이언트 ID>"
client_secret = "<Google OAuth 클라이언트 비밀값>"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

`.streamlit/secrets.toml`에는 실제 비밀값이 있으므로 저장소에 커밋하지 마세요. `SUPABASE_SERVICE_ROLE_KEY`는 서버에서만 사용하며 브라우저에 전달하거나 공개해서는 안 됩니다.

## 클라우드 설정

1. Supabase 프로젝트의 **Project Settings → API**에서 Project URL과 `service_role` 키를 확인해 위 Secrets에 등록합니다.
2. 앱을 Streamlit Community Cloud에 배포하고 배포 주소를 OAuth 리디렉션 URI로 설정합니다.
3. Google Cloud Console에서 웹 애플리케이션 OAuth 클라이언트를 만들고, Secrets의 `redirect_uri`를 승인된 리디렉션 URI에 등록합니다. 로컬 테스트 시에는 `http://localhost:8501/oauth2callback`을 등록하세요.
4. Supabase **SQL Editor**에서 다음 테이블을 한 번 생성합니다.

   ```sql
   create table public.agent_taikun_state (
       user_id text not null,
       department text not null,
       history jsonb not null default '[]'::jsonb,
       plan text not null default '',
       approved boolean not null default false,
       updated_at timestamptz not null default now(),
       primary key (user_id, department)
   );
   alter table public.agent_taikun_state enable row level security;
   ```

로그인 사용자의 Google OIDC 식별자별로 데이터가 분리됩니다. 같은 계정으로 다른 기기에서 로그인하면 저장된 기록을 볼 수 있습니다. 다른 기기에 이미 열린 화면은 다음 상호작용 또는 새로고침 시 최신 상태를 불러옵니다. 기존 버전에서 브라우저 세션에만 남아 있던 대화 기록은 자동 이전되지 않습니다.

## 로컬 실행

`.streamlit/secrets.toml`에 위 설정을 입력한 뒤 실행합니다.

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```
