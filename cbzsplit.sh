#! /bin/sh

# create empty dir

# For each book in dir
#	create empty directory from filename in tmpdir
#	unzip there
#	process all files (split etc)
#	zip, -split.cbz, copy back to first dir.

TMPDIR="$(mktemp -d -t cbzsplit)"
#trap "rm -rf '$TMPDIR'" EXIT INT HUP TERM
echo "TMPDIR: ${TMPDIR}"

# Check args..
# $1 exists.. dr_slump_tome_01.cbz

#find $1 -type f | grep "cbz$" | while read COMIC
find $1 -type f | grep "dr_slump_tome_01.cbz" | while read COMIC
do
	COMIC_FILENAME=$(basename ${COMIC})
	echo "Processing ${COMIC_FILENAME}..."
	PAGE=0
	
	cp ${COMIC} ${TMPDIR}
	cd ${TMPDIR}
	
	COMIC_CONTENTS="${COMIC_FILENAME%.*}"
	mkdir ${COMIC_CONTENTS}
	unzip -j ${COMIC_FILENAME} -d ${COMIC_CONTENTS} >/dev/null
	rm ${COMIC_FILENAME}
	
	#mogrify -format jpg -crop 50%x100% 02.jpg #split in 2
	#convert 03.jpg -fuzz 80% -trim +repage 03_trim.jpg #trim around with fuzz
	#convert 03.jpg -chop 5×10 -rotate 180 -chop 5×10 -rotate 180 03_crop.jpg #crop sides (10 cotés, 5 top bas)
	
done

# http://dahlia.kr/wand/