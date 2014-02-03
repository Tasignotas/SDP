import nxt


class Connection:


    def __init__(self, name='NXT'):
        print 'Connecting to NXT Brick with name %s' % name
        self.brick = nxt.locator.find_one_brick(
            name=name, method=nxt.locator.Method(usb=False))
        if self.brick:
            print 'Connection successful.'


    def close(self):
        """
        TODO
        Close connection to the brick, return success or failure.
        """
        pass