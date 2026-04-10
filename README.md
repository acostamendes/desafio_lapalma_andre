> Repositório dedicado à criação da estrutura para um desafio técnico, com foco em conceitos de observabilidade e na abordagem mental do nosso novo colega de equipe, carinhosamente chamado de novo membro do conselho

# 🎲 Desafio SRE / Observabilidade - Dice API

Este projeto é uma evolução do repositório base [timelapalma/desafio](https://github.com/timelapalma/desafio). O objetivo foi subir a infraestrutura de telemetria e **otimizá-la para um cenário de operação real**, aplicando práticas de Engenharia de Confiabilidade e garantindo a rastreabilidade (Tracing) das requisições.

## 🏗️ Arquitetura e Stack
- **Aplicação:** Python/Flask com instrumentação nativa via OpenTelemetry (OTel).
- **Coletor Central:** OpenTelemetry Collector Contrib (Pipeline unificado).
- **Armazenamento:** Prometheus (Métricas) e Grafana Loki (Logs).
- **Visualização e Alertas:** Grafana.

## 🚀 Minhas Implementações e Melhorias

Ao analisar a arquitetura base, identifiquei oportunidades de otimização na extração de valor dos dados e no monitoramento:

1. **Structured Logging via OTLP:** Em vez de logs em texto plano que dependem de agentes de leitura de disco (I/O intensivo), a aplicação emite JSONs estruturados direto da memória para o Collector via rede. Isso garante que metadados críticos, como `trace_id` e `span_id`, não se percam.
2. **Query-Time Parsing com LogQL:** Para facilitar a vida da equipe de operações (On-call), os logs estruturados no Loki são visualizados no Grafana utilizando queries avançadas de LogQL. Através do comando `| json | line_format`, transformamos payloads complexos em linhas de leitura imediata (ex: `[ERROR] Trace: ID | Mensagem`)
3. **Chaos Engineering & Validação de SLOs:** Utilizei as rotas `/fail` (falha dura) e `/latest` (degradação/latência injetada) para validar a eficácia dos *Service Level Indicators (SLIs)*. Isso prova que o monitoramento é capaz de detectar anomalias de "cauda longa" (Percentil 99 - p99) que costumam ser mascaradas ao se olhar apenas para o tempo médio de resposta.
4. **Correção de Volumes Docker:** Ajuste na montagem de volumes e permissões do `docker-compose` para garantir a inicialização resiliente do OTel Collector.

## 🛠️ Como executar e testar
1. Suba a stack inteira: `docker compose -f 'observability/compose.yml' up -d --build`
2. Gere tráfego de sucesso: `curl http://localhost:5000/`
3. Simule um incidente de erro 500: `curl http://localhost:5000/fail`
4. Simule lentidão severa (teste de p99): `curl http://localhost:5000/latest`
5. Acesse o Grafana em `http://localhost:3000` (Explore > Loki) e utilize queries como `{service_name="dice-api"} | json | line_format "[{{.severity}}] Trace: {{.traceid}} | {{.body}}"` para explorar os dados.
6. Para finalizar: `docker compose -f 'observability/compose.yml' down`
