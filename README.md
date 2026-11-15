# 에이전트 타이쿤

Streamlit 대시보드는 로그인 없이 열립니다. 부서 채팅 기록과 승인 상태는 현재 브라우저 세션에만 저장되므로, 새 세션이나 다른 기기에서는 공유되지 않습니다. Google OAuth 및 Supabase 연동은 현재 비활성화되어 있습니다.

## 실행

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

대시보드 조회에는 OAuth나 Supabase 설정이 필요하지 않습니다. 기획안 생성을 사용하려면 `GOOGLE_API_KEY`를 환경 변수 또는 Streamlit Secrets에 설정해야 합니다.
