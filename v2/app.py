import argparse
from domain.domain import Config
from api import api

# see https://www.uvicorn.org/
api.run()

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-a','--app_server',default='127.0.0.1')
#     parser.add_argument('-b','--app_port',default=8081, type=int)
#     parser.add_argument('-d','--db_server',default='localhost')
#     parser.add_argument('-p','--db_port',default=27017, type=int)
#     parser.add_argument('-c','--db_collection',default='LegoPlans')
#     args = parser.parse_args()

#     # TODO: Use a config...

#     api.run(Config(args.app_server,args.app_port, args.db_server, args.db_port, args.db_collection))
