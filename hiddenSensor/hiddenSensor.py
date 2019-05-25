import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x\n")
    sys.exit(1)


from lib.controller.Controller import Controller
from lib.argument.Argument import Argument
from thirdparty.dirsearch import CLIOutput


class hiddenSensor(object):
    def __init__(self):
        self.arguments = Argument()
        self.output = CLIOutput()
        self.controller = Controller(self.arguments, self.output)


if __name__ == '__main__':
    hiddenSensor()
