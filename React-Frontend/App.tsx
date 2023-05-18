import 'react-native-gesture-handler';
import {NavigationContainer} from '@react-navigation/native';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import React from 'react';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';
import {StatusBar, StyleSheet, useColorScheme} from 'react-native';
import {Colors} from 'react-native/Libraries/NewAppScreen';

//Components added from internal
import {Devices} from './Components/DeviceScreen';
import Home from './Components/HomeScreen';
import Production from './Components/ProductionScreen';
import AddTask from './Components/AddTaskScreen';

const Tab = createBottomTabNavigator();

function App(): JSX.Element {
  const isDarkMode = useColorScheme() === 'dark';
  const backgroundStyle = {
    backgroundColor: isDarkMode ? Colors.darker : Colors.lighter,
  };

  return (
    <NavigationContainer>
      <StatusBar
        barStyle={isDarkMode ? 'light-content' : 'dark-content'}
        backgroundColor={backgroundStyle.backgroundColor}
      />

      <Tab.Navigator>
        <Tab.Screen name="Home" component={Home} options={{headerShown: false, tabBarIcon: ({color, size}) => (
            <MaterialCommunityIcons name={'home-circle'} color={color} size={size}/> )}}/>
        <Tab.Screen name="Devices" component={Devices} options={{headerShown: false, tabBarIcon: ({color, size}) => (
              <MaterialCommunityIcons name={'devices'} color={color} size={size}/> )}}/>
        <Tab.Screen name="Production" component={Production} options={{headerShown: false, tabBarIcon: ({color, size}) => (
              <MaterialCommunityIcons name={'solar-power'} color={color} size={size}/> )}}/>
        <Tab.Screen name="Add Task" component={AddTask} options={{headerShown: false, tabBarIcon: ({color, size}) => (
              <MaterialCommunityIcons name={'plus-thick'} color={color} size={size}/> )}}/>
      </Tab.Navigator>
    </NavigationContainer>
  );
}
StyleSheet.create({
  containerrow: {
    flex: 1,
    justifyContent: 'space-evenly',
    flexDirection: 'row',
  },
  containercol: {
    flex: 1,
    justifyContent: 'space-evenly',
    flexDirection: 'column',
  },
  touchablesimp: {
    flex: 1,
    justifyContent: 'space-evenly',
  },
  button: {
    margin: 5,
    flex: 1,
    alignItems: 'center',
    backgroundColor: '#2196F3',
  },
  buttonText: {
    textAlign: 'center',
    padding: 20,
    color: 'white',
  },
});
export default App;
