# Goolge Cloud Platform

## Deploying to a VM

TODO: add username and password behind nginx

### Create VM

First set some environment variables:

```bash
# Set these to your own values where they are empty

# Set this to your own project id
export PROJECT_ID=
# Set this to your own IP address or 0.0.0.0 to allow all
export YOUR_IP_ADDRESS=

# Set these to your own values or leave as is
export REGION=us-central1
export ZONE=us-central1-a
export INSTANCE_NAME=anomstack
export MACHINE_TYPE=e2-standard-2
export RANGE=10.0.0.0/24
```

Create a service account:

```bash
gcloud iam service-accounts create anomstack-service-account \
    --project=$PROJECT_ID \
    --description="Anomstack service account" \
    --display-name="Anomstack service account"
```

Create the VPC network for Anomstack:

```bash
# Create the VPC network
gcloud compute networks create anomstack --project=$PROJECT_ID

# Create the subnet
gcloud compute networks subnets create anomstack \
    --network=anomstack \
    --region=$REGION \
    --range=$RANGE \
    --project=$PROJECT_ID

# Create the firewall rule to allow traffic
gcloud compute firewall-rules create allow-anomstack-internal \
    --network=anomstack \
    --allow=tcp,udp,icmp \
    --source-ranges=$RANGE \
    --project=$PROJECT_ID

# Create the firewall rule to allow SSH traffic
gcloud compute firewall-rules create allow-ssh \
    --network=anomstack \
    --allow=tcp:22 \
    --source-ranges=$YOUR_IP_ADDRESS \
    --project=$PROJECT_ID

# Create the firewall rule to allow traffic to Dagster UI
gcloud compute firewall-rules create allow-anomstack-3000 \
    --network=anomstack \
    --allow=tcp:3000 \
    --source-ranges=$YOUR_IP_ADDRESS \
    --project=$PROJECT_ID
```

Create the VM:

```bash
# Create the VM
gcloud compute instances create $INSTANCE_NAME \
--project=$PROJECT_ID \
--zone=$ZONE \
--machine-type=$MACHINE_TYPE \
--service-account="anomstack-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
--network-interface="network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=anomstack" \
--create-disk="auto-delete=yes,boot=yes,device-name=$INSTANCE_NAME,image=projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20231101,mode=rw,size=50,type=projects/$PROJECT_ID/zones/$ZONE/diskTypes/pd-balanced"
```

### Configure VM

#### Docker: Install Docker

After the VM is created, SSH into it:

```bash
# SSH into the VM
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID
```

[Install Docker](https://docs.docker.com/engine/install/ubuntu/):

```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker Engine:
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify that Docker Engine is installed correctly by running the hello-world image:
sudo docker run hello-world
```

#### Docker: Install Anomstack

```bash
# clone anomstack
git clone https://github.com/andrewm4894/anomstack.git

# or

# clone repo at specific release tag
# git clone -b v0.0.1 https://github.com/andrewm4894/anomstack.git

# cd into anomstack
cd anomstack

# copy .env file
cp .example.env .env

# edit .env as needed or leave as is for local duckdb based setup

# start anomstack
sudo docker compose up -d --build
```

Once the containers are up and running, you can access the UI at `http://<your-vm-ip>:3000`.

#### Systemd: Install Anomstack

```bash
# Create anomstack user
sudo useradd -m -d /home/anomstack anomstack

# Switch to anomstack user
sudo -su anomstack

# Clone anomstack into /home/anomstack/anomstack
git clone https://github.com/andrewm4894/anomstack.git /home/anomstack/anomstack
# or
# Clone repo at specific release tag
# git clone -b v0.0.1 https://github.com/andrewm4894/anomstack.git

# cd into anomstack
cd /home/anomstack/anomstack

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install requirements
pip3 install -r requirements.txt

# Copy .env file
cp .example.env .env

# Run anomstack locally
dagster dev -f anomstack/main.py
```

Assuming everything is working, you can now create a systemd service to run anomstack.

```bash
# Create the systemd service file
cat << EOF | sudo tee /etc/systemd/system/anomstack.service
[Unit]
Description=Anomstack Service
After=network.target

[Service]
User=anomstack
WorkingDirectory=/home/anomstack/anomstack
ExecStart=/home/anomstack/anomstack/.venv/bin/python /home/anomstack/anomstack/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd to read new service file
sudo systemctl daemon-reload

# Enable and start the Anomstack service
sudo systemctl enable anomstack.service
sudo systemctl start anomstack.service
```

### Adding Your Metrics

After you add whatever environment variables you need to the `.env` file, you can add your metrics to the `metrics` folder.

#### Docker

Once ready you can stop and then rebuild the containers:

```bash
# from within anomstack folder

# stop anomstack
sudo docker compose down

# rebuild anomstack with latest metrics and changes
sudo docker compose up -d --build
```
