import 'react-native-gesture-handler';
import React, {useEffect, useState} from 'react';
import {Alert, FlatList, Text, TextInput, TouchableHighlight, View,} from 'react-native';
import DatePicker from 'react-native-date-picker';
import {createNativeStackNavigator} from '@react-navigation/native-stack';

//local components:
import {FlatItem} from './FlatItem';
import {styles} from './stylesheet';
import {callurl, job, program, proptions, machine} from './LocalTypes';

const AStack = createNativeStackNavigator();

function DateToForm(date: Date): string{
  return date.getFullYear() + '-' +
      date.getMonth() + '-' +
      date.getDate() + ' ' +
      date.getHours() + ':' +
      date.getMinutes() + ':' +
      date.getSeconds()
}

//Requests
async function sendJob(jobparams: job): Promise<void> {

  const starT: string = DateToForm(jobparams.start);
  const deaD: string = DateToForm(jobparams.deadline);

  if (jobparams.id === undefined) {
    Alert.alert('No device selected');
  } else {
    Alert.alert(jobparams.id + ' Has been scheduled');
    try {
      await fetch(callurl + 'schedule?id=' + jobparams.id +
          '&data=' + JSON.stringify(jobparams.data) +
          '&duration=' + jobparams.duration +
          '&draw=' + jobparams.draw +
          '&deadline=' + deaD + '&start=' + starT, {
        method: 'POST'
      });
    } catch (error) {
      Alert.alert('Sorry, an error happened');
      console.log(error);

    }
  }
}

async function getPrograms(iD: string) {
  try {
    const id = encodeURIComponent(iD);
    const response = await fetch(callurl + 'ListPrograms?id=' + id, {method: 'GET', headers: {'Content-Type':'application/json'}});

    switch (response.status) {
      case 200: {
        let pdata = JSON.parse(await response.text());

        let progdata: program[] = pdata.data.programs;

        return progdata;
      }
      case 400: {
        Alert.alert('Not Authorized');

        let progdata: program[] = [{constraint: 'Unauthorized', key: 'Unauthorized' }];

        return progdata;
      }
      case 500: {
        let progdata: program[] = [{constraint: 'Empty', key: 'Empty' }];

        Alert.alert('This device has no programs, Please go back');

        return progdata;
      }
      default: {
        let progdata: program[] = [{constraint: 'Empty', key: 'Empty' }];

        Alert.alert('Unimplemented Stuff, good job finding it');

        return progdata;
      }
    }
  } catch (error) {
    Alert.alert('Sorry, an error happened');
    console.log(error);

  }
  let fakejob: program[] = [{constraint: 'error', key: 'error' }];

  return fakejob;
}

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

function doJob(job: job, navigation: any): void{

  if((job.draw != '' && job.duration != '') && (job.draw != '0' && job.duration != '0') && (job.deadline > job.start) && (((job.deadline.getTime() - job.start.getTime())/1000) > parseInt(job.duration))) {
    sendJob(job).then();
    navigation.navigate('Devices');
  }else{
    Alert.alert('Invalid parameters');
  }
}

//Screens below
const DeadlineScreen = ({navigation, route}: any) => {
  const [date, setDate] = useState(new Date());
  const [sdate, setsDate] = useState(new Date());
  const [draw, setDraw] = useState<string>('0');
  const [duration, setDura] = useState<string>('0');
  const deviceID = route.params.id;
  const clownkey: any[] = [];
  const j: job = {id: deviceID, data: {data: {key: route.params.key,
        options: clownkey}},
    duration: duration, draw: draw, deadline: date, start: sdate};

  for(let x = 0; route.params.options.length > x; x++){
    j.data.data.options.push({key: route.params.geninf[x].key, value: route.params.options[x]});
  }
  function changeToNum(text: string){
    return text.replace(/[^0-9]/g, '');
  }
  return(<View style={styles.containercol}>
    <Text>Start time</Text>
    <DatePicker
        style={styles.datePicker}
        date={sdate} onDateChange={setsDate}
        minimumDate={new Date()}
        fadeToColor={'#baeda9'}
    />
    <Text>Deadline</Text>
    <DatePicker
        style={styles.datePicker}
        date={date} onDateChange={setDate}
        minimumDate={new Date()}
        fadeToColor={'#baeda9'}
    />
    <Text>Draw (kw)</Text>
    <TextInput style={styles.textinp} keyboardType={'numeric'} onChangeText={(text) => setDraw(changeToNum(text))} value={draw}/>
    <Text>Duration (s)</Text>
    <TextInput style={styles.textinp} keyboardType={'numeric'} onChangeText={(text) => setDura(changeToNum(text))} value={duration}/>
    <TouchableHighlight onPress={() => doJob(j, navigation)}>
      <Text>Schedule Task</Text>
    </TouchableHighlight>
  </View>);
};
const TaskOptionsScreen = ({navigation, route}: any) => {
  const [programs, setPrograms] = useState<program[]>();
  const deviceID = route.params.dID;

  useEffect(() => {
    async function getdata(){
      const programdata = await getPrograms(deviceID);

      setPrograms(programdata);
    }

    getdata().then();
  }, []);

  const renderitem = ({item}: {item: program}) => {
    const backgroundcolor = '#77c967';
    const color = '#000000';

    return (
        <FlatItem
            item={item.key}
            backgroundColor={backgroundcolor}
            textColor={color}
            onpress={() => {navigation.navigate('Task Specifics', {id: deviceID, prog: item.key});
            }}
        />
    );
  };

  return (
    <View style={styles.containercol}>
      <FlatList
          ItemSeparatorComponent={({highlighted}) => (
              <View style={[styles.sepStyle, highlighted && {marginLeft: 0}]} />
          )}
          data={programs}
          keyExtractor={item => item.key}
          renderItem={renderitem}
          contentContainerStyle={styles.flatList}
      />
    </View>
  );
};

const TaskSpecifications = ({navigation, route}: any) => {
  const [key, setkey] = useState<string>('');
  const [prodata, setProdata] = useState<proptions[]>([]);
  const [selectvalue, setValue] = useState<string[]>([]);
  const id = route.params.id;
  const prog = route.params.prog;
  const flatlistarray = [];


  function handleflatupdate(index: number, val: string){

    if(selectvalue.length <= index || selectvalue.length === 0){

      setValue([...selectvalue, val]);
    }else{
      const nextVal: string[] = selectvalue.map((s, i) => {
        if(index === i){
          return val;
        }else{
          return s;
        }


      });
      setValue(nextVal);
    }
  }

  useEffect(() => {
    async function programSpec(id: string, program: string) {
      try {
        const Id = encodeURIComponent(id);
        const prog = encodeURIComponent(program);
        const response = await fetch(callurl + 'ListProgramOptions?id=' + Id + '&program=' + prog, {method: 'GET', headers: {'Content-Type':'application/json'}});
        let optionargs: proptions[] = [];
        const jdata = JSON.parse(await response.text());

        setkey(jdata.data.key);
        for (let i = 0; i < jdata.data.options.length; i++) {
          optionargs.push({
            vals: jdata.data.options[i].constraints.allowedvalues,
            key: jdata.data.options[i].key,
            type: jdata.data.options[i].type,
            unit: jdata.data.options[i].unit,
          });
        }


        setProdata(optionargs);
      } catch (error) {
        Alert.alert('The Following Error has occurred:' + error);
      }

    }
    programSpec(id, prog).then();
  }, []);


  if (prodata.length <= 0) {
    return (<View>
      <Text>Loading</Text>
    </View>);
  } else {
    for(let i = 0; i < prodata.length; i++){
      flatlistarray.push(
          <FlatList
          ItemSeparatorComponent={({highlighted}) => (
              <View style={[styles.sepStyle, highlighted && {marginLeft: 0}]} />
          )}
          data={prodata[i].vals}
          renderItem={({item}: { item: string}) => {
            const backgroundColor = item === selectvalue[i] ? '#38702d' : '#77c967';
            const textcolor = item === selectvalue[i] ? '#77c967' : '#38702d';
            return (<FlatItem
                item={item}
                backgroundColor={backgroundColor}
                textColor={textcolor}
                onpress={() => handleflatupdate(i, item)}
            />);
          }}
          keyExtractor={(item, index) => i.toString() + index.toString()}
          extraData={[prodata, selectvalue]}
          contentContainerStyle={styles.flatList}
      />)
    }
    return (<View style={styles.containercol}>
      {flatlistarray}
      <TouchableHighlight style={styles.touchablesimp} onPress={() => navigation.navigate('Deadline set', {id: id, program: prog, options: selectvalue, geninf: prodata, key: key})}>
        <Text>Confirm choices</Text>
      </TouchableHighlight>
    </View>);
  }
};

const AddTask = ({navigation}: any) => {
  const [dData, setdData] = useState<machine[]>();

  useEffect(() => {
    async function getdata(){
      const devicedata = await searchDevices();
      setdData(devicedata);
    }
    getdata().then();
  }, []);


  const renderitem = ({item}: {item: machine}) => {
    const backgroundcolor = '#77c967';
    const color = '#000000';

    return (
      <FlatItem
        item={item.name}
        backgroundColor={backgroundcolor}
        textColor={color}
        onpress={() => navigation.navigate('Task Options', {dID: item.id})}
      />
    );
  };

  return (
      <FlatList
        ItemSeparatorComponent={({highlighted}) => (
          <View style={[styles.sepStyle, highlighted && {marginLeft: 0}]} />
        )}
        data={dData}
        renderItem={renderitem}
        keyExtractor={item => item.id.toString()}
        contentContainerStyle={styles.flatList}
      />
  );
};

//Main component
function AddTaskStack() {
  return (
    <AStack.Navigator>
      <AStack.Screen name={'Devices'} component={AddTask} />
      <AStack.Screen name={'Task Options'} component={TaskOptionsScreen} />
      <AStack.Screen name={'Task Specifics'} component={TaskSpecifications}/>
      <AStack.Screen name={'Deadline set'} component={DeadlineScreen}/>
    </AStack.Navigator>
  );
}

export default AddTaskStack;
