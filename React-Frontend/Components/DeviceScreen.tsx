import 'react-native-gesture-handler';
import React, {useEffect, useState} from 'react';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {FlatList, Text, View, TouchableHighlight, Alert} from 'react-native';

//Local components
import {FlatItem} from './FlatItem';
import {styles} from './stylesheet';
import {callurl, machine} from "./LocalTypes";

const Stack = createNativeStackNavigator();


//Screens:
const MachineScreen = ({route}: any) => {
  const itemId = route.params.itId;
  const title = route.params.title;

  return (
    <View style={styles.deviceView}>
      <Text>Device name: {title}</Text>
      <Text>Device ID: {itemId}</Text>
      <TouchableHighlight>
        <Text>Confirm update</Text>
      </TouchableHighlight>
    </View>
  );
};

const AddDeviceScreen = () => {
  return (
    <View style={styles.containercol}>
      <Text>Add Device info here</Text>
        <TouchableHighlight onPress={searchDevices}>
            <Text>Find devices</Text>
        </TouchableHighlight>
    </View>
  );
};

const Mainscreen =  ({navigation}: any) => {

    const [dData, setdData] = useState<machine[]>()

    useEffect(() => {
        async function getdata(){
            const devicedata = await searchDevices();
            setdData(devicedata);

        }
        getdata().then();
    }, []);


    const renderitem = ({item}: { item: machine }) => {
        const backgroundcolor = '#38702d';
        const color = '#ffffff';
        const title: string = item.name;
        const itID: number = item.id;

        return (
            <FlatItem
                item={item.name}
                backgroundColor={backgroundcolor}
                textColor={color}
                onpress={() =>
                    navigation.navigate('Machine', {itId: itID, title: title})
                }
            />
        );
    };
    return (
        <View style={styles.containercol}>
            <FlatList
                ItemSeparatorComponent={({highlighted}) => (
                    <View style={[styles.sepStyle, highlighted && {marginLeft: 0}]}/>
                )}
                data={dData}
                renderItem={renderitem}
                keyExtractor={item => item.id.toString()}
                contentContainerStyle={styles.flatList}
            />
            <TouchableHighlight style={styles.touchablesimp} onPress={() => navigation.navigate('Add Device')}>
                <Text>Add Device</Text>
            </TouchableHighlight>
        </View>
    );
};


//Requests:
const searchDevices = async () => {

    let jdata;
    try {
        const response = await fetch(callurl + 'Devices/FindDevices', {method: 'GET', headers: {'Content-Type':'application/json'}}).then();
        jdata = JSON.parse(await response.text());

    }
    catch(error){
        Alert.alert('Sorry, an error happened');
        console.log(error);
        const failure: machine[] = [{
            brand: "Error",
            connected: false,
            enumber: "Error",
            id: 0,
            name: "Error",
            type: "Error",
            vib: "Error",
            API_type: "Error"
        },];
        return failure;
    }

    const devicekeys = [];
    for(let x in jdata){
        devicekeys.push(x);
    }

    let machines: machine[] = [];

    for(let i = 0; i < devicekeys.length; i++){
        machines.push(jdata[devicekeys[i]]);
    }

    return machines;
};


//Main component
export function Devices(): JSX.Element {
  return (
    <Stack.Navigator initialRouteName={'Main'}>
      <Stack.Screen name={'Machine'} component={MachineScreen} />
      <Stack.Screen name={'Add Device'} component={AddDeviceScreen} />
      <Stack.Screen name={'Main'} component={Mainscreen} />
    </Stack.Navigator>
  );
}
