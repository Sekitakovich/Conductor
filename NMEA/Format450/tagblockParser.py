class TagBlockParser:

    ''' analyze tagblock and returns dict '''

    def parse(self, src):
        result = {}
        for c in src.split(','):
            ppp = c.split(':')
            result[ppp[0]] = ppp[1]

        return result

if __name__ == '__main__':

    tb = TagBlockParser()
    print(tb)

