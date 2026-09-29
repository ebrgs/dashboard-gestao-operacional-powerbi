"""Gera dados demonstrativos e recompõe o projeto Power BI editável."""

from __future__ import annotations

import base64
import csv
import io
import json
import random
from datetime import date, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REPORT = ROOT / "Gestao_Operacional.Report"
MODEL = ROOT / "Gestao_Operacional.SemanticModel"
PAGE = "832a9227b8b74c7388d9"
VISUALS = REPORT / "definition" / "pages" / PAGE / "visuals"
SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json"
RNG = random.Random(20260928)


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def lit(value: str) -> dict:
    return {"expr": {"Literal": {"Value": value}}}


def color(value: str) -> dict:
    return {"solid": {"color": lit(f"'{value}'")}}


def prop(**values: dict) -> list[dict]:
    return [{"properties": values}]


def col(name: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Entity": "Operacao"}}, "Property": name}}


def measure(name: str) -> dict:
    return {"Measure": {"Expression": {"SourceRef": {"Entity": "Operacao"}}, "Property": name}}


def projection(field: dict, name: str) -> dict:
    return {"field": field, "queryRef": f"Operacao.{name}", "nativeQueryRef": name}


def visual(name: str, kind: str, x: int, y: int, width: int, height: int, z: int, **content: dict) -> None:
    value = {
        "$schema": SCHEMA,
        "name": name,
        "position": {"x": x, "y": y, "z": z, "width": width, "height": height, "tabOrder": z},
        "visual": {"visualType": kind, **content},
    }
    write_json(VISUALS / name / "visual.json", value)


def box(name: str, text: str, x: int, y: int, width: int, height: int, size: int, fg: str, z: int, bold: bool = False) -> None:
    style = {"fontFamily": "Segoe UI", "fontSize": f"{size}pt", "color": fg}
    if bold:
        style["fontWeight"] = "bold"
    visual(name, "textbox", x, y, width, height, z,
           objects={"general": prop(paragraphs=[{"textRuns": [{"value": text, "textStyle": style}]}])},
           visualContainerObjects={"background": prop(show=lit("false")),
                                   "border": prop(show=lit("false"))})


def rect(name: str, x: int, y: int, width: int, height: int, fill: str, z: int) -> None:
    visual(name, "shape", x, y, width, height, z,
           objects={
               "shape": [{"properties": {"tileShape": lit("'rectangle'")}, "selector": {"id": "default"}}],
               "fill": [{"properties": {"show": lit("true"), "fillColor": color(fill)}, "selector": {"id": "default"}}],
               "outline": [{"properties": {"show": lit("false")}, "selector": {"id": "default"}}],
           })


def chrome(title: str | None = None, bg: str = "#FFFFFF") -> dict:
    result = {
        "background": prop(show=lit("true"), color=color(bg), transparency=lit("0D")),
        "border": prop(show=lit("true"), color=color("#DCE5EB"), width=lit("1D"), radius=lit("8D")),
    }
    if title:
        result["title"] = prop(show=lit("true"), text=lit(f"'{title}'"),
                               fontSize=lit("11D"), fontColor=color("#203445"), bold=lit("true"))
    return result


def generate_rows() -> list[dict]:
    teams = ["Equipe A", "Equipe B", "Equipe C", "Equipe D"]
    services = ["Manutenção", "Instalação", "Inspeção", "Atendimento"]
    sites = ["Unidade Norte", "Unidade Centro", "Unidade Sul"]
    month_names = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]
    rows: list[dict] = []
    current = date(2025, 1, 1)
    end = date(2026, 8, 31)
    while current <= end:
        if current.weekday() < 5:
            for t, team in enumerate(teams):
                service = services[(current.toordinal() + t * 3) % len(services)]
                site = sites[(current.toordinal() // 7 + t) % len(sites)]
                employee = f"Funcionário {t * 4 + ((current.toordinal() // 3) % 4) + 1:02d}"
                season = 1 + 0.08 * (current.month in (3, 4, 8, 9))
                target = round(RNG.randint(54, 104) * season)
                team_factor = [0.99, 0.88, 1.06, 0.94][t]
                service_factor = {"Manutenção": 0.94, "Instalação": 0.90, "Inspeção": 1.07, "Atendimento": 1.02}[service]
                status_pick = RNG.random()
                status = "Concluído" if status_pick < 0.78 else ("Em andamento" if status_pick < 0.97 else "Pendente")
                realized = 0 if status == "Pendente" else max(1, round(target * team_factor * service_factor * RNG.uniform(0.82, 1.14)))
                if status == "Em andamento":
                    realized = round(realized * RNG.uniform(0.50, 0.85))
                regular = round(RNG.uniform(7.2, 8.5), 1) if status != "Pendente" else 0
                extra = (round(RNG.choice([0, 0, 0, 0.5, 1, 1.5, 2]) * (1.3 if target > 94 else 1), 1)
                         if status != "Pendente" else 0)
                rows.append({
                    "Data": current.isoformat(), "Mes": f"{month_names[current.month-1]}/{current:%y}", "Equipe": team,
                    "Serviço": service, "Meta": target, "Realizado": realized,
                    "Horas trabalhadas": regular, "Horas extras": extra, "Colaborador": employee,
                    "Local": site, "Status": status, "MesOrdem": current.year * 100 + current.month,
                })
        current += timedelta(days=1)
    return rows


def build_data_and_model() -> tuple[list[dict], bytes]:
    rows = generate_rows()
    fields = list(rows[0])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    csv_bytes = stream.getvalue().encode("utf-8")
    data_file = ROOT / "dados" / "operacao_ficticia.csv"
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_bytes(csv_bytes)

    encoded = base64.b64encode(csv_bytes).decode("ascii")
    m = [
        "let",
        f'    Fonte = Csv.Document(Binary.FromText("{encoded}", BinaryEncoding.Base64), [Delimiter=",", Columns=12, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        '    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),',
        '    Tipos = Table.TransformColumnTypes(Cabecalhos, {{"Data", type date}, {"Mes", type text}, {"Equipe", type text}, {"Serviço", type text}, {"Meta", Int64.Type}, {"Realizado", Int64.Type}, {"Horas trabalhadas", type number}, {"Horas extras", type number}, {"Colaborador", type text}, {"Local", type text}, {"Status", type text}, {"MesOrdem", Int64.Type}}, "en-US")',
        "in",
        "    Tipos",
    ]
    columns = []
    for name, dtype in [("Data", "dateTime"), ("Mes", "string"), ("Equipe", "string"),
                        ("Serviço", "string"), ("Meta", "int64"), ("Realizado", "int64"),
                        ("Horas trabalhadas", "double"), ("Horas extras", "double"),
                        ("Colaborador", "string"), ("Local", "string"), ("Status", "string"),
                        ("MesOrdem", "int64")]:
        item = {"name": name, "dataType": dtype, "sourceColumn": name, "summarizeBy": "none"}
        if name == "Data":
            item["formatString"] = "dd/MM/yyyy"
        elif name == "Mes":
            item["sortByColumn"] = "MesOrdem"
        elif name == "MesOrdem":
            item["isHidden"] = True
        elif name in ("Horas trabalhadas", "Horas extras"):
            item["formatString"] = "0.0"
        columns.append(item)

    metric_defs = [
        ("Realizado total", "SUM('Operacao'[Realizado])", "#,##0"),
        ("Meta total", "SUM('Operacao'[Meta])", "#,##0"),
        ("Cumprimento da meta", "DIVIDE([Realizado total], [Meta total], 0)", "0.0%"),
        ("Horas extras totais", "SUM('Operacao'[Horas extras])", "#,##0.0"),
        ("Horas totais", "SUM('Operacao'[Horas trabalhadas]) + [Horas extras totais]", "#,##0.0"),
        ("Produtividade por hora", "DIVIDE([Realizado total], [Horas totais], 0)", "0.0"),
    ]
    measures = [{"name": name, "expression": expr, "formatString": fmt,
                 "displayFolder": "Indicadores"} for name, expr, fmt in metric_defs]
    model = {
        "compatibilityLevel": 1601,
        "model": {
            "culture": "pt-BR", "sourceQueryCulture": "en-US",
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "discourageImplicitMeasures": True,
            "dataAccessOptions": {"legacyRedirects": True, "returnErrorValuesAsNull": True},
            "tables": [{"name": "Operacao", "columns": columns, "measures": measures,
                        "partitions": [{"name": "Operacao", "mode": "import",
                                        "source": {"type": "m", "expression": m}}]}],
        },
    }
    write_json(MODEL / "model.bim", model)
    write_json(MODEL / "definition.pbism", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2", "settings": {"qnaEnabled": False},
    })
    return rows, csv_bytes


def build_visuals() -> None:
    rect("header_background", 0, 0, 1280, 85, "#142C3F", 0)
    rect("header_accent", 0, 0, 8, 85, "#31B9A3", 1)
    box("dashboard_title", "GESTÃO OPERACIONAL", 28, 2, 650, 46, 18, "#FFFFFF", 2, True)
    box("dashboard_subtitle", "Produtividade, execução e desempenho  •  dados fictícios", 29, 46, 730, 34, 10, "#BED2DF", 3)
    box("dashboard_period", "JAN 2025  —  AGO 2026", 998, 24, 265, 34, 10, "#D9E8EF", 4, True)

    slicers = [("filter_period", "Período", "Data", "Between", 28),
               ("filter_team", "Equipe", "Equipe", "Dropdown", 338),
               ("filter_service", "Serviço", "Serviço", "Dropdown", 648),
               ("filter_site", "Local", "Local", "Dropdown", 958)]
    for idx, (name, title, field, mode, x) in enumerate(slicers):
        visual(name, "slicer", x, 94, 294, 77, 10 + idx,
               query={"queryState": {"Values": {"projections": [projection(col(field), field)]}}},
               objects={
                   "data": prop(mode=lit(f"'{mode}'")),
                   "header": prop(show=lit("true"), text=lit(f"'{title}'"), bold=lit("true"),
                                  fontColor=color("#203445"), textSize=lit("10D")),
               }, visualContainerObjects=chrome())

    cards = [
        ("kpi_realizado", "Realizado", "Realizado total", "#1E887B"),
        ("kpi_meta", "Meta", "Meta total", "#284E71"),
        ("kpi_cumprimento", "% de cumprimento", "Cumprimento da meta", "#1E887B"),
        ("kpi_produtividade", "Produtividade (unid./h)", "Produtividade por hora", "#284E71"),
        ("kpi_extras", "Horas extras", "Horas extras totais", "#B16A2D"),
    ]
    for idx, (name, label, metric, tint) in enumerate(cards):
        x = 28 + idx * 246
        visual(name, "cardVisual", x, 189, 230, 115, 20 + idx,
               query={"queryState": {"Data": {"projections": [projection(measure(metric), metric)]}}},
               objects={
                   "value": [{"properties": {"fontSize": lit("27D"), "bold": lit("true"),
                                              "labelDisplayUnits": lit("1D"),
                                              "fontColor": color(tint)}, "selector": {"id": "default"}}],
                   "label": [{"properties": {"text": lit(f"'{label}'"), "fontSize": lit("10D"),
                                              "fontColor": color("#5A6F7E"),
                                              "position": lit("'aboveValue'")}, "selector": {"id": "default"}}],
               }, visualContainerObjects=chrome())

    charts = [
        ("trend_monthly", "Evolução mensal", "lineChart", "Mes", ["Realizado total", "Meta total"], 28, 321),
        ("target_vs_actual", "Meta x realizado por equipe", "clusteredColumnChart", "Equipe", ["Realizado total", "Meta total"], 648, 321),
        ("team_performance", "Desempenho por equipe", "clusteredBarChart", "Equipe", ["Cumprimento da meta"], 28, 514),
        ("service_mix", "Distribuição por serviço", "donutChart", "Serviço", ["Realizado total"], 648, 514),
    ]
    for idx, (name, title, kind, category, metrics, x, y) in enumerate(charts):
        chart_objects = ({"categoryAxis": prop(showAxisTitle=lit("false"), fontSize=lit("8D")),
                          "valueAxis": prop(showAxisTitle=lit("false"))}
                         if kind != "donutChart" else {})
        visual(name, kind, x, y, 604, 185, 40 + idx,
               query={"queryState": {
                   "Category": {"projections": [projection(col(category), category)]},
                   "Y": {"projections": [projection(measure(metric), metric) for metric in metrics]},
               }}, objects=chart_objects,
               visualContainerObjects=chrome(title))


def build_theme() -> None:
    file_name = "GestaoOperacional-20260928.json"
    write_json(REPORT / "StaticResources" / "RegisteredResources" / file_name, {
        "name": file_name,
        "dataColors": ["#1E887B", "#92AFC3", "#D9A15B", "#284E71", "#8AA5B9"],
        "background": "#FFFFFF", "foreground": "#203445", "tableAccent": "#1E887B",
        "textClasses": {
            "title": {"fontFace": "Segoe UI Semibold", "fontSize": 12, "color": "#203445"},
            "label": {"fontFace": "Segoe UI", "fontSize": 10, "color": "#6E8090"},
        },
    })
    report_path = REPORT / "definition" / "report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    base = report["themeCollection"]["baseTheme"]
    report["themeCollection"]["customTheme"] = {
        "name": file_name,
        "reportVersionAtImport": base["reportVersionAtImport"],
        "type": "RegisteredResources",
    }
    report["resourcePackages"] = [package for package in report["resourcePackages"]
                                  if package["name"] != "RegisteredResources"]
    report["resourcePackages"].append({
        "name": "RegisteredResources", "type": "RegisteredResources",
        "items": [{"name": file_name, "path": file_name, "type": "CustomTheme"}],
    })
    report["settings"]["locale"] = "pt-BR"
    write_json(report_path, report)


def build_preview(rows: list[dict]) -> None:
    columns = ("Data", "Mes", "Equipe", "Serviço", "Meta", "Realizado",
               "Horas trabalhadas", "Horas extras", "Local")
    packed = [[row[key] for key in columns] for row in rows]
    template = (ROOT / "preview.template.html").read_text(encoding="utf-8")
    html = template.replace("__DATA__", json.dumps(packed, ensure_ascii=False, separators=(",", ":")))
    (ROOT / "previsualizacao.html").write_text(html, encoding="utf-8")


def main() -> None:
    rows, csv_bytes = build_data_and_model()
    build_visuals()
    build_theme()
    build_preview(rows)
    print(f"Gerados {len(rows)} registros; CSV com {len(csv_bytes):,} bytes.")
    print(f"Realizado: {sum(int(r['Realizado']) for r in rows):,}")
    print(f"Meta: {sum(int(r['Meta']) for r in rows):,}")


if __name__ == "__main__":
    main()
