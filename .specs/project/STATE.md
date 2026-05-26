# Project State

## Decisions

- O desafio sera tratado como projeto greenfield.
- O MVP prioriza os requisitos obrigatorios do PDF antes dos bonus.
- A pipeline deve ser demonstravel com os anexos B a F e nao tentar cobrir toda a linguagem PL/pgSQL.
- Bonus preferencial inicial: QA com pytest/checks estaticos, por ser diretamente alinhado aos criterios de avaliacao.
- Implementacao inicial usa FastAPI, LangGraph, sqlparse, psycopg, PostgreSQL via Docker Compose, pytest e ruff.
- A geracao usa wrappers Python com SQL delegado para preservar semantica de PL/pgSQL no MVP.
- A proxima feature planejada adiciona AI configuravel sem tornar chave de provider obrigatoria.
- A camada AI deve receber contexto estruturado de parsing/analise, nao apenas a procedure bruta.
- A camada AI foi implementada com provider OpenAI opcional via Responses API e fallback deterministico.
- O reparo AI de codigo invalido e limitado a uma tentativa.

## Blockers

- Chaves de LLM, caso usadas, dependem de configuracao local via variaveis de ambiente.
- Docker Desktop precisa estar rodando para validar PostgreSQL local via `docker compose up -d postgres`.

## Deferred Ideas

- Langfuse self-hosted com screenshots de traces.
- Equivalencia comportamental contra banco de teste populado.
- LLM-as-judge com rubrica objetiva para evaluation.
- Provider local via Ollama ou outro runtime local, apos a abstracao de provider estar estavel.

## Notes

- Fonte dos requisitos: `Desafio_Tecnico_Inovacao_v2_candidatos.pdf`.
