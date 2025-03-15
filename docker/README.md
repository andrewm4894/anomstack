## Docker

### Anomstack Dashboard

```bash
docker build -t anomstack-dashboard -f docker/Dockerfile.anomstack_dashboard .
```

```bash
docker run -p 5000:5000 anomstack-dashboard
```

