#!/bin/bash

# Script para compilar el documento LaTeX con bibliografía (APA 7 con biblatex)

echo "Compilando documento LaTeX (primera vez)..."
pdflatex -interaction=nonstopmode main.tex

echo "Procesando bibliografía con biber (APA 7)..."
biber main

echo "Recompilando (segunda vez)..."
pdflatex -interaction=nonstopmode main.tex

echo "Recompilando (tercera vez) para resolver referencias..."
pdflatex -interaction=nonstopmode main.tex

echo ""
echo "¡Compilación completada! Revisa main.pdf"
