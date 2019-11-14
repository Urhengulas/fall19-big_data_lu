from src.visualization.modules import ChartModule

class CarChartModule(ChartModule):

    def render(self,model):
        current_values = []


        for s in self.series:
            id = s["Label"]
            state = "CHARGING"

            val = model.agent(id).charge


            current_values.append(val)
        return current_values