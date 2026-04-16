#!/bin/bash

# Configurações
PROJETO="/opt/automacoes/GSG/gestao/diretoria/dashboards"
BACKUP_DIR="$PROJETO/backups_interno"
mkdir -p $BACKUP_DIR

case $1 in
    backup)
        VERSAO=$2
        if [ -z "$VERSAO" ]; then echo "Erro: Digite a versão (ex: v4)"; exit 1; fi
        echo "Gerando backup da $VERSAO..."
        mkdir -p "$BACKUP_DIR/$VERSAO"
        # Copia apenas o código e banco, ignora a venv e a própria pasta de backup
        rsync -av --progress $PROJETO/ "$BACKUP_DIR/$VERSAO/" --exclude "venv" --exclude "backups_interno" --exclude ".git" --exclude "gerenciar_versao.sh"
        echo "✅ Versão $VERSAO salva com sucesso!"
        ;;

    restaurar)
        VERSAO=$2
        if [ -z "$VERSAO" ]; then echo "Erro: Digite a versão para restaurar (ex: v4)"; exit 1; fi
        echo "⚠️ Restaurando para a versão $VERSAO..."
        rsync -av --delete "$BACKUP_DIR/$VERSAO/" $PROJETO/ --exclude "venv" --exclude "backups_interno" --exclude "gerenciar_versao.sh"
        echo "✅ Sistema restaurado para $VERSAO. Reinicie o Uvicorn."
        ;;

    limpar)
        VERSAO=$2
        if [ -z "$VERSAO" ]; then echo "Erro: Digite a versão antiga para deletar"; exit 1; fi
        echo "Limpando versão antiga $VERSAO..."
        rm -rf "$BACKUP_DIR/$VERSAO"
        echo "✅ Versão $VERSAO removida."
        ;;
    *)
        echo "Uso: ./gerenciar_versao.sh [backup|restaurar|limpar] [versao]"
        ;;
esac
