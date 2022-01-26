from utils import getMetadata, getArgs

if __name__ == "__main__":
    args = getArgs()
    getMetadata(args.output_dir)
