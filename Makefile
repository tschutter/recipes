all: KEYWORDS index.html

KEYWORDS: *.txt
	grep --no-filename keywords: *.txt\
	| grep -v "^keywords:$$"\
	| cut --delimiter=' ' --fields=2-\
	| awk '{c=split($$0, s, ","); for (n=1; n<=c; n++) print s[n] }'\
	| sed 's/^  *//'\
	| sort\
	| uniq --count\
	> KEYWORDS

index.html: *.txt
	./BUILD_INDEX.py
