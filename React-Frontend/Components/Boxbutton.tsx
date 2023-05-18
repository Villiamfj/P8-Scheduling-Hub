import {StyleSheet, Text, TouchableHighlight, View} from 'react-native';
import React from 'react';

type TouchableProps = {
  ButtonText: string;
};

function Boxbutton(props: TouchableProps): JSX.Element {
  return (
    <TouchableHighlight style={styles.touchablesimp} underlayColor="#FF1694">
      <View style={styles.button}>
        <Text style={styles.buttonText}>{props.ButtonText}</Text>
      </View>
    </TouchableHighlight>
  );
}
export function Childbox(props: any): JSX.Element {
  return (
    <View style={[styles.containerrow]}>
      {props.left}
      {props.right}
    </View>
  );
}

export default Boxbutton;

const styles = StyleSheet.create({
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
