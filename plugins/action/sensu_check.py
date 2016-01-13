from ansible.utils import parse_kv, template


class ActionModule(object):
    """
    TODO: FIXME when upgrading to Ansible 2.x
    """

    TRANSFERS_FILES = False

    def __init__(self, runner):
        self.runner = runner
        self.basedir = runner.basedir

    def _arg_or_fact(self, arg_name, fact_name, args, inject):
        res = args.get(arg_name)
        if res is not None:
            return res

        template_string = '{{ %s }}' % fact_name
        res = template.template(self.basedir, template_string, inject)
        return None if res == template_string else res

    def _merge_args(self, module_args, complex_args):
        args = {}
        if complex_args:
            args.update(complex_args)

        kv = parse_kv(module_args)
        args.update(kv)

        return args

    def run(self, conn, tmp, module_name, module_args, inject, complex_args=None, **kwargs):
        args = self._merge_args(module_args, complex_args)

        check_handler = self._arg_or_fact('handler', 'monitoring.check_handler', args, inject)

        complex_args['handler'] = check_handler
        module_return = self.runner._execute_module(conn, tmp, 'sensu_check', module_args, inject=inject,
                                             complex_args=args)

        return module_return
