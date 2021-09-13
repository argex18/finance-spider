import pymongo
from os import system


def mongo_checkup(**kwargs) -> int:
    mongodb_params = {
        "db_uri": kwargs["db_uri"] if kwargs["db_uri"] else None,
        # "db_name": kwargs["db_name"] if kwargs["db_name"] else None,
        # "db_host": kwargs["db_host"] if kwargs["db_host"] else None,
        # "db_port": kwargs["db_port"] if kwargs["db_port"] else None,
    }

    try:
        if not mongodb_params["db_uri"]:
            raise AttributeError("Error: missing mandatory argument 'db_uri'.")

        mongo_db = pymongo.MongoClient(f"{mongodb_params['db_uri']}")
        if mongo_db is None:
            if system("service MongoDB status") is not 0:
                print("MongoDB service isn't running on the current machine")
                raise SystemError()
        return 0

    except AttributeError as ae:
        for arg in ae.args:
            print(arg)
        print("Impossible to establish a database connection.")
        return -1
    except SystemError as se:
        for arg in se.args:
            print(arg)
        print("Problems with the MongoDB service spotted on the system")
        return -2
