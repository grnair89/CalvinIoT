from calvin.actor.actor import Actor, condition, guard, ActionResult
from calvin.runtime.north.calvin_token import ExceptionToken

class ComputeAverage(Actor):
    """
      Averages input temperature value received from network with input from local
      temperature sensor connected to actor node'
      Inputs :
        temp_network : integer
        temp_sensor : integer
      Output :
        result : an integer
    """

    def init(self):
        pass

    @condition(action_input=[('temp_network', 1), ('temp_sensor', 1)], action_output=[('result', 1)])
    @guard(lambda self, n, d: d != 0)
    def divide(self, temp_network, temp_sensor):
        """Normal case, return division"""
        result = (temp_network + temp_sensor) / 2
        return ActionResult(production=(result,))

    @condition(action_input=[('temp_network', 1), ('temp_sensor', 1)], action_output=[('result', 1)])
    @guard(lambda self, n, d: (n+d) == 0)
    def divide_by_zero(self, temp_network, temp_sensor):
        """Exceptional case: return exception token"""
        result = ExceptionToken("Division by 0")
        return ActionResult(production=(result,))

    # @condition(action_input=[('temp_network', 1), ('temp_sensor', 1)], action_output=[('result', 1)])
    # @guard(lambda self, n, s: (n + s) == 0)
    # def divide_by_zero(self, temp_network, temp_sensor):
    #     """Exceptional case: return exception token"""
    #     result = ExceptionToken("Division by 0")
    #     return ActionResult(production=(result,))

    action_priority = (divide_by_zero, divide)