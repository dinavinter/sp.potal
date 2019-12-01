
function logout() {
    gigya.socialize.logout({onError: errorHandler})
}

function showProfile() {
    var params = {
        screenSet: "Default-ProfileUpdate",
        containerID: "div",
        startScreen: "gigya-update-profile-screen",
        conflictHandling: "saveProfileAndFail"
    };
    gigya.accounts.showScreenSet(params);
}
 
function showAccountJson() { 
    gigya.accounts.getAccountInfo({ callback:showResponse, include: "groups, *" });

    function showResponse(response) {
        document.getElementById('div').innerHTML = "<pre>"+JSON.stringify(response, undefined, 2)+"</pre>";
    }

}

async function showRegistration() {

    var screenSet="Default-RegistrationLogin";
    if(window.location.hash == "#invite")
    {
        screenSet= "Invite-RegistrationLogin"
    }

    return new Promise((resolve, reject) => {
        var params = {
            screenSet: screenSet,
            containerID: 'div',
            startScreen: "gigya-login-screen",
            include:"groups",
            onAfterSubmit: r=>onCallback(r, resolve, reject)

        };
        gigya.accounts.showScreenSet(params);

    });

    function onCallback(eventObj, resolve, reject){
        if ( eventObj.response.errorCode != 0) {
            reject(eventObj.response);
            return;
        }
        document.getElementById('div').innerHTML = "";

        var account= loadAccount().catch(reject);
        account .then(r=>setAccountVariables(r));
        account .then(r=>resolve(r));

     }

}

 
function showSelfRegistration() {
    var params = {
        screenSet: "Default-OrganizationRegistration",
        containerID: "div",
        onAfterSubmit: showResponse

    };
    gigya.accounts.showScreenSet(params);

    function showResponse(eventObj) {
        if (eventObj.response.errorCode == 0) {
            document.getElementById('div').innerHTML = "<center> Request submitted</center>";
        }
    }
}


function openDelegatedAdmin() {
    gigya.accounts.b2b.openDelegatedAdminLogin({orgId:getCookie('orgId')});
}


 async function loadAccount() {
     return new Promise((resolve, reject) => {
         setTimeout(() => {
             gigya.accounts.getAccountInfo({ callback:r=>onCallback(r, resolve, reject), include: "groups, *" });
         }, 2000)
     });

     function onCallback(response, resolve, reject){
         if ( response.errorCode != 0) {
             reject(response);
             return;
         }
         setAccountVariables(response);
         resolve(response);
     }
}

function setAccountVariables(response) {
        if ( response.errorCode != 0) {
            return;
        }

        var uid= response.UID;
        var org = response["groups"]["organizations"][0];

        setCookie("uid", uid);
        setCookie("orgId", org.orgId);

    }


    function setCookie(cname, cvalue, exdays) {
        var d = new Date();
        d.setTime(d.getTime() + (exdays*24*60*60*1000));
        var expires = "expires="+ d.toUTCString();
        document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
    }


function errorHandler(e) {
    console.log(e);
}


function getCookie(name) {
    var cookies = document.cookie.split(';');
    for (var i=0; i < cookies.length; i++) {
        var c = cookies[i].split('=');
        if (c[0].trim() == name) {
            return c[1];
        }
    }
    return "";
}


