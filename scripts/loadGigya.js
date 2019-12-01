import {clientCfg, load_config} from "./configuration.js";
import {sites} from "./default-sites.js";

export default function loadGigya(domain,   apiKey) {
    var gigurl = `https://cdns.${domain}.gigya.com/js/socialize.js?apikey=${apiKey}`;
	var eScript = document.createElement("script");
	eScript.src = gigurl;
	document.head.appendChild(eScript);
	
}

if(!clientCfg.apiKey)
{
	load_config(sites['slo-gs'])
}

loadGigya(clientCfg.domain, clientCfg.apiKey);