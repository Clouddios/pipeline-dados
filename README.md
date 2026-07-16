# Pipeline de Importação de Dados

## Sobre o projeto

Este é um projeto de consolidação backend. A ideia não é acumular tecnologias novas — é aprofundar o que já é meu ponto forte, **Python + SQL**, construindo um sistema com mentalidade de produção de verdade, não um tutorial.

**O que o sistema faz:** recebe arquivos (CSV) de importação de dados, valida cada linha, processa em background sem perder nem duplicar registros mesmo quando algo falha no meio, e expõe visibilidade sobre o que está acontecendo — quantos arquivos foram processados, quais falharam, e por quê.

**Por que esse projeto e não outro:** um pipeline de importação explora diretamente minha base mais forte (SQL) e, ao mesmo tempo, comporta naturalmente os conceitos que separam um pleno de um júnior: transações, idempotência, retry, dead-letter, multi-tenancy e observabilidade — sem precisar aprender uma linguagem nova pra isso.

**Critério de sucesso:** não é terminar rápido. É conseguir explicar cada decisão do sistema numa conversa técnica, sem depender de anotação.

## Stack

- **API:** FastAPI + Pydantic
- **Banco:** PostgreSQL via SQLAlchemy
- **Fila/cache:** Redis (RQ ou Celery a partir da Semana 6)
- **Infra local:** Docker + docker-compose
- **Testes:** pytest (a partir da Semana 15-16)

## Como rodar localmente

```bash
docker-compose up -d          # sobe Postgres e Redis
python3 -m venv venv
source venv/Scripts/activate  # Windows/Git Bash — no Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health`
Documentação interativa: `http://localhost:8000/docs`

---

## Roteiro do projeto

O projeto é construído em 7 fases ao longo de 16 semanas (~10h/semana). Cada fase tem um propósito específico — a ordem não é arbitrária, cada uma constrói em cima da anterior.

### ✅ Fase 1 — Fundamentos (Semanas 1-2) — Concluída

**Por que essa fase existe:** antes de codar o pipeline, era preciso fechar as lacunas que apareceriam toda hora depois — não como teoria abstrata, mas como prática que seria usada já na fase seguinte.

**O que foi construído:** API FastAPI conectada ao PostgreSQL via SQLAlchemy, rodando em Docker junto com Redis. Sem endpoints de negócio ainda — só os experimentos que validam os fundamentos abaixo.

**O que aprendi de verdade:**

- **Transação é tudo-ou-nada.** Testado na prática: um `INSERT` que quebra no meio de um lote desfaz *todos* os registros daquela transação, mesmo os que estavam corretos. Por isso o pipeline processa **uma linha por transação**, não o arquivo inteiro de uma vez — erro numa linha não pode derrubar as outras 499.
- **Índice acelera busca, mas tem custo.** Medido com `EXPLAIN ANALYZE` em 50 mil registros: busca por coluna de alta cardinalidade (`filename`, praticamente único por linha) caiu de 3.7ms (`Seq Scan`, examinando a tabela inteira) para 0.056ms (`Index Scan`) — **~66x mais rápido**. Já em coluna de baixa cardinalidade (`status`, só 4 valores possíveis), o ganho foi bem menor (`Bitmap Heap Scan`, ~2ms) porque o resultado ainda cobre uma fatia grande da tabela. Índice não é "sempre bom" — tem custo de espaço e deixa todo `INSERT`/`UPDATE` mais lento, então só faz sentido em colunas realmente consultadas com frequência (`WHERE`/`JOIN`/`ORDER BY`) e de alta seletividade.
- **Idempotência não é sobre impedir reprocessamento — é sobre reprocessar sem quebrar nada.** Construída com três peças juntas: constraint `UNIQUE` (impede duplicata no nível do banco, não só no código), upsert (`ON CONFLICT ... DO UPDATE`, decide o que fazer quando a chave já existe) e um campo `atualizado_em` (metadado pode mudar a cada execução — o que não pode mudar é o dado de negócio, tipo o valor de uma venda, de forma inconsistente).

---

### ⬜ Fase 2 — MVP do pipeline (Semanas 3-5) — Em andamento

**Por que essa fase existe:** é o coração do projeto — a primeira versão do pipeline que já funciona de ponta a ponta, sem fila e sem distribuído ainda. O objetivo é acertar o "caminho feliz" bem feito antes de adicionar complexidade.

**O que vai ser construído:** endpoint de upload de arquivo CSV, parsing em streaming (sem carregar tudo na memória), validação linha a linha com Pydantic, gravação em lote no banco, e um relatório final de quantas linhas entraram e quantas falharam (e por quê).

**Critério de pronto:** subir um CSV de 50 mil linhas com algumas propositalmente quebradas, e o sistema processar as boas, reportar as ruins com o motivo exato, sem travar nem estourar memória.

**Execução:** *(a preencher conforme a fase avança)*

---

### ⬜ Fase 3 — Processamento confiável em background (Semanas 6-8)

**Por que essa fase existe:** é a peça que mais separa "script" de "sistema" — processar em background e garantir que nada se perde nem duplica quando algo falha no meio.

**O que vai ser construído:** processamento assíncrono via fila (RQ ou Celery + Redis), retry com backoff exponencial, dead-letter queue para jobs que falham repetidamente, e idempotência real a nível de arquivo inteiro (não só de linha).

**Critério de pronto:** derrubar o worker no meio do processamento de um arquivo grande, subir de novo, e o sistema retomar sem perder nem duplicar dado.

**Execução:** *(a preencher conforme a fase avança)*

---

### ⬜ Fase 4 — Visibilidade: painel e observabilidade (Semanas 9-10)

**Por que essa fase existe:** um sistema que ninguém consegue olhar por dentro é um sistema que ninguém confia.

**O que vai ser construído:** painel funcional simples mostrando arquivos em processamento/concluídos/com erro, detalhe de falhas por linha, opção de reprocessar, logging estruturado (JSON) e métricas básicas (tempo médio de processamento, taxa de erro, tamanho da fila).

**Critério de pronto:** olhar o painel e saber exatamente o que está acontecendo no sistema agora, sem consultar o banco direto.

**Execução:** *(a preencher conforme a fase avança)*

---

### ⬜ Fase 5 — Multi-tenant e API séria (Semanas 11-12)

**Por que essa fase existe:** multi-tenancy é um sinal forte de senioridade em entrevista, e faz sentido natural aqui — cada empresa/cliente sobe seus próprios arquivos, sem ver os dos outros.

**O que vai ser construído:** conceito de tenant no modelo de dados, autenticação via JWT, isolamento de dados testado ativamente entre tenants, rate limiting básico (token bucket).

**Critério de pronto:** provar, com teste (não só "acho que sim"), que um tenant nunca vê dado de outro.

**Execução:** *(a preencher conforme a fase avança)*

---

### ⬜ Fase 6 — Primeiro passo pro distribuído (Semanas 13-14)

**Por que essa fase existe:** o conceito central de "microsserviços orientados a eventos", introduzido com calma, sem trocar de linguagem nem inventar complexidade desnecessária.

**O que vai ser construído:** separação em 2 serviços (API + Worker) comunicando via fila/eventos, correlation ID propagado entre os dois pra rastrear o caminho completo de uma requisição.

**Critério de pronto:** seguir, só pelos logs, o caminho completo de um arquivo desde o upload até o resultado final, passando pelos dois serviços.

**Execução:** *(a preencher conforme a fase avança)*

---

### ⬜ Fase 7 — Mentalidade de produção (Semanas 15-16)

**Por que essa fase existe:** é o que fecha o portfólio e mostra pensamento de produção, não de tutorial.

**O que vai ser construído:** testes automatizados, CI (GitHub Actions), `docker-compose` unificado, diagrama de arquitetura, ADRs documentando as decisões tomadas ao longo do projeto, e um post técnico final.

**Critério de pronto:** alguém abrir o repositório e entender o sistema e o porquê das decisões em menos de 5 minutos.

**Execução:** *(a preencher conforme a fase avança)*

---

## Princípio-guia

> A meta não é acumular tecnologia — é sair no fim conseguindo explicar cada peça do sistema com segurança, numa conversa, sem depender de anotação. Profundidade em Python + SQL vale mais, nesse momento da carreira, do que amplitude em várias stacks.

## E depois?

Ao fechar as 16 semanas, os próximos passos naturais (não agora, só no radar):
- Evoluir o pipeline pra um cenário mais distribuído de verdade (3+ serviços, schema registry, saga pattern), reaproveitando tudo que já foi aprendido aqui.
- Só então, se fizer sentido pro objetivo de carreira, considerar uma stack nova (Go, ou PHP/Laravel se mirar vagas específicas) — como ampliação, não como base.
