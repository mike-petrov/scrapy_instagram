import axios from 'axios';

const server = 'https://cors-anywhere.herokuapp.com/http://104.248.137.87/api';
let token = null;

function serverRequest(link, json = {}, onPopup) {
    const headers = {
        headers: {}
    }
    if (token) {
        headers.headers.Authorization = `Bearer ${token}`;
    }

    return axios.post(server + link, json, headers).catch((error) => {
        const err = error.toString();
        // Error: Network Error
        // Error: Request failed with status code 400
        // Error: Request failed with status code 429
        let err_response;
        if (err === 'Error: Request failed with status code 429') {
            err_response = 429;
            onPopup('error', 'Слишком много запросов, попробуйте позже');
        } else if (err === 'Error: Network Error') {
            err_response = 'network';
            onPopup('error', 'Нет доступа к интернету, попробуйте позже');
        } else {
            err_response = 400;
            onPopup('error', 'Что-то пошло не так, попробуйте еще раз');
        }
        return {
            data: {
                status: 'error',
                type: err_response,
            },
        };
    });
}

export function authUser(json, onPopup) {
    return new Promise((resolve) => {
        serverRequest('/auth', json, onPopup).then((res) => {
            if (res.data && res.data.token) {
              token = res.data.token;
            }
            resolve(res.data);
        });
    });
}

export function getParse(json, onPopup) {
    return new Promise((resolve) => {
        serverRequest('/parse/get', json, onPopup).then((res) => {
            resolve(res.data);
        });
    });
}

export function addParse(json, onPopup) {
    return new Promise((resolve) => {
        serverRequest('/parse/add', json, onPopup).then((res) => {
            resolve(res.data);
        });
    });
}

export function deleteParse(json, onPopup) {
    return new Promise((resolve) => {
        serverRequest('/parse/delete', json, onPopup).then((res) => {
            resolve(res.data);
        });
    });
}

export function dataSearch(json, onPopup) {
    return new Promise((resolve) => {
        serverRequest('/search', json, onPopup).then((res) => {
            resolve(res.data);
        });
    });
}
