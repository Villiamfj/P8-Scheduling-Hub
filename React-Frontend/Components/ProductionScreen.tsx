import 'react-native-gesture-handler';
import React from 'react';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {Alert, FlatList, Text, TouchableHighlight, View,} from 'react-native';

//Local components
import {styles} from './stylesheet';
import {FlatItem} from './FlatItem';
import {callurl, machine} from "./LocalTypes";

export const PStack = createNativeStackNavigator();

//Requests
const searchDevices = async () => {
    try {
        return await fetch(callurl + 'Devices/FindDevices', {method: 'GET'});
    }
    catch(error){
        console.log(error);
        Alert.alert('Sorry, an error happened');
    }

    return;
};


//Screens
const Mainscreen = ({navigation}: any) => {
  const Dummy: machine[] = [{
      brand: "Error",
      connected: false,
      enumber: "Error",
      id: 0,
      name: "Error",
      type: "Error",
      vib: "Error",
      API_type: "Error"
  },];
  //const conDevices = searchDevices();

  const renderitem = ({item}: {item: machine}) => {
    const backgroundcolor = '#77c967';
    const color = '#000000';

    return (
      <FlatItem
        item={item.name}
        backgroundColor={backgroundcolor}
        textColor={color}
        onpress={() => navigation.navigate('Device')}
      />
    );
  };

  return (
    <View style={styles.containercol}>
      <FlatList
        data={Dummy}
        renderItem={renderitem}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.flatList}
      />
      <TouchableHighlight
        onPress={() => navigation.navigate('Add Device')}
        style={styles.touchablesimp}>
        <Text>Add Production device</Text>
      </TouchableHighlight>
    </View>
  );
};

const Devicescreen = () => {
  return (
    <View style={styles.deviceView}>
      <Text>Device Screen</Text>
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


//Main component
function Production(): JSX.Element {
  return (
    <PStack.Navigator initialRouteName={'Production Devices'}>
      <PStack.Screen name={'Production Devices'} component={Mainscreen} />
      <PStack.Screen name={'Device'} component={Devicescreen} />
      <PStack.Screen name={'Add Device'} component={AddDeviceScreen} />
    </PStack.Navigator>
  );
}

export default Production;
