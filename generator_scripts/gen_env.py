def generate_env(_name="net"):
    """
    This function will generate a .env file at the current working directory
    :param _name: Name of the Docker Compose project. Just leave it at "net"
    """
    f = open(".env", "w")
    f.write("COMPOSE_PROJECT_NAME={}".format(_name))
    f.close()
    print("========================================")
    print(">>> .env has been dumped!")
    print("========================================")
