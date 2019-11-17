from src.visualization.modules import ChartModule

class ControllerChartModule(ChartModule):

    def render(self,model):
        current_values = []


        for s in self.series:
            id = s["Label"]


            val = model.agent(id).customer_average_waiting_time


            current_values.append(val)
        return current_values