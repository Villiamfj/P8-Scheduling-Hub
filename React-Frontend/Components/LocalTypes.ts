

export const callurl = 'http://10.0.2.2:8080/';

export type program = {
    constraint: any,
    key: string,
};

export type status = {
    devicename: string,
    running: boolean,
    finished: boolean,
};

export type proptions = {
    vals: string[],
    key: string,
    type: string,
    unit: string,
}

export type job = {
    id: string | undefined,
    data: any,
    duration: string,
    draw: string,
    deadline: Date,
    start: Date,
}

export type machine = {API_type: string,
    brand: string,
    connected: boolean,
    enumber: string,
    id: number,
    name: string,
    type: string,
    vib: string};

export type ItemS = {item: string,
    backgroundColor: string,
    textColor: string,
    onpress: () => void;};
