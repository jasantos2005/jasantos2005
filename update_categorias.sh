#!/bin/bash
# Atualizar categorias dos produtos conforme planilha

cd /opt/automacoes/GSG/gestao/diretoria/dashboards

./venv/bin/python3 << 'PYEOF'
import sqlite3
DB = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/gsg_estoque.db"
conn = sqlite3.connect(DB)

# 187 produtos com categorias definidas da planilha
updates = [
    ("INFRA", "399"), ("INFRA", "398"), ("INFRA", "677"), ("GERAL", "424"),
    ("GERAL", "460"), ("GERAL", "482"), ("GERAL", "474"), ("GERAL", "467"),
    ("GERAL", "459"), ("GERAL", "672"), ("GERAL", "671"), ("CASA", "450"),
    ("GERAL", "562"), ("GERAL", "487"), ("GERAL", "448"), ("GERAL", "631"),
    ("GERAL", "674"), ("GERAL", "673"), ("CASA", "383"), ("INFRA", "409"),
    ("INFRA", "410"), ("INFRA", "412"), ("INFRA", "408"), ("CASA", "564"),
    ("CASA", "583"), ("INFRA", "415"), ("INFRA", "425"), ("GERAL", "574"),
    ("GERAL", "402"), ("INFRA", "413"), ("GERAL", "571"), ("GERAL", "480"),
    ("GERAL", "504"), ("GERAL", "509"), ("GERAL", "462"), ("GERAL", "461"),
    ("GERAL", "463"), ("GERAL", "466"), ("GERAL", "465"), ("GERAL", "497"),
    ("GERAL", "659"), ("GERAL", "502"), ("GERAL", "414"), ("INFRA", "556"),
    ("CASA", "422"), ("CASA", "423"), ("CASA", "507"), ("INFRA", "427"),
    ("INFRA", "421"), ("GERAL", "345"), ("CASA", "407"), ("INFRA", "555"),
    ("INFRA", "416"), ("INFRA", "417"), ("INFRA", "615"), ("GERAL", "676"),
    ("GERAL", "346"), ("GERAL", "639"), ("GERAL", "359"), ("GERAL", "617"),
    ("GERAL", "433"), ("GERAL", "434"), ("GERAL", "621"), ("GERAL", "483"),
    ("GERAL", "484"), ("GERAL", "485"), ("GERAL", "220"), ("GERAL", "358"),
    ("CASA", "387"), ("CASA", "386"), ("GERAL", "477"), ("GERAL", "588"),
    ("INFRA", "443"), ("GERAL", "349"), ("INFRA", "418"), ("GERAL", "442"),
    ("CASA", "381"), ("CASA", "380"), ("CASA", "435"), ("CASA", "669"),
    ("CASA", "441"), ("GERAL", "533"), ("GERAL", "420"), ("GERAL", "517"),
    ("GERAL", "608"), ("GERAL", "649"), ("GERAL", "541"), ("INFRA", "455"),
    ("INFRA", "456"), ("INFRA", "453"), ("INFRA", "458"), ("INFRA", "454"),
    ("GERAL", "521"), ("GERAL", "687"), ("GERAL", "512"), ("GERAL", "688"),
    ("GERAL", "650"), ("GERAL", "563"), ("GERAL", "351"), ("GERAL", "35"),
    ("GERAL", "439"), ("INFRA", "438"), ("INFRA", "400"), ("INFRA", "401"),
    ("GERAL", "534"), ("GERAL", "531"), ("GERAL", "675"), ("GERAL", "518"),
    ("GERAL", "516"), ("GERAL", "481"), ("GERAL", "670"), ("GERAL", "632"),
    ("GERAL", "392"), ("GERAL", "393"), ("GERAL", "657"), ("GERAL", "654"),
    ("GERAL", "656"), ("GERAL", "655"), ("GERAL", "653"), ("INFRA", "440"),
    ("CASA", "577"), ("CASA", "576"), ("CASA", "494"), ("CASA", "510"),
    ("CASA", "579"), ("CASA", "578"), ("CASA", "634"), ("CASA", "585"),
    ("CASA", "565"), ("CASA", "613"), ("CASA", "552"), ("CASA", "522"),
    ("CASA", "575"), ("CASA", "624"), ("CASA", "511"), ("CASA", "385"),
    ("CASA", "573"), ("CASA", "523"), ("CASA", "551"), ("CASA", "586"),
    ("GERAL", "488"), ("GERAL", "532"), ("GERAL", "645"), ("GERAL", "536"),
    ("GERAL", "496"), ("GERAL", "686"), ("INFRA", "390"), ("GERAL", "479"),
    ("GERAL", "567"), ("GERAL", "355"), ("INFRA", "449"), ("INFRA", "636"),
    ("INFRA", "391"), ("GERAL", "468"), ("GERAL", "560"), ("GERAL", "515"),
    ("CASA", "550"), ("GERAL", "389"), ("GERAL", "395"), ("INFRA", "549"),
    ("GERAL", "486"), ("GERAL", "535"), ("GERAL", "348"), ("CASA", "384"),
    ("CASA", "616"), ("CASA", "651"), ("CASA", "652"), ("CASA", "658"),
    ("GERAL", "561"), ("GERAL", "637"), ("GERAL", "581"), ("GERAL", "646"),
    ("GERAL", "640"), ("GERAL", "642"), ("INFRA", "529"), ("INFRA", "406"),
    ("INFRA", "405"), ("INFRA", "403"), ("INFRA", "404"), ("INFRA", "431"),
    ("INFRA", "432"), ("INFRA", "548"), ("INFRA", "430"), ("INFRA", "428"),
    ("INFRA", "429"), ("INFRA", "526"), ("GERAL", "352"),
]

ok = 0
for cat, pid in updates:
    r = conn.execute("UPDATE produtos SET categoria=? WHERE id_produto=?", (cat, pid))
    if r.rowcount > 0:
        ok += 1

conn.commit()

# Resultado
print(f"✅ {ok} produtos atualizados")
rows = conn.execute("SELECT categoria, COUNT(*) as n FROM produtos GROUP BY categoria ORDER BY n DESC").fetchall()
for r in rows:
    print(f"  {r[0]}: {r[1]} produtos")

# Verificar produtos sem categoria definida
sem_cat = conn.execute("SELECT COUNT(*) as n FROM produtos WHERE categoria='GERAL' OR categoria IS NULL").fetchone()
print(f"\n  Total GERAL (sem categoria específica): {sem_cat[0]}")
conn.close()
PYEOF

echo ""
echo "✅ Categorias atualizadas — acesse /dashboard/estoque/casa e /dashboard/estoque/infra"
