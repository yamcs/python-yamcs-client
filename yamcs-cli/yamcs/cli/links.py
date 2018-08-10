def list_(args):
    print('links', args)


def enable(args):
    print('enable', args)


def configure_list(parser):
    parser.set_defaults(func=list_)


def configure_enable(parser):
    parser.add_argument('links', metavar='<name>', type=str, nargs='+', help='name of the link', default=enable)
    #parser.set_defaults(func=enable)


def configure_parser(parser):
    # parser.set_defaults(func=list_)
    subparsers = parser.add_subparsers(title='commands', metavar='<command>')
    
    list_parser = subparsers.add_parser('list', help='List links')
    configure_list(list_parser)
    
    enable_parser = subparsers.add_parser('enable', help='Enable a link')
    configure_enable(enable_parser)

    disable_parser = subparsers.add_parser('disable', help='Disable a link')
    describe_parser = subparsers.add_parser('describe', help='Describe link')
