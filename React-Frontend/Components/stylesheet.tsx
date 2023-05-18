import {StyleSheet} from "react-native";

export const styles = StyleSheet.create({
    containercol: {
        flexGrow: 1,
        justifyContent: 'space-evenly',
        alignContent: 'stretch',
        backgroundColor: '#baeda9',
        height: '100%',
    },
    touchablesimp: {
        justifyContent: 'space-evenly',
        alignItems: 'center',
        width: 'auto',
        backgroundColor: '#008080',
        alignSelf: 'stretch',
        height: '5%',
        padding: '1%',
    },
    button: {
        margin: 5,
        flex: 0.5,
        width: '50%',
        alignItems: 'center',
        backgroundColor: '#2196F3',
    },
    buttonText: {
        color: '#ffffff',
    },
    listItem: {
        textAlign: 'center',
        backgroundColor: '#74f74f',
    },
    listItText: {
        textAlign: 'center',
        color: '#000000',
        fontSize: 20,
    },
    flatList: {
        justifyContent: 'space-evenly',
        alignItems: 'stretch',
        flexGrow: 1,
        overflow: "scroll",
        backgroundColor: '#baeda9',
    },
    sepStyle: {
        color: '#000000',
        height: '20%',
        width: '10%',
    },
    deviceView: {
        flex: 1,
        backgroundColor: '#baeda9',

    },
    datePicker: {
        alignSelf: "center",
        height: 100,
    },
    textinp: {
        margin: 5,
        borderWidth: 4,
        borderColor: '#ffffff'
    }
});
