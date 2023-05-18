import {Alert, Button, FlatList, Linking, Text, TouchableHighlight, View} from 'react-native';
import React, {useEffect, useState} from 'react';
import {createNativeStackNavigator} from "@react-navigation/native-stack";
import Plotly from "react-native-plotly";

//local components
import {styles} from "./stylesheet";
import {callurl, status} from "./LocalTypes";
import {convertToDate} from "react-native-chart-kit/dist/contribution-graph/DateHelpers";

const MStack = createNativeStackNavigator();

type SetupProps = {
  url: string,
  children: string,
};

//Screens

const Welcome = ({navigation}: any) => {
  return (<View style={styles.containercol}>
    <TouchableHighlight style={styles.touchablesimp} underlayColor={'#009090'} onPress={() => navigation.navigate('Setup')}>
      <Text>Go to setup</Text>
    </TouchableHighlight>
    <TouchableHighlight style={styles.touchablesimp} underlayColor={'#009090'} onPress={() => navigation.navigate('Status')}>
      <Text>Go to status</Text>
    </TouchableHighlight>
  </View>)
}

const Setup = () => {
  return (
      <View style={styles.containercol}>
        <UrlButton url={callurl + 'auth_homeconnect'}>Home Connect Authorization</UrlButton>
      </View>
  )
};

const TaskStatus = () => {

  const [status, setStatus] = useState<status[]>([]);
  const [up, flip] = useState<boolean>(false);
  const [pdata, uppdataa] = useState<any[]>([{
      x: [1, 2, 3, 4, 5],
      y: [1, 2, 3, 4, 8],
      type: 'scatter',
  }]);
  const layout = {
        xaxis: {title: "Date"},
        yaxis: {title: "kw"},
        title: "Status"
  };

  useEffect(()=> {
    const interval = setInterval(() => {flip(!up);}, 10000);
    async function updateStatus(){
      let temp = await getStatus();
      uppdataa(await getStats());
      if(temp.length != 0){
        setStatus(temp);
      }
    }
    updateStatus().then();
    return () => clearInterval(interval);
  },[up]);



  const renderItem = ({item}: {item: status}) => {

    const backgroundcolor = item.running ? '#8FD16E' : '#B33A3A';

    return (<View style={{flexDirection: 'row', justifyContent: 'space-evenly'}}>
      <Text>{item.devicename}</Text>
      <Text>Running Status:</Text>
      <Text style={{backgroundColor: backgroundcolor}}>{String(item.running)}</Text>
      <Text>Finished:</Text>
      <Text>{String(item.finished)}</Text>
    </View>)
  }



  return (<View style={styles.containercol}>
    <Plotly data={pdata} layout={layout}/>
    <FlatList contentContainerStyle={styles.flatList} data={status} renderItem={renderItem}/>
  </View> );
}


//Requests
async function getStatus(): Promise<status[]> {

  const rdata: status[] = [];
  try {
    const response = await fetch(callurl + 'jobStatus', {method: 'GET'});

    let temp = JSON.parse(await response.text());


    for(let i = 0; i < temp.length; i++){
      rdata.push({finished: temp[i].finished, running: temp[i].running, devicename: temp[i].device.name});
    }

    return rdata;
  }
  catch(error){
      console.log(error + 'On status call');
    return rdata;
  }
}

async function getStats(): Promise<any> {

    let retdata;
    try {
        const response = await fetch(callurl + 'stats', {method: 'GET', headers: {'Content-Type':'application/json'}});
        let json = JSON.parse(await response.text());

        retdata = [
            { x: json.forecastx.map(convertToDate), y: json.forecasty, mode:"lines", name:"Forecast"},
            { x: json.prodx.map(convertToDate), y: json.prod, mode:"lines", name: "history"},
            { x: json.xdraw, y: json.ydraw, mode:"lines", name:"device draw"}
        ];
    }
    catch (error){
        console.log(error + 'on stats');
    }

    return retdata;
}

async function buttonPress(callUrl: string): Promise<void>  {
  try {
    const response = await fetch(callUrl, {method: 'GET'});
      return Linking.openURL(response.url);
  }
  catch(error){
    Alert.alert('The Following Error has occurred:' + error);

    return;
  }
}

//local component
const UrlButton = ({url, children}: SetupProps) => {
  return(
      <Button title={children} onPress={() => buttonPress(url)}/>
  );
}

//Main element
function Home(): JSX.Element {
  return (
   <MStack.Navigator initialRouteName={'Welcome'}>
     <MStack.Screen name={'Welcome'} component={Welcome}/>
     <MStack.Screen name={'Setup'} component={Setup}/>
     <MStack.Screen name={'Status'} component={TaskStatus}/>
   </MStack.Navigator>
  );
}




export default Home;
