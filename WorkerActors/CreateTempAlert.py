from calvin.actor.actor import Actor, condition
# from calvin.runtime.north.calvin_token import ExceptionToken


class ComputeAverage(Actor):
    """
      Get the input temperature value sensor and creates an event token on the outport'
      Inputs :
        temp_sensor : integer
      Output :
        result : an integer
    """

    def init(self):
        self.result = result

    @condition(action_input=['temp_sensor'], action_output=['result'])
    def decide_event(self, temp_network, temp_sensor):
        """Normal case, return division"""
        if temp_sensor > 100:
            self.result = "high"
        if  temp_sensor < 50:
            self.result = "low"

    @condition(action_input=['temp_sensor'], action_output=['result'])
    def trigger_event(self, temp_network, temp_sensor):
        """Normal case, return division"""
        if temp_sensor > 100:
            result = "high"
        if temp_sensor < 50:
            result = "low"
        return (result,)

    action_priority = (decide_event, )