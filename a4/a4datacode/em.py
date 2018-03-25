class Case:

    def __init__(self, sloe, fori, dega, trimo, dunn):
        self.sloepnea = sloe
        self.foriennditis = fori
        self.degar_spots = dega
        self.trimono = trimo
        self.dunnetts = dunn


def load_data(filename):
    with open(filename, 'r') as f:
        for l in f.readlines():
            sloe, fori, dega, trimo, dunn = l.strip().split(' ')
            case = Case(sloe, fori, dega, trimo, dunn)
            print case


def main():
    load_data('traindata.txt')


if __name__ == '__main__':
    main()
