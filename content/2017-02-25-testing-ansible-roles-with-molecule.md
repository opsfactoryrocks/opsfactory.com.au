Title: Testing Ansible Roles with Molecule
Date: 2017-02-26
Category: Automation
Tags: ansible, confmg, molecule, docker, testinfra
Slug: ansible-role-testing-with-molecule
Authors: Michael Crilly
Summary: Developers have TDD/BDD, we have Molecule and Testinfra

When I first started programming some 20 years ago, testing was never a thing I had heard of. I'm not certain it even existed as a concept back then. In fact a recent talk from [John Romero](http://blog.felipe.rs/2017/02/25/id-software-programming-principles/) of [DOOM and Quake fame](https://en.wikipedia.org/wiki/Id_Software) clearly demonstrated that testing essentially boiled down to constantly building/compiling and running your software, over and over. I doubt TDD and BDD were a thing.

Now we're at the point in our industry when testing is a big deal, and rightly so. I believe TDD, when [considered carefully](http://david.heinemeierhansson.com/2014/tdd-is-dead-long-live-testing.html), or something of its ilk, is an important means of testing whether or not your future changes are safe; whether or not business requirements are still being met; and whether or not a new feature or patch introduces regression.

I've wanted TDD/BDD for infrastructure and configuration management for some time now, for the same reasons as above, and these days we have a great set of tools for introducing tests to our Ansible Roles. Let's take a look at these tools, delve into them a bit, and see what they can do, but first...

### Giving a bit back
Giving back to the OSS community is an important part of our industry (and something I'm guilty of not doing enough), so by the end of this article we will have introduced Molecule and Testinfra tests to an open-source Ansible Role and submitted a PR.

## Some caveats
There are some issues with these tools. For example, you have to use a systemd "enabled" Docker image otherwise it becomes next to impossible to test if a service can be started or not. Such a test is very important, of course, but for those not willing to put in the effort, just testing files, packages, users, and so on, are in place could be sufficient.

Here is a list of known issues at the time of writing:

- A systemd enabled Docker image must be used for Ubuntu and CentOS
- You might have to write a systemd service file for the package you want to install if the package maintainer doesn't provide one
- You have to be able/willing to trust unofficial images from Docker Hub
- You may be locked into the latest versions of CentOS and Ubuntu - I haven't tested earlier versions whilst researching for this article

I've been informed that Molecule 2.0 makes a lot of tasks and things easier and better, so I'm certainly looking forward to that release.

## The tools themselves
So, what tools are we devling into, exactly? Let's list them out:

- Molecule
- Testinfra
- Docker
- ansible-lint
- flake8

Although the list looks somewhat intimidating, we will actually touch on Molecule for 40% of the work, and Testinfra for the other 60%. Molecule requires little in the way of setup provided your needs are simple, but Testinfra requires writing some basic Python functions to get the tests in place.

The other tools are used and introduced transparently by Molecule.

### Prerequisites
If you want to work through this article, you'll need the following peices of software:

- Ansible 2.2.1
- Molecule
- Testinfra
- Docker (I'm using Docker on OS X)

Ansible, Molecule, and Testinfra are all installable via `pip`. Docker has an installer for OS X and I presume, Linux and Windows also.

## Our task for today
So how are we going to delve into the tools here, and what problem are we going to solve? I've selected a random Role off of Ansible Galaxy and decided we will focus on adding in Molecule and Testinfra based tests (and removing any other tests that currently exist.) The Role installs and manages an NginX installation, so it's pretty useful to begin with. It's relatively complete and ripe for testing.

The repository in question [ansible-nginx](https://github.com/nickjj/ansible-nginx) by [nickjj](https://nickjanetakis.com). I've never met the guy, but I'm sure he's a gentlemen and a scholar. His Role is decent enough for our focus today.

Because the Role only supports Ubuntu Server, we will be focusing on a single Docker image based on Ubuntu 16 which supports systemd. Getting systemd support in CentOS is something I will cover in another article, although the [CentOS Docker Hub page explains how](https://hub.docker.com/_/centos/).

## To the point
Let's crack on with the task at hand and start being somewhat useful.

Firstly, start by forking the repository above and clone your fork of it. Now we have a working Ansible Role we can introduce tests to. Molecule gives us a handy command line interface for introducing the basic configuration needed:

```
molecule init --provider docker
```

The default provider is [Vagrant](https://www.vagrantup.com/) so we override that default and replace it with Docker.

As a side note, I'm currently working on integrating AWS as a provider, as I feel using VMs instead of containers gives a much better 1-2-1 comparison.

Once the command has been execute you'll have a new file in the repository's root called `molecule.yml`, let's edit it and dump in some content:

```yaml
---
driver:
  name: docker
docker:
  containers:
    - name: ansible-nginx
      image: solita/ubuntu-systemd
      image_version: latest
      privileged: True
verifier:
  name: testinfra
```

What we're doing here is simple:

- Docker is our driver (what will give us our virtualised environment)
- We're starting up a single container based on the `solita/ubuntu-systemd` image
    + It's important to note that's run in privileged mode: this is required
    + We're using a none official Ubuntu image so that we gain systemd support
- We're setting the default (and preferred) verifier to Testinfra so that it's invoked

Next we put in place some Testinfra tests. Edit the now existing `tests/test_default.py` (because Molecule created it for us) file and dump the following into it:

```python
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_service(Service):
    present = [
        "nginx"
    ]

    if present:
        for service in present:
            s = Service(service)
            assert s.is_running
            assert s.is_enabled


def test_files(File):
    present = [
        "/etc/nginx/nginx.conf",
    ]

    if present:
        for file in present:
            f = File(file)
            assert f.exists
            assert f.is_file


def test_packages(Package):
    present = [
        "nginx"
    ]

    if present:
        for package in present:
            p = Package(package)
            assert p.is_installed


def test_directories(File):
    present = [
        "/etc/nginx",
        "/etc/nginx/ssl",
        "/etc/nginx/conf.d",
        "/etc/nginx/sites-enabled",
        "/etc/nginx/sites-available",
        "/usr/share/nginx/html",
    ]

    absent = [
        "/var/www/html",
        "/etc/nginx/sites-enabled/default",
        "/etc/nginx/sites-available/default",
    ]

    if present:
        for directory in present:
            d = File(directory)
            assert d.is_directory
            assert d.exists

    if absent:
        for directory in absent:
            d = File(directory)
            assert not d.exists
```

When it comes to the tests, they're really quite simple:

- We use a simple set of lists to contain files and directories
- Same with packages we expect to be installed
- Then we loop over the lists and check they exist or do not exist
- We have to use some magic to tell Testinfra how to reach the containers to do its tests

Those of you who are used to working with [flake8](http://flake8.pycqa.org/en/latest/) linted Python scripts (it's pretty new to me, if I'm being honest) will notice the formatting of the above Python script is indeed flake8 compliant.

Now we can actually run our tests. Here is some example output based on the above `molecule.yml` and `test_default.py` files:

```
$ molecule test
--> Destroying instances...
Stopping container ansible-nginx...
Removed container ansible-nginx.
--> Checking playbook's syntax...

playbook: playbook.yml
--> Creating instances...
Creating container ansible-nginx with base image solita/ubuntu-systemd:latest...
Container created.
--> Starting Ansible Run...

PLAY [all] *********************************************************************

TASK [setup] *******************************************************************
ok: [ansible-nginx]

...

PLAY RECAP *********************************************************************
ansible-nginx              : ok=11   changed=10   unreachable=0    failed=0

--> Idempotence test in progress (can take a few minutes)...
--> Starting Ansible Run...
Idempotence test passed.
--> Executing ansible-lint...
--> Executing flake8 on *.py files found in tests/...
--> Executing testinfra tests found in tests/...
============================= test session starts ==============================
platform darwin -- Python 2.7.12, pytest-3.0.6, py-1.4.32, pluggy-0.4.0
rootdir: /Users/michaelc/Documents/git/ansible-roles/ansible-nginx, inifile:
plugins: testinfra-1.4.5
collected 4 itemss

tests/test_default.py ....

============================ pytest-warning summary ============================
WP1 None Module already imported so can not be re-written: testinfra
================= 4 passed, 1 pytest-warnings in 1.62 seconds ==================
--> Destroying instances...
Stopping container ansible-nginx...
Removed container ansible-nginx.
```

For some, this may have taken several minutes (it did for me on my connection), but for those on fast connections, it would have been much quicker. When plugged into TravisCI or another managed CI service, you'll probably get very good speeds when it comes to packages installations.

Hopefully you're convinced adding in tests is not only very easy (minus a few little edge cases) but a good idea, too. Some benefits that comes to mind:

- Writing tests first means you're taking (business) requirements and mapping them into business tests
- Future changes to the code base can be tested against the same set of requirements to compliance
- Other users will hold the code base in higher regards knowing tests are being used to quality control
- Linting means you're following good standards and allows others to easily adopt and hack against your code base
- You can have a CI/CD process automatically run the tests and halt any delivery pipelines on failure, preventing faulty code reaching production systems

And so on.

## So what now?
Armed with this information, I think you should now go and add some tests to your Ansible Roles collection and see if your code is really idempotent.
