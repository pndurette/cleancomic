import os, sys, argparse, re
import zipfile, tempfile, shutil
import traceback

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
						# TODO add % fuzz (imagemagick)
	actions.add_argument("-s", "--split",
						help="Split pages vertically, in the middle (for side-by-side page scans)",
						action="store_true")
	args = parser.parse_args()
	if not (args.contrast or args.trim or args.split):
		parser.error('You need to specify at least one action. See --help')
	return args

# Cleans one comic
def cleanOne(comic_path):
	args = processArguments()
	# Determine if comic_path is a zip (cbz) file
	if not zipfile.is_zipfile(comic_path):
		print "Error: %s skiped. Doesn't appear to be a zip file." % os.path.basename(comic_path)
	else:
		# 0. Init
		cbz_work_dir = tempfile.mkdtemp()
		cbz_new_dir = tempfile.mkdtemp()
		print "The cbz_work_dir: %s" % cbz_work_dir
		print "The cbz_new_dir: %s" % cbz_new_dir
		
		# 1. Extract
		cbz = zipfile.ZipFile(comic_path, 'r')
		for f in cbz.namelist():
			# If file match standard cbz file (<digits>.jpg) extract it
			if re.match("^\d*.jpg$", f): 
				cbz.extract(f, cbz_work_dir)
		cbz.close()
		
		# Do things
		#if args.trim: actionTrim()
		
		# Re-compress to destination
		
		# 10. Cleanup
		shutil.rmtree(cbz_work_dir)
		shutil.rmtree(cbz_new_dir)
		
		

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