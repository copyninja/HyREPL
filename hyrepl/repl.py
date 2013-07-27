from hy.lex.machine import Machine
from hy.compiler import hy_compile
from hy.importer import ast_compile, hy_eval, import_buffer_to_hst
from hy.lex import tokenize
import imp
import sys
import traceback
from io import StringIO




class Repl(object):
    """Repl simulation."""

    # As with normal hy evulation, everything is in reality a top level module.
    mod = imp.new_module("__main__")

    def eval(self, code):
        """Evals the given code.
           Returns a dict with reponses."""
        self.ret = []

        # We might catch errors when tokenizing code.
        try:
            tokens = tokenize(code)
        except:
            self._format_excp(sys.exc_info())
            return self.ret

        # Setting stdout in a way so we can catch anything printed and return that
        oldout = sys.stdout
        oldin = sys.stdin
        stdout = None
        sys.stdout = StringIO()

        for i in tokens:
            try:
                p = str(hy_eval(i, self.mod.__dict__, "__main__"))
            except:
                self._format_excp(sys.exc_info())
            else:
                self.ret.append({"value": p, "ns": 'None'})
                # If there is nothing in return, we see if anything is in stdout
                if p == "None":
                    stdout = sys.stdout.getvalue()
                    if stdout:
                        self.ret.append({'out': stdout})
        
        sys.stdout = oldout
        return self.ret

    def _format_excp(self, trace):
        # Format return exception
        exc_type, exc_value, exc_traceback = trace
        self.ret.append({'status': ['eval-error'], 'ex': exc_type.__name__, 'root-ex': exc_type.__name__})
        self.ret.append({'err': str(exc_value)})



    def eval_file(*args):
        """MIA"""
        pass
