# A tutorial on deploying python web applications 

This is a short tutorial that explains how to create and deploy a dockerised 
python web-application. Such application takes a list of numbers as input and 
returns the corresponding sum. It is built using Flask with ngnix, and deployed 
using Ansible and Vagrant. 

# Quick start

The code in the project folder is ready-to-go. If you don't care about the 
step-by-step explanation, you can get it up and running with few commands:

````
# Build the vagrant VM
vagrant up

# Execute the app (and get the result)
# This sums 1+2 and returns 3
curl -d "[1,2]" -X POST http://127.0.0.1:8080/sum_list

# Stop and destroy the vagrant VM
vagrant halt
vagrant destroy
````

# Step-by-step tutorial

This is a thorough explanation of the entire code. It covers the following:

 1. [Create a virtual machine](#Create-a-virtual-machine)
 2. [Ansible](#Ansible)
 3. [Docker](#Docker)
 4. [Flask nginx and supervisor](#Flask-nginx-and-supervisor)
 5. [Finally some python](#Finally-some-python)

## Create a virtual machine

In order to keep our local environment as clean as possible and to simulate
an "external" production server in which to deploy our app, we are going to 
create a virtual machine were all necessary dependencies and the app itself
will be installed. This will be done with Vagrant.

### What is Vagrant?

Vagrant is an open-source software aimed to manage virtual machines, developed 
by HashiCorp (`https://www.vagrantup.com/intro/index.html`). 

If on a Mac, you 
can simply install it with:

````
brew cask install Vagrant
brew cask install virtualbox # needed by Vagrant
````

### How to use Vagrant

Once Vagrant is installed, we need a Vagrantfile in order to setup its 
configuration. There is already a ready-to-go Vagrantfile in the project
 folder. However, if you want to create a clean one, you can run:

````
vagrant init 
````

This will place a Vagrantfile in the current directory. Now, to create the VM 
the only needed command is:

````
vagrant up
````

N.B. Don't try to do this before reading the next point (What's inside the 
Vagrantfile). If you created a clean file, you will need a little modification
to get it running.

This will build the VM and get it up and running in a couple of minutes. You 
can then enter the VM by typing 

````
vagrant ssh
````

Finally, you can stop and destroy the machine with:

````
vagrant halt
vagrant destroy
````
 
### What's inside the Vagrantfile

The default Vagrantfile is pretty big, but most of it is commented. I will 
shortly go through the uncommented lines below, ignoring the rest. You can find
more information at: `https://www.vagrantup.com/docs/vagrantfile/version.html`.

To start with, Vagrant defines the style of the configuration. This is done 
with:

````
Vagrant.configure("2") do |config|
````

The 2 represent the version used in the configuration file. 

The following uncommented line is:

````
config.vm.box = "base"
````

This defines the type of box used for the VM. "base" is a placeholder. Vagrant
does not run with such configuration. You need to change it to an existing 
box name as:

````
config.vm.box = "ubuntu/xenial64"
````

This will deploy Ubuntu as soon as we start the VM. There is nothing
else you need. You can now try to start the VM.

If you did not create a default Vagrantfile but you look inside the file 
given with the project, you will realise that it is a bit more complicated.
It includes the following:

````
  config.vm.define :dockervm do |dockervm|
        # name of host
        dockervm.vm.hostname = "dockervm"
        # OS
        dockervm.vm.box = "ubuntu/xenial64"
        # forward port from host to guest (docker)
        config.vm.network "forwarded_port", guest: 80, host: 8080

        # pip configuration
        dockervm.vm.provision "shell",inline: <<-SHELL
                export DEBIAN_FRONTEND=noninteractive
                apt-get update
                apt-get install -y python-pip
        SHELL

        # ansible configuration
        dockervm.vm.provision "ansible" do |ansible|
                ansible.verbose = "v"
                ansible.playbook = "playbook.yml"
                ansible.extra_vars = 
                { ansible_python_interpreter:"/usr/bin/python" }
        end
  end
````

The "ansible configuration" part is explained in the next block, 
let's look at the rest for a moment. 

At first we define a virtual machine called "dockervm" (Vagrant 
support multiple virtual machines working together). Again, we define the
operating system, and we define ports that we will use to communicate with such
VMs. The following part is instead dedicated to installing pip, within the 
"dockervm". Here we tell Vagrant to run the installation of pip through a shell
command.

## Ansible

Ansible is an orchestration engine that automates deployment and configuration
management. It is developed by Ansible Inc. \
Documentation is available at: `https://docs.ansible.com` . 
It can be installed via pip.

### How to use Ansible

Ansible is based on the following key elements:

 - Playbooks: a bunch of yml files used by ansible to know which commands
to send to which server.
 - Tasks: an action written in the playbook that has an associated name.
 - Hosts: remote machines managed by ansible that have an associated IP.
 - Roles: a set of sub-tasks used within the playbooks. Roles are generally 
 indipendent and they allow to keep the deployment clean and orderly. They 
 can be associated to specific hosts.
 - Many other things that are not relevant in this example.
 
Ansible reads the commands from the playbooks, connects to the desired nodes
via ssh and runs the package installation (and whatever else we need) on such 
nodes.

### The playbook

There is one playbook in the project folder, called "playbook.yml". This is 
the main script that tells Ansible what to do. The first part of the playbook 
defines its name, on which hosts to act, and other few things. The second part,
"pre_tasks", is the first thing executed by Ansible. In this specific case, 
we check whether python is there (if not, it is installed), and we load some
environment variables (which are setup in the "variables/default_var.yml"). 

These variables are:
 - source_code_dir: where the python code is
 - dest_code_dir: where the app will be installed
 - docker_group_members: which users can access the docker socket
 
The last part defines which roles need to be run. These have indipendent yml 
files in the "roles" folder. 

The "base" role is dedicated to configuring docker. 
The other ("test") is dedicated to building docker, and then testing the 
application. 

### Ansible in Vagrant

As I mentioned above, a part of the Vagrantfile is used to run the Ansible 
notebooks:

```
dockervm.vm.provision "ansible" do |ansible|
    ansible.verbose = "v"
    ansible.playbook = "playbook.yml"
    ansible.extra_vars = { ansible_python_interpreter:"/usr/bin/python" }
end
```     

This little piece of code tells Vagrant to run Ansible in verbose mode,
to run the "playbook.yml" playbook and using the python interpreter at that 
location.

## Docker

Docker is a tool for containerisation that allows to package applications with 
all the needed libraries and deploy them in a consistent way, independently
from the machine and relative settings. More information at: 
`https://www.docker.com` .

### How to use Docker

Docker is based on a list of commands that can be found in one (or more)
Dockerfile(s). The one used for the deployment of our application is stored 
under `code/Dockerfile`. The Dockerfile usually starts with a `FROM` that tells 
docker which image to use as base for the creation of the container. Such 
images are stored on the dockerhub. You can find some examples at:
`https://hub.docker.com` . Additional libraries can then be installed on top
of this image, together with the code we are interested in.

To make things easier we use docker-compose to build and run our docker image. 
Docker-compose is a tool to orchestrate multiple docker container, which use a 
quite simple grammar. It needs a separate yml file called `docker-compose.yml`.
Such files defines which version of compose to use and some other features as
which port to expose. 

If you want to bypass the deployment on Vagrant, you can get our code up and 
running by simply typing:

```
docker-compose up
```

Once you do so (within the code directory), you can test that the program 
actually works by asking:

```
curl -d "[1,2]" -X POST http://localhost:80/sum_list 
```

It should return 3. The container can be killed with:

```
docker-compose down
```

### The Dockerfile

The Dockerfile is quite a complicated object. I won't go through it step by 
step in the README file, but it has been commented properly and it should be 
self explanatory. 


## Flask nginx and supervisor

So, let's talk a bit about architecture. First we have a Vagrant machine. That
can be considered as our external server, where we want our code to run, and 
which should be able to answer to our http request when we call the right IP
and port. By default this IP-port will be: `127.0.0.1:8080` , as defined in 
the Vagrantfile. 

Inside such "server", we have a docker container. The docker container is 
where our python application will run. In the Vagrantfile we have also defined
that whenever the port 8080 is called, the request is forwarded to port 80. 
The container therefore needs to listen to port 80 and forward the request to
our python application. In fact, the docker-compose file defines that whatever
goes in from port 80 is passed to port 80 inside the container itself. 

Inside the container we have quite a complicate setup. 

First we have Flask. Flask (`https://palletsprojects.com/p/flask/`) 
is a web framework written in Python. 
The Flask app is defined in `code/app/main.py` . That's a simple piece
of code. It imports our code, which is stored in `code/yabasic` , and it 
defines 3 endpoints:
 - `/`: a health check. It simply returns 'Hello, World!' .
 - `/sum_list`: the main endpoint that returns the sum of the list elements.
 - `/sum_list_test`: a copy of the endpoint above, for testing purposes.
 
Flask and Docker could be used as they are. However, Flask built-in server
is not suitable for production and it does not scale well (it serves only one
request per time). A much more robust option is ngnix. However, ngnix is unable 
to run python scripts, therefore it needs to communicate with Flake. This 
communication is done by using the uwsgi protocol, via the uWSGI web server. 

To recap: the request reaches the docker container. The docker container passes
such request to nginx which then communicates with Flask via uwsgi protocol.
Flask decode the request, process the code and passes back the answer. 

To make things a bit more complicated, Docker let us initialise the container 
with one and only one process. So how can we run ngnix, uWSGI and Flask all 
together? With supervisor. Supervisor let us coordinates the different parts
and take care of restarting processes when they die. 

Let's go in the detail of the different configurations:

 - supervisor: supervisor is started by docker (it is in fact the last command
    in the Dockerfile that gives the green light to supervisor). 
    It is configured via the `supervisord.conf` file. 
    This tells supervisor to start both uWSGI and ngnix. 
 - ngnix: this is configured with `ngnix.conf` . I am not going through this. 
    Just note that `ngnix.conf` calls an addition configuration file: 
    `flask-site-ngnix.conf`
 - uwsgi: as I mentioned, Flask is not run directly by ngnix. It is actually 
    called by uWSGI. This is done by `app/wsgi.py`. uWSGI has also and 
    additional configuration file called `uwsgi.ini`. If you remember, this is 
    called by the `supervisor.conf`.  
    
## Finally some python

The python code is stored under `code/yabasic`. It is composed of few
functions that are called by the Flask application. It is so basic that
I refuse to go through it :) 


 



