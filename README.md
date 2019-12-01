# b2b-test
 
https://dinavinter.github.io/b2b-portal/index.html

 
**Site config**
* Go to "Site Settings" in CDC and add .*/github.io/* and .*/localhost/* to trusted urls
* Enable site under "Organization management"
  
 
********** **Config** **********
* Go to "Client config"
    * set your apiKey, domain and portal app id
    * press "save"  

********** **Working local** **********
* Clone repository or create your own using "template repository"
* Run server\install.bat
* In power shell:
    * cd  .\server
    * py .\server.py

* Browse https:\\localhost:4580\index.html
     
    
** delegated admin flow **  
*Invite new user to organization and associate with delegated admin role using plainId console.
*Go to test page and login with the password you got through invitation email
*Press on organization management 
*You should be redirected to plain id console in organization scope

** view assets **  
*Invite new user to organization and associate with role that linked to a policy using plainId console.
*Go to test page and login with the password you got through invitation email
*Press on get assets
*You view user assets 



