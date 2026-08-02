from website_workflows.workflow_registry import WORKFLOW_REGISTRY, get_workflow_for_domain

def execute_website_workflow(domain_or_title: str, steps: list) -> bool:
    """Executes steps using the registered workflow for the domain/title, observing after each step."""
    workflow = get_workflow_for_domain(domain_or_title)
    if not workflow:
        return False

    print(f"[Website Workflow Framework]: Activated '{workflow.name}' Workflow for {domain_or_title}")
    for step in steps:
        success = workflow.execute_step(step)
        workflow.observe_and_continue()
        if not success:
            break
    return True
