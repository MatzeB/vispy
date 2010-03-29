#!/bin/bash
pushd ../examples > /dev/null

# Create images
for e in *.py; do
	./makeexample.sh $e
	PDFS="$PDFS `basename $e .py`.pdf"
done

popd

rm -rf build
mkdir -p build
BUILD="build"
EXAMPLES="$BUILD/images.part"
for p in $PDFS; do
	BASE="`basename $p .pdf`"
	echo "Producing example '$BASE'"

	cp ../examples/$p $BUILD
	PDF="$BUILD/$BASE.pdf"
	PNG="$BUILD/$BASE.png"
	convert -density 300 $PDF -resize 384x384 $PNG

	SYNTAX="$BUILD/${BASE}_source.html"
	vim -c ':let html_number_lines=0' -c ':let html_use_css=1' -c ':TOhtml' -c ":w $SYNTAX" -c ':q!' -c ':q!' ../examples/$BASE.py

	cat >> $EXAMPLES << __EOF__
	<div id="example">
		<a href="${BASE}_source.html"><img src="images/$BASE.png"/></a>
	</div>
__EOF__
done

