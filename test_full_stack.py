"""Full stack test for the Intelligent Task Automation Agent."""
import sys
sys.path.insert(0, '.')

def test():
    print("TEST 1: Direct SDK client")
    from backend.utils.gemini_client import create_llm
    llm = create_llm()
    r = llm.invoke([('human', 'Say only the word: WORKS')])
    print("  Result:", repr(r.content))

    print("TEST 2: BaseAgent._call_llm")
    from backend.agents.base_agent import BaseAgent
    class T(BaseAgent): pass
    resp = T()._call_llm('Say exactly: AGENT_OK')
    print("  Result:", repr(resp))

    print("TEST 3: All 6 agents + Orchestrator")
    from backend.core.orchestrator import TaskOrchestrator
    orch = TaskOrchestrator(base_path='.')
    print("  All agents initialized OK")

    print("TEST 4: Full goal decomposition")
    g = orch.goal_decomposer.decompose_goal(
        'Set up a new Python project with FastAPI and README'
    )
    print("  Tasks generated:", len(g.tasks))
    for t in g.tasks:
        print("   *", t.description[:70])

    print()
    print("==== ALL TESTS PASSED ====")

if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
