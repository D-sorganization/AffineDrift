@echo off
echo Compiling Volume I: Foundations of Exact Linearization and Contraction...
cd Volume_I
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
cd ..

echo Compiling Volume II: Transverse Control and The Architecture of Trajectories...
cd Volume_II
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
cd ..

echo Compilation Complete! Look for main.pdf in both Volume_I and Volume_II folders.
