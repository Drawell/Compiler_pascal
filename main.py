import os
import mel_parser



def main():
    prog = mel_parser.parse('''
            
        ''')
    print(*prog.tree, sep=os.linesep)

if __name__ == '__main__':
    main()