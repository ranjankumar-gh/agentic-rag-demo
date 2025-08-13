from app.agent import SimpleAgent

def test_agent_basic():
    a = SimpleAgent()
    res = a.run("prepaid 4G offers maharashtra 2GB/day")
    assert "plans" in res
    assert isinstance(res["plans"], list)
