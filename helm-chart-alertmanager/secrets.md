# How to create secrets

Test via 
```
export SLACK_URL='your_url'

$ curl ${SLACK_URL} -d '{"text": "This is a line of text in a channel.\nAnd this is another line of text."}
  
$ curl ${SLACK_URL} -d '{"text": "A very important thing has occurred! <https://alert-system.com/alerts/1234|Click here> for details!"}'
  
$ curl ${SLACK_URL} -d "{\"channel\": \"#alertmanager-webhooks\", \"username\": \"webhookbot\", \"text\": \"This is posted to #my-channel-here and comes from a bot named webhookbot.\", \"icon_emoji\": \":ghost:\"}"
```

Create a new secret named alertmanager-secrets with keys for each file in folder bar
```
$ kubectl create secret generic alertmanager-secrets --from-file=secrets/
```