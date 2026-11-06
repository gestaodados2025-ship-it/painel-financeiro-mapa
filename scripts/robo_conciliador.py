import pandas as pd
import requests
import json
import re
from datetime import datetime
from pathlib import Path

UGS_PRINCIPAIS = ["130010", "130141", "130255", "135098", "420013"]

URLS_EXE_2026 = {
    "EXE_PADRAO": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFcFQpuXUjut17Ftj89ugQvu-eK-ZPI7a90FoPOnhcvXFSL2ymU-WOPiYwBT8qa8tzCeyo05q_YanW/pub?gid=1204904051&single=true&output=csv",
    "EXE_MDIR": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFcFQpuXUjut17Ftj89ugQvu-eK-ZPI7a90FoPOnhcvXFSL2ymU-WOPiYwBT8qa8tzCeyo05q_YanW/pub?gid=32904262&single=true&output=csv"
}

URLS_RAP_2026 = {
    "20ZV": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1255285299&single=true&output=csv",
    "20ZY": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1626303078&single=true&output=csv",
    "2000": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1251866406&single=true&output=csv",
    "215A": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=2071147261&single=true&output=csv",
    "2161": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=240279963&single=true&output=csv",
    "214Z": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=557514819&single=true&output=csv",
    "21B6": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=238112304&single=true&output=csv",
    "8593": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=296590604&single=true&output=csv",
    "8622": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1039014086&single=true&output=csv",
    "00PN": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1888642019&single=true&output=csv",
    "8606": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1419215442&single=true&output=csv",
    "OUTRAS": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=132081842&single=true&output=csv"
}

ORDEM_MESES = {
    "JAN/2026": 1, "FEV/2026": 2, "MAR/2026": 3, "ABR/2026": 4,
    "MAI/2026": 5, "JUN/2026": 6, "JUL/2026": 7, "AGO/2026": 8,
    "SET/2026": 9, "OUT/2026": 10, "NOV/2026": 11, "DEZ/2026": 12
}

def br_to_float(val):
    if pd.isna(val):
        return 0.0
    s = str(val).strip().replace("R$", "").replace(" ", "")
    if not s or s in ["'-8", "'-9", "NAO SE APLICA", "-"]:
        return 0.0
    s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return 0.0

def extrair_ne_curta(ne_ccor):
    if pd.isna(ne_ccor):
        return ""
    m = re.search(r"(\d{4}NE\d{6})", str(ne_ccor).upper())
    return m.group(1) if m else str(ne_ccor).strip()

def ler_aba_tesouro(url, origem):
    try:
        df_raw = pd.read_csv(url, header=None, dtype=str, on_bad_lines="skip")
        header_idx = 0
        for idx, row in df_raw.head(15).iterrows():
            linha_str = " ".join(row.dropna().astype(str)).upper()
            if "ANO LAN" in linha_str or "UG EXECUTORA" in linha_str or "NE CCOR" in linha_str:
                header_idx = idx
                break
        df = pd.read_csv(url, skiprows=header_idx, dtype=str, on_bad_lines="skip")
        df["ORIGEM_ABA"] = origem
        return df
    except Exception as e:
        print(f"[AVISO] Erro ao ler {origem}: {e}")
        return pd.DataFrame()

def processar_planilhas():
    dfs_exe = [ler_aba_tesouro(url, nome) for nome, url in URLS_EXE_2026.items()]
    df_exe = pd.concat(dfs_exe, ignore_index=True)

    dfs_rap = [ler_aba_tesouro(url, f"RAP_{nome}") for nome, url in URLS_RAP_2026.items()]
    df_rap = pd.concat(dfs_rap, ignore_index=True)

    empenhos_consolidados = {}
    evolucao_mensal = {}

    if not df_exe.empty and "NE CCor" in df_exe.columns:
        df_exe["MES_ORDEM"] = df_exe["Mês Lançamento"].str.strip().str.upper().map(ORDEM_MESES).fillna(0).astype(int)
        df_exe = df_exe[df_exe["MES_ORDEM"] > 0]

        cols_chave = [c for c in ["Mês Lançamento", "UG Executora", "PTRES", "Plano Orçamentário", "PI", "Natureza Despesa Detalhada", "NE CCor"] if c in df_exe.columns]
        df_exe = df_exe.drop_duplicates(subset=cols_chave, keep="first")

        for col_val in ["DESPESAS EMPENHADAS (CONTROLE EMPENHO)", "DESPESAS EMPENHADAS A LIQUIDAR (CONTROLE EMP)", "DESPESAS LIQUIDADAS A PAGAR(CONTROLE EMPENHO)", "DESPESAS PAGAS (CONTROLE EMPENHO)"]:
            if col_val in df_exe.columns:
                df_exe[col_val] = df_exe[col_val].apply(br_to_float)
            else:
                df_exe[col_val] = 0.0

        df_exe = df_exe.sort_values("MES_ORDEM")
        for ne_ccor, grupo in df_exe.groupby("NE CCor"):
            ne_str = str(ne_ccor).strip()
            if not ne_str or ne_str in ["'-8", "'-9", "NAO SE APLICA"]:
                continue

            pago_anterior = 0.0
            for _, row in grupo.iterrows():
                mes = str(row.get("Mês Lançamento", "")).strip().upper()
                pago_acum = row["DESPESAS PAGAS (CONTROLE EMPENHO)"]
                movimento_mes = max(0.0, pago_acum - pago_anterior)
                pago_anterior = pago_acum

                evolucao_mensal.setdefault(mes, {"EXE_PAGO_MES": 0.0, "RAP_PAGO_MES": 0.0})
                evolucao_mensal[mes]["EXE_PAGO_MES"] += movimento_mes

            ult = grupo.iloc[-1]
            empenhos_consolidados[ne_str] = {
                "tipo_recurso": "EXE001 (Exercicio 2026)",
                "ne_ccor": ne_str,
                "ne_curta": extrair_ne_curta(ne_str),
                "mes_referencia": ult.get("Mês Lançamento", ""),
                "ug_executora": ult.get("UG Executora", ""),
                "acao": ult.get("Ação Governo", ""),
                "ptres": ult.get("PTRES", ""),
                "favorecido": ult.get("NE CCor - Favorecido", ""),
                "processo": ult.get("NE - Núm. Processo", ""),
                "contrato_planilha": ult.get("Contrato", ""),
                "departamento": ult.get("DEPARTAMENTO", ""),
                "empenhado": round(ult["DESPESAS EMPENHADAS (CONTROLE EMPENHO)"], 2),
                "a_liquidar": round(ult["DESPESAS EMPENHADAS A LIQUIDAR (CONTROLE EMP)"], 2),
                "liquidado_a_pagar": round(ult["DESPESAS LIQUIDADAS A PAGAR(CONTROLE EMPENHO)"], 2),
                "pago_acumulado": round(ult["DESPESAS PAGAS (CONTROLE EMPENHO)"], 2)
            }

    if not df_rap.empty and "NE CCor" in df_rap.columns:
        df_rap["MES_ORDEM"] = df_rap["Mês Lançamento"].str.strip().str.upper().map(ORDEM_MESES).fillna(0).astype(int)
        df_rap = df_rap[df_rap["MES_ORDEM"] > 0]

        cols_rap_val = [
            "RESTOS A PAGAR PROCESSADOS A PAGAR",
            "RESTOS A PAGAR NAO PROCESSADOS A LIQUIDAR",
            "RESTOS A PAGAR NAO PROCESSADOS A PAGAR",
            "RESTOS A PAGAR PROCESSADOS PAGOS",
            "RESTOS A PAGAR NAO PROCESSADOS PAGOS"
        ]
        for col_val in cols_rap_val:
            if col_val in df_rap.columns:
                df_rap[col_val] = df_rap[col_val].apply(br_to_float)
            else:
                df_rap[col_val] = 0.0

        df_rap = df_rap.sort_values("MES_ORDEM")
        for ne_ccor, grupo in df_rap.groupby("NE CCor"):
            ne_str = str(ne_ccor).strip()
            if not ne_str or ne_str in ["'-8", "'-9", "NAO SE APLICA"]:
                continue

            pago_anterior = 0.0
            for _, row in grupo.iterrows():
                mes = str(row.get("Mês Lançamento", "")).strip().upper()
                pago_acum = row["RESTOS A PAGAR PROCESSADOS PAGOS"] + row["RESTOS A PAGAR NAO PROCESSADOS PAGOS"]
                movimento_mes = max(0.0, pago_acum - pago_anterior)
                pago_anterior = pago_acum

                evolucao_mensal.setdefault(mes, {"EXE_PAGO_MES": 0.0, "RAP_PAGO_MES": 0.0})
                evolucao_mensal[mes]["RAP_PAGO_MES"] += movimento_mes

            ult = grupo.iloc[-1]
            a_pagar_total = ult["RESTOS A PAGAR PROCESSADOS A PAGAR"] + ult["RESTOS A PAGAR NAO PROCESSADOS A PAGAR"]
            pago_total = ult["RESTOS A PAGAR PROCESSADOS PAGOS"] + ult["RESTOS A PAGAR NAO PROCESSADOS PAGOS"]

            empenhos_consolidados[ne_str] = {
                "tipo_recurso": f"RAP001 ({ult.get('ORIGEM_ABA', 'RAP')})",
                "ne_ccor": ne_str,
                "ne_curta": extrair_ne_curta(ne_str),
                "mes_referencia": ult.get("Mês Lançamento", ""),
                "ug_executora": ult.get("UG Executora", ""),
                "acao": ult.get("Ação Governo", ""),
                "ptres": ult.get("PI", ""),
                "favorecido": ult.get("NE CCor - Favorecido", ""),
                "processo": ult.get("NE - Núm. Processo", ""),
                "contrato_planilha": ult.get("Contrato", ""),
                "departamento": ult.get("DEPARTAMENTO", ""),
                "empenhado": round(a_pagar_total + pago_total + ult["RESTOS A PAGAR NAO PROCESSADOS A LIQUIDAR"], 2),
                "a_liquidar": round(ult["RESTOS A PAGAR NAO PROCESSADOS A LIQUIDAR"], 2),
                "liquidado_a_pagar": round(a_pagar_total, 2),
                "pago_acumulado": round(pago_total, 2)
            }

    return list(empenhos_consolidados.values()), evolucao_mensal

def buscar_contratos_vigentes():
    contratos_vigentes = []
    hoje = datetime.now().strftime("%Y-%m-%d")
    for ug in UGS_PRINCIPAIS:
        url = f"https://contratos.comprasnet.gov.br/api/contrato/ug/{ug}"
        try:
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                for c in r.json():
                    vig_fim = str(c.get("vigencia_fim") or "")
                    if not vig_fim or vig_fim >= hoje:
                        contratos_vigentes.append({
                            "ug": ug,
                            "numero": c.get("numero", ""),
                            "processo": c.get("processo", ""),
                            "fornecedor": c.get("fornecedor", {}).get("nome", "") if isinstance(c.get("fornecedor"), dict) else str(c.get("fornecedor", "")),
                            "objeto": c.get("objeto", ""),
                            "vigencia_fim": vig_fim,
                            "valor_global": c.get("valor_global", 0)
                        })
        except Exception as e:
            print(f"[AVISO] API Contratos UG {ug}: {e}")
    return contratos_vigentes

def buscar_parcerias_transferegov():
    parcerias = []
    ugs_filtro = ",".join(UGS_PRINCIPAIS)
    url = f"https://api-publica.transferegov.gestao.gov.br/discricionarias/instrumento?ug_emitente=in.({ugs_filtro})&limit=500"
    try:
        r = requests.get(url, timeout=25)
        if r.status_code == 200:
            for p in r.json():
                sit = str(p.get("situacao", "")).upper()
                if "EXECU" in sit or "VIGENTE" in sit or "ASSINADO" in sit:
                    parcerias.append({
                        "ug": p.get("ug_emitente", ""),
                        "instrumento": p.get("nr_instrumento", ""),
                        "modalidade": p.get("modalidade", "Parceria"),
                        "processo": p.get("nr_processo", ""),
                        "proponente": p.get("nm_proponente", ""),
                        "situacao": p.get("situacao", ""),
                        "valor_global": p.get("vl_global", 0)
                    })
    except Exception as e:
        print(f"[AVISO] API Transferegov: {e}")
    return parcerias

if __name__ == "__main__":
    print("Processando planilhas EXE 2026 e RAP 2026...")
    empenhos, evolucao = processar_planilhas()
    print(f"Total de Notas de Empenho consolidadas: {len(empenhos)}")

    contratos = buscar_contratos_vigentes()
    parcerias = buscar_parcerias_transferegov()

    saida = {
        "atualizado_em": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "ugs_monitoradas": UGS_PRINCIPAIS,
        "evolucao_mensal": evolucao,
        "empenhos_tesouro": empenhos,
        "contratos_vigentes": contratos,
        "parcerias_vigentes": parcerias
    }

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    with open("data/processed/dados_painel.json", "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    print("Arquivo data/processed/dados_painel.json gerado com sucesso!")
