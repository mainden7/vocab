from vocab.cli import parser


def main():
    parser = parser.get_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
