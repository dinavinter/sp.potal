import create_client_jwt from './jwt.js';
import {clientCfg} from "./configuration.js";
import './crypto-js.js'
// import {fetch} from 'https://polyfill.io/v3/polyfill.js?features=fetch-polyfill';
 
export async function getAssets(appId, container) {

    //get account 
    var account = await loadAccount();

    if(!appId)
    {
        appId= clientCfg.portal
    }
    //set org id welcome text
    var org = account["groups"]["organizations"][0];
    var orgId = org["orgId"];
    var uid = account["UID"];
 
    //get portal application assets
    var auth = await authorizationToken(appId, orgId, uid);
    var assets = auth.assets.templates;
    container.innerHTML = `<pre> app: ${appId} </br> organization: ${orgId} </br>assets:</br>${JSON.stringify(assets, undefined, 2)}</pre>`;


}
 
 

function  authorizationToken(app, orgId, uid) {
    const url = `https://cors-proc.herokuapp.com/avoid-cors/${clientCfg.plainId}/runtime/${clientCfg.apiKey}/authorization/token/${app}`;
    const body = {
        "identity": {
            "type": "user",
            "id": uid
        },
        "context": {
            "organization": orgId
        }
    };

    return fetch(url, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin', // include, *same-origin, omit
        headers: {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Authorization': "Bearer " + create_client_jwt(clientCfg.clientId, clientCfg.clientSecret),
            
        },
        redirect: 'follow',
        referrer: 'no-referrer',
        body: JSON.stringify(body),
        
    })
        .then(response => response.json());
}


function getCookie(name) {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var c = cookies[i].split('=');
        if (c[0].trim() == name) {
            return c[1];
        }
    }
    return "";
}


