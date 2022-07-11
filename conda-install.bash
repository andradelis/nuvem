FAILED=false

REQ_FILE="requirements.yaml"
CONDA_ENV_NAME=$(grep "name:" $REQ_FILE | cut -c 7-)

if [ -f "$REQ_FILE" ]; then
    echo "O ambiente $CONDA_ENV_NAME será criado!"
    conda env create --file $REQ_FILE 
else
    echo "FALHA: $REQ_FILE não existe no repositório!"
    FAILED=true
fi

if [ "$FAILED" = true ]; then
    exit 1
fi

exit 0