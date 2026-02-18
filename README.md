# 🚕 Boas Práticas SQL: Protegendo Recursos contra Sobrecarga e Crash

Projeto de portfólio que demonstra como queries SQL **seguras** (LIMIT, projeção, filtros precoces) previnem consumo excessivo de recursos e possíveis crashes, enquanto queries **agressivas** podem travar o processo.

## Objetivo
Mostrar empiricamente que precauções de recursos **melhoram performance e estabilidade**, sem custo significativo.

## Metodologia

O projeto compara o desempenho de consultas SQL em um dataset real de aproximadamente 3 milhões de linhas (viagens de táxi amarelo em NYC – Janeiro/2023), utilizando o DuckDB como engine de processamento in-memory.

Para cada par de consultas, a versão **simples** representa uma abordagem direta, enquanto a versão **otimizada** incorpora boas práticas recomendadas para reduzir o consumo de recursos e melhorar a eficiência:

### Boas práticas aplicadas nas queries otimizadas

As queries otimizadas seguem três técnicas principais, aplicadas de forma consistente nos cinco testes:

- **Projeção de colunas**  
  Selecionar apenas as colunas necessárias (`SELECT col1, col2...`) em vez de `SELECT *`. Isso diminui significativamente a quantidade de dados lidos da memória e processados pelo engine.  Usada nos testes 1, 3 e 5 (preview, top valores e ordenamento).

- **Uso de LIMIT**  
  Restringir explicitamente o número de linhas retornadas, evitando que o engine processe o dataset inteiro quando o resultado final será parcial.  
  Aplicada nos testes 1 e 5.

- **Filtros precoces (early filtering)**  
  Aplicar a cláusula `WHERE` o mais cedo possível, antes de agregações ou ordenações, para reduzir o volume de linhas que entram nas operações mais custosas.  
  Usada nos testes 2 (filtro por data ≥ 15/01/2023) e 4 (filtro passenger_count ≥ 2).

Essas técnicas são especialmente eficazes em engines column-oriented como o DuckDB, que beneficiam-se da leitura seletiva de colunas e da redução precoce do volume de dados.

### Medições
- **Tempo de execução**: medido exclusivamente no processamento da query (sem I/O de rede ou leitura repetida do arquivo).
- **Consumo de memória**: variação (Δ) em MB durante a execução da query.
- Ambiente: Python + DuckDB + Streamlit (dataset carregado uma única vez em memória).

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

### live [streamlit]("https://luisturra-boas-praticas-sql-protegendo-rec-streamlit-app-5ohvtd.streamlit.app/")

## Resultados e Conclusões

Os testes foram executados em um dataset real de ~3 milhões de linhas (NYC Yellow Taxi – Janeiro/2023) usando DuckDB em memória.

**Observações principais:**

- Em **todos os casos**, a query otimizada apresentou **tempo de execução igual ou inferior** à query simples.
- O **consumo de memória** foi **consistentemente menor** ou igual nas queries otimizadas, com diferença drástica no caso ordenamento completo do dataset.
- O teste 5 demonstra o impacto mais significativo: a query simples consumiu **459.5 MB** adicionais e levou **1.29 segundos**, enquanto a otimizada usou apenas **0.7 MB** e executou em **0.01 segundos**.

**Conclusão geral:**  
Boas práticas de escrita de SQL não apenas protegem recursos, mas frequentemente **melhoram a performance**. Projeção de colunas, aplicação precoce de filtros e uso de LIMIT evitam processamento desnecessário, tornando as consultas mais eficientes e escaláveis em datasets grandes.

Esse comportamento é esperado em engines column-oriented como DuckDB, que beneficiam-se fortemente da redução de colunas e linhas processadas.