body = $response.body.replace(/\"chargeMT":1/g, '\"chargeMT":0').replace(/\"charge":1/g, '\"charge":0');

$done({body});