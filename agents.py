import os

from crewai import Agent, LLM


MODEL_NAME = "gemini/gemini-1.5-pro"

DEPARTMENTS = {
    "youtube": {
        "name": "유튜브 제작부",
        "manager": (
            "유튜브 제작부장",
            "유튜브 음악 플레이리스트와 쇼츠 기획안을 총괄하는 부서장",
            "실무진 결과를 검토하고 저작권, 사실성, 문맥 및 플랫폼 적합성 위험을 걸러 "
            "최종 기획안으로 정리합니다. 확인되지 않은 권리나 사실을 단정하지 않습니다.",
        ),
        "workers": [
            (
                "플레이리스트 기획자",
                "유튜브 음악 플레이리스트 구성 및 채널 콘텐츠 전략 실무자",
                "분위기와 청취 상황에 맞는 플레이리스트 콘셉트, 구성 흐름, 제목과 설명을 "
                "기획합니다. 특정 곡의 사용 권리를 확인된 것처럼 표현하지 않습니다.",
            ),
            (
                "쇼츠 대본 작가",
                "유튜브 쇼츠의 짧은 영상 대본과 후킹 문구 실무자",
                "시청자에게 명확하고 자연스러운 짧은 영상 대본, 장면 흐름, 후킹 문구를 "
                "작성합니다. 오해를 부르는 주장과 무단 인용을 피합니다.",
            ),
        ],
    },
    "webnovel": {
        "name": "웹소설 제작부",
        "manager": (
            "웹소설 제작부장",
            "블로그 콘텐츠와 대체역사 웹소설 기획을 총괄하는 부서장",
            "실무진 결과를 검토하고 저작권, 시대적 문맥, 사실과 허구의 구분을 점검해 "
            "최종 기획안으로 정리합니다.",
        ),
        "workers": [
            (
                "네이버 블로그 작가",
                "네이버 블로그용 정보성 글과 콘텐츠 구성 실무자",
                "독자와 검색 의도를 고려해 읽기 쉬운 블로그 글의 개요와 초안을 "
                "작성합니다. 출처가 필요한 사실은 확인 필요성을 표시합니다.",
            ),
            (
                "대체역사 세계관 설계자",
                "대체역사 웹소설의 세계관 및 서사 설계 실무자",
                "역사적 분기점, 세계관 규칙, 세력 관계와 서사 전개를 설계합니다. "
                "실제 역사와 창작 설정을 구분하고 기존 작품의 표현을 모방하지 않습니다.",
            ),
        ],
    },
    "business": {
        "name": "신사업 기획부",
        "manager": (
            "신사업 기획부장",
            "프롬프트 상품과 V2L 기반 신사업 조사를 총괄하는 부서장",
            "실무진 결과를 검토하고 시장 가정, 안전·규제 및 실행 리스크를 표시해 "
            "검증 가능한 최종 기획안으로 정리합니다.",
        ),
        "workers": [
            (
                "크몽 프롬프트 기획자",
                "크몽에서 제공할 프롬프트 상품의 작성 및 구성 실무자",
                "구매자가 활용하기 쉬운 독창적인 프롬프트와 사용 안내, 상품 구성을 "
                "작성합니다. 성과를 보장하는 표현은 사용하지 않습니다.",
            ),
            (
                "V2L 신사업 리서처",
                "V2L 기반 서비스와 사업 기회 조사 실무자",
                "V2L 활용 사례, 고객 문제, 수익 모델과 검증 과제를 구조화합니다. "
                "검증되지 않은 시장 수치나 안전·규제 정보를 사실처럼 제시하지 않습니다.",
            ),
        ],
    },
}


def create_llm() -> LLM:
    """Create the shared Gemini model client using the environment API key."""
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY가 설정되지 않았습니다. .env 파일에 API 키를 입력해 주세요."
        )
    return LLM(model=MODEL_NAME, api_key=api_key)


def create_department_agents(department_key: str, llm: LLM) -> tuple[Agent, list[Agent]]:
    """Build one department manager and its specialist agents."""
    if department_key not in DEPARTMENTS:
        raise ValueError(f"알 수 없는 부서입니다: {department_key}")

    department = DEPARTMENTS[department_key]
    manager_role, manager_goal, manager_backstory = department["manager"]
    manager = Agent(
        role=manager_role,
        goal=manager_goal,
        backstory=manager_backstory,
        llm=llm,
        allow_delegation=True,
        verbose=False,
    )
    workers = [
        Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            llm=llm,
            allow_delegation=False,
            verbose=False,
        )
        for role, goal, backstory in department["workers"]
    ]
    return manager, workers
