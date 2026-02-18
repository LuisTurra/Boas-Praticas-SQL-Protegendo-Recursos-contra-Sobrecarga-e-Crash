# 🚕 Boas Práticas SQL: Protegendo Recursos contra Sobrecarga e Crash

Projeto de portfólio que demonstra como queries SQL **seguras** (LIMIT, projeção, filtros precoces) previnem consumo excessivo de recursos e possíveis crashes, enquanto queries **agressivas** podem travar o processo.

## Objetivo
Mostrar empiricamente que precauções de recursos **melhoram performance e estabilidade**, sem custo significativo.

## Tecnologias
- Python + DuckDB (leve e eficiente)
- Streamlit (dashboard interativo)
- Dataset real: NYC Yellow Taxi (Jan/2023) carregado via HTTP

## Como rodar
1. `pip install -r requirements.txt`
2. `streamlit run app.py`

## Resultados esperados
- Queries seguras: menor tempo, muito menos memória, zero risco de crash
- Queries agressivas: picos altos de memória e risco real de OOM

### live[]

### Relatorio[]

## Resultados e Conclusões

Os testes foram executados em um dataset real de ~3 milhões de linhas (NYC Yellow Taxi – Janeiro/2023) usando DuckDB em memória.

**Observações principais:**

- Em **todos os casos**, a query otimizada (com boas práticas: projeção de colunas, LIMIT e filtros precoces) apresentou **tempo de execução igual ou inferior** à query simples.
- O **consumo de memória** foi **consistentemente menor** ou igual nas queries otimizadas, com diferença drástica no caso mais extremo (ordenamento completo do dataset).
- O teste 5 demonstra o impacto mais significativo: a query simples consumiu **459.5 MB** adicionais e levou **1.29 segundos**, enquanto a otimizada usou apenas **0.7 MB** e executou em **0.01 segundos**.

**Conclusão geral:**  
Boas práticas de escrita de SQL não apenas protegem recursos (memória/CPU), mas frequentemente **melhoram a performance**. Projeção de colunas, aplicação precoce de filtros e uso de LIMIT evitam processamento desnecessário, tornando as consultas mais eficientes e escaláveis em datasets grandes.

Esse comportamento é esperado em engines column-oriented como DuckDB, que beneficiam-se fortemente da redução de colunas e linhas processadas.