
# %.dvi : %.tex
# 	latex $<

manual.dvi : manual.tex manual-cap-??.tex
	latex manual

view-dvi : manual.dvi
#	xdvi -paper 31cmx22cm $^ &
	xdvi -s 6 $^ &

dvi : manual.dvi

# $< is equivalent to $^ ?
%.ps : %.dvi
#	dvips -t landscape -o $@ $<
	dvips -o $@ $<

ps : manual.ps

view-ps : manual.ps
	gv $^ &

%.pdf: %.ps
	ps2pdf $^

#%.pdf: %.dvi
#	dvipdfm $^

pdf : manual.pdf

view-pdf: manual.pdf
	cygstart $^

.PHONY: view-ps, view-pdf, view-dvi, ps, pdf, dvi

