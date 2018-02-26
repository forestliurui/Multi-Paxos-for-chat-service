import yaml
from subprocess import call

def server_script_mode(config_file):

    with open(config_file, 'r') as config_handler:
        config = yaml.load(config_handler)

    f = int(config['f']) #the number of failure that can be tolerated

    num_server = 2*f + 1

    call(['bash','start_servers.sh', str(num_server), config_file])




if __name__ == "__main__":
    from optparse import OptionParser, OptionGroup

    parser = OptionParser(usage = "Usage!")
    options, args = parser.parse_args()
    options = dict(options.__dict__)

    server_script_mode(*args, **options)





