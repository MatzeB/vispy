#!/bin/bash

set -e

rm -rf build
mkdir -p build
cat > build/doc.tex <<'__EOF__'
\documentclass[a4paper]{report}

\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[ngerman]{babel}
\usepackage[rgb]{xcolor}
\usepackage{tikz}

\begin{document}

	\thispagestyle{empty}
	\input{picture.tex}

\end{document}
__EOF__

export PYTHONPATH="..:$PYTHONPATH"
python $1 > build/picture.tex
pushd build > /dev/null
pdflatex doc.tex
pdfcrop doc.pdf doc.pdf
cp doc.pdf ../`basename $1 .py`.pdf
popd > /dev/null
