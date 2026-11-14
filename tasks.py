from crewai import Task

from agents import DEPARTMENTS


TASK_GUIDANCE = {
    "youtube": (
        "플레이리스트 콘셉트와 쇼츠 대본을 포함하고, 음악·영상 소재의 저작권 확인이 "
        "필요한 지점을 명확히 표시하세요."
    ),
    "webnovel": (
        "블로그 글의 구성과 대체역사 세계관 방향을 제안하고, 역사적 사실과 창작 설정을 "
        "구분하세요."
    ),
    "business": (
        "크몽 프롬프트 상품과 V2L 사업 기회를 함께 다루고, 검증이 필요한 시장·안전·규제 "
        "가정을 명확히 표시하세요."
    ),
}


def create_department_task(department_key: str, workers: list) -> Task:
    """Create the department's deliverable, reviewed by its hierarchical manager."""
    if department_key not in DEPARTMENTS:
        raise ValueError(f"알 수 없는 부서입니다: {department_key}")

    department_name = DEPARTMENTS[department_key]["name"]
    worker_names = ", ".join(worker.role for worker in workers)
    return Task(
        description=(
            "최종결정권자가 전달한 요청을 바탕으로 부서 최종 기획안을 작성하세요.\n"
            "요청: {request}\n"
            f"담당 실무진: {worker_names}\n"
            f"부서별 요구사항: {TASK_GUIDANCE[department_key]}\n\n"
            "부서장은 실무진의 결과를 통합하고 저작권 및 문맥 리스크를 검토하세요. "
            "근거가 없는 수치·사실은 만들지 말고 '확인 필요'로 표시하세요. "
            "최종 출력은 한국어로, 다음 항목을 포함한 실행 가능한 기획안으로 작성하세요: "
            "목표, 핵심 제안, 실행 단계, 리스크 및 확인 사항, 성공 기준."
        ),
        expected_output=(
            f"{department_name}의 검토가 끝난 한국어 최종 기획안. "
            "목표, 핵심 제안, 실행 단계, 리스크 및 확인 사항, 성공 기준을 포함합니다."
        ),
    )
