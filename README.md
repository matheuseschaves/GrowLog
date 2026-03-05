# 🌿 GrowLog — App Desktop de Cultivo

App desktop em Python + PyQt6 para monitoramento de cultivo.

## Estrutura do Projeto

```
GrowLogPC/
├── main.py                 # Ponto de entrada — roda aqui
├── requirements.txt        # Dependências
├── growlog.db              # Banco SQLite (criado automaticamente)
│
├── database/
│   └── models.py           # Modelos do banco (Plant, Log, Task)
│
├── ui/
│   ├── theme.py            # Tema escuro (QSS)
│   └── widgets.py          # Componentes reutilizáveis + diálogos
│
└── views/
    ├── dashboard.py        # Tela dashboard
    ├── plants.py           # Tela de plantas
    ├── history.py          # Tela de histórico/logs
    └── calendar_view.py    # Tela de calendário
```

## Como Rodar

### 1. Ative o ambiente virtual

```bash
venv\Scripts\activate
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Execute

```bash
cd GrowLogPC
python main.py
```

## Funcionalidades

- **Dashboard** — visão geral com cards de stats, tabela de plantas e atividade recente
- **Plantas** — cadastro completo com strain, fase, meio, ambiente e data de início
- **Registros** — rega (volume, pH, EC, runoff), nutrição (produto, dose) e anotações livres
- **Calendário** — tarefas agendadas com destaque visual por status (pendente/atrasada/concluída)
- **Histórico** — todos os registros com filtro por planta
- **Sidebar** — navegação lateral moderna com tema escuro
