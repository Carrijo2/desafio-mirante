from app.graph.state import initial_state
from app.nodes.parsing import parse_sql
from app.nodes.semantic_analysis import analyze_semantics


def test_semantic_analysis_detects_cursor_and_jsonb() -> None:
    state = initial_state(
        """
        CREATE OR REPLACE PROCEDURE sp_demo(IN p_data DATE)
        LANGUAGE plpgsql AS $$
        DECLARE
            cur_items CURSOR FOR SELECT 1;
            v_total NUMERIC(18,2) := 0;
        BEGIN
            OPEN cur_items;
            FETCH cur_items INTO v_total;
            INSERT INTO log_auditoria(detalhes) VALUES (jsonb_build_object('x', 1));
            CLOSE cur_items;
        END;
        $$;
        """
    )

    state = parse_sql(state)
    state = analyze_semantics(state)

    findings = state["semantic_findings"]
    assert findings["cursor"] is True
    assert findings["jsonb"] is True
    assert findings["parameters"][0]["name"] == "p_data"
    assert any("cursor" in risk.lower() for risk in state["report"]["risks"])

