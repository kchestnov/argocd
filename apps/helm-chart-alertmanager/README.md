### Standalone Alertmanager installation

#### How to create secrets


Create a new secret named alertmanager-secrets with keys for each file in folder bar
```
$ kubectl create secret generic alertmanager-secrets --from-file=secrets/
```

Modify values.yaml 
```
  extraSecretMounts:
    - name: alertmanager-secrets
      mountPath: /etc/alertmanager-secrets/
      secretName: alertmanager-secrets
      readOnly: true
      
  config:
    enabled: true
    global:
      # Mapped to extraSecretMounts created manually
      slack_api_url_file: /etc/alertmanager-secrets/slack_url_example
```


#### Test SLACK API
```
export SLACK_URL='your_url'

$ curl ${SLACK_URL} -d '{"text": "This is a line of text in a channel.\nAnd this is another line of text."}
  
$ curl ${SLACK_URL} -d '{"text": "A very important thing has occurred! <https://alert-system.com/alerts/1234|Click here> for details!"}'
  
$ curl ${SLACK_URL} -d "{\"channel\": \"#alertmanager-webhooks\", \"username\": \"webhookbot\", \"text\": \"This is posted to #my-channel-here and comes from a bot named webhookbot.\", \"icon_emoji\": \":ghost:\"}"
```