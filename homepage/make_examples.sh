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
	<div class="example">
__EOF__
	./extract_text.py < ../examples/$BASE.py | ./Markdown.pl >> $EXAMPLES
	cat >> $EXAMPLES << __EOF__
		<p>
			<a href="${BASE}_source.html">[Source]</a>
			<a href="images/${BASE}.pdf">[PDF]</a>
		</p>
		<div id="example image">
			<img src="images/$BASE.png"/>
		</div>
	</div>
__EOF__

done

cat index_top $EXAMPLES index_bottom > index.html
