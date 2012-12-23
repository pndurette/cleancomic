import os, sys, argparse, re
import zipfile, zlib, tempfile, shutil
import traceback

import subprocess

#from wand.image import Image
#from wand.display import display

# TODO: Cbz not found: doesn't do anything
# TODO: Use Wand
# TODO: --contrast
# TODO: --pretend
# TODO: check destination exists
# TODO: add % fuzz (trim imagemagick)
# TODO: intelligent trim depeding on right-to-left

# Process arguments
def processArguments():
	#parser = argparse.ArgumentParser(description="Cleans up CBZ files for better reading on e-readers", formatter_class=RawTextHelpFormatter) # 2.7+
	parser = argparse.ArgumentParser(description="Cleans up CBZ files for better reading on e-readers")
	parser.add_argument("source", help="CBZ file | directoy containing CBZ files to clean up")
	parser.add_argument("destination", help="Where to save the processed comic(s)")
	parser.add_argument("--pretend", help="Applies only to one page and saves it as pretend[0/1].jpg for preview",action="store_true")
	parser.add_argument("--right", help="Specify this is a right-to-left book.\n--trim and --split will take this into account.",action="store_true")
	
	actions = parser.add_argument_group('Actions')
	actions.add_argument("-c", "--contrast", help="Attempts to boost contrast", action="store_true")
	actions.add_argument("-t", "--trim", help="Attempts to trim white space", action="store_true")
	actions.add_argument("-s", "--split", help="Split pages vertically, in the middle\n(for side-by-side page scans)", action="store_true")
	args = parser.parse_args()
	
	if not (args.contrast or args.trim or args.split):
		parser.error('You need to specify at least one action. See --help')
	args.destination = os.path.abspath(args.destination)
	return args

# Cleans one comic
def cleanOne(comic_path):
	args = processArguments()
	if not zipfile.is_zipfile(comic_path):
		print "Error: %s skiped. Doesn't appear to be a zip file." % os.path.basename(comic_path)
		return
	
	# Create "<cbz_name>" dir inside <tmp dir> (for the zip)
	(cbz_dir, cbz_name) = os.path.split(comic_path)
	(cbz_basename, cbz_extension) = os.path.splitext(cbz_name)
	
	cbz_work_dir = tempfile.mkdtemp()
	os.mkdir("%s/%s" % (cbz_work_dir, cbz_basename))
	cbz_work_dir = "%s/%s" % (cbz_work_dir, cbz_basename)
	print "The cbz_work_dir: %s" % cbz_work_dir
	
	# Extract
	doExtract(comic_path, cbz_work_dir)
			
	# Actions
	if args.split: doSplit(cbz_work_dir, args.right)
	if args.trim: doTrim(cbz_work_dir, args.right)
	#if args.contrast: doContrast(cbz_work_dir)
	
	# Recompress
	doCompress(cbz_work_dir, args.destination, cbz_name)
	
	# Cleanup
	shutil.rmtree(cbz_work_dir)

def doExtract(comic_path, work_dir):
	cbz = zipfile.ZipFile(comic_path, 'r')
	for member in cbz.namelist():
		fname = os.path.basename(member)
		# If dir/<file> match standard cbz file (<digits>.jpg) extract it
		#if re.match("^\d*.jpg$", fname): 
		# skip directories
		if not fname: continue

		# copy file
		source = cbz.open(member)
		target = file(os.path.join(work_dir, fname), "wb")
		shutil.copyfileobj(source, target)
		source.close()
		target.close()
	cbz.close()
	
def doCompress(work_dir, dest, cbz_name):
	new_cbz = zipfile.ZipFile('%s/%s' % (dest, cbz_name), 'w', zipfile.ZIP_DEFLATED)
	for fname in os.listdir(work_dir):
		f = os.path.join(work_dir, fname)
		new_cbz.write(f, arcname = fname)
	new_cbz.close()
		
def doSplit(work_dir, rtl):
	for f in os.listdir(work_dir):
		subprocess.call("mogrify -format jpg -crop 50%%x100%% %s/%s" % (work_dir, f), shell=True)
		
	# Renumber files to xxx.jpg
	filecount = 0
	if rtl:
		# Right to left
		i = -1
		file_list = os.listdir(work_dir)
		maxf = len(file_list)
	
		# If pages are A, B, C, D, E, F, they become B, A, D, C, F, E
		while (i < maxf):
			i += 2
			if not i >= maxf:
				print file_list[i], filecount
				os.rename("%s/%s" % (work_dir, file_list[i]),"%s/%03d.jpg" % (work_dir, filecount))
				filecount += 1
				print file_list[i-1], filecount
				os.rename("%s/%s" % (work_dir, file_list[i-1]),"%s/%03d.jpg" % (work_dir, filecount))
				filecount += 1
	else:
		# Left to right
		for f in os.listdir(work_dir):
			os.rename("%s/%s" % (work_dir, f),"%s/%03d.jpg" % (work_dir, filecount))
			filecount+=1

def doTrim(work_dir, ltr):
	for f in os.listdir(work_dir):
		fpath = os.path.join(work_dir, f)
		subprocess.call("convert %s -chop 5x5 -rotate 180 -chop 20x5 -rotate 180 %s" % (fpath,fpath), shell=True)
		subprocess.call("convert %s -fuzz 40%% -trim +repage %s" % (fpath, fpath), shell=True)
	
def doContrast():
	pass	

# Main
def main():
	args = processArguments()
	if os.path.isdir(args.source):
		path = os.path.split(args.source)[0]
		filelist = os.listdir(args.source)
		for f in filelist: cleanOne(os.path.join(path, f))
	elif os.path.isfile(args.source):
		cleanOne(args.source)

# Execution
if __name__ == "__main__":
	main()
