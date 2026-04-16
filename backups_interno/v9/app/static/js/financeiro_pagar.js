const fmt = (v) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v || 0);

async function updateUI() {
    // Busca as datas dos inputs (que devem estar no seu base/layout.html)
    const start = document.getElementById('date-start')?.value || "";
    const end = document.getElementById('date-end')?.value || "";
    
    try {
        // Rota que deu 200 OK nos seus logs
        const res = await fetch(`/api/financeiro/resumo?inicio=${start}&fim=${end}`);
        const result = await res.json();
        
        if (result.status === 'success') {
            const d = result.data;
            
            // --- Lógica para CONTAS A RECEBER (Página Index) ---
            if (document.getElementById('prazo-perc')) {
                document.getElementById('prazo-perc').innerText = `${d.pagamento_prazo?.percentual_no_prazo || 0}%`;
                document.getElementById('prazo-val').innerText = fmt(d.pagamento_prazo?.total_pago_no_prazo);
                document.getElementById('rec-perc').innerText = `${d.recuperacao_mes_ant?.taxa_recuperacao || 0}%`;
                document.getElementById('rec-val').innerText = fmt(d.recuperacao_mes_ant?.total_recuperado);
                document.getElementById('arpu-val').innerText = fmt(d.arpu_caixa?.arpu_real);
                document.getElementById('inad-mes-perc').innerText = `${d.inadimplencia_mes?.percentual_inadimplencia || 0}%`;
                document.getElementById('exp-mes-val').innerText = fmt(d.exposicao_mes?.total_exposto);
            }

            // --- Lógica para CONTAS A PAGAR (Sincronizada com seu novo HTML) ---
            if (document.getElementById('passivo-total')) {
                document.getElementById('passivo-total').innerText = fmt(d.passivo_total?.total);
                document.getElementById('passivo-vencido').innerText = fmt(d.passivo_vencido?.total);
                document.getElementById('pressao-30d').innerText = fmt(d.pressao_30d?.total);
                document.getElementById('projecao-90d').innerText = fmt(d.projecao_90d?.total);
                
                // Sustentabilidade: busca o valor da query SQL correspondente
                const sust = d.sustentabilidade?.total || d.sustentabilidade?.indice || 0;
                document.getElementById('sustentabilidade').innerText = `${sust}%`;
            }
        }
    } catch (e) {
        console.error("Erro na comunicação com a API Axiom:", e);
    }
}

// Inicializa automaticamente e vincula ao botão se ele existir
document.addEventListener('DOMContentLoaded', () => {
    updateUI();
    const btn = document.querySelector('.btn-success') || document.querySelector('button[onclick="updateUI()"]');
    if (btn) btn.addEventListener('click', updateUI);
});
