from app.graph.state import initial_state
from app.nodes.validation import validate_generated_code


def test_validation_marks_invalid_python_as_failure() -> None:
    state = initial_state("select 1")
    state["generated_code"] = "def broken(:\n    pass"

    result = validate_generated_code(state)

    assert result["status"] == "falha"
    assert result["validation"]["ast_parse"] is False

