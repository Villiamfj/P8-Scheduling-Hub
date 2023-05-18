import 'react-native-gesture-handler';
import React from 'react';
import {
    Text,
    TouchableHighlight,

} from 'react-native';

//Local components
import {styles} from "./stylesheet";
import {ItemS} from "./LocalTypes";

function splitOndot(splittee: string): string{
    const splitarray: string[] = splittee.split('.');

    return splitarray[splitarray.length - 1];
}

export const FlatItem = ({item, backgroundColor, textColor, onpress}: ItemS) => (
    <TouchableHighlight underlayColor={'#69b35b'} onPress={onpress} style={[styles.listItem, {backgroundColor}]}>
        <Text style={[styles.listItText, {color: textColor}]}>{splitOndot(item)}</Text>
    </TouchableHighlight>
);
