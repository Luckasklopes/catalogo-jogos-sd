#!/bin/bash
echo "Subindo containers..."
docker compose up --build -d
echo "Aplicação disponível em http://localhost:8000"
echo "Documentação disponível em http://localhost:8000/docs"
