from langgraph.graph import END, START, StateGraph

from app.graph.state import ModernizationState, initial_state
from app.nodes.generation import generate_python
from app.nodes.parsing import parse_sql
from app.nodes.semantic_analysis import analyze_semantics
from app.nodes.validation import validate_generated_code


def build_graph():
    workflow = StateGraph(ModernizationState)
    workflow.add_node("parsing", parse_sql)
    workflow.add_node("semantic_analysis", analyze_semantics)
    workflow.add_node("generation", generate_python)
    workflow.add_node("validation", validate_generated_code)

    workflow.add_edge(START, "parsing")
    workflow.add_edge("parsing", "semantic_analysis")
    workflow.add_edge("semantic_analysis", "generation")
    workflow.add_edge("generation", "validation")
    workflow.add_edge("validation", END)
    return workflow.compile()


graph = build_graph()


def run_modernization(
    source_code: str,
    schema_context: str | None = None,
    metadata: dict[str, object] | None = None,
) -> ModernizationState:
    state = initial_state(source_code, schema_context, metadata)
    return graph.invoke(state)

