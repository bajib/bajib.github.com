#
# Prepare one section of the publication list (it is called by bibgen.sh)
# The arguments are:
#   1 : bib file
#   2 : query (if empty string, then no selection is done)
#   3 : partial output file prefix
#   4 : full prefix for the whole resulting file
#   5 : section title
#
if test -z "$2"
then
    $BIB_2_HTML -s ieeetr --nodoc --no-header --no-footer --no-keywords -t "$5" -d -r -o $4 $1
else
    $BIB_2_BIB -oc tmp-citefile -ob tmp-bibfile.bib -c "$2" $1
    $BIB_2_HTML -s ieeetr --nodoc --no-header --no-footer --no-keywords -citefile tmp-citefile \
    -nf confsite "conference site" \
    -nf pubsite "publisher site" \
    -nf url "html" \
    -nf pdf "pdf" \
    -t "$5" -d -r -o $4 tmp-bibfile.bib
    rm -f tmp-citefile tmp-bibfile.bib
fi

sed -e 's/<a name/<a class="a-id" id/' \
-e 's/``/<b>/' \
-e "s/''/<\/b>/" \
-e "s/<br \/>/ /" \
-e 's/<td align/<td class="ref-col" align/' \
-e "s/\[ /\[\&nbsp;/" \
-e "s/ \]/\&nbsp;\]/" \
-e 's/<table>/<table cellpadding="4">/' $4.html > $3.html

sed -e 's/h1><p>/h1>\
<div>/' \
-e 's/^<p>/<div>/' \
-e 's/^<\/p>/<\/div>/' \
-e 's/<a name/<a class="a-id" id/' $4_bib.html > $3_bib.html
