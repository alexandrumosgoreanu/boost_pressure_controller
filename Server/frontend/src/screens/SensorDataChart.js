import React, { useEffect, useRef, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  //ResponsiveContainer,
} from "recharts";
import { Row, Container } from "react-bootstrap";


const SensorChart = () => {
  const ws = useRef();
  const [data, setData] = useState([]);

  useEffect(() => {
    //Send request to our websocket server using the "/request" path
    ws.current = new WebSocket("ws://192.168.100.149:3000");
    
    ws.current.onopen = (ev) => {
      console.log("Connection opened");
    }

    ws.current.onmessage = (ev) => {
      const message = JSON.parse(ev.data);
      let newDataArray = [
        ...data,
        {
          id: message.date,
          targetBoost: message.targetBoost,
          actualBoost: message.actualBoost,
        },
      ];
      console.log(newDataArray);
      setData((currentData) => limitData(currentData, message));
    };

    ws.current.onclose = (ev) => {
      console.log("Client socket close!");
    };

    //We limit the number of reads to the last 100 readings and drop the last read
    function limitData(currentData, message) {
      if (currentData.length > 100) {
        console.log("Limit reached, dropping first record!");
        currentData.shift();
      }
      return [
        ...currentData,
        {
          id: message.date,
          targetBoost: message.targetBoost,
          actualBoost: message.actualBoost,
        },
      ];
    }

    return () => {
      console.log("Cleaning up! ");
      ws.current.close();
    };
  }, []);

  //Display the chart using rechart.js
  return (
    <Container className="p-3">
      <Row className="justify-content-md-center">
        <h1 className="header">Real time MAP Sensor Data Using Websockets</h1>
      </Row>
      <Row className="justify-content-md-center">
        <div style={{ width: 1200, height: 600 }}>
         
            <LineChart
              width={1200}
              height={600}
              data={data}
              margin={{
                top: 0,
                right: 0,
                left: 0,
                bottom: 0,
              }}
            >
              <CartesianGrid strokeDasharray="2 2" />
              <XAxis 
                dataKey="id" 
                tick={{fontSize: 6}} 
                tickCount="5"/>
              <YAxis
                name = "Presiune" 
                label="Bar"
                scale="linear"
                tick={{fontSize: 8}}
                tickCount="15"
                domain={[-0.10, 1.6]}
                padding={{ top: 20, bottom: 20 }}
                />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="targetBoost"
                stroke="#FF0000"
                activeDot={{ r: 8 }}
                strokeDasharray="2 2"
              />
               <Line
                type="monotone"
                dataKey="actualBoost"
                stroke="#0000FF"
                activeDot={{ r: 8 }}
                strokeWidth="1"
              />
              {/* <Line type="monotone" dataKey="uv" stroke="#82ca9d" /> */}
            </LineChart>
        
        </div>
      </Row>
    </Container>
  );
};

export default SensorChart;
