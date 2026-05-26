import ast

from app.graph.modernization_graph import run_modernization


def test_graph_generates_valid_python() -> None:
    source = """
    CREATE OR REPLACE FUNCTION fn_saldo_cliente(p_cliente_id BIGINT)
    RETURNS NUMERIC(18,2)
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN 0;
    END;
    $$;
    """

    state = run_modernization(source)

    assert state["status"] == "sucesso"
    assert state["generated_code"]
    ast.parse(state["generated_code"])
    assert set(state["report"]["stages"]) == {
        "parsing",
        "semantic_analysis",
        "generation",
        "validation",
    }

