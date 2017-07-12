import subprocess

class DD(object):

    @staticmethod
    def run_io(iocfg):
        """ Executes dd command based on the config argument.
            - Args :
                  - IO Configuration for dd command.
            - Returns :
                  - True on success, False on failure.
        """
        cmd = "dd if=" + iocfg['IF'] + " of=" + iocfg['OF'] + \
            " bs=" + iocfg['BS'] + " count=" + iocfg['COUNT']

        print(" Running IOs now CMD :------- " + cmd)

        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        ret = True
        if proc.wait() != iocfg['RC']:
            print("ERROR : Failed to execute " + cmd + ".")
            ret = False

        return ret 
