import penman
from server.server import Server

if __name__ == "__main__":
    graphs = penman.load("C:/Users/jonas/Documents/Work/data/Edinburgh/amr3.0/data/amrs/split/dev/"
                         "amr-release-3.0-amrs-dev-bolt.txt")

    print(len(graphs))
    print(graphs[0])

    server = Server(graphs)
    server.start()


