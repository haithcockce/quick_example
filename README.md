# Containerized Tradedesk pull/Snowflake push thingy

- You should be able to do most of this with the `start_eample.sh` executable. Alternatively, you can do it manually. 

### Requirements

- Docker/Podman
- Docker-compose

### Prebuild and pre-execution stuff

You will need to fill in all the stuff on a per-customer basis. 

- To put in"key" crentials and general query info, edit `quick_example.yaml`'s environment section.
    - The environment section is a series of key-value pairs that become environment variables in the container. 
	- These are used in the python script to do specific queries and auths. 
	- The "key" part of the key-value pairs is the variable name. 
	- The "value" part of hte key-value pairs is the value the variable has. 
	- As such, if the snowflake username/password is "example" and "badpass", you would update them to the following: 
	    - "SNOWSQL_USER=example"
		- "SNOWSQL_PASSWORD=badpass"

- Specific queries need to go in `example.py`. 
- You can change the name of the docker image by using custom values in `$IMAGE_NAME`. 

### Manual build and execution

1. Build the container

    ```bash
	$ docker build -t $IMAGE_NAME .
	```

2. Run the container

    ```bash
	$ docker-compose -f quick_example.yaml up -d
	```

