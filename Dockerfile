from fedora:latest
run dnf install python3-pip -y
workdir /example
add ./* /example/
run pip3 install virtualenv
run virtualenv -p python3.10 env
run source env/bin/activate
run pip3 install -r requirements.txt

