#
# My publication list generator
#
# The entries go to the correct section based on the content of the MVpubtype field (see below) in the file index.html
# instead in the file by-year.html they go grouped by year
#

#
# Setup the directory containing the various script pieces and the two executables (from http://www.lri.fr/~filliatr/bibtex2html/)
#
# In the $BIB_GEN_DIR directory edit also the HTML header and footers to suit your needs
#
export BIB_GEN_DIR=bibgen
export BIB_2_HTML=$BIB_GEN_DIR/bibtex2html-1.79.exe
export BIB_2_BIB=$BIB_GEN_DIR/bib2bib-1.79.exe

#
# The input bib file and the html out files (the OUT_PUB_BIB one should be named publications_bib.html)
#
export IN_PUB_BIB=../../Research/bib/MVpublications.bib
export OUT_PUB_LIST=../../web/new-pages/publications/index.html
export OUT_PUB_BIB=../../web/new-pages/publications/publications_bib.html
export OUT_YEAR_LIST=../../web/new-pages/publications/by-year.html

#
# Range of dates for the publications
#
export BIB_TODAY=`date +%Y`
export BIB_START=2001

#
# Generate the various sections (grouped by MVpubtype)
#
$BIB_GEN_DIR/bib-section.sh  $IN_PUB_BIB "MVpubtype : 'refereed'" referred publications "Refereed papers"
$BIB_GEN_DIR/bib-section.sh  $IN_PUB_BIB "MVpubtype : 'books'" books publications "Books and book chapters"
$BIB_GEN_DIR/bib-section.sh  $IN_PUB_BIB "MVpubtype : 'conferences' or MVpubtype : 'poster'" conferences publications "Conference papers and posters"
$BIB_GEN_DIR/bib-section.sh  $IN_PUB_BIB "MVpubtype : 'general'" other publications "Other (not refereed or for non specialists)"

#
# Combine them into the whole publication list
#
cat $BIB_GEN_DIR/template-header.html referred.html books.html conferences.html other.html $BIB_GEN_DIR/template-footer.html > $OUT_PUB_LIST

rm -f referred.html books.html conferences.html other.html
rm -f referred_bib.html books_bib.html conferences_bib.html other_bib.html

#
# Create the initial publication_bib.html file
#
$BIB_GEN_DIR/bib-section.sh $IN_PUB_BIB "" whole publications " "

#
# Edit the resulting html ('publications.bib' could be changed to a more sensible content for the H1 title on the page)
#
sed -e 's/^<h1>.*$/<h1>publications.bib<\/h1>/' \
-e 's/^<p>/<div>/' \
-e 's/^<\/p>/<\/div>/' \
-e 's/<a name/<a class="a-id" id/' whole_bib.html > tmp-whole-bib.html

#
# Assemble the complete publications_bib.html file
#
cat $BIB_GEN_DIR/template-bib-header.html tmp-whole-bib.html $BIB_GEN_DIR/template-bib-footer.html > $OUT_PUB_BIB

rm -f tmp-whole-bib.html whole_bib.html whole.html
rm -f publications_bib.html publications.html

#
# Generate the list for each year
#
for year in `seq $BIB_TODAY -1 $BIB_START`
do
    $BIB_GEN_DIR/bib-section.sh  $IN_PUB_BIB "year = $year" $year publications "$year"
done

#
# Combine them into the whole publication list by year
#
cp $BIB_GEN_DIR/template-header.html  $OUT_YEAR_LIST
for year in `seq $BIB_TODAY -1 $BIB_START`
do
    cat $year.html >> $OUT_YEAR_LIST
    rm -f $year.html ${year}_bib.html
done
cat $BIB_GEN_DIR/template-footer.html >> $OUT_YEAR_LIST

rm -f publications_bib.html publications.html
