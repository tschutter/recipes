KEYWORDS:=../KEYWORDS.txt
METAKEYS:=../METAKEYS.txt
README:=../README.md

all: $(KEYWORDS) $(METAKEYS) $(README)

clean:
	rm $(KEYWORDS) $(METAKEYS) $(README)

$(KEYWORDS): ../r/*.md
	grep --no-filename keywords: ../r/*.md\
	| grep -v "^keywords:$$"\
	| sed 's/.*keywords: *//'\
	| awk '{c=split($$0, s, ","); for (n=1; n<=c; n++) print s[n] }'\
	| sed 's/^  *//'\
	| sort\
	| uniq -c\
	> $(KEYWORDS)

$(METAKEYS): ../r/*.md
	grep --no-filename --only-matching "^- [^:]*:" ../r/*.md\
	| sort\
	| uniq -c\
	> $(METAKEYS)

$(README): ../r/*.md
	./build_readme.py
