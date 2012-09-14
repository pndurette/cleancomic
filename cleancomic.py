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


# Process arguments
def processArguments():
	parser = argparse.ArgumentParser(description="Cleans up CBZ files for better reading on eReaders")
	parser.add_argument("source",
						help="CBZ file | directoy containing CBZ files to clean up")
	parser.add_argument("destination",
						help="Where to save the processed comic(s)")
	parser.add_argument("--pretend",
						help="Applies only to one page and saves it as pretend[0/1].jpg for preview",
						action="store_true")
	actions = parser.add_argument_group('Actions')
	actions.add_argument("-c", "--contrast",
						help="Attempts to boost contrast",
						action="store_true")
	actions.add_argument("-t", "--trim",
						help="Attempts to trim white space",
						action="store_true")
	actions.add_argument("-r", "--right",
						help="Specify this is a right-to-left book. --trim and --split will take this into account.",
						action="store_true")
	actions.add_argument("-s", "--split",
						help="Split pages vertically, in the middle (for side-by-side page scans)",
						action="store_true")
	args = parser.parse_args()
	if not (args.contrast or args.trim or args.split):
		parser.error('You need to specify at least one action. See --help')
	args.destination = os.path.abspath(args.destination)
	return args

# Cleans one comic
def cleanOne(comic_path):
	args = processArguments()
	# Determine if comic_path is a zip (cbz) file
	if not zipfile.is_zipfile(comic_path):
		print "Error: %s skiped. Doesn't appear to be a zip file." % os.path.basename(comic_path)
	else:
		# 0. Init
		(cbz_dir, cbz_name) = os.path.split(comic_path)
		(cbz_basename, cbz_extension) = os.path.splitext(cbz_name)
		
		# Create "<cbz_name>" dir inside <tmp dir> (for the zip)
		cbz_work_dir = tempfile.mkdtemp()
		os.mkdir("%s/%s" % (cbz_work_dir, cbz_basename))
		cbz_work_dir = "%s/%s" % (cbz_work_dir, cbz_basename)
		print "The cbz_work_dir: %s" % cbz_work_dir
		
		# 1. Extract
		print comic_path
		cbz = zipfile.ZipFile(comic_path, 'r')
		for member in cbz.namelist():
			fname = os.path.basename(member)
			# If dir/<file> match standard cbz file (<digits>.jpg) extract it
			#if re.match("^\d*.jpg$", fname): 
			# skip directories
			if not fname: continue

			# copy file
			source = cbz.open(member)
			target = file(os.path.join(cbz_work_dir, fname), "wb")
			shutil.copyfileobj(source, target)
			source.close()
			target.close()
		cbz.close()
				
		# 2. Split
		if args.split:
			for f in os.listdir(cbz_work_dir):
				subprocess.call("mogrify -format jpg -crop 50%%x100%% %s/%s" % (cbz_work_dir, f), shell=True)
				
			# Renumber files to xxx.jpg
			# filecount = 0
			# for f in os.listdir(cbz_work_dir):
			# 	os.rename("%s/%s" % (cbz_work_dir, f),"%s/%03d.jpg" % (cbz_work_dir, filecount))
			# 	filecount+=1
			
			i = -1
			filecount = 0
			file_list = os.listdir(cbz_work_dir)
			maxf = len(file_list)
			
			while (i < maxf):
				i += 2
				if not i >= maxf:
					print file_list[i], filecount
					os.rename("%s/%s" % (cbz_work_dir, file_list[i]),"%s/%03d.jpg" % (cbz_work_dir, filecount))
					filecount += 1
					print file_list[i-1], filecount
					os.rename("%s/%s" % (cbz_work_dir, file_list[i-1]),"%s/%03d.jpg" % (cbz_work_dir, filecount))
					filecount += 1
				
		# 3. Trim
		if args.trim:	
			for f in os.listdir(cbz_work_dir):
				fpath = "%s/%s" % (cbz_work_dir, f)
				subprocess.call("convert %s -chop 5x5 -rotate 180 -chop 20x5 -rotate 180 %s" % (fpath,fpath), shell=True)
				subprocess.call("convert %s -fuzz 40%% -trim +repage %s" % (fpath, fpath), shell=True)
				
		# 4. Boost contrast
		# ...
		
		# 9. Recompress
		new_cbz = zipfile.ZipFile('%s/%s' % (args.destination, cbz_name), 'w', zipfile.ZIP_DEFLATED)
		for fname in os.listdir(cbz_work_dir):
			f = os.path.join(cbz_work_dir, fname)
			new_cbz.write(f, arcname = fname)
		new_cbz.close()

		# 10. Cleanup
		#shutil.rmtree(cbz_work_dir)
		
		

# Main
def main():
	args = processArguments()
	if os.path.isdir(args.source):
		filelist = os.listdir(args.source)
		for f in filelist: cleanOne(f)
	elif os.path.isfile(args.source):
		cleanOne(args.source)
	else:
		"Error: source is something else" #TODO fix this

# Execution
if __name__ == "__main__":
	main()