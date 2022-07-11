FAILED=false
REQ_FILE="requirements.yaml"
REPOSITORY_NAME=$(echo ${PWD##*/})

if [ "$REPOSITORY_NAME" = "$CONDA_DEFAULT_ENV" ]; then
    echo "O ambiente $CONDA_DEFAULT_ENV será exportado!"
else
    echo "FALHA: $CONDA_DEFAULT_ENV não condiz com o repositório $REPOSITORY_NAME."
    echo "FALHA: o ambiente conda e o repositório precisam ter o mesmo nome!"
    exit 1
fi

if [ -f "$REQ_FILE" ]; then
    echo "$REQ_FILE existe!"
else
    echo "FALHA: $REQ_FILE não existe no repositório!"
    conda env export --no-builds | grep -v "^prefix: " > $REQ_FILE
    FAILED=true
fi

REQUIREMENTS=$(cat $REQ_FILE)
NEW_REQUIREMENTS=$(conda env export --no-builds | grep -v "^prefix:")

if [ "$NEW_REQUIREMENTS" = "$REQUIREMENTS" ]; then
    echo "$REQ_FILE está atualizado!"
else
    echo "FALHA: $REQ_FILE do repositório não está atualizado!"
    conda env export --no-builds | grep -v "^prefix:" > $REQ_FILE
    echo "Foi atualizado!"
    FAILED=true
fi

if [ "$FAILED" = true ]; then
    exit 1
fi
exit 0