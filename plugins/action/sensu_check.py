from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    def _get_handler(self, args, task_vars):
        handler = args.get('handler')
        if handler is not None:
            return handler

        fact = task_vars.get('monitoring', {}).get('check_handler')
        return None if handler == fact else handler

    def run(self, tmp=None, task_vars=None):
        args = self._task.args.copy()
        args['handler'] = self._get_handler(args, task_vars)
        return self._execute_module(
            module_name='sensu_check', module_args=args, task_vars=task_vars
        )
