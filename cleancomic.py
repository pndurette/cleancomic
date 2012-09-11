import os, sys, argparse
import traceback

# Process arguments
parser = argparse.ArgumentParser(description="Cleans up CBZ files for better reading on eReaders")
parser.add_argument("target",
					help="CBZ file | directoy containing CBZ files to clean up")
parser.add_argument("-b", "--boost",
					help="Attempts to boost contrast.",
					action="store_true")
parser.add_argument("-c", "--crop",
					help="Attempts to crop white space.",
					action="store_true")
					# add % (imagemagick)
parser.add_argument("-s", "--split",
					help="Split pages vertically, in the middle (for side-by-side page scans).",
					action="store_true")
parser.add_argument("--pretend",
					help="Applies only to one page and saves it as pretend[0/1].jpg for preview.",
					action="store_true")
args = parser.parse_args()

# Cleans one comic
def cleanOne(comicpath):
	print args.target

def isCbz(comicpath):
	pass

# Main execution
if __name__ == "__main__":
	# detect if args.target is dir, if yes, call clean on each
	# else call clean on each
	if os.path.isdir(args.target):
		pass
	elif os.path.isfile(args.target) and isCbz(args.target):
		pass
	else:
		# Check if it's not a cbz / zip etc.
		# Else quit
		pass
