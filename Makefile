KEYWORDS: *.txt
	grep --no-filename keywords: *.txt\
	| cut --delimiter=' ' --fields=2-\
	| sort\
	| uniq\
	> KEYWORDS
