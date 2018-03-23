KEYWORDS:=../KEYWORDS
README:=../README.md

all: $(KEYWORDS) $(README)

clean:
	rm $(KEYWORDS) $(README)

$(KEYWORDS): ../r/*.txt
	grep --no-filename keywords: ../r/*.txt\
	| grep -v "^keywords:$$"\
	| cut -d ' ' -f 2-\
	| awk '{c=split($$0, s, ","); for (n=1; n<=c; n++) print s[n] }'\
	| sed 's/^  *//'\
	| sort\
	| uniq -c\
	> $(KEYWORDS)

$(README): ../r/*.txt
	./build_readme.py
