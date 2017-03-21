from calvin.actor.actor import Actor, condition, guard, ActionResult
from calvin.runtime.north.calvin_token import ExceptionToken

class InputAverage(Actor):
    """
      Averages input on port 'temp1' with input on port 'temp2'
      Inputs :
        temp1 : integer
        temp2 : integer
      Output :
        result : an integer
    """

    def init(self):
        pass

    @condition(action_input=[('temp1', 1), ('temp2', 1)], action_output=[('result', 1)])
    @guard(lambda self, n, d: d != 0)
    def divide(self, temp1, temp2):
        """Normal case, return division"""
        result = (temp1 + temp2) / 2
        return ActionResult(production=(result,))

    @condition(action_input=[('temp1', 1), ('temp2', 1)], action_output=[('result', 1)])
    @guard(lambda self, n, d: (n+d) == 0)
    def divide_by_zero(self, temp1, temp2):
        """Exceptional case: return exception token"""
        result = ExceptionToken("Division by 0")
        return ActionResult(production=(result,))

    action_priority = (divide_by_zero, divide)