import argparse


if __name__ == "__main__":
	description = "a fucking damn dns"
	parser = argparse.ArgumentParser(description=description)

	parser.add_argument('-P', '--port',
						help='Port used for the request.',
						required=True)
	parser.add_argument('-C', '--cache',
						help='Cache Timeout in [ms], default value is 3600.',
						type=int)

	args = parser.parse_args()

	port = args.port
	
	cache_timeout = 3600
	if args.cache_timeout:
		cache = args.cache_timeout



