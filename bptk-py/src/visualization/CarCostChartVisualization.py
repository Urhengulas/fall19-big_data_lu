from src.visualization.modules import ChartModule

class CarCostChartModule(ChartModule):

    def render(self,model):
        current_values = []


        for s in self.series:
            value_to_observe = s["Label"]

            val = 0

            agent_ids = model.agent_ids("CAR")

            for id in agent_ids:

                val += getattr(model.agent(id),value_to_observe)


            current_values.append(val)
        return current_values