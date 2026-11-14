# 에이전트 타이쿤

Streamlit 웹앱으로, 휴대폰·태블릿·PC에서 같은 Google 계정으로 로그인하면 부서별 대화와 기획안 및 승인 상태를 공유합니다. 각 화면은 실행할 때 클라우드의 최신 기록을 불러옵니다.

## 클라우드 배포

1. Supabase 프로젝트를 만들고 **Project Settings → API**에서 Project URL과 `service_role` 키를 확인합니다.
2. 앱을 Streamlit Community Cloud에 배포합니다.
3. 앱의 **Settings → Secrets**에 다음 값을 설정합니다. 실제 비밀값은 코드나 저장소에 넣지 마세요.

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

4. Google Cloud Console에서 웹 애플리케이션 OAuth 클라이언트를 만들고, 위 `redirect_uri`를 승인된 리디렉션 URI에 등록합니다. 로컬에서 테스트할 때는 `http://localhost:8501/oauth2callback`을 사용합니다.
5. Supabase **SQL Editor**에서 다음 테이블을 한 번 생성합니다.

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

`SUPABASE_SERVICE_ROLE_KEY`는 서버에서만 사용하며 브라우저에 전달하거나 공개 저장소에 올리지 마세요. 사용자 식별과 계정별 기록 분리는 앱의 Google 로그인 세션을 기준으로 합니다.

로그인 사용자의 Google OIDC 식별자별로 데이터가 분리됩니다. 같은 계정으로 다른 기기에서 로그인하면 저장된 기록을 볼 수 있습니다. 다른 기기에 이미 열린 화면은 다음 상호작용 또는 새로고침 시 최신 상태를 불러옵니다. 기존 버전에서 브라우저 세션에만 남아 있던 대화 기록은 자동 이전되지 않습니다.

## 로컬 실행

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

로컬 실행 시에도 Supabase 설정, Google OAuth 설정 및 `GOOGLE_API_KEY`가 필요합니다. Streamlit 인증 설정은 `.streamlit/secrets.toml`에 두고, API 키는 환경 변수 또는 Streamlit Secrets로 제공할 수 있습니다. 비밀값 파일은 저장소에 커밋하지 마세요.
