KEYWORDS:=../KEYWORDS.txt
README:=../README.md

all: $(KEYWORDS) $(README)

clean:
	rm $(KEYWORDS) $(README)

$(KEYWORDS): ../r/*.md
	grep --no-filename keywords: ../r/*.md\
	| grep -v "^keywords:$$"\
	| sed 's/.*keywords: *//'\
	| awk '{c=split($$0, s, ","); for (n=1; n<=c; n++) print s[n] }'\
	| sed 's/^  *//'\
	| sort\
	| uniq -c\
	> $(KEYWORDS)

$(README): ../r/*.md
	./build_readme.py
