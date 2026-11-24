# Sistema Multiagente de Processamento e Validação de Faturas

Projeto académico para o Tema 5 de Agentes Inteligentes e Sistemas Multiagentes.

## O que faz
O sistema processa faturas em texto, extrai os campos principais, valida regras contabilísticas com Python, encaminha exceções para análise e produz um relatório e uma tabela CSV. Inclui três agentes (Extrator, Tratamento de Exceções e Reporter) e um validador determinístico separado.

## Requisitos
- Python 3.10 ou superior
- Dependências de `requirements.txt`
- Ollama instalado localmente para executar os agentes com IA, sem API paga

## Instalação
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Para usar IA gratuitamente, instale o Ollama em https://ollama.com/download e, no terminal, execute:
```bash
ollama pull llama3.2:3b
```
Copie `.env.example` para `.env`. O projeto comunica com o Ollama em `http://localhost:11434`; não é necessária chave API. O Ollama tem de estar em execução enquanto o projeto é utilizado. Se não quiser executar um modelo, defina `LLM_PROVIDER=none` para usar o parser local de demonstração. Nunca publique ficheiros `.env`.

## Executar
```bash
python main.py
```

O programa lê os ficheiros `data/invoices/*.txt` e cria:
- `outputs/results.json`: dados extraídos, validação e análise de exceções;
- `outputs/results.csv`: tabela final para análise;
- `outputs/accounting_report.md`: relatório para contabilidade;
- `logs/agent_messages.log`: registo da comunicação e execução dos componentes.

## Testes
```bash
python -m pytest
```

## Estrutura
```text
aism_invoice_project/
├── data/invoices/       # 10 faturas sintéticas de teste
├── src/
│   ├── agents/          # Extrator, exceções e reporter
│   ├── models.py        # Estruturas de dados
│   ├── validator.py     # Regras determinísticas
│   ├── pipeline.py      # Coordenação dos componentes
│   └── llm.py           # Integração opcional OpenAI
├── tests/               # Testes unitários
├── outputs/             # Resultados gerados
├── logs/                # Logs de execução
├── main.py
├── requirements.txt
└── .env.example
```

## Dados de teste
As dez faturas incluídas são dados sintéticos criados para este projeto, não documentos reais. Foram concebidas para testar faturas válidas, erro aritmético, imposto em falta, número duplicado, data inválida e divergência entre linhas e subtotal. Não representam um dataset público nem têm licença externa.

## Agentes e coordenação
1. **Agente 1 — Extrator:** converte texto em JSON estruturado. Usa o modelo local configurado no Ollama (por omissão, `llama3.2:3b`); não requer chave API. Se `LLM_PROVIDER=none`, usa o parser local limitado ao formato de exemplo.
2. **Validador Python:** verifica campos obrigatórios, formato da data, duplicados, soma das linhas e subtotal + imposto = total.
3. **Agente 2 — Tratamento de exceções:** só é chamado quando existem erros. Propõe análise/correções, mas não altera os valores extraídos automaticamente.
4. **Agente 3 — Reporter:** cria um resumo fiel ao estado da validação.

A comunicação entre os componentes é feita através de objetos Python/JSON. O logger regista as etapas em `logs/agent_messages.log`.

## Limitações
- O parser local só reconhece o formato textual definido nas faturas de demonstração.
- A validação aritmética usa uma tolerância de 0,02 EUR para arredondamentos.
- A deteção de duplicados é feita dentro de uma execução.
- A análise por LLM depende do modelo local, dos recursos do computador e da qualidade do texto.
- O sistema não substitui a aprovação de um contabilista. Casos ambíguos devem ser revistos por uma pessoa.

## Declaração de utilização de IA
O grupo utilizou o ChatGPT de forma limitada, exclusivamente como apoio à elaboração do ficheiro README.md e à identificação e correção de alguns erros técnicos que não conseguiu resolver autonomamente. A utilização de IA não substituiu o desenvolvimento realizados pelos elementos do grupo.

## Autoria
- Diogo Costa 
- Rodrigo Nogueira
- Ricardo Kanhoca
