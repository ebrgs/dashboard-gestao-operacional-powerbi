# Dashboard de Gestão Operacional em Power BI

Projeto de portfólio com cenário e dados **100% fictícios**. O relatório acompanha produção, cumprimento de metas, produtividade e horas extras de quatro equipes em três unidades.

## Abrir o projeto

1. Abra [Gestao_Operacional.pbip](Gestao_Operacional.pbip) no Power BI Desktop.
2. Se o Desktop solicitar, habilite o formato de relatório aprimorado **PBIR** nas opções de recursos de visualização.
3. Clique em **Atualizar** para carregar os dados no modelo. O arquivo de cache de dados do Desktop não faz parte deste projeto.

O modelo usa uma cópia da base CSV incorporada ao código M. Por isso, o projeto pode ser movido de pasta sem quebrar o caminho da fonte. Para alterar os dados de demonstração, edite o gerador e execute `python gerar_projeto.py`; depois atualize o relatório no Desktop.

## Entregas

| Arquivo | Uso |
| --- | --- |
| `Gestao_Operacional.pbip` | Entrada do projeto editável no Power BI Desktop |
| `Gestao_Operacional.Report/` | Página, visuais, filtros e tema PBIR |
| `Gestao_Operacional.SemanticModel/` | Modelo tabular TMSL com medidas DAX |
| `dados/operacao_ficticia.csv` | Base fictícia em UTF-8 |
| `dashboard-powerbi.png` | Captura da página renderizada no Power BI Desktop |
| `previsualizacao.html` | Prévia interativa independente do Power BI |
| `previsualizacao.png` | Imagem da prévia para apresentação do portfólio |
| `gerar_projeto.py` | Recria os dados, o modelo, os visuais e a prévia |

## Conteúdo do dashboard

- **KPIs:** realizado, meta, cumprimento da meta, produtividade por hora e horas extras.
- **Gráficos:** evolução mensal, meta x realizado por equipe, desempenho por equipe e distribuição por serviço.
- **Filtros:** período, equipe, serviço e local.
- **Tema:** azul petróleo, verde e tons neutros, com layout 16:9.

## Base e regras

A base possui **1.736 registros** entre **01/01/2025 e 31/08/2026**, somente em dias úteis. Cada registro representa a operação diária de uma equipe, com um colaborador, serviço e unidade. Há quatro equipes, quatro tipos de serviço, três unidades e 16 colaboradores fictícios.

| Indicador | Cálculo |
| --- | --- |
| Realizado | Soma de `Realizado` |
| Meta | Soma de `Meta` |
| Cumprimento | Realizado ÷ Meta |
| Horas extras | Soma de `Horas extras` |
| Produtividade | Realizado ÷ (horas trabalhadas + horas extras) |

O campo `Status` indica a situação da atividade (`Concluído`, `Em andamento` ou `Pendente`). Atividades pendentes têm realizado e horas iguais a zero, mas mantêm a meta planejada. Todas as medidas respeitam os filtros do relatório.

## Validação

Os arquivos PBIR foram validados com `powerbi-report-author validate`: **0 erros e 0 avisos**. O projeto foi aberto no **Power BI Desktop**, atualizado e conferido visualmente. Os cinco indicadores e os quatro gráficos carregaram com os dados esperados. A captura nativa está em `dashboard-powerbi.png`; a prévia HTML também foi aberta no Microsoft Edge.

O arquivo entregue é um projeto **PBIP**, que preserva os visuais e o modelo em arquivos editáveis. Caso prefira um único arquivo `.pbix`, abra o projeto no Desktop, atualize os dados e use **Arquivo > Salvar como > Arquivo do Power BI (.pbix)**.

Referências de formato: [projetos PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview), [relatório PBIR](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report) e [modelo semântico](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset).
