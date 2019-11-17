# Showcase Big Data

1. Install docker (see (docker installation instructions)[https://docs.docker.com/install/]) 
2. Run docker-compose: ```docker-compose up```

    * JupyterLab is available at: [http://localhost:8888](http://localhost:8888)
    * Kibana is available at: [http://localhost:5601](http://localhost:5601)
    * Elasticsearch is available at: [http://localhost:9201](http://localhost:9201) and [http://localhost:9202](http://localhost:9202) 

3. In JupyterLab: Open the notebook notebooks/showcase_big_data.ipynb

4. Start simulation: run the notebook and then hit the "Start" button

5. Access [Kibana](http://localhost:5601) and go to the Discover page

6. Setup the index pattern ```*_car```, using ```timestamp``` for the time dimension 

7. On the "Visualize" page: Create  a line visualisation that shows revenue over time (you need to set up a bucket for the X-axis/Histogram/time with interval 1) and save it.

8. Create another line visualisation with  ```total revenue / time``` 

9. Create a heatmap visualisataion with a 20x20 grid for the taxi positions (pos_x, pos_y)

9. Create a dashboard that shows the visualisations (last 15min). Set it to refresh automatically every 10s.  Save the dashboard.

10. Go to the management page and chose export. This create an export.ndjson file which you import next time you start the showcase, via the import button.

    HINT: you can find predefined dashboards in  ```kibana\big_data.ndjson```.

11. Turn on Kibana stack monitoring - you should see two nodes with 9 master shards and 9 replica shards

12. Run some experiments with ``elasticsearch``:

    * From the stack monitoring page, go into the nodes page - this shows you how the shards are distributed over the nodes
    * Add a third ES node: ```docker run -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" -e "node.name=es_node3" -e "node.master=false" -e "node.data=true" -e "discovery.seed_hosts=es_node1,es_node2" -e "cluster.name=showcase_cluster" --network showcase_big_data_bdn --name es_node3 -p 9203:9200 elasticsearch:7.4.1```
    * Stop that node: ```docker stop es_node3``` and see what happens to the replica shards (you can now remove the container with ```docker rm es_node3```)

    * Reset all containers (```docker-compose down``` followed by ```docker-compose up```)  and now start the simulation with 10 cars (change the config in JupyterLab ```/scenarios/abm.json``` before starting the simulation: ```CARMODEL.scenarios.scenario.agents[car].count:10```). See how many shards there are now.

