<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Coordenação Financeira SDR/MAPA — Painel de Execução e Conciliação</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>
</head>
<body class="bg-slate-50 text-slate-800 font-sans">

  <!-- Cabeçalho Institucional -->
  <header class="bg-emerald-900 text-white shadow-md">
    <div class="max-w-7xl mx-auto px-6 py-4 flex flex-wrap justify-between items-center gap-4">
      <div>
        <span class="text-xs uppercase tracking-widest text-emerald-300 font-semibold">MAPA · Órgão 22000 · SDR</span>
        <h1 class="text-xl font-bold">Coordenação Financeira — Esteira de Pagamentos e Robô Tesouro</h1>
        <p class="text-xs text-emerald-200">UGs Principais: 130010, 130141, 130255, 135098, 420013 + Recursos Compartilhados (EXE001 & RAP001)</p>
      </div>
      <div class="flex items-center gap-3">
        <span id="status-sincronizacao" class="bg-emerald-800 border border-emerald-600 text-xs px-3 py-1.5 rounded-full">
          Sincronizando planilhas EXE/RAP...
        </span>
        <button onclick="carregarBasesAoVivo()" class="bg-amber-500 hover:bg-amber-600 text-slate-900 font-semibold text-xs px-4 py-2 rounded shadow">
          Rodar Robô Conciliador Agora
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl mx-auto px-6 py-6 space-y-6">

    <!-- Cards de Resumo (Posição do Último Mês sem Duplicar) -->
    <section class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white p-4 rounded-lg shadow-sm border-l-4 border-blue-600">
        <p class="text-xs text-slate-500 uppercase font-semibold">A Liquidar (Posição Atual)</p>
        <p id="kpi-aliquidar" class="text-xl font-bold text-slate-800 mt-1">R$ 0,00</p>
        <p class="text-[11px] text-slate-400 mt-1">Último mês disponível (EXE + RAP)</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow-sm border-l-4 border-amber-500">
        <p class="text-xs text-slate-500 uppercase font-semibold">Liquidado a Pagar (Fila Real)</p>
        <p id="kpi-apagar" class="text-xl font-bold text-amber-600 mt-1">R$ 0,00</p>
        <p class="text-[11px] text-slate-400 mt-1">Pronto para pagamento no SIAFI</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow-sm border-l-4 border-emerald-600">
        <p class="text-xs text-slate-500 uppercase font-semibold">Total Pago Acumulado (Ano)</p>
        <p id="kpi-pago" class="text-xl font-bold text-emerald-700 mt-1">R$ 0,00</p>
        <p class="text-[11px] text-slate-400 mt-1">Confirmado no Tesouro Gerencial</p>
      </div>
      <div class="bg-white p-4 rounded-lg shadow-sm border-l-4 border-purple-600">
        <p class="text-xs text-slate-500 uppercase font-semibold">Processos na Esteira</p>
        <p id="kpi-processos" class="text-xl font-bold text-purple-700 mt-1">0 processos</p>
        <p id="kpi-conciliados" class="text-[11px] text-emerald-600 font-medium mt-1">0 confirmados pelo Robô</p>
      </div>
    </section>

    <!-- Navegação de Abas -->
    <div class="border-b border-slate-200 flex gap-6 text-sm font-semibold">
      <button onclick="trocarAba('esteira')" id="tab-esteira" class="pb-3 border-b-2 border-emerald-700 text-emerald-800">
        1. Esteira de Pagamentos (Orçamentário → Financeiro → Executor → Robô)
      </button>
      <button onclick="trocarAba('tesouro')" id="tab-tesouro" class="pb-3 text-slate-500 hover:text-slate-800">
        2. Base Consolidada EXE001 + RAP001 (Sem Duplicação)
      </button>
      <button onclick="trocarAba('mensal')" id="tab-mensal" class="pb-3 text-slate-500 hover:text-slate-800">
        3. Movimento Mensal Isolado (Mês Atual − Mês Anterior)
      </button>
    </div>

    <!-- ABA 1: ESTEIRA OPERACIONAL -->
    <section id="sec-esteira" class="space-y-6">
      <!-- Formulário de Entrada (Área Demandante / Setor Orçamentário) -->
      <div class="bg-white p-5 rounded-lg shadow-sm border border-slate-200">
        <h2 class="text-sm font-bold text-slate-700 uppercase mb-3">Novo Encaminhamento para Pagamento (Validação Orçamentária → Financeiro)</h2>
        <div class="grid grid-cols-1 md:grid-cols-6 gap-3 text-xs">
          <div>
            <label class="block text-slate-600 mb-1 font-medium">Processo SEI</label>
            <input id="inp-processo" type="text" placeholder="21000.012345/2026-00" class="w-full border rounded px-2.5 py-2" />
          </div>
          <div>
            <label class="block text-slate-600 mb-1 font-medium">Modalidade</label>
            <select id="inp-modalidade" class="w-full border rounded px-2.5 py-2">
              <option value="Contrato">Contrato</option>
              <option value="Termo de Fomento">Termo de Fomento</option>
              <option value="Convênio">Convênio</option>
              <option value="Contrato de Repasse">Contrato de Repasse</option>
              <option value="Suprimento de Fundos">Suprimento de Fundos</option>
            </select>
          </div>
          <div class="md:col-span-2">
            <label class="block text-slate-600 mb-1 font-medium">Nota de Empenho (Digite para buscar saldo na planilha)</label>
            <input id="inp-ne" list="lista-nes" onchange="preencherDadosNE()" type="text" placeholder="Ex: 130005000012024NE000715 ou 2026NE..." class="w-full border rounded px-2.5 py-2 font-mono" />
            <datalist id="lista-nes"></datalist>
          </div>
          <div>
            <label class="block text-slate-600 mb-1 font-medium">Valor a Pagar (R$)</label>
            <input id="inp-valor" type="number" step="0.01" placeholder="15000.00" class="w-full border rounded px-2.5 py-2" />
          </div>
          <div>
            <label class="block text-slate-600 mb-1 font-medium">Distribuir ao Executor</label>
            <select id="inp-executor" class="w-full border rounded px-2.5 py-2">
              <option value="Aguardando Distribuição">Aguardando Distribuição</option>
              <option value="Executor 01">Executor 01</option>
              <option value="Executor 02">Executor 02</option>
              <option value="Executor 03">Executor 03</option>
            </select>
          </div>
        </div>
        <div class="mt-3 flex flex-wrap justify-between items-center gap-2 text-xs">
          <span id="info-saldo-ne" class="text-slate-500 italic">Selecione uma Nota de Empenho para o Orçamentário confirmar o saldo automaticamente.</span>
          <button onclick="adicionarProcessoEsteira()" class="bg-emerald-700 hover:bg-emerald-800 text-white font-semibold px-4 py-2 rounded">
            Confirmar Saldo Orçamentário & Incluir na Fila
          </button>
        </div>
      </div>

      <!-- Tabela da Esteira com Conciliação do Robô -->
      <div class="bg-white rounded-lg shadow-sm border border-slate-200 overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-100 text-slate-600 uppercase">
            <tr>
              <th class="p-3">Processo / Modalidade</th>
              <th class="p-3">NE / Fonte (EXE ou RAP)</th>
              <th class="p-3">Favorecido / Depto</th>
              <th class="p-3 text-right">Valor Solicitado</th>
              <th class="p-3">Executor Financeiro</th>
              <th class="p-3">Ação do Executor</th>
              <th class="p-3">Auditoria do Robô (Tesouro)</th>
            </tr>
          </thead>
          <tbody id="tabela-esteira" class="divide-y divide-slate-200"></tbody>
        </table>
      </div>
    </section>

    <!-- ABA 2: RADAR DE SALDOS EXE001 + RAP001 -->
    <section id="sec-tesouro" class="hidden space-y-4">
      <div class="bg-white p-4 rounded-lg shadow-sm border border-slate-200 flex flex-wrap gap-3 items-center justify-between">
        <input id="filtro-tesouro" oninput="renderizarTabelaTesouro()" type="text" placeholder="Filtrar por NE, UG (130010, 130141, 130005...), Favorecido, Ação ou Departamento..." class="border rounded px-3 py-2 text-xs w-full md:w-96" />
        <span class="text-xs text-slate-500">Exibindo estritamente a <strong>Posição do Último Mês</strong> de cada NE (Sem duplicar meses anteriores)</span>
      </div>
      <div class="bg-white rounded-lg shadow-sm border border-slate-200 overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-100 text-slate-600 uppercase">
            <tr>
              <th class="p-3">Origem / Últ. Mês</th>
              <th class="p-3">UG Exec.</th>
              <th class="p-3">Ação / Depto</th>
              <th class="p-3">NE CCor</th>
              <th class="p-3">Favorecido</th>
              <th class="p-3 text-right">A Liquidar</th>
              <th class="p-3 text-right">Liquidado a Pagar</th>
              <th class="p-3 text-right">Pago Acumulado</th>
            </tr>
          </thead>
          <tbody id="tabela-tesouro" class="divide-y divide-slate-200"></tbody>
        </table>
      </div>
    </section>

    <!-- ABA 3: MOVIMENTO ISOLADO DE CADA MÊS -->
    <section id="sec-mensal" class="hidden space-y-4">
      <div class="bg-white p-5 rounded-lg shadow-sm border border-slate-200">
        <h3 class="text-sm font-bold text-slate-700 mb-1">Cálculo de Execução Mensal Isolada (Desacumulado)</h3>
        <p class="text-xs text-slate-500 mb-4">Fórmula aplicada por Nota de Empenho: <strong>Movimento do Mês = Acumulado do Mês Atual − Acumulado do Mês Imediatamente Anterior</strong>.</p>
        <div id="grid-mensal" class="grid grid-cols-1 md:grid-cols-4 gap-4"></div>
      </div>
    </section>

  </main>

  <script>
    // Links CSV diretos das duas planilhas (EXE complementar + RAP)
    const FONTES_CSV = [
      { nome: "EXE 2026 Padrão", tipo: "EXE", url: "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFcFQpuXUjut17Ftj89ugQvu-eK-ZPI7a90FoPOnhcvXFSL2ymU-WOPiYwBT8qa8tzCeyo05q_YanW/pub?gid=1204904051&single=true&output=csv" },
      { nome: "EXE 2026 MDIR", tipo: "EXE", url: "https://docs.google.com/spreadsheets/d/e/2PACX-1vRFcFQpuXUjut17Ftj89ugQvu-eK-ZPI7a90FoPOnhcvXFSL2ymU-WOPiYwBT8qa8tzCeyo05q_YanW/pub?gid=32904262&single=true&output=csv" },
      { nome: "RAP 20ZV", tipo: "RAP", url: "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1255285299&single=true&output=csv" },
      { nome: "RAP 20ZY", tipo: "RAP", url: "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1626303078&single=true&output=csv" },
      { nome: "RAP 2000", tipo: "RAP", url: "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=1251866406&single=true&output=csv" },
      { nome: "RAP 215A", tipo: "RAP", url: "https://docs.google.com/spreadsheets/d/e/2PACX-1vRklhyNnCOR8-bgKvQJPz1SZCxSDaWUc5xID81uKQNPFe4-7MSC7I8KqwKHg2U0ZzJvJ3kczn2dTGDM/pub?gid=2071147261&single=true&output=csv" }
    ];

    const ORDEM_MES = { "JAN/2026": 1, "FEV/2026": 2, "MAR/2026": 3, "ABR/2026": 4, "MAI/2026": 5, "JUN/2026": 6, "JUL/2026": 7, "AGO/2026": 8, "SET/2026": 9, "OUT/2026": 10, "NOV/2026": 11, "DEZ/2026": 12 };

    let mapaEmpenhos = {};
    let movimentoPorMes = {};
    let filaEsteira = JSON.parse(localStorage.getItem("esteira_mapa_sdr") || "[]");

    function brToFloat(v) {
      if (!v) return 0;
      const limpo = String(v).replace(/R\$|\s/g, "").replace(/\./g, "").replace(",", ".");
      const num = parseFloat(limpo);
      return isNaN(num) ? 0 : num;
    }

    function formatarMoeda(v) {
      return Number(v || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    }

    async function lerCSV(fonte) {
      return new Promise((resolve) => {
        Papa.parse(fonte.url, {
          download: true,
          skipEmptyLines: true,
          complete: (res) => resolve({ fonte, linhas: res.data }),
          error: () => resolve({ fonte, linhas: [] })
        });
      });
    }

    async function carregarBasesAoVivo() {
      document.getElementById("status-sincronizacao").textContent = "Lendo abas EXE e RAP...";
      mapaEmpenhos = {};
      movimentoPorMes = {};

      const resultados = await Promise.all(FONTES_CSV.map(lerCSV));
      const historicoPorNE = {};

      resultados.forEach(({ fonte, linhas }) => {
        let idxHeader = linhas.findIndex(l => l.some(c => String(c).toUpperCase().includes("NE CCOR")));
        if (idxHeader === -1) return;
        const cabecalho = linhas[idxHeader].map(c => String(c).trim());

        for (let i = idxHeader + 1; i < linhas.length; i++) {
          const row = linhas[i];
          const obj = {};
          cabecalho.forEach((col, idx) => { if (col && obj[col] === undefined) obj[col] = row[idx]; });

          const ne = String(obj["NE CCor"] || "").trim();
          const mes = String(obj["Mês Lançamento"] || "").trim().toUpperCase();
          if (!ne || ne === "'-9" || ne === "'-8" || ne === "NAO SE APLICA" || !ORDEM_MES[mes]) continue;

          let aLiquidar = 0, aPagar = 0, pago = 0;
          if (fonte.tipo === "EXE") {
            aLiquidar = brToFloat(obj["DESPESAS EMPENHADAS A LIQUIDAR (CONTROLE EMP)"]);
            aPagar = brToFloat(obj["DESPESAS LIQUIDADAS A PAGAR(CONTROLE EMPENHO)"]);
            pago = brToFloat(obj["DESPESAS PAGAS (CONTROLE EMPENHO)"]);
          } else {
            aLiquidar = brToFloat(obj["RESTOS A PAGAR NAO PROCESSADOS A LIQUIDAR"]);
            aPagar = brToFloat(obj["RESTOS A PAGAR PROCESSADOS A PAGAR"]) + brToFloat(obj["RESTOS A PAGAR NAO PROCESSADOS A PAGAR"]);
            pago = brToFloat(obj["RESTOS A PAGAR PROCESSADOS PAGOS"]) + brToFloat(obj["RESTOS A PAGAR NAO PROCESSADOS PAGOS"]);
          }

          if (!historicoPorNE[ne]) historicoPorNE[ne] = {};
          // Desduplicação entre abas complementares no mesmo mês
          historicoPorNE[ne][mes] = {
            origem: fonte.nome,
            mes,
            ordem: ORDEM_MES[mes],
            ug: obj["UG Executora"] || "",
            acao: obj["Ação Governo"] || "",
            favorecido: obj["NE CCor - Favorecido"] || "",
            processo: obj["NE - Núm. Processo"] || "",
            depto: obj["DEPARTAMENTO"] || "",
            aLiquidar,
            aPagar,
            pago
          };
        }
      });

      // Calcula posição do último mês e movimento mensal isolado (Mês Atual - Mês Anterior)
      Object.entries(historicoPorNE).forEach(([ne, mesesObj]) => {
        const listaMeses = Object.values(mesesObj).sort((a, b) => a.ordem - b.ordem);
        let pagoAnterior = 0;
        listaMeses.forEach(item => {
          const movIsolado = Math.max(0, item.pago - pagoAnterior);
          pagoAnterior = item.pago;
          movimentoPorMes[item.mes] = (movimentoPorMes[item.mes] || 0) + movIsolado;
        });
        mapaEmpenhos[ne] = listaMeses[listaMeses.length - 1];
      });

      atualizarKPIs();
      popularDatalistNE();
      renderizarEsteira();
      renderizarTabelaTesouro();
      renderizarMovimentoMensal();
      document.getElementById("status-sincronizacao").textContent = `Sincronizado (${Object.keys(mapaEmpenhos).length} NEs ativas)`;
    }

    function atualizarKPIs() {
      let totLiq = 0, totPagar = 0, totPago = 0;
      Object.values(mapaEmpenhos).forEach(e => {
        totLiq += e.aLiquidar;
        totPagar += e.aPagar;
        totPago += e.pago;
      });
      document.getElementById("kpi-aliquidar").textContent = formatarMoeda(totLiq);
      document.getElementById("kpi-apagar").textContent = formatarMoeda(totPagar);
      document.getElementById("kpi-pago").textContent = formatarMoeda(totPago);
    }

    function popularDatalistNE() {
      const dl = document.getElementById("lista-nes");
      dl.innerHTML = Object.entries(mapaEmpenhos).slice(0, 400).map(([ne, d]) =>
        `<option value="${ne}">${d.origem} | ${d.favorecido} | A Pagar: ${formatarMoeda(d.aPagar)}</option>`
      ).join("");
    }

    function preencherDadosNE() {
      const ne = document.getElementById("inp-ne").value.trim();
      const info = document.getElementById("info-saldo-ne");
      if (mapaEmpenhos[ne]) {
        const d = mapaEmpenhos[ne];
        info.innerHTML = `<strong class="text-emerald-700">Saldo Localizado (${d.origem} - ${d.mes}):</strong> Favorecido: ${d.favorecido} | Liquidado a Pagar: <strong>${formatarMoeda(d.aPagar)}</strong> | Já Pago: <strong>${formatarMoeda(d.pago)}</strong>`;
        if (d.processo && d.processo !== "'-9") document.getElementById("inp-processo").value = d.processo;
      } else {
        info.textContent = "NE ainda não localizada nas abas carregadas ou digitada parcialmente.";
      }
    }

    function adicionarProcessoEsteira() {
      const proc = document.getElementById("inp-processo").value.trim() || "S/N";
      const mod = document.getElementById("inp-modalidade").value;
      const ne = document.getElementById("inp-ne").value.trim();
      const valor = parseFloat(document.getElementById("inp-valor").value || "0");
      const exec = document.getElementById("inp-executor").value;
      if (!ne || valor <= 0) return alert("Informe a Nota de Empenho e o Valor a Pagar.");

      const dadosNE = mapaEmpenhos[ne] || { origem: "Manual", favorecido: "Não identificado", depto: "-", pago: 0 };
      filaEsteira.unshift({
        id: Date.now(),
        processo: proc,
        modalidade: mod,
        ne,
        origem: dadosNE.origem,
        favorecido: dadosNE.favorecido,
        depto: dadosNE.depto,
        valor,
        executor: exec,
        statusExecutor: "Pendente",
        ob: ""
      });
      salvarEsteira();
      renderizarEsteira();
    }

    function marcarPagoExecutor(id) {
      const ob = prompt("Informe o número da Ordem Bancária (OB) ou Documento Hábil pago no SIAFI:");
      if (ob === null) return;
      filaEsteira = filaEsteira.map(p => p.id === id ? { ...p, statusExecutor: "Pago pelo Executor", ob: ob.trim() || "OB Emitida" } : p);
      salvarEsteira();
      renderizarEsteira();
    }

    function alterarExecutor(id, novoExec) {
      filaEsteira = filaEsteira.map(p => p.id === id ? { ...p, executor: novoExec } : p);
      salvarEsteira();
      renderizarEsteira();
    }

    function salvarEsteira() {
      localStorage.setItem("esteira_mapa_sdr", JSON.stringify(filaEsteira));
    }

    function renderizarEsteira() {
      const tbody = document.getElementById("tabela-esteira");
      let confirmadosRobo = 0;

      tbody.innerHTML = filaEsteira.map(p => {
        const dTesouro = mapaEmpenhos[p.ne];
        const pagoTesouro = dTesouro ? dTesouro.pago : 0;
        const confirmado = pagoTesouro >= p.valor && p.valor > 0;
        if (confirmado) confirmadosRobo++;

        let badgeRobo = `<span class="px-2 py-1 rounded bg-slate-100 text-slate-600 font-medium">Aguardando OB no Tesouro</span>`;
        if (confirmado) {
          badgeRobo = `<span class="px-2 py-1 rounded bg-emerald-100 text-emerald-800 font-bold">✓ Confirmado no Tesouro (${formatarMoeda(pagoTesouro)})</span>`;
        } else if (p.statusExecutor === "Pago pelo Executor") {
          badgeRobo = `<span class="px-2 py-1 rounded bg-amber-100 text-amber-800 font-semibold">⟳ Pago pelo Executor (${p.ob}) · Aguardando D+1 Tesouro</span>`;
        }

        return `
          <tr class="hover:bg-slate-50">
            <td class="p-3 font-medium">${p.processo}<br><span class="text-[11px] text-slate-500">${p.modalidade}</span></td>
            <td class="p-3 font-mono">${p.ne}<br><span class="text-[11px] text-emerald-700 font-sans">${p.origem}</span></td>
            <td class="p-3">${p.favorecido}<br><span class="text-[10px] text-slate-400">${p.depto}</span></td>
            <td class="p-3 text-right font-bold">${formatarMoeda(p.valor)}</td>
            <td class="p-3">
              <select onchange="alterarExecutor(${p.id}, this.value)" class="border rounded px-2 py-1 text-xs">
                <option ${p.executor === 'Aguardando Distribuição' ? 'selected' : ''}>Aguardando Distribuição</option>
                <option ${p.executor === 'Executor 01' ? 'selected' : ''}>Executor 01</option>
                <option ${p.executor === 'Executor 02' ? 'selected' : ''}>Executor 02</option>
                <option ${p.executor === 'Executor 03' ? 'selected' : ''}>Executor 03</option>
              </select>
            </td>
            <td class="p-3">
              ${p.statusExecutor === "Pago pelo Executor"
                ? `<span class="text-emerald-700 font-semibold">Informado Pago (${p.ob})</span>`
                : `<button onclick="marcarPagoExecutor(${p.id})" class="bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1 rounded text-xs">Informar Pagamento</button>`
              }
            </td>
            <td class="p-3">${badgeRobo}</td>
          </tr>
        `;
      }).join("") || `<tr><td colspan="7" class="p-6 text-center text-slate-400">Nenhum processo na fila. Selecione uma Nota de Empenho acima para testar a conciliação automática!</td></tr>`;

      document.getElementById("kpi-processos").textContent = `${filaEsteira.length} processos`;
      document.getElementById("kpi-conciliados").textContent = `${confirmadosRobo} confirmados pelo Robô`;
    }

    function renderizarTabelaTesouro() {
      const termo = (document.getElementById("filtro-tesouro").value || "").toUpperCase();
      const linhas = Object.entries(mapaEmpenhos)
        .filter(([ne, d]) => !termo || ne.includes(termo) || d.favorecido.toUpperCase().includes(termo) || d.ug.includes(termo) || d.depto.toUpperCase().includes(termo) || d.acao.toUpperCase().includes(termo))
        .slice(0, 150);

      document.getElementById("tabela-tesouro").innerHTML = linhas.map(([ne, d]) => `
        <tr class="hover:bg-slate-50">
          <td class="p-3 font-semibold text-emerald-800">${d.origem} <span class="text-slate-400 font-normal">(${d.mes})</span></td>
          <td class="p-3 font-mono">${d.ug}</td>
          <td class="p-3">${d.acao}<br><span class="text-[10px] text-slate-400">${d.depto}</span></td>
          <td class="p-3 font-mono font-medium">${ne}</td>
          <td class="p-3">${d.favorecido}</td>
          <td class="p-3 text-right">${formatarMoeda(d.aLiquidar)}</td>
          <td class="p-3 text-right font-semibold text-amber-700">${formatarMoeda(d.aPagar)}</td>
          <td class="p-3 text-right font-bold text-emerald-700">${formatarMoeda(d.pago)}</td>
        </tr>
      `).join("");
    }

    function renderizarMovimentoMensal() {
      const mesesOrdenados = Object.keys(movimentoPorMes).sort((a, b) => ORDEM_MES[a] - ORDEM_MES[b]);
      document.getElementById("grid-mensal").innerHTML = mesesOrdenados.map(m => `
        <div class="p-4 border rounded-lg bg-slate-50">
          <p class="text-xs font-bold text-slate-500">${m} (Movimento Isolado)</p>
          <p class="text-lg font-bold text-emerald-800 mt-1">${formatarMoeda(movimentoPorMes[m])}</p>
          <p class="text-[11px] text-slate-400">Descontado o acumulado do mês anterior</p>
        </div>
      `).join("");
    }

    function trocarAba(aba) {
      ["esteira", "tesouro", "mensal"].forEach(id => {
        document.getElementById(`sec-${id}`).classList.toggle("hidden", id !== aba);
        document.getElementById(`tab-${id}`).className = id === aba
          ? "pb-3 border-b-2 border-emerald-700 text-emerald-800 font-bold"
          : "pb-3 text-slate-500 hover:text-slate-800";
      });
    }

    carregarBasesAoVivo();
  </script>
</body>
</html>
