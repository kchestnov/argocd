``` bash
# Create folder
curl -XPOST http://127.0.0.1:3000/api/folders -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'Authorization: Bearer glsa_tEPMbQp0YEfBoT54Dp3OCbFR8OmQ9XtX_aa9c4a31' -d '{"title": "Department DEF", "uid": "100"}'

# Create dashboard
curl -XPOST http://127.0.0.1:3000/api/dashboards/db -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'Authorization: Bearer glsa_tEPMbQp0YEfBoT54Dp3OCbFR8OmQ9XtX_aa9c4a31' -d "@dashboards/team1/test.json"
```
