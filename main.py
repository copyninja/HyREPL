from hyrepl.connection import nREPLServerHandler

def main():
    try:
        t = nREPLServerHandler("127.0.0.1", 9999)
        t.start()
    except KeyboardInterrupt:
        t.stop()


if __name__ == '__main__':
    main()