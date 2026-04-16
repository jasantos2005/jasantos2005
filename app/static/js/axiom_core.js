/**
 * IATCH AXIOM - Core JS Engine
 * Gerencia Filtros Globais, Interatividade e Chamadas API
 */

const Axiom = {
    // Configurações de Data Padrão (Mês Atual)
    init: function() {
        const now = new Date();
        const firstDay = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
        const lastDay = now.toISOString().split('T')[0];

        document.getElementById('start_date').value = firstDay;
        document.getElementById('end_date').value = lastDay;
        
        console.log("Axiom Core Initialized.");
    },

    // Função para buscar dados de qualquer endpoint respeitando os filtros
    fetchData: async function(endpoint, params = {}) {
        const token = localStorage.getItem('axiom_token');
        if (!token) window.location.href = '/';

        const start = document.getElementById('start_date').value;
        const end = document.getElementById('end_date').value;
        
        const url = new URL(window.location.origin + endpoint);
        url.searchParams.append('start', start);
        url.searchParams.append('end', end);
        Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));

        try {
            const response = await fetch(url, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.status === 401 || response.status === 403) window.location.href = '/';
            return await response.json();
        } catch (err) {
            console.error("Axiom Fetch Error:", err);
            return null;
        }
    },

    // Formatação de Moeda Padrão Axiom
    formatCurrency: function(value) {
        return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
    }
};

document.addEventListener('DOMContentLoaded', () => Axiom.init());
