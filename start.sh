#!/bin/bash
echo -e "\033[1;36mInicializando o Hermes Agent Ecosystem...\033[0m"

HAS_GPU=false

if [ "$1" == "--force-gpu" ]; then
    HAS_GPU=true
elif [ "$1" == "--force-cpu" ]; then
    HAS_GPU=false
else
    if command -v nvidia-smi &> /dev/null; then
        if nvidia-smi &> /dev/null; then
            HAS_GPU=true
        fi
    fi
fi

OVERRIDE_FILE="docker-compose.override.yml"

if [ "$HAS_GPU" = true ]; then
    echo -e "\033[1;32mPlaca NVIDIA detectada! Ativando aceleração via CUDA (GPU).\033[0m"
    cat <<EOF > $OVERRIDE_FILE
services:
  qwen-engine:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
EOF
else
    echo -e "\033[1;33mNenhuma placa NVIDIA detectada. O sistema rodará em modo CPU.\033[0m"
    if [ -f "$OVERRIDE_FILE" ]; then
        rm -f $OVERRIDE_FILE
    fi
fi

echo -e "\033[1;36mSubindo os containers do Docker Compose...\033[0m"
docker compose up -d

echo -e "\033[1;32mVerificação de GPU e inicialização concluídas com sucesso!\033[0m"
