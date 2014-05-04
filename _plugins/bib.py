#!/usr/bin/env python
# Does two tasks:
#
# 1) Generates pubs.html as refereed pubs then non-refereed pubs,
#    sorted reverse-chronologically
# 2) Generates LaTeX-formatted publications, same format

import sys, os, re, time, datetime

# Generate non-refereed pubs (tech reports, theses, or has the field
# "nonrefereed"; does have me as author); put refs into nonref.txt
os.system("bib2bib -oc nonref.txt -c '$type : \"TECHREPORT\" or $type : \"PHDTHESIS\" or exists NONREFEREED' -c 'author : \"Owens\"' owens.bib")

# Generate refereed pubs (not tech reports, theses, or has the field
# \"nonrefereed\"; does have me as author); put refs into ref.txt
os.system("bib2bib -oc ref.txt -c '! $type : \"TECHREPORT\"' -c '! $type : \"PHDTHESIS\"' -c '! exists NONREFEREED' -c 'author : \"Owens\"' owens.bib")

pubs_html = ''

# iterate over refereed and non-refereed
for o in [ ['', '--no-footer', 'ref.txt'], ['Non-', '', 'nonref.txt'] ]:
  # output is pubs.html
  pubs_html += '<h1>%sRefereed Publications</h1>' % o[0]

  # add non-/refereed pubs to pubs.html
  # sort by reverse-date; don't generate keys; use owens_web.bbl
  # writes into owens.html
  os.system("bibtex2html -d -r -dl -nokeys -m macros.tex -citefile %s -s owens_web -nodoc %s owens.bib" % (o[2], o[1]))
  owens_html = open('owens.html')
  pubs_html += owens_html.read()
  owens_html.close()

# change \"[ bib ]\" into \"[&nbsp;bib&nbsp;]\"
biblinkRE = re.compile(r'\[ (<a href="[^"]+">bib</a>) ]')
pubs_html = biblinkRE.sub(r'[&nbsp;\1&nbsp;]', pubs_html)
# remove explicit line breaks
deletebrRE = re.compile(r'<br />')
pubs_html = deletebrRE.sub('', pubs_html)

# write into output file pubs.html
pubs_html_file = open('pubs.html', 'w')
print >> pubs_html_file, pubs_html
pubs_html_file.close()

# and finally, generate owens_bib.html
os.system("bib2bib -oc all.txt -c 'author : \"Owens\"' owens.bib")
os.system("bibtex2html -citefile all.txt owens.bib")

# copy to website
os.system("scp pubs.html fac-linux.ece.ucdavis.edu:Html/src/pubs.html")
os.system("scp owens_bib.html fac-linux.ece.ucdavis.edu:Html/owens_bib.html")
os.system("ssh fac-linux.ece.ucdavis.edu 'cd Html/src; ./build.py'")


#########

# now we're going to generate a LaTeX version of my pubs, also sorted

# RE selects bibitems from bbl (key stored in group(1), entry in group(2))
bibitemRE = re.compile(r'\\bibitem\[\]\{([^\}]+)\}(.*)', re.DOTALL)
# refs.tex will contain the LaTeX version of my pubs
refs_tex = open('../cv/refs.tex', 'w')

# separately loop through refereed and non-refereed pubs
for o in [ ['ref', 'Refereed'], ['nonref', 'Other'] ]:
  # generate an aux file
  # start by putting all cited keys (in order) with -print-keys in owens.aux
  os.system("bibtex2html -q -d -r -nokeys -citefile %s.txt -s owens_web -nodoc --no-footer -print-keys owens.bib > owens.aux" % o[0])
  owens_aux = open('owens.aux')
  sorted_keys = owens_aux.read().split('\n')
  owens_aux.close()
  # owens_aux file now contains the sorted keys, as does sorted_keys

  # now, put the aux file in the actual format that LaTeX wants
  # start with \citation{key} for each ref
  owens_aux = open('owens.aux', 'w')
  for key in sorted_keys:
    if key:
      print >> owens_aux, r'\citation{%s}' % key
  # then add bibstyle (which bst file) and bibdata (which bib file)
  print >> owens_aux, r'\bibstyle{../cv/owens_cv}'
  print >> owens_aux, r'\bibdata{owens}'
  # finally add a bibcite key for each ref
  for key in sorted_keys:
    if key: 
      print >> owens_aux, r'\bibcite{%s}{%s}' % (key, key)
  owens_aux.close()

  # create owens.bbl by calling bibtex (takes owens.bib, owens.aux and
  # owens_cv.bbl as inputs)
  os.system("bibtex owens")

  owens_bbl = open('owens.bbl')

  # now we have a bbl file full of bibitems that have properly
  # formatted LaTeX refs (not necessarily in the right order). But
  # sorted_keys is in the right order, so put each bibentry in a hash
  # and then walk through all the keys in sorted_keys, writing into
  # refs.tex
  refhash = {}
  for ref in owens_bbl.read().split('\n\n'):
    m = bibitemRE.search(ref)
    if m:
      refhash[m.group(1)] = m.group(2)
  print >> refs_tex, r'\section{\textsc{%s\\ Publications}}' % o[1]
  for key in sorted_keys:
    if key:
      print >> refs_tex, refhash[key]
  owens_bbl.close()
refs_tex.close()
os.system("cd ../cv; latexmk -pdf cv.tex")
os.system("scp ../cv/cv.pdf fac-linux.ece.ucdavis.edu:Html/cv/cv.pdf")

# clean up temp files
os.remove("owens.html")
os.remove("owens.blg")
os.remove("nonref.txt")
os.remove("ref.txt")
os.remove("all.txt")
