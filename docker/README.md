## Docker

### Anomstack Dashboard

```bash
docker build -t anomstack-dashboard -f docker/Dockerfile.anomstack_dashboard .
```

```bash
docker run -p 5003:5003 anomstack-dashboard
```

