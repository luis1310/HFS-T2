#!/bin/bash

# Script para compilar el documento LaTeX con bibliografía

echo "Compilando documento LaTeX..."
pdflatex -interaction=nonstopmode main.tex

echo "Procesando bibliografía con bibtex..."
bibtex main

echo "Recompilando (primera vez)..."
pdflatex -interaction=nonstopmode main.tex

echo "Recompilando (segunda vez) para resolver referencias..."
pdflatex -interaction=nonstopmode main.tex

echo ""
echo "¡Compilación completada! Revisa main.pdf"
