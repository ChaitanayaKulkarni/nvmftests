from utils.shell import Cmd

ret = Cmd.exec_cmd("ls -lrth ")

print(ret)
